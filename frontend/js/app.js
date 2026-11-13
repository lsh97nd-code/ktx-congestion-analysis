'use strict';

/*
 * KTX 예매난 위험도 분석 및 대체 이동수단 선택 AI 비서
 * frontend/js/app.js
 *
 * 연결 API
 * - GET  /api/data/summary
 * - GET  /api/data
 * - POST /api/data
 * - DELETE /api/data/{document_id}
 * - POST /api/chat
 * - GET  /api/conversations
 */

const API_BASE_URL = String(window.APP_CONFIG?.API_BASE_URL || '')
  .trim()
  .replace(/\/+$/, '');

const SEED_DATA_END_DATE = '2023-12-01';
const TEST_DATA_MIN_DATE = '2024-01-01';
const DATA_LIST_LIMIT = 12;
const SVG_NAMESPACE = 'http://www.w3.org/2000/svg';
const CHART_WIDTH = 900;
const CHART_HEIGHT = 320;
const CHART_MARGIN = Object.freeze({ top: 22, right: 24, bottom: 54, left: 76 });
const EXPORT_FIELDS = Object.freeze(['id', 'date', 'value', 'memo']);
let currentDataItems = [];

const elements = {
  refreshSummaryButton: document.getElementById('refresh-summary-button'),
  summaryMessage: document.getElementById('summary-message'),
  summaryPeriod: document.getElementById('summary-period'),
  summaryCount: document.getElementById('summary-count'),
  summaryAverage: document.getElementById('summary-average'),
  summaryMax: document.getElementById('summary-max'),
  summaryMin: document.getElementById('summary-min'),
  summaryTrend: document.getElementById('summary-trend'),
  summaryChange: document.getElementById('summary-change'),
  summaryRecentLabel: document.getElementById('summary-recent-label'),
  summaryPreviousLabel: document.getElementById('summary-previous-label'),
  summaryRecentAverage: document.getElementById('summary-recent-average'),
  summaryPreviousAverage: document.getElementById('summary-previous-average'),
  demandChartWrap: document.getElementById('demand-chart-wrap'),
  demandChart: document.getElementById('demand-chart'),
  demandChartSummary: document.getElementById('demand-chart-summary'),
  demandChartEmpty: document.getElementById('demand-chart-empty'),
  demandChartDetails: document.getElementById('demand-chart-details'),
  demandChartTableBody: document.getElementById('demand-chart-table-body'),

  dataForm: document.getElementById('data-form'),
  dataDate: document.getElementById('data-date'),
  dataValue: document.getElementById('data-value'),
  dataMemo: document.getElementById('data-memo'),
  addDataButton: document.getElementById('add-data-button'),
  refreshDataButton: document.getElementById('refresh-data-button'),
  downloadCsvButton: document.getElementById('download-csv-button'),
  downloadJsonButton: document.getElementById('download-json-button'),
  dataMessage: document.getElementById('data-message'),
  dataList: document.getElementById('data-list'),

  chatForm: document.getElementById('chat-form'),
  messageInput: document.getElementById('message-input'),
  submitButton: document.getElementById('submit-button'),
  formMessage: document.getElementById('form-message'),

  loadingArea: document.getElementById('loading-area'),
  answerArea: document.getElementById('answer-area'),
  answerText: document.getElementById('answer-text'),
  conversationId: document.getElementById('conversation-id'),
  modelName: document.getElementById('model-name'),

  refreshButton: document.getElementById('refresh-conversations-button'),
  historyMessage: document.getElementById('history-message'),
  conversationList: document.getElementById('conversation-list'),
};

function setStatus(element, message = '', type = '') {
  element.textContent = message;
  element.classList.remove('error', 'success');

  if (type) {
    element.classList.add(type);
  }
}

function setElementHidden(element, hidden) {
  if (hidden) {
    element.setAttribute?.('hidden', '');
  } else {
    element.removeAttribute?.('hidden');
  }
}

function setChatLoading(isLoading) {
  elements.loadingArea.hidden = !isLoading;
  elements.submitButton.disabled = isLoading;
  elements.messageInput.disabled = isLoading;
  elements.submitButton.textContent = isLoading ? '분석 중...' : '질문하기';
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || '';

  if (contentType.includes('application/json')) {
    return response.json();
  }

  const text = await response.text();
  return text ? { detail: text } : {};
}

function getErrorMessage(data, fallbackMessage) {
  if (!data) {
    return fallbackMessage;
  }

  if (typeof data.detail === 'string') {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => item?.msg || JSON.stringify(item))
      .join(' / ');
  }

  if (typeof data.message === 'string') {
    return data.message;
  }

  return fallbackMessage;
}

