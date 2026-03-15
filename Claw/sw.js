// ══════════════════════════════════════════
//  农历闹钟 Service Worker
//  版本: 1.0.0
// ══════════════════════════════════════════

const CACHE_NAME = 'lunar-alarm-v2';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-96.png'
];

// ── 安装：预缓存核心资源 ──
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

// ── 激活：清理旧缓存 ──
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ── 拦截请求：Cache First 策略 ──
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        // 只缓存成功的 GET 请求
        if (!response || response.status !== 200 || event.request.method !== 'GET') {
          return response;
        }
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      }).catch(() => {
        // 离线时返回主页面
        if (event.request.destination === 'document') {
          return caches.match('/index.html');
        }
      });
    })
  );
});

// ── 推送通知（为未来扩展预留）──
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || '农历提醒';
  const options = {
    body: data.body || '今天是农历吉祥日！',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-96.png',
    vibrate: [200, 100, 200, 100, 200],
    data: { url: data.url || '/lunar-alarm.html' },
    actions: [
      { action: 'open', title: '查看详情' },
      { action: 'close', title: '知道了' }
    ]
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

// ── 通知点击 ──
self.addEventListener('notificationclick', event => {
  event.notification.close();
  if (event.action === 'close') return;
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(list => {
      for (const client of list) {
        if (client.url.includes('index') && 'focus' in client) {
          return client.focus();
        }
      }
      return clients.openWindow('/index.html');
    })
  );
});
