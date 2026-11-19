/* SOARiA メンバーサイト：通知を受け取って表示し、アイコンに新着の数を出す */
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

function getCfg() {
  return new Promise(res => {
    try {
      const r = indexedDB.open('soaria', 1);
      r.onupgradeneeded = () => r.result.createObjectStore('kv');
      r.onsuccess = () => {
        const q = r.result.transaction('kv').objectStore('kv').get('cfg');
        q.onsuccess = () => res(q.result || null);
        q.onerror = () => res(null);
      };
      r.onerror = () => res(null);
    } catch (e) { res(null); }
  });
}

self.addEventListener('push', e => {
  e.waitUntil((async () => {
    let info = { title: 'SOARiA', body: '新着があります', url: './', tag: 'soaria', count: 0 };
    try {
      const cfg = await getCfg();
      if (cfg && cfg.api && cfg.device) {
        const r = await fetch(cfg.api, { method: 'POST', body: JSON.stringify({ fn: 'pushInfo', args: [cfg.device] }), credentials: 'omit', redirect: 'follow', cache: 'no-store' });
        const j = await r.json();
        if (j && j.ok) info = Object.assign(info, j.ok);
      }
    } catch (err) { /* 取れなくても通知は出す */ }
    try {
      if (self.navigator.setAppBadge) {
        if (info.count > 0) await self.navigator.setAppBadge(info.count);
        else await self.navigator.clearAppBadge();
      }
    } catch (err) {}
    await self.registration.showNotification(info.title, {
      body: info.body, icon: 'icon-192.png', badge: 'icon-192.png', tag: info.tag, renotify: true, data: { url: info.url }
    });
  })());
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = new URL((e.notification.data && e.notification.data.url) || './', self.registration.scope).href;
  e.waitUntil((async () => {
    const list = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const c of list) {
      if (c.url.startsWith(self.registration.scope)) { await c.focus(); try { await c.navigate(url); } catch (err) {} return; }
    }
    await self.clients.openWindow(url);
  })());
});
