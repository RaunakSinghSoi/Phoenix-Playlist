/* PhoenixPlaylist – frontend logic */

let lastBatchResult = null;

// ── Helpers ────────────────────────────────────────────────────────────────

function setLoading(btnEl, loading) {
  if (loading) {
    btnEl.disabled = true;
    btnEl.dataset.originalText = btnEl.textContent;
    btnEl.innerHTML = '<span class="spinner"></span>Working…';
  } else {
    btnEl.disabled = false;
    btnEl.textContent = btnEl.dataset.originalText || btnEl.textContent;
  }
}

function showResult(el, html, isError = false) {
  el.innerHTML = html;
  el.className = 'result-box' + (isError ? ' error' : '');
  el.classList.remove('hidden');
}

function moodClass(mood) { return `mood-${mood}`; }

function moodEmoji(mood) {
  return { happy: '🌟', sad: '🌧️', energetic: '⚡', chill: '🍃' }[mood] || '🎵';
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso.replace(' ', 'T') + 'Z');
  return d.toLocaleDateString('en-CA', { month: 'short', day: 'numeric', year: 'numeric' });
}

function trackItemHTML(result) {
  const t = result.track || {};
  const img = t.album_image || '';
  const imgTag = img
    ? `<img src="${img}" alt="${t.name}" loading="lazy" />`
    : `<div style="width:36px;height:36px;background:#2e2e3d;border-radius:4px;flex-shrink:0"></div>`;
  return `
    <div class="track-item">
      ${imgTag}
      <div class="track-item-info">
        <div class="track-item-title">${t.name || 'Unknown'}</div>
        <div class="track-item-artist">${t.artist || ''}</div>
      </div>
    </div>`;
}

// ── Single Track Recognition ───────────────────────────────────────────────

async function recognizeTrack() {
  const input    = document.getElementById('query-input');
  const resultEl = document.getElementById('recognize-result');
  const btn      = document.querySelector('#recognize-section .btn');
  const query    = input.value.trim();

  if (!query) { showResult(resultEl, 'Please enter a song title or artist + title.', true); return; }

  setLoading(btn, true);
  try {
    const res  = await fetch('/api/recognize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();

    if (data.error) { showResult(resultEl, `Error: ${data.error}`, true); return; }

    const t    = data.track || {};
    const mood = data.mood  || {};
    const af   = data.audio_features || {};

    const imgTag = t.album_image
      ? `<img src="${t.album_image}" alt="${t.name}" style="width:72px;height:72px;border-radius:8px;object-fit:cover;flex-shrink:0" />`
      : '';

    const previewBtn = t.preview_url
      ? `<button class="btn btn-outline btn-sm" style="margin-top:.5rem" onclick="togglePreview('${t.preview_url}', this)">Play Preview</button>`
      : '';

    const energy  = af.energy  != null ? `${Math.round(af.energy  * 100)}%` : 'N/A';
    const valence = af.valence != null ? `${Math.round(af.valence * 100)}%` : 'N/A';
    const bpm     = af.tempo   != null ? `${Math.round(af.tempo)} BPM`     : 'N/A';

    showResult(resultEl, `
      <div class="track-card">
        ${imgTag}
        <div class="track-info">
          <h3>${t.name || query}</h3>
          <p>${t.artist || ''} &mdash; ${t.album || ''}</p>
          <p style="font-size:.8rem;color:var(--muted)">BPM: ${bpm} &nbsp;|&nbsp; Energy: ${energy} &nbsp;|&nbsp; Positivity: ${valence}</p>
          <span class="mood-tag ${moodClass(mood.mood)}">${moodEmoji(mood.mood)} ${mood.label || mood.mood}</span>
          <span style="font-size:.78rem;color:var(--muted);margin-left:.5rem">Confidence: ${Math.round((mood.confidence || 0) * 100)}%</span>
          ${previewBtn}
          ${t.external_url ? `<br><a href="${t.external_url}" target="_blank" rel="noopener" style="font-size:.82rem;color:var(--green);margin-top:.4rem;display:inline-block">Open in Spotify</a>` : ''}
        </div>
      </div>
    `);
  } catch (err) {
    showResult(resultEl, `Network error: ${err.message}`, true);
  } finally {
    setLoading(btn, false);
  }
}

// ── Audio preview ──────────────────────────────────────────────────────────

let currentAudio = null;
function togglePreview(url, btn) {
  if (currentAudio && !currentAudio.paused) {
    currentAudio.pause();
    btn.textContent = 'Play Preview';
    return;
  }
  currentAudio = new Audio(url);
  currentAudio.play();
  btn.textContent = 'Pause';
  currentAudio.onended = () => { btn.textContent = 'Play Preview'; };
}

// ── Batch Playlist Generation ──────────────────────────────────────────────

async function generatePlaylist() {
  const textarea   = document.getElementById('batch-input');
  const moodFilter = document.getElementById('mood-filter').value;
  const resultEl   = document.getElementById('batch-result');
  const boardsEl   = document.getElementById('mood-boards');
  const btn        = document.querySelector('#batch-section .btn-primary');

  const lines = textarea.value.split('\n').map(l => l.trim()).filter(Boolean);
  if (!lines.length) { showResult(resultEl, 'Please enter at least one song per line.', true); return; }

  setLoading(btn, true);
  boardsEl.classList.add('hidden');
  resultEl.classList.add('hidden');

  try {
    const res  = await fetch('/api/playlist/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ songs: lines, mood: moodFilter || undefined }),
    });
    const data = await res.json();

    if (data.error) { showResult(resultEl, `Error: ${data.error}`, true); return; }

    lastBatchResult = data.playlists;
    renderMoodBoards(data.playlists);
    boardsEl.classList.remove('hidden');
  } catch (err) {
    showResult(resultEl, `Network error: ${err.message}`, true);
  } finally {
    setLoading(btn, false);
  }
}