function getChatAnswer(data) {
  return (
    data.answer ??
    data.assistant_message ??
    data.response ??
    data.message ??
    'AI 답변을 받았지만 표시할 답변 필드를 찾지 못했습니다.'
  );
}

function getConversationId(data) {
  return data.conversation_id ?? data.id ?? '-';
}

function getModelName(data) {
  return data.model ?? data.model_name ?? '-';
}

function formatNumber(value, maximumFractionDigits = 0) {
  if (value === null || value === undefined || value === '') {
    return '-';
  }

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return String(value);
  }

  return new Intl.NumberFormat('ko-KR', {
    maximumFractionDigits,
  }).format(number);
}

function formatSummaryDate(value) {
  if (!value) {
    return '-';
  }

  const match = String(value).match(/^(\d{4})-(\d{2})/);

  if (!match) {
    return String(value);
  }

  return `${match[1]}.${match[2]}`;
}

async function fetchSummary() {
  const response = await fetch(`${API_BASE_URL}/api/data/summary`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `데이터 요약 조회에 실패했습니다. (HTTP ${response.status})`
      )
    );
  }

  return data;
}

function renderSummary(summary) {
  if (!summary || typeof summary !== 'object' || Array.isArray(summary)) {
    throw new Error('데이터 요약 응답 형식이 올바르지 않습니다.');
  }

  const periodStart = formatSummaryDate(summary.period_start);
  const periodEnd = formatSummaryDate(summary.period_end);
  const changePct = summary.change_pct;
  const trendWindowMonths =
    Number.isInteger(summary.trend_window_months) && summary.trend_window_months > 0
      ? summary.trend_window_months
      : 12;

  elements.summaryPeriod.textContent = `${periodStart} ~ ${periodEnd}`;
  elements.summaryCount.textContent = formatNumber(summary.count);
  elements.summaryAverage.textContent = formatNumber(summary.average, 2);
  elements.summaryMax.textContent = formatNumber(summary.max);
  elements.summaryMin.textContent = formatNumber(summary.min);
  elements.summaryTrend.textContent =
    typeof summary.trend === 'string' && summary.trend.trim()
      ? summary.trend
      : '-';
  elements.summaryRecentLabel.textContent = `최근 ${trendWindowMonths}개월 월평균`;
  elements.summaryPreviousLabel.textContent = `직전 ${trendWindowMonths}개월 월평균`;
  elements.summaryRecentAverage.textContent = formatNumber(
    summary.recent_window_avg !== undefined
      ? summary.recent_window_avg
      : summary.recent_12_month_avg,
    2
  );
  elements.summaryPreviousAverage.textContent = formatNumber(
    summary.previous_window_avg !== undefined
      ? summary.previous_window_avg
      : summary.previous_12_month_avg,
    2
  );

  const numericChange = Number(changePct);
  const hasValidChange =
    changePct !== null &&
    changePct !== undefined &&
    changePct !== '' &&
    Number.isFinite(numericChange);

  if (!hasValidChange) {
    elements.summaryChange.textContent = '변화율 계산 데이터 부족';
    return;
  }

  const sign = numericChange > 0 ? '+' : '';
  elements.summaryChange.textContent = `직전 ${trendWindowMonths}개월 대비 ${sign}${formatNumber(
    numericChange,
    2
  )}%`;
}

async function loadSummary({ silent = false } = {}) {
  elements.refreshSummaryButton.disabled = true;

  if (!silent) {
    setStatus(elements.summaryMessage, '데이터 요약을 불러오는 중입니다.');
  }

  try {
    const summary = await fetchSummary();
    renderSummary(summary);

    if (!silent) {
      setStatus(
        elements.summaryMessage,
        '현재 Firestore 데이터 요약을 불러왔습니다.',
        'success'
      );
    }
  } catch (error) {
    console.error('GET /api/data/summary 오류:', error);

    setStatus(
      elements.summaryMessage,
      `데이터 요약을 불러오지 못했습니다. ${error.message}`,
      'error'
    );
  } finally {
    elements.refreshSummaryButton.disabled = false;
  }
}


function getDataItems(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  if (Array.isArray(data?.data)) {
    return data.data;
  }

  if (Array.isArray(data?.records)) {
    return data.records;
  }

  return [];
}

