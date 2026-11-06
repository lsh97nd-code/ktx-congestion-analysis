'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../js/app.js'), 'utf8');

function renderSummary(summary) {
  const elements = new Map();
  const context = {
    window: { APP_CONFIG: { API_BASE_URL: 'http://localhost:8001' } },
    document: {
      getElementById(id) {
        const element = { textContent: '' };
        elements.set(id, element);
        return element;
      },
      addEventListener() {},
    },
  };
  vm.runInNewContext(source, context);
  context.renderSummary(summary);
  return (id) => elements.get(id).textContent;
}

test('summary labels and values use the configured trend window', () => {
  const text = renderSummary({
    trend_window_months: 6,
    recent_window_avg: 1200,
    previous_window_avg: 1000,
    recent_12_month_avg: 800,
    previous_12_month_avg: 700,
    change_pct: 20,
  });
  assert.equal(text('summary-recent-label'), '최근 6개월 월평균');
  assert.equal(text('summary-previous-label'), '직전 6개월 월평균');
  assert.equal(text('summary-recent-average'), '1,200');
  assert.equal(text('summary-previous-average'), '1,000');
  assert.equal(text('summary-change'), '직전 6개월 대비 +20%');
});

test('summary remains compatible with a legacy 12-month response', () => {
  const text = renderSummary({
    recent_12_month_avg: 900,
    previous_12_month_avg: 1000,
    change_pct: -10,
  });
  assert.equal(text('summary-recent-label'), '최근 12개월 월평균');
  assert.equal(text('summary-previous-label'), '직전 12개월 월평균');
  assert.equal(text('summary-recent-average'), '900');
  assert.equal(text('summary-previous-average'), '1,000');
  assert.equal(text('summary-change'), '직전 12개월 대비 -10%');
});

test('explicit unavailable window values do not display legacy averages', () => {
  const text = renderSummary({
    trend_window_months: 3,
    recent_window_avg: null,
    previous_window_avg: null,
    recent_12_month_avg: 900,
    previous_12_month_avg: 1000,
    change_pct: null,
  });
  assert.equal(text('summary-recent-label'), '최근 3개월 월평균');
  assert.equal(text('summary-recent-average'), '-');
  assert.equal(text('summary-previous-average'), '-');
  assert.equal(text('summary-change'), '변화율 계산 데이터 부족');
});

test('zero averages and zero change remain valid values', () => {
  const text = renderSummary({
    trend_window_months: 1,
    recent_window_avg: 0,
    previous_window_avg: 0,
    change_pct: 0,
  });
  assert.equal(text('summary-recent-average'), '0');
  assert.equal(text('summary-previous-average'), '0');
  assert.equal(text('summary-change'), '직전 1개월 대비 0%');
});
