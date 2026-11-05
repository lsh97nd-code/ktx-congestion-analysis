'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../js/app.js'), 'utf8');

function formFixture({ month = '2024-02', value = '7000000', memo = '테스트' } = {}) {
  const elements = new Map();
  const saved = [];
  const context = {
    window: { APP_CONFIG: { API_BASE_URL: 'http://localhost:8001' } },
    console,
    document: {
      getElementById(id) {
        const element = { value: '', classList: { add() {}, remove() {} } };
        elements.set(id, element);
        return element;
      },
      addEventListener() {},
    },
  };
  vm.runInNewContext(source, context);
  elements.get('data-date').value = month;
  elements.get('data-value').value = value;
  elements.get('data-memo').value = memo;
  context.createDataItem = async (payload) => { saved.push(JSON.parse(JSON.stringify(payload))); };
  context.loadDataItems = async () => {};
  context.loadSummary = async () => {};
  return {
    elements,
    saved,
    submit: () => context.handleDataSubmit({ preventDefault() {} }),
  };
}

test('monthly form sends the first day without changing the passenger count', async () => {
  const fixture = formFixture();
  await fixture.submit();
  assert.deepEqual(fixture.saved, [{ date: '2024-02-01', value: 7000000, memo: '테스트' }]);
});

for (const value of ['', '1.5', '-1', '9007199254740992']) {
  test(`monthly form rejects invalid passenger count: ${value || '(empty)'}`, async () => {
    const fixture = formFixture({ value });
    await fixture.submit();
    assert.deepEqual(fixture.saved, []);
    assert.match(fixture.elements.get('data-message').textContent, /정수 승차인원/);
  });
}

for (const month of ['2024-02-15', '2024-13', '2023-12']) {
  test(`monthly form rejects invalid or protected month: ${month}`, async () => {
    const fixture = formFixture({ month });
    await fixture.submit();
    assert.deepEqual(fixture.saved, []);
  });
}