function normalizeDateValue(value) {
  if (!value) {
    return '';
  }

  if (typeof value === 'string') {
    return value.slice(0, 10);
  }

  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return value.toISOString().slice(0, 10);
  }

  if (typeof value === 'object') {
    const seconds = Number(value._seconds ?? value.seconds);

    if (Number.isFinite(seconds)) {
      return new Date(seconds * 1000).toISOString().slice(0, 10);
    }
  }

  return String(value).slice(0, 10);
}

function getDataDocumentId(item) {
  return (
    item?.document_id ??
    item?.id ??
    normalizeDateValue(item?.date) ??
    ''
  );
}

function getDataDate(item) {
  const value = item?.date ?? getDataDocumentId(item);
  return normalizeDateValue(value) || '-';
}

function getMonthIndex(dateValue) {
  const match = String(dateValue).match(/^(\d{4})-(\d{2})-01$/);
  if (!match) {
    return null;
  }

  const year = Number(match[1]);
  const month = Number(match[2]);
  if (!Number.isInteger(year) || month < 1 || month > 12) {
    return null;
  }

  return year * 12 + month - 1;
}

function buildDemandChartModel(items) {
  const byMonth = new Map();

  for (const item of Array.isArray(items) ? items : []) {
    const date = getDataDate(item);
    const monthIndex = getMonthIndex(date);
    const value = Number(item?.value);
    if (monthIndex === null || !Number.isFinite(value) || value < 0) {
      continue;
    }

    byMonth.set(monthIndex, { date, monthIndex, value });
  }

  const records = [...byMonth.values()].sort(
    (left, right) => left.monthIndex - right.monthIndex
  );
  if (!records.length) {
    return { records: [], points: [], segments: [], xLabels: [], yTicks: [] };
  }

  const plotWidth = CHART_WIDTH - CHART_MARGIN.left - CHART_MARGIN.right;
  const plotHeight = CHART_HEIGHT - CHART_MARGIN.top - CHART_MARGIN.bottom;
  const firstMonth = records[0].monthIndex;
  const lastMonth = records[records.length - 1].monthIndex;
  const monthSpan = Math.max(lastMonth - firstMonth, 1);
  const maximumValue = Math.max(...records.map((record) => record.value));
  const yScaleMaximum = maximumValue > 0 ? maximumValue : 1;

  const points = records.map((record) => ({
    ...record,
    x:
      records.length === 1
        ? CHART_MARGIN.left + plotWidth / 2
        : CHART_MARGIN.left +
          ((record.monthIndex - firstMonth) / monthSpan) * plotWidth,
    y:
      CHART_MARGIN.top +
      plotHeight -
      (record.value / yScaleMaximum) * plotHeight,
  }));

  const segments = [];
  for (const point of points) {
    const previous = segments.at(-1)?.at(-1);
    if (!previous || point.monthIndex - previous.monthIndex !== 1) {
      segments.push([point]);
    } else {
      segments.at(-1).push(point);
    }
  }

  const labelTarget = Math.min(7, points.length);
  const labelIndexes = new Set();
  for (let index = 0; index < labelTarget; index += 1) {
    labelIndexes.add(
      labelTarget === 1
        ? 0
        : Math.round((index * (points.length - 1)) / (labelTarget - 1))
    );
  }
  const xLabels = [...labelIndexes].map((index) => points[index]);

  const yTicks =
    maximumValue === 0
      ? [
          {
            value: 0,
            y: CHART_MARGIN.top + plotHeight,
          },
        ]
      : Array.from({ length: 5 }, (_, index) => {
          const ratio = index / 4;
          return {
            value: maximumValue * ratio,
            y: CHART_MARGIN.top + plotHeight - ratio * plotHeight,
          };
        });

  return {
    records,
    points,
    segments,
    xLabels,
    yTicks,
    minimumValue: Math.min(...records.map((record) => record.value)),
    maximumValue,
  };
}

function createSvgElement(name, attributes = {}, text = '') {
  const element = document.createElementNS(SVG_NAMESPACE, name);
  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, String(value));
  }
  if (text) {
    element.textContent = text;
  }
  return element;
}

