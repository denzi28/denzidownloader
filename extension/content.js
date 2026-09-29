// Puts a small DenziDownloader button on every sizeable <video>; clicking it downloads that video (best quality, default folder).
(() => {
  const ICON = chrome.runtime.getURL('icons/indir.png');
  const MIN_W = 200, MIN_H = 120;
  const buttons = new Map(); // video -> button

  function videoUrl(video) {
    // On feeds (Instagram, X, TikTok…) the page URL isn't the clip's URL; look for its post link.
    const scope = video.closest('article') || video.parentElement?.parentElement?.parentElement;
    const a = scope?.querySelector('a[href*="/reel/"],a[href*="/p/"],a[href*="/status/"],a[href*="/video/"],a[href*="watch?v="],a[href*="/shorts/"]');
    return a ? a.href : location.href;
  }

  function makeButton(video) {
    const b = document.createElement('img');
    b.src = ICON;
    b.title = 'Download with DenziDownloader';
    Object.assign(b.style, {
      position: 'fixed', width: '64px', height: '64px', borderRadius: '50%', cursor: 'pointer',
      zIndex: 2147483647, boxShadow: '0 2px 8px #000a', border: '2px solid #fff',
      transition: 'transform .15s, opacity .2s', objectFit: 'cover', display: 'none',
    });
    b.onmouseenter = () => (b.style.transform = 'scale(1.15)');
    b.onmouseleave = () => (b.style.transform = '');
    // Sites often listen for mouse events on the player; keep them from swallowing our click.
    for (const ev of ['mousedown', 'mouseup', 'pointerdown', 'pointerup', 'dblclick'])
      b.addEventListener(ev, e => e.stopPropagation(), true);
    b.addEventListener('click', async e => {
      e.preventDefault(); e.stopPropagation();
      if (b.dataset.busy) return;
      b.dataset.busy = '1'; b.style.opacity = '.5'; b.title = 'Starting…';
      toast(b, 'Analyzing video…');
      let res;
      try {
        res = await chrome.runtime.sendMessage({type: 'download', url: videoUrl(video)});
      } catch {
        return finish(b, '⚠ Extension was updated. Reload this page and try again.', '#e5484d');
      }
      if (!res?.ok) return finish(b, '⚠ ' + (res?.error || 'Failed'), '#e5484d');
      toast(b, 'Downloading… (hover the button for progress)');
      b.title = 'Downloading…';
      const tick = async () => {
        let s;
        try { s = await chrome.runtime.sendMessage({type: 'status', id: res.id}); } catch { return finish(b, '⚠ Lost connection to the extension', '#e5484d'); }
        const j = s?.job;
        if (j?.status === 'done') return finish(b, '✅ Saved to ' + j.dir, '#30a46c');
        if (j?.status === 'error') return finish(b, '⚠ ' + j.error, '#e5484d');
        b.title = `Downloading… ${j?.percent ?? 0}%`;
        setTimeout(tick, 1000);
      };
      tick();
    }, true);
    document.body.appendChild(b);
    return b;
  }

  let toastEl, toastTimer;
  function toast(b, msg) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      Object.assign(toastEl.style, {
        position: 'fixed', maxWidth: '320px', padding: '8px 12px', borderRadius: '8px', background: '#181b22',
        color: '#fff', font: '13px/1.4 system-ui,sans-serif', zIndex: 2147483647, boxShadow: '0 2px 10px #000a',
        border: '1px solid #4f8cff', pointerEvents: 'none',
      });
      document.body.appendChild(toastEl);
    }
    const r = b.getBoundingClientRect();
    toastEl.textContent = msg;
    toastEl.style.top = r.bottom + 8 + 'px';
    toastEl.style.left = Math.max(8, r.right - 320) + 'px';
    toastEl.style.display = 'block';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (toastEl.style.display = 'none'), 5000);
  }

  function finish(b, msg, color) {
    toast(b, msg);
    b.title = msg; b.style.opacity = '1'; b.style.borderColor = color;
    delete b.dataset.busy;
    setTimeout(() => (b.style.borderColor = '#fff'), 4000);
  }

  function update() {
    for (const v of document.querySelectorAll('video')) {
      if (!buttons.has(v)) buttons.set(v, makeButton(v));
    }
    for (const [v, b] of buttons) {
      const r = v.getBoundingClientRect();
      const visible = v.isConnected && r.width >= MIN_W && r.height >= MIN_H &&
        r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth;
      if (!v.isConnected) { b.remove(); buttons.delete(v); continue; }
      b.style.display = visible ? 'block' : 'none';
      if (visible) {
        b.style.top = Math.max(r.top, 0) + 12 + 'px';
        b.style.left = Math.min(r.right, innerWidth) - 74 + 'px';
      }
    }
  }

  setInterval(update, 400);
  addEventListener('scroll', update, true);
  addEventListener('resize', update);
})();