function renderMoodBoards(playlists) {
  const grid = document.getElementById('mood-grid');
  grid.innerHTML = '';
  const moods = [
    { key: 'happy',     label: 'Happy',     emoji: '🌟' },
    { key: 'sad',       label: 'Sad',       emoji: '🌧️' },
    { key: 'energetic', label: 'Energetic', emoji: '⚡' },
    { key: 'chill',     label: 'Chill',     emoji: '🍃' },
  ];
  for (const { key, label, emoji } of moods) {
    const tracks  = playlists[key] || [];
    const bucket  = document.createElement('div');
    bucket.className = 'mood-bucket';
    const tracksHTML = tracks.length
      ? tracks.map(trackItemHTML).join('')
      : `<p class="hint" style="font-size:.82rem">No tracks classified here.</p>`;
    bucket.innerHTML = `
      <div class="mood-bucket-header">
        <span class="mood-tag ${moodClass(key)}">${emoji} ${label}</span>
        <span class="mood-count">${tracks.length}</span>
      </div>
      <div class="track-list">${tracksHTML}</div>`;
    grid.appendChild(bucket);
  }
}

// ── Push to Spotify ────────────────────────────────────────────────────────

async function pushToSpotify() {
  const mood     = document.getElementById('push-mood').value;
  const resultEl = document.getElementById('push-result');
  const btn      = document.querySelector('.push-area .btn-spotify');

  if (!lastBatchResult || !(lastBatchResult[mood] || []).length) {
    showResult(resultEl, `No tracks in the "${mood}" playlist to push.`, true);
    return;
  }

  setLoading(btn, true);
  try {
    const res  = await fetch('/api/playlist/push', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tracks: lastBatchResult[mood], mood }),
    });
    const data = await res.json();

    if (data.error) { showResult(resultEl, `Error: ${data.error}`, true); return; }

    showResult(resultEl, `
      <strong>Playlist created:</strong> ${data.name}<br/>
      ${data.tracks_added} tracks added.<br/>
      <a href="${data.playlist_url}" target="_blank" rel="noopener" style="color:var(--green)">Open in Spotify</a>
    `);
    loadHistory();
  } catch (err) {
    showResult(resultEl, `Network error: ${err.message}`, true);
  } finally {
    setLoading(btn, false);
  }
}

// ── History ────────────────────────────────────────────────────────────────

async function loadHistory() {
  const listEl  = document.getElementById('history-list');
  const statsEl = document.getElementById('stats-row');
  if (!listEl) return;

  listEl.innerHTML = '<p class="hint">Loading…</p>';

  try {
    const [histRes, statsRes] = await Promise.all([
      fetch('/api/history'),
      fetch('/api/history/stats'),
    ]);
    const histData  = await histRes.json();
    const statsData = await statsRes.json();

    if (statsData.stats && statsData.stats.length) {
      statsEl.innerHTML = statsData.stats.map(s => `
        <div class="stat-chip">
          <span>${moodEmoji(s.mood_category)}</span>
          <strong>${s.playlist_count}</strong>
          <span>${s.mood_category} playlist${s.playlist_count !== 1 ? 's' : ''}</span>
          <span style="color:var(--border)">·</span>
          <strong>${s.total_tracks}</strong>
          <span>tracks</span>
        </div>`).join('');
      statsEl.classList.remove('hidden');
    }

    const playlists = histData.playlists || [];
    if (!playlists.length) {
      listEl.innerHTML = '<p class="hint">No playlists saved yet. Generate and push one above.</p>';
      return;
    }

    listEl.innerHTML = `<div class="history-list">${playlists.map(p => `
      <div class="history-item">
        <div class="history-item-left">
          <span class="mood-tag ${moodClass(p.mood_category)}">${moodEmoji(p.mood_category)} ${p.mood_category}</span>
          <div>
            <div class="history-item-name">${p.playlist_name}</div>
            <div class="history-item-meta">${p.track_count} tracks &nbsp;·&nbsp; ${formatDate(p.created_at)}</div>
          </div>
        </div>
        <div class="history-item-right">
          ${p.spotify_url ? `<a href="${p.spotify_url}" target="_blank" rel="noopener" class="btn btn-spotify btn-sm">Open</a>` : ''}
        </div>
      </div>`).join('')}
    </div>`;
  } catch (err) {
    listEl.innerHTML = `<p class="hint" style="color:#f43f5e">Failed to load history: ${err.message}</p>`;
  }
}

// ── Enter key support ──────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('query-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') recognizeTrack();
  });
});