function renderDemandChart(items) {
  const model = buildDemandChartModel(items);
  elements.demandChart.replaceChildren();
  elements.demandChartTableBody.replaceChildren();

  if (!model.records.length) {
    setElementHidden(elements.demandChartWrap, true);
    setElementHidden(elements.demandChartDetails, true);
    setElementHidden(elements.demandChartEmpty, false);
    elements.demandChartEmpty.textContent = '표시할 월별 승차 수요 데이터가 없습니다.';
    elements.demandChartSummary.textContent = '그래프에 표시할 데이터가 없습니다.';
    return model;
  }

  for (const tick of model.yTicks) {
    elements.demandChart.append(
      createSvgElement('line', {
        class: 'chart-grid-line',
        x1: CHART_MARGIN.left,
        x2: CHART_WIDTH - CHART_MARGIN.right,
        y1: tick.y,
        y2: tick.y,
      }),
      createSvgElement(
        'text',
        {
          class: 'chart-axis-label chart-axis-label-y',
          x: CHART_MARGIN.left - 12,
          y: tick.y + 4,
          'text-anchor': 'end',
        },
        formatNumber(tick.value)
      )
    );
  }

  for (const point of model.xLabels) {
    elements.demandChart.appendChild(
      createSvgElement(
        'text',
        {
          class: 'chart-axis-label chart-axis-label-x',
          x: point.x,
          y: CHART_HEIGHT - 20,
          'text-anchor': 'middle',
        },
        point.date.slice(0, 7)
      )
    );
  }

  for (const segment of model.segments) {
    if (segment.length > 1) {
      const path = segment
        .map(
          (point, index) =>
            `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`
        )
        .join(' ');
      elements.demandChart.appendChild(
        createSvgElement('path', {
          class: 'chart-line',
          d: path,
          fill: 'none',
        })
      );
    }
  }

  for (const point of model.points) {
    const circle = createSvgElement('circle', {
      class: 'chart-point',
      cx: point.x,
      cy: point.y,
      r: model.points.length === 1 ? 5 : 2.8,
    });
    circle.appendChild(
      createSvgElement(
        'title',
        {},
        `${point.date.slice(0, 7)}: ${formatNumber(point.value)}명`
      )
    );
    elements.demandChart.appendChild(circle);
  }

  const tableFragment = document.createDocumentFragment();
  for (const record of model.records) {
    const row = document.createElement('tr');
    const dateCell = document.createElement('td');
    const valueCell = document.createElement('td');
    dateCell.textContent = record.date.slice(0, 7);
    valueCell.textContent = `${formatNumber(record.value)}명`;
    row.append(dateCell, valueCell);
    tableFragment.appendChild(row);
  }
  elements.demandChartTableBody.appendChild(tableFragment);

  setElementHidden(elements.demandChartWrap, false);
  setElementHidden(elements.demandChartDetails, false);
  setElementHidden(elements.demandChartEmpty, true);
  elements.demandChartSummary.textContent =
    `${model.records[0].date.slice(0, 7)}부터 ` +
    `${model.records.at(-1).date.slice(0, 7)}까지 ${model.records.length}개월, ` +
    `최소 ${formatNumber(model.minimumValue)}명 · 최대 ${formatNumber(model.maximumValue)}명`;

  return model;
}

function normalizeExportRows(items) {
  return (Array.isArray(items) ? items : [])
    .map((item) => ({
      id: String(getDataDocumentId(item) || ''),
      date: getDataDate(item),
      value: Number(item?.value),
      memo: String(item?.memo ?? ''),
    }))
    .filter(
      (item) =>
        /^\d{4}-\d{2}-01$/.test(item.date) &&
        Number.isSafeInteger(item.value) &&
        item.value >= 0
    )
    .sort((left, right) => left.date.localeCompare(right.date));
}

function escapeCsvCell(value, { protectFormula = false } = {}) {
  let text = String(value ?? '');
  if (protectFormula && /^[\s]*[=+\-@]/.test(text)) {
    text = `'${text}`;
  }
  return `"${text.replace(/"/g, '""')}"`;
}

function serializeDataCsv(items) {
  const rows = normalizeExportRows(items);
  const lines = [EXPORT_FIELDS.join(',')];
  for (const row of rows) {
    lines.push(
      EXPORT_FIELDS.map((field) =>
        escapeCsvCell(row[field], {
          protectFormula: field === 'id' || field === 'date' || field === 'memo',
        })
      ).join(',')
    );
  }
  return `\uFEFF${lines.join('\r\n')}\r\n`;
}

function serializeDataJson(items) {
  return `${JSON.stringify(normalizeExportRows(items), null, 2)}\n`;
}

function setExportButtonsEnabled(enabled) {
  elements.downloadCsvButton.disabled = !enabled;
  elements.downloadJsonButton.disabled = !enabled;
}

