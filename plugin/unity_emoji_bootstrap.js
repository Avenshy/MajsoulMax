/* Refresh only the cached in-game emoji panel before Unity mounts its files. */
(() => {
  const original = window.createUnityInstance;
  window.createUnityInstance = async (...args) => {
    const controller = new AbortController();
    const {signal} = controller;
    const timer = setTimeout(() => controller.abort(new DOMException('Emoji cache update timed out', 'TimeoutError')), 8000);
    let db;
    let writing;
    const wait = operation => new Promise((resolve, reject) => {
      const abort = () => reject(signal.reason);
      Promise.resolve(operation).then(resolve, reject).finally(() => signal.removeEventListener('abort', abort));
      if (signal.aborted) abort();
      else signal.addEventListener('abort', abort, {once: true});
    });
    signal.addEventListener('abort', () => {
      if (writing) writing.abort();
      db?.close();
    }, {once: true});
    const options = {cache: 'no-store', credentials: 'omit', signal};
    try {
      await wait(fetch('/assetbundles/ASTC/bundle_info_so.majset', options));
      const response = await wait(fetch('/_majsoulmax/emoji-panel-assets', options));
      if (!response.ok) throw new Error('Emoji asset manifest unavailable');
      const {tag, assets} = await wait(response.json());
      const databases = await wait(indexedDB.databases());
      if (databases.some(database => database.name === '/idbfs')) {
        db = await wait(new Promise((resolve, reject) => {
          const request = indexedDB.open('/idbfs');
          request.onsuccess = () => {
            if (signal.aborted) {
              request.result.close();
              reject(signal.reason);
            } else {
              resolve(request.result);
            }
          };
          request.onerror = () => reject(request.error);
        }));
        try {
          const read = request => new Promise((resolve, reject) => {
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
          });
          const keys = await wait(read(db.transaction('FILE_DATA').objectStore('FILE_DATA').getAllKeys()));
          for (const asset of assets) {
            const matches = keys.filter(key => key.includes('/ABM-Fold/') && key.endsWith('/' + asset.name));
            for (const key of matches) {
              const record = await wait(read(db.transaction('FILE_DATA').objectStore('FILE_DATA').get(key)));
              if (record.maxEmojiPatchTag === tag) continue;
              const resource = await wait(fetch(asset.url + '?max_emoji_patch=' + tag, options));
              if (!resource.ok || resource.headers.get('x-majsoulmax-emoji-panel') !== tag) continue;
              record.contents = new Uint8Array(await wait(resource.arrayBuffer()));
              record.timestamp = new Date();
              record.maxEmojiPatchTag = tag;
              signal.throwIfAborted();
              await wait(new Promise((resolve, reject) => {
                const transaction = db.transaction('FILE_DATA', 'readwrite');
                writing = transaction;
                transaction.objectStore('FILE_DATA').put(record, key);
                transaction.oncomplete = () => {
                  writing = undefined;
                  resolve();
                };
                transaction.onerror = transaction.onabort = () => {
                  writing = undefined;
                  reject(transaction.error);
                };
              }));
            }
          }
        } finally {
          db.close();
        }
      }
    } catch (error) {
      console.warn('MajsoulMAX emoji panel cache update failed:', error.message);
    } finally {
      clearTimeout(timer);
    }
    return original(...args);
  };
})();
