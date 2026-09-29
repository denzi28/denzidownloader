const BASE = 'http://127.0.0.1:8765';

async function api(path, body) {
  const r = await fetch(BASE + path, body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : {});
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || 'Error');
  return j;
}

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  (async () => {
    try {
      if (msg.type === 'download') {
        const info = await api('/api/info', {url: msg.url});
        const {id} = await api('/api/download', {url: msg.url, mode: 'video', title: info.title});
        reply({ok: true, id, title: info.title});
      } else if (msg.type === 'status') {
        const job = (await api('/api/jobs')).find(j => j.id === msg.id);
        reply({ok: true, job});
      }
    } catch (e) {
      const offline = e instanceof TypeError;
      reply({ok: false, error: offline ? "DenziDownloader app isn't running. Open it first." : e.message});
    }
  })();
  return true; // async reply
});