function downloadDataFile(format) {
  const rows = normalizeExportRows(currentDataItems);
  if (!rows.length) {
    setStatus(elements.dataMessage, '다운로드할 데이터가 없습니다.', 'error');
    return;
  }

  const isCsv = format === 'csv';
  const content = isCsv ? serializeDataCsv(rows) : serializeDataJson(rows);
  const mimeType = isCsv
    ? 'text/csv;charset=utf-8'
    : 'application/json;charset=utf-8';
  const filename = isCsv
    ? 'ktx-monthly-data.csv'
    : 'ktx-monthly-data.json';
  const objectUrl = URL.createObjectURL(new Blob([content], { type: mimeType }));
  const link = document.createElement('a');
  link.href = objectUrl;
  link.download = filename;
  link.hidden = true;
  document.body.appendChild(link);

  try {
    link.click();
    setStatus(
      elements.dataMessage,
      `전체 ${rows.length}건을 ${format.toUpperCase()} 파일로 만들었습니다.`,
      'success'
    );
  } finally {
    link.remove();
    URL.revokeObjectURL(objectUrl);
  }
}

function isProtectedSeedData(item) {
  const date = getDataDate(item);
  return /^\d{4}-\d{2}-\d{2}$/.test(date) && date <= SEED_DATA_END_DATE;
}

async function fetchDataItems() {
  const response = await fetch(`${API_BASE_URL}/api/data`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `데이터 목록 조회에 실패했습니다. (HTTP ${response.status})`
      )
    );
  }

  return getDataItems(data);
}

async function createDataItem(payload) {
  const response = await fetch(`${API_BASE_URL}/api/data`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `데이터 추가에 실패했습니다. (HTTP ${response.status})`
      )
    );
  }

  return data;
}

async function deleteDataItem(documentId) {
  const response = await fetch(
    `${API_BASE_URL}/api/data/${encodeURIComponent(documentId)}`,
    {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
      },
    }
  );

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `데이터 삭제에 실패했습니다. (HTTP ${response.status})`
      )
    );
  }

  return data;
}

function createDataRow(item) {
  const row = document.createElement('tr');
  const date = getDataDate(item);
  const documentId = getDataDocumentId(item);
  const protectedSeed = isProtectedSeedData(item);

  const dateCell = document.createElement('td');
  dateCell.textContent = date;

  const valueCell = document.createElement('td');
  valueCell.textContent = `${formatNumber(item?.value)} 명`;

  const memoCell = document.createElement('td');
  memoCell.textContent = item?.memo ?? '-';

  const actionCell = document.createElement('td');
  const deleteButton = document.createElement('button');
  deleteButton.type = 'button';
  deleteButton.className = 'data-delete-button';

  if (protectedSeed || !documentId) {
    deleteButton.textContent = '원본 보호';
    deleteButton.disabled = true;
    deleteButton.title = '기존 2010~2023 Seed 데이터는 Frontend에서 삭제하지 않습니다.';
  } else {
    deleteButton.textContent = '삭제';
    deleteButton.dataset.documentId = documentId;
    deleteButton.addEventListener('click', () => {
      handleDeleteData(item, deleteButton);
    });
  }

  actionCell.appendChild(deleteButton);
  row.append(dateCell, valueCell, memoCell, actionCell);

  return row;
}

function renderDataItems(items) {
  elements.dataList.replaceChildren();

  if (!items.length) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 4;
    cell.className = 'data-empty';
    cell.textContent = '저장된 데이터가 없습니다.';
    row.appendChild(cell);
    elements.dataList.appendChild(row);
    return;
  }

  const sorted = [...items].sort((a, b) =>
    getDataDate(b).localeCompare(getDataDate(a))
  );

  const fragment = document.createDocumentFragment();

  sorted.slice(0, DATA_LIST_LIMIT).forEach((item) => {
    fragment.appendChild(createDataRow(item));
  });

  elements.dataList.appendChild(fragment);
}

async function loadDataItems({ silent = false } = {}) {
  elements.refreshDataButton.disabled = true;

  if (!silent) {
    setStatus(elements.dataMessage, 'Firestore 데이터 목록을 불러오는 중입니다.');
  }

  try {
    const items = await fetchDataItems();
    currentDataItems = [...items];
    renderDataItems(items);
    renderDemandChart(items);
    setExportButtonsEnabled(items.length > 0);

    if (!silent) {
      setStatus(
        elements.dataMessage,
        `전체 ${items.length}건 중 최근 ${DATA_LIST_LIMIT}건을 표시했습니다.`,
        'success'
      );
    }
  } catch (error) {
    currentDataItems = [];
    setExportButtonsEnabled(false);
    renderDemandChart([]);
    elements.demandChartEmpty.textContent =
      '월별 수요 그래프를 불러오지 못했습니다.';
    console.error('GET /api/data 오류:', error);
    setStatus(
      elements.dataMessage,
      `데이터 목록을 불러오지 못했습니다. ${error.message}`,
      'error'
    );
  } finally {
    elements.refreshDataButton.disabled = false;
  }
}

