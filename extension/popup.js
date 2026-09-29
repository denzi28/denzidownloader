const BASE = 'http://127.0.0.1:8765';
const $ = id => document.getElementById(id);
let info = null, mode = 'video', dir = '';

const api = async (path, body) => {
  const r = await fetch(BASE + path, body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : {});
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || 'Error');
  return j;
};
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const fmtS = b => b ? ` (~${(b / 1048576).toFixed(0)} MB)` : '';

function fillQuality() {
  $('quality').innerHTML = mode === 'audio'
    ? '<option value="320">320 kbps (best)</option><option value="192" selected>192 kbps</option><option value="128">128 kbps</option>'
    : '<option value="">Best available</option>' + info.heights.map(h => `<option value="${h.height}">${h.height}p${fmtS(h.size)}</option>`).join('');
}
function setMode(m) {
  mode = m;
  $('tVideo').classList.toggle('on', m === 'video');
  $('tAudio').classList.toggle('on', m === 'audio');
  fillQuality();
}
$('tVideo').onclick = () => setMode('video');
$('tAudio').onclick = () => setMode('audio');

async function analyze() {
  const url = $('url').value.trim();
  if (!url) return;
  $('err').textContent = ''; $('opts').hidden = true;
  $('go').disabled = true; $('go').textContent = '…';
  try {
    info = await api('/api/info', {url});
    $('thumb').src = info.thumbnail || '';
    $('title').textContent = info.title || 'Untitled';
    $('sub').textContent = [info.site, info.uploader].filter(Boolean).join(' · ');
    $('opts').hidden = false;
    setMode(mode);
  } catch (e) { $('err').textContent = e.message; }
  $('go').disabled = false; $('go').textContent = 'Analyze';
}
$('go').onclick = analyze;
$('url').addEventListener('keydown', e => e.key === 'Enter' && analyze());

async function setDir(path) {
  const c = await api('/api/config', {download_dir: path});
  dir = c.download_dir; $('dir').textContent = dir; $('manual').hidden = true;
}
$('change').onclick = async () => {
  try {
    const c = await api('/api/pick-folder', {});
    dir = c.download_dir; $('dir').textContent = dir;
  } catch { $('manual').hidden = false; }
};
$('setDir').onclick = () => setDir($('manualDir').value).catch(e => $('err').textContent = e.message);

$('dl').onclick = async () => {
  try {
    await api('/api/download', {
      url: $('url').value.trim(), mode, title: info.title, download_dir: dir,
      height: mode === 'video' ? $('quality').value : null,
      audio_quality: mode === 'audio' ? $('quality').value : null,
    });
    poll();
  } catch (e) { $('err').textContent = e.message; }
};

const played = new Set();
let firstPoll = true;
async function poll() {
  const js = await api('/api/jobs');
  for (const j of js) if (j.status === 'done' && !played.has(j.id)) {
    played.add(j.id);
    if (firstPoll) continue; // don't replay for downloads finished before the popup opened
    const a = new Audio('sounds/notify.mp3'); a.volume = 0.15; a.play().catch(() => {}); setTimeout(() => a.pause(), 3000);
  }
  firstPoll = false;
  $('jobs').innerHTML = js.slice(0, 4).map(j => `<div class="job">${j.mode === 'audio' ? '🎵' : '🎬'} ${esc(j.title)}<br>
    <span class="mute">${j.status === 'error' ? esc(j.error) : j.status === 'done' ? '✅ Saved to ' + esc(j.dir) : j.status + ' ' + j.percent + '%'}</span>
    ${['done', 'error'].includes(j.status) ? '' : `<div class="bar"><div style="width:${j.percent}%"></div></div>`}</div>`).join('');
  if (js.some(j => !['done', 'error'].includes(j.status))) setTimeout(poll, 800);
}

(async () => {
  try {
    const c = await api('/api/config');
    dir = c.download_dir; $('dir').textContent = dir;
  } catch {
    $('offline').hidden = false; $('main').hidden = true; return;
  }
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  if (tab?.url && /^https?:/.test(tab.url)) { $('url').value = tab.url; analyze(); }
  poll();
})();
