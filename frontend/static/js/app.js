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

function moodClass(mood) {
  return `mood-${mood}`;
}

function moodEmoji(mood) {
  return { happy: '🌟', sad: '🌧️', energetic: '⚡', chill: '🍃' }[mood] || '🎵';
}

function trackItemHTML(track) {
  const shazam = track.shazam || {};
  const spotify = track.spotify || {};
  const img = spotify.album_image || shazam.image_url || '';
  const title = shazam.title || spotify.name || 'Unknown';
  const artist = shazam.artist || spotify.artist || '';
  const imgTag = img
    ? `<img src="${img}" alt="${title}" loading="lazy" />`
    : `<div style="width:36px;height:36px;background:#2e2e3d;border-radius:4px;flex-shrink:0"></div>`;
  return `
    <div class="track-item">
      ${imgTag}
      <div class="track-item-info">
        <div class="track-item-title">${title}</div>
        <div class="track-item-artist">${artist}</div>
      </div>
    </div>`;
}

// ── Single Track Recognition ───────────────────────────────────────────────

async function recognizeTrack() {
  const input = document.getElementById('query-input');
  const resultEl = document.getElementById('recognize-result');
  const btn = document.querySelector('#recognize-section .btn');
  const query = input.value.trim();

  if (!query) {
    showResult(resultEl, 'Please enter a song title or artist + title.', true);
    return;
  }

  setLoading(btn, true);
  try {
    const res = await fetch('/api/recognize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();

    if (data.error) {
      showResult(resultEl, `Error: ${data.error}`, true);
      return;
    }

    const shazam = data.shazam || {};
    const spotify = data.spotify || {};
    const mood = data.mood || {};
    const af = data.audio_features || {};

    const img = spotify.album_image || shazam.image_url || '';
    const imgTag = img
      ? `<img src="${img}" alt="${shazam.title}" style="width:72px;height:72px;border-radius:8px;object-fit:cover;flex-shrink:0" />`
      : '';

    const previewBtn = spotify.preview_url
      ? `<button class="btn btn-outline" style="margin-top:.5rem;font-size:.8rem" onclick="togglePreview('${spotify.preview_url}', this)">▶ Preview</button>`
      : '';

    const energy = af.energy != null ? `${Math.round(af.energy * 100)}%` : 'N/A';
    const valence = af.valence != null ? `${Math.round(af.valence * 100)}%` : 'N/A';
    const bpm = af.tempo != null ? `${Math.round(af.tempo)} BPM` : 'N/A';

    showResult(resultEl, `
      <div class="track-card">
        ${imgTag}
        <div class="track-info">
          <h3>${shazam.title || spotify.name || query}</h3>
          <p>${shazam.artist || spotify.artist || ''}</p>
          <p style="font-size:.8rem;color:var(--muted)">Genre: ${shazam.genre || 'Unknown'} &nbsp;|&nbsp; BPM: ${bpm}</p>
          <p style="font-size:.8rem;color:var(--muted)">Energy: ${energy} &nbsp;|&nbsp; Positivity: ${valence}</p>
          <span class="mood-tag ${moodClass(mood.mood)}">${moodEmoji(mood.mood)} ${mood.label || mood.mood}</span>
          <span style="font-size:.78rem;color:var(--muted);margin-left:.5rem">Confidence: ${Math.round((mood.confidence || 0) * 100)}%</span>
          ${previewBtn}
        </div>
      </div>
    `);
  } catch (err) {
    showResult(resultEl, `Network error: ${err.message}`, true);
  } finally {
    setLoading(btn, false);
  }
}

// ── Audio preview toggle ───────────────────────────────────────────────────

let currentAudio = null;
function togglePreview(url, btn) {
  if (currentAudio && !currentAudio.paused) {
    currentAudio.pause();
    btn.textContent = '▶ Preview';
    return;
  }
  currentAudio = new Audio(url);
  currentAudio.play();
  btn.textContent = '⏸ Pause';
  currentAudio.onended = () => { btn.textContent = '▶ Preview'; };
}

// ── Batch Playlist Generation ──────────────────────────────────────────────

async function generatePlaylist() {
  const textarea = document.getElementById('batch-input');
  const moodFilter = document.getElementById('mood-filter').value;
  const resultEl = document.getElementById('batch-result');
  const boardsEl = document.getElementById('mood-boards');
  const btn = document.querySelector('#batch-section .btn-primary');

  const lines = textarea.value.split('\n').map(l => l.trim()).filter(Boolean);
  if (!lines.length) {
    showResult(resultEl, 'Please enter at least one song per line.', true);
    return;
  }

  setLoading(btn, true);
  boardsEl.classList.add('hidden');
  resultEl.classList.add('hidden');

  try {
    const res = await fetch('/api/playlist/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ songs: lines, mood: moodFilter || undefined }),
    });
    const data = await res.json();

    if (data.error) {
      showResult(resultEl, `Error: ${data.error}`, true);
      return;
    }

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
    const tracks = playlists[key] || [];
    const bucket = document.createElement('div');
    bucket.className = 'mood-bucket';

    const tracksHTML = tracks.length
      ? tracks.map(trackItemHTML).join('')
      : `<p class="hint" style="font-size:.82rem">No tracks classified here.</p>`;

    bucket.innerHTML = `
      <div class="mood-bucket-header">
        <span class="mood-bucket-title"><span class="mood-tag ${moodClass(key)}">${emoji} ${label}</span></span>
        <span class="mood-count">${tracks.length}</span>
      </div>
      <div class="track-list">${tracksHTML}</div>`;
    grid.appendChild(bucket);
  }
}

// ── Push to Spotify ────────────────────────────────────────────────────────

async function pushToSpotify() {
  const mood = document.getElementById('push-mood').value;
  const resultEl = document.getElementById('push-result');
  const btn = document.querySelector('.push-area .btn-spotify');

  if (!lastBatchResult || !(lastBatchResult[mood] || []).length) {
    showResult(resultEl, `No tracks in the "${mood}" playlist to push.`, true);
    return;
  }

  setLoading(btn, true);
  try {
    const res = await fetch('/api/playlist/push', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tracks: lastBatchResult[mood], mood }),
    });
    const data = await res.json();

    if (data.error) {
      showResult(resultEl, `Error: ${data.error}`, true);
      return;
    }

    showResult(resultEl, `
      <strong>✅ Playlist created!</strong><br/>
      <strong>${data.name}</strong> — ${data.tracks_added} tracks added.<br/>
      <a href="${data.playlist_url}" target="_blank" rel="noopener" style="color:var(--green)">Open in Spotify ↗</a>
    `);
  } catch (err) {
    showResult(resultEl, `Network error: ${err.message}`, true);
  } finally {
    setLoading(btn, false);
  }
}

// ── Enter key support ──────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('query-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') recognizeTrack();
  });
});