async function handleDataSubmit(event) {
  event.preventDefault();

  const month = elements.dataDate.value;
  const date = `${month}-01`;
  const rawValue = elements.dataValue.value.trim();
  const value = Number(rawValue);
  const memo = elements.dataMemo.value.trim();

  if (
    !/^\d{4}-(0[1-9]|1[0-2])$/.test(month) ||
    !rawValue ||
    !Number.isSafeInteger(value) ||
    value < 0 ||
    !memo
  ) {
    setStatus(
      elements.dataMessage,
      '기준 월, 0 이상의 정수 승차인원 값, 메모를 모두 입력해 주세요.',
      'error'
    );
    return;
  }

  if (date < TEST_DATA_MIN_DATE) {
    setStatus(
      elements.dataMessage,
      `원본 Seed 데이터와 겹치지 않도록 ${TEST_DATA_MIN_DATE} 이후 날짜를 사용해 주세요.`,
      'error'
    );
    return;
  }

  elements.addDataButton.disabled = true;
  setStatus(elements.dataMessage, '테스트 데이터를 Firestore에 추가하는 중입니다.');

  try {
    await createDataItem({
      date,
      value,
      memo,
    });

    setStatus(
      elements.dataMessage,
      `${date} 테스트 데이터를 추가했습니다. 아래 목록에서 삭제할 수 있습니다.`,
      'success'
    );

    elements.dataValue.value = '';
    elements.dataMemo.value = '';

    await Promise.all([
      loadDataItems({ silent: true }),
      loadSummary({ silent: true }),
    ]);
  } catch (error) {
    console.error('POST /api/data 오류:', error);
    setStatus(
      elements.dataMessage,
      `데이터 추가 중 오류가 발생했습니다. ${error.message}`,
      'error'
    );
  } finally {
    elements.addDataButton.disabled = false;
  }
}

async function handleDeleteData(item, deleteButton = null) {
  const documentId = getDataDocumentId(item);
  const date = getDataDate(item);

  if (!documentId || isProtectedSeedData(item)) {
    return;
  }

  const confirmed = window.confirm(
    `${date} 테스트 데이터를 삭제할까요?\n원본 168건은 삭제되지 않습니다.`
  );

  if (!confirmed) {
    return;
  }

  if (deleteButton) {
    deleteButton.disabled = true;
  }

  setStatus(elements.dataMessage, `${date} 데이터를 삭제하는 중입니다.`);

  try {
    await deleteDataItem(documentId);

    setStatus(
      elements.dataMessage,
      `${date} 테스트 데이터를 삭제했습니다.`,
      'success'
    );

    await Promise.all([
      loadDataItems({ silent: true }),
      loadSummary({ silent: true }),
    ]);
  } catch (error) {
    if (deleteButton?.isConnected) {
      deleteButton.disabled = false;
    }

    console.error('DELETE /api/data/{document_id} 오류:', error);
    setStatus(
      elements.dataMessage,
      `데이터 삭제 중 오류가 발생했습니다. ${error.message}`,
      'error'
    );
  }
}

async function submitChat(message) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `AI 요청에 실패했습니다. (HTTP ${response.status})`
      )
    );
  }

  return data;
}

async function handleChatSubmit(event) {
  event.preventDefault();

  const message = elements.messageInput.value.trim();

  setStatus(elements.formMessage);
  elements.answerArea.hidden = true;

  if (!message) {
    setStatus(elements.formMessage, '질문을 입력해 주세요.', 'error');
    elements.messageInput.focus();
    return;
  }

  setChatLoading(true);

  try {
    const data = await submitChat(message);

    elements.answerText.textContent = getChatAnswer(data);
    elements.conversationId.textContent = getConversationId(data);
    elements.modelName.textContent = getModelName(data);
    elements.answerArea.hidden = false;

    setStatus(
      elements.formMessage,
      'AI 답변을 정상적으로 받았습니다.',
      'success'
    );

    /*
     * /api/chat이 Firestore에 대화를 자동 저장하므로,
     * 답변을 받은 뒤 최근 대화 목록도 자동으로 갱신합니다.
     */
    await loadConversations({ silent: true });
  } catch (error) {
    console.error('POST /api/chat 오류:', error);

    setStatus(
      elements.formMessage,
      `질문 처리 중 오류가 발생했습니다. ${error.message}`,
      'error'
    );
  } finally {
    setChatLoading(false);
  }
}

