'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../js/app.js'), 'utf8');

function loadAppFunctions() {
  const context = {
    window: { APP_CONFIG: { API_BASE_URL: 'http://localhost:8001' } },
    document: {
      getElementById() {
        return {};
      },
      addEventListener() {},
    },
  };
  vm.runInNewContext(source, context);
  return context;
}

test('visibility helper removes the hidden attribute from SVG elements', () => {
  const app = loadAppFunctions();
  const attributes = new Map([['hidden', '']]);
  let hiddenPropertyWrites = 0;
  const svg = {
    setAttribute(name, value) {
      attributes.set(name, value);
    },
    removeAttribute(name) {
      attributes.delete(name);
    },
    set hidden(_value) {
      hiddenPropertyWrites += 1;
      attributes.set('hidden', 'false');
    },
  };

  app.setElementHidden(svg, false);
  assert.equal(attributes.has('hidden'), false);
  assert.equal(hiddenPropertyWrites, 0);
  app.setElementHidden(svg, true);
  assert.equal(attributes.has('hidden'), true);
});

test('chart visibility is controlled by an HTML wrapper, not the SVG', () => {
  const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');
  assert.match(html, /id="demand-chart-wrap"[^>]*hidden/);
  assert.doesNotMatch(html, /id="demand-chart"[^>]*hidden/);
});

test('chart model sorts all records and breaks the line at missing months', () => {
  const app = loadAppFunctions();
  const model = app.buildDemandChartModel([
    { date: '2024-04-01', value: 40 },
    { date: '2024-01-01', value: 0 },
    { date: '2024-02-01', value: 20 },
  ]);

  assert.deepEqual(
    Array.from(model.records, (item) => item.date),
    ['2024-01-01', '2024-02-01', '2024-04-01']
  );
  assert.deepEqual(
    Array.from(model.segments, (segment) => segment.length),
    [2, 1]
  );
  assert.equal(model.minimumValue, 0);
  assert.equal(model.maximumValue, 40);
  assert.ok(model.points.every((point) => Number.isFinite(point.x) && Number.isFinite(point.y)));
});

test('chart model handles one zero-value month without invalid coordinates', () => {
  const app = loadAppFunctions();
  const model = app.buildDemandChartModel([
    { date: '2024-01-01', value: 0 },
  ]);

  assert.equal(model.points.length, 1);
  assert.equal(model.segments.length, 1);
  assert.equal(model.yTicks.length, 1);
  assert.ok(Number.isFinite(model.points[0].x));
  assert.ok(Number.isFinite(model.points[0].y));
});

test('chart uses the complete dataset instead of the 12-row table limit', () => {
  const app = loadAppFunctions();
  const records = Array.from({ length: 168 }, (_, index) => {
    const year = 2010 + Math.floor(index / 12);
    const month = String((index % 12) + 1).padStart(2, '0');
    return { date: `${year}-${month}-01`, value: index };
  });

  assert.equal(app.buildDemandChartModel(records).records.length, 168);
});

test('CSV export includes every row, UTF-8 BOM, escaping, and formula protection', () => {
  const app = loadAppFunctions();
  const csv = app.serializeDataCsv([
    {
      id: '2024-02-01',
      date: '2024-02-01',
      value: 0,
      memo: '  =SUM(1,2)',
    },
    {
      id: '2024-01-01',
      date: '2024-01-01',
      value: 10,
      memo: '한글, "따옴표"\n줄바꿈',
    },
  ]);

  assert.ok(csv.startsWith('\uFEFFid,date,value,memo\r\n'));
  assert.match(csv, /"2024-01-01","2024-01-01","10","한글, ""따옴표""\n줄바꿈"/);
  assert.match(csv, /"2024-02-01","2024-02-01","0","'  =SUM\(1,2\)"/);
  assert.ok(csv.indexOf('2024-01-01') < csv.indexOf('2024-02-01'));
});

test('JSON export preserves numeric values and original memo text', () => {
  const app = loadAppFunctions();
  const memo = '@수식처럼 보이지만 JSON에서는 원문';
  const json = app.serializeDataJson([
    { id: '2024-01-01', date: '2024-01-01', value: 0, memo },
  ]);
  const parsed = JSON.parse(json);

  assert.equal(parsed[0].value, 0);
  assert.equal(parsed[0].memo, memo);
  assert.ok(!json.startsWith('\uFEFF'));
});
