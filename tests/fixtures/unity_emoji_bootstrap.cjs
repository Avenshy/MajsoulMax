const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

(async () => {
  const scenario = process.argv[3];
  let timer, cleared = false, started = 0, closed = 0, aborted = 0, committed = 0;
  let stage, openRequest, writeTransaction;
  const requests = [];
  const warnings = [];
  const tag = '__max_emoji_v1';
  const key = '/idbfs/test/ABM-Fold/WebGL/panel.majset';
  const never = () => new Promise(() => {});
  const request = result => {
    const query = {result};
    queueMicrotask(() => query.onsuccess());
    return query;
  };
  const db = {
    close() {closed++;},
    transaction(store, mode) {
      const transaction = {
        objectStore() {
          return {
            getAllKeys: () => request([key]),
            get: () => request({contents: new Uint8Array([1]), timestamp: new Date(), mode: 33206,
                               maxEmojiPatchTag: scenario === 'already_patched' ? tag : undefined}),
            put(record, writtenKey) {
              assert.equal(writtenKey, key);
              assert.equal(record.maxEmojiPatchTag, tag);
              assert.deepEqual([...record.contents], [2, 3]);
              stage = 'write';
              if (scenario !== 'timeout_write') queueMicrotask(() => {
                committed++;
                transaction.oncomplete();
              });
            },
          };
        },
        abort() {
          aborted++;
          transaction.onabort();
        },
      };
      if (mode === 'readwrite') writeTransaction = transaction;
      return transaction;
    },
  };
  const context = {
    AbortController, DOMException, Date, Uint8Array, Promise,
    console: {warn: (...args) => warnings.push(args)},
    setTimeout(callback, delay) {
      assert.equal(delay, 8000);
      timer = callback;
      return 1;
    },
    clearTimeout(id) {assert.equal(id, 1); cleared = true;},
    window: {createUnityInstance(...args) {
      started++;
      assert.deepEqual(args, ['canvas', 'config', 'progress']);
      if (scenario === 'timeout_write') assert.equal(aborted, 1);
      return 'unity';
    }},
    indexedDB: {
      databases: async () => scenario === 'success_empty' ? [] : [{name: '/idbfs'}],
      open() {
        stage = 'open';
        openRequest = {result: db};
        if (scenario !== 'timeout_open') queueMicrotask(() => openRequest.onsuccess());
        return openRequest;
      },
    },
    async fetch(url, options) {
      requests.push({url, signal: options.signal});
      assert.equal(options.credentials, 'omit');
      if (scenario === 'timeout_fetch') {stage = 'fetch'; return never();}
      if (url.includes('emoji-panel-assets')) return {
        ok: true,
        json() {
          stage = 'body';
          return scenario === 'timeout_body' ? never() : Promise.resolve({tag, assets: [{name: 'panel.majset', url: '/assetbundles/ASTC/panel.majset'}]});
        },
      };
      return {ok: true, headers: {get: () => tag}, arrayBuffer: async () => new Uint8Array([2, 3]).buffer};
    },
  };
  vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'), context);
  const boot = context.window.createUnityInstance('canvas', 'config', 'progress');
  await new Promise(resolve => setImmediate(resolve));
  if (scenario.startsWith('timeout_')) {
    assert.equal(started, 0);
    assert.equal(stage, scenario.slice('timeout_'.length));
    assert.equal(typeof timer, 'function');
    timer();
  }
  assert.equal(await boot, 'unity');
  assert.equal(started, 1);
  assert.equal(cleared, true);
  assert.ok(requests.every(request => request.signal === requests[0].signal));
  if (scenario.startsWith('timeout_')) {
    assert.equal(requests[0].signal.aborted, true);
    assert.equal(warnings.length, 1);
    assert.equal(committed, 0);
  } else {
    assert.equal(warnings.length, 0);
  }
  if (scenario === 'timeout_open') {
    openRequest.onsuccess();
    assert.equal(closed, 1, 'a late database connection must close');
  }
  if (scenario === 'already_patched') assert.equal(requests.length, 2, 'cached panel must not download again');
  if (scenario === 'success_write') assert.equal(committed, 1);
  if (writeTransaction && scenario === 'timeout_write') assert.ok(closed >= 1);
  console.log(scenario + ': passed');
})().catch(error => {console.error(error); process.exitCode = 1;});