async function fetchConversations() {
  const response = await fetch(`${API_BASE_URL}/api/conversations`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `대화 목록 조회에 실패했습니다. (HTTP ${response.status})`
      )
    );
  }

  /*
   * 현재 API가 배열을 직접 반환하는 경우를 기본으로 하되,
   * { conversations: [...] } 또는 { items: [...] } 형태도 허용합니다.
   */
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.conversations)) {
    return data.conversations;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  return [];
}


async function fetchConversationById(conversationId) {
  const response = await fetch(
    `${API_BASE_URL}/api/conversations/${encodeURIComponent(conversationId)}`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    }
  );

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(
      getErrorMessage(
        data,
        `대화를 불러오지 못했습니다. (HTTP ${response.status})`
      )
    );
  }

  return data;
}

function getConversationMessages(conversation) {
  if (Array.isArray(conversation?.messages) && conversation.messages.length > 0) {
    return conversation.messages
      .filter((message) => message && typeof message === 'object')
      .map((message) => ({
        role: message.role ?? 'unknown',
        content: message.content ?? message.message ?? '',
      }))
      .filter((message) => String(message.content).trim());
  }

  const messages = [];
  const userMessage = conversation?.user_message ?? conversation?.message;
  const assistantMessage =
    conversation?.assistant_message ?? conversation?.answer ?? conversation?.response;

  if (userMessage) {
    messages.push({ role: 'user', content: userMessage });
  }

  if (assistantMessage) {
    messages.push({ role: 'assistant', content: assistantMessage });
  }

  return messages;
}

function renderLoadedConversation(container, conversation) {
  container.replaceChildren();

  const heading = document.createElement('h3');
  heading.className = 'loaded-conversation-title';
  heading.textContent = '불러온 대화';
  container.appendChild(heading);

  const messages = getConversationMessages(conversation);

  if (!messages.length) {
    const empty = document.createElement('p');
    empty.className = 'loaded-conversation-empty';
    empty.textContent = '불러온 대화에 표시할 메시지가 없습니다.';
    container.appendChild(empty);
    return;
  }

  messages.forEach((message) => {
    const item = document.createElement('div');
    const role = message.role === 'assistant' ? 'assistant' : 'user';
    item.className = `loaded-message loaded-message-${role}`;

    const label = document.createElement('strong');
    label.textContent = role === 'assistant' ? 'AI 답변' : '사용자 질문';

    const content = document.createElement('p');
    content.textContent = String(message.content);

    item.append(label, content);
    container.appendChild(item);
  });
}

async function handleLoadConversation(conversationId, button, container) {
  if (!conversationId || conversationId === '-') {
    setStatus(elements.historyMessage, '대화 ID가 없어 불러올 수 없습니다.', 'error');
    return;
  }

  button.disabled = true;
  button.textContent = '불러오는 중...';
  setStatus(elements.historyMessage, '선택한 대화를 불러오는 중입니다.');

  try {
    const conversation = await fetchConversationById(conversationId);
    renderLoadedConversation(container, conversation);
    container.hidden = false;
    button.textContent = '다시 불러오기';

    setStatus(
      elements.historyMessage,
      `대화 ID ${conversationId}를 불러왔습니다.`,
      'success'
    );
  } catch (error) {
    console.error('GET /api/conversations/{conversation_id} 오류:', error);
    button.textContent = '대화 불러오기';
    setStatus(
      elements.historyMessage,
      `대화를 불러오지 못했습니다. ${error.message}`,
      'error'
    );
  } finally {
    button.disabled = false;
  }
}

function formatDateTime(value) {
  if (!value) {
    return '시간 정보 없음';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

function createConversationCard(conversation) {
  const article = document.createElement('article');
  article.className = 'conversation-card';

  const question = document.createElement('p');
  question.className = 'conversation-question';
  question.textContent =
    conversation.user_message ??
    conversation.message ??
    '질문 내용 없음';

  const answer = document.createElement('p');
  answer.className = 'conversation-answer';
  answer.textContent =
    conversation.assistant_message ??
    conversation.answer ??
    conversation.response ??
    '답변 내용 없음';

  const meta = document.createElement('p');
  meta.className = 'conversation-meta';

  const id = conversation.id ?? conversation.conversation_id ?? '-';
  const createdAt = formatDateTime(conversation.created_at);

  meta.textContent = `대화 ID: ${id} · ${createdAt}`;

  const actions = document.createElement('div');
  actions.className = 'conversation-card-actions';

  const loadButton = document.createElement('button');
  loadButton.type = 'button';
  loadButton.className = 'conversation-load-button';
  loadButton.textContent = '대화 불러오기';
  loadButton.disabled = !id || id === '-';

  const loadedArea = document.createElement('div');
  loadedArea.className = 'loaded-conversation';
  loadedArea.hidden = true;

  loadButton.addEventListener('click', () => {
    handleLoadConversation(id, loadButton, loadedArea).catch((error) => {
      console.error('대화 불러오기 처리 중 예상치 못한 오류:', error);
    });
  });

  actions.appendChild(loadButton);
  article.append(question, answer, meta, actions, loadedArea);

  return article;
}

function renderConversations(conversations) {
  elements.conversationList.replaceChildren();

  if (!conversations.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-message';
    empty.textContent = '저장된 대화가 없습니다.';
    elements.conversationList.appendChild(empty);
    return;
  }

  const sorted = [...conversations].sort((a, b) => {
    const aTime = new Date(a.created_at ?? 0).getTime();
    const bTime = new Date(b.created_at ?? 0).getTime();

    return bTime - aTime;
  });

  const fragment = document.createDocumentFragment();

  sorted.forEach((conversation) => {
    fragment.appendChild(createConversationCard(conversation));
  });

  elements.conversationList.appendChild(fragment);
}

async function loadConversations({ silent = false } = {}) {
  elements.refreshButton.disabled = true;

  if (!silent) {
    setStatus(elements.historyMessage, '최근 대화를 불러오는 중입니다.');
  }

  try {
    const conversations = await fetchConversations();

    renderConversations(conversations);

    if (!silent) {
      const count = conversations.length;
      setStatus(
        elements.historyMessage,
        `최근 대화 ${count}건을 불러왔습니다.`,
        'success'
      );
    }
  } catch (error) {
    console.error('GET /api/conversations 오류:', error);

    setStatus(
      elements.historyMessage,
      `대화 목록을 불러오지 못했습니다. ${error.message}`,
      'error'
    );
  } finally {
    elements.refreshButton.disabled = false;
  }
}

function validateRequiredElements() {
  const missing = Object.entries(elements)
    .filter(([, element]) => !element)
    .map(([name]) => name);

  if (missing.length > 0) {
    console.error(
      `필수 HTML 요소를 찾지 못했습니다: ${missing.join(', ')}`
    );
    return false;
  }

  return true;
}

function initializeApp() {
  if (!validateRequiredElements()) {
    return;
  }

  if (!API_BASE_URL) {
    console.error('API_BASE_URL이 설정되지 않았습니다. Frontend 빌드 설정을 확인하세요.');
    for (const statusElement of [
      elements.summaryMessage,
      elements.dataMessage,
      elements.formMessage,
      elements.historyMessage,
    ]) {
      setStatus(
        statusElement,
        '서비스 연결 설정을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.',
        'error'
      );
    }
    for (const button of [
      elements.refreshSummaryButton,
      elements.refreshDataButton,
      elements.downloadCsvButton,
      elements.downloadJsonButton,
      elements.addDataButton,
      elements.submitButton,
      elements.refreshButton,
    ]) {
      button.disabled = true;
    }
    return;
  }

  elements.refreshSummaryButton.addEventListener('click', () => {
    Promise.all([loadSummary(), loadDataItems({ silent: true })]);
  });

  elements.dataForm.addEventListener('submit', handleDataSubmit);
  elements.refreshDataButton.addEventListener('click', () => {
    loadDataItems();
  });
  elements.downloadCsvButton.addEventListener('click', () => {
    downloadDataFile('csv');
  });
  elements.downloadJsonButton.addEventListener('click', () => {
    downloadDataFile('json');
  });

  elements.chatForm.addEventListener('submit', handleChatSubmit);
  elements.refreshButton.addEventListener('click', () => {
    loadConversations();
  });

  /*
   * 페이지를 열면 Firestore 데이터 Summary, 데이터 목록, 최근 대화 목록을
   * 각각 자동으로 한 번 조회합니다.
   */
  loadSummary();
  loadDataItems();
  loadConversations();
}

document.addEventListener('DOMContentLoaded', initializeApp);
