'use strict';

/* ═══════════════════════════════════════
   PULSE — AI News Intelligence
   Clean JS · No technical jargon exposed
═══════════════════════════════════════ */

// ── THEME ──────────────────────────────
function toggleTheme() {
  const curr = document.documentElement.getAttribute('data-theme') || 'light';
  const next = curr === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('pulse_theme', next);
}

// ── STATE ──────────────────────────────
let count = 5;
let source = 'rss';
let allResults = [];
const HK = 'pulse_history';

// ── DISCOVER DATA ──────────────────────
const TOPICS = [
  { topic: 'Artificial Intelligence', desc: 'Breakthroughs, research and industry shifts', color: 'var(--dot-blue)',   cat: 'Technology' },
  { topic: 'India economy',           desc: 'Markets, policy and financial developments',  color: 'var(--dot-green)',  cat: 'Economy' },
  { topic: 'Climate change',          desc: 'Environment, policy and sustainability',       color: 'var(--dot-teal)',   cat: 'Environment' },
  { topic: 'Space exploration',       desc: 'Missions, discoveries and aerospace',          color: 'var(--dot-purple)', cat: 'Science' },
  { topic: 'Cybersecurity',           desc: 'Digital threats, data safety and privacy',     color: 'var(--dot-red)',    cat: 'Security' },
  { topic: 'Electric vehicles',       desc: 'EV market, batteries and clean transport',     color: 'var(--dot-amber)',  cat: 'Transport' },
  { topic: 'Global markets',          desc: 'Stocks, forex, commodities and trade',         color: 'var(--dot-blue)',   cat: 'Finance' },
  { topic: 'Healthcare',              desc: 'Medicine, research and public health',          color: 'var(--dot-green)',  cat: 'Health' },
];

// ── INIT ───────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  buildDiscover();
  refreshHistory();
  document.getElementById('topicInput')
    .addEventListener('keydown', e => { if (e.key === 'Enter') runSearch(); });
});

// ── DISCOVER GRID ──────────────────────
function buildDiscover() {
  document.getElementById('discoverGrid').innerHTML = TOPICS.map(t => `
    <div class="disc-card" onclick="quickSearch('${esc(t.topic)}')">
      <div class="disc-dot-row">
        <span class="disc-dot" style="background:${t.color}"></span>
        <span class="disc-cat">${esc(t.cat)}</span>
      </div>
      <div class="disc-topic">${esc(t.topic)}</div>
      <div class="disc-desc">${esc(t.desc)}</div>
      <div class="disc-cta">Analyze <span>→</span></div>
    </div>`).join('');
}

// ── CONTROLS ───────────────────────────
function adjustCount(d) {
  count = Math.min(8, Math.max(1, count + d));
  document.getElementById('countVal').textContent = count;
}

function setSource(src) {
  source = src;
  document.getElementById('srcRss').classList.toggle('active', src === 'rss');
  document.getElementById('srcGnews').classList.toggle('active', src === 'gnews');
}

function quickSearch(topic) {
  document.getElementById('topicInput').value = topic;
  runSearch();
}

// ── SEARCH ─────────────────────────────
async function runSearch() {
  const topic = document.getElementById('topicInput').value.trim();
  if (!topic) { showAlert('Please enter a topic to explore.', 'error'); return; }

  const btn = document.getElementById('searchBtn');
  btn.disabled = true;

  showAlert(`Gathering and analyzing articles about "${topic}"…`, 'loading', true);
  document.getElementById('discoverSection').style.display = 'none';
  document.getElementById('resultsSection').style.display  = 'none';

  try {
    const res  = await fetch('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, num_articles: count })
    });
    const data = await res.json();

    if (data.error) {
      showAlert('Something went wrong. Please try again.', 'error');
      document.getElementById('discoverSection').style.display = 'block';
      return;
    }

    allResults = data.results || [];

    if (!allResults.length) {
      showAlert(`No articles found for "${topic}". Try a broader search term.`, 'error');
      document.getElementById('discoverSection').style.display = 'block';
      return;
    }

    saveSearch(topic, allResults.length);
    showAlert(`Found ${allResults.length} article${allResults.length > 1 ? 's' : ''} about "${topic}"`, 'success');
    setTimeout(hideAlert, 4000);

    document.getElementById('resultsHeading').textContent = `"${topic}"`;
    document.getElementById('resultsBadge').textContent   = `${allResults.length} articles`;
    document.getElementById('resultsSection').style.display = 'block';
    renderArticles(allResults);

    document.getElementById('resultsSection')
      .scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch {
    showAlert('Cannot connect to the backend. Please make sure it is running.', 'error');
    document.getElementById('discoverSection').style.display = 'block';
  } finally {
    btn.disabled = false;
  }
}

// ── RENDER ARTICLES ────────────────────
function renderArticles(results) {
  document.getElementById('articlesGrid').innerHTML =
    results.map((item, i) => buildCard(item, i)).join('');
}

function buildCard(item, i) {
  const a   = item.analysis || {};
  const sen = a.sentiment || 'Neutral';
  const cat = a.category  || 'General';
  const pts = (a.key_points || []).slice(0, 3);

  const senClass = sen === 'Positive' ? 'tag-pos' : sen === 'Negative' ? 'tag-neg' : 'tag-neu';

  return `
  <article class="article-card" style="animation-delay:${i * 60}ms">
    <div class="ac-top">
      <div class="ac-title">${esc(item.title)}</div>
      <span class="ac-source">${esc(item.source || 'News')}</span>
    </div>

    <div class="ac-tags">
      <span class="tag tag-cat">${esc(cat)}</span>
      <span class="tag ${senClass}">${esc(sen)}</span>
    </div>

    <div class="ac-divider"></div>

    <div>
      <div class="field-lbl">Summary</div>
      <p class="ac-summary">${esc(a.summary || '—')}</p>
    </div>

    <div>
      <div class="field-lbl">Plain explanation</div>
      <div class="ac-explain">${esc(a.explanation || '—')}</div>
    </div>

    ${pts.length ? `<div>
      <div class="field-lbl">Key points</div>
      <ul class="ac-points">${pts.map(p => `<li>${esc(p)}</li>`).join('')}</ul>
    </div>` : ''}

    <div class="ac-footer">
      <a class="ac-link" href="${esc(item.url)}" target="_blank" rel="noopener">
        Read full article →
      </a>
    </div>
  </article>`;
}

// ── SORT ───────────────────────────────
function sortBy(val) {
  const order = {
    positive: { Positive: 0, Neutral: 1, Negative: 2 },
    negative: { Negative: 0, Neutral: 1, Positive: 2 },
    neutral:  { Neutral: 0, Positive: 1, Negative: 2 },
  };
  const sorted = [...allResults];
  if (order[val]) {
    sorted.sort((a, b) =>
      (order[val][a.analysis?.sentiment] ?? 1) -
      (order[val][b.analysis?.sentiment] ?? 1)
    );
  }
  renderArticles(sorted);
}

// ── ALERT ──────────────────────────────
function showAlert(msg, type, spinner = false) {
  const el  = document.getElementById('alert');
  const sp  = document.getElementById('alertSpinner');
  const txt = document.getElementById('alertText');
  el.className  = `alert ${type}`;
  txt.textContent = msg;
  sp.className  = 'alert-spinner' + (spinner ? '' : ' off');
}
function hideAlert() {
  document.getElementById('alert').classList.add('hidden');
}

// ── HISTORY ────────────────────────────
function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HK)) || []; }
  catch { return []; }
}

function saveSearch(topic, n) {
  const h = loadHistory().filter(x => x.topic.toLowerCase() !== topic.toLowerCase());
  h.unshift({ topic, count: n, time: new Date().toISOString() });
  localStorage.setItem(HK, JSON.stringify(h.slice(0, 30)));
  refreshHistory();
}

function deleteSearch(i, e) {
  e.stopPropagation();
  const h = loadHistory(); h.splice(i, 1);
  localStorage.setItem(HK, JSON.stringify(h));
  refreshHistory();
}

function clearHistory() {
  localStorage.removeItem(HK); refreshHistory();
}

function refreshHistory() {
  const h   = loadHistory();
  const cnt = document.getElementById('historyCount');
  cnt.textContent = h.length;
  cnt.style.display = h.length ? 'flex' : 'none';

  const list = document.getElementById('historyList');
  if (!h.length) {
    list.innerHTML = `<div class="drawer-empty">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      <p>No searches yet</p></div>`;
    return;
  }
  list.innerHTML = h.map((x, i) => {
    const d = new Date(x.time);
    const ts = d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
             + ' · ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    return `<div class="h-item" onclick="reSearch('${esc(x.topic)}')">
      <div class="h-item-left">
        <div class="h-item-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        </div>
        <div class="h-item-info">
          <div class="h-item-topic">${esc(x.topic)}</div>
          <div class="h-item-meta">${x.count} articles · ${ts}</div>
        </div>
      </div>
      <button class="h-item-del" onclick="deleteSearch(${i}, event)" title="Remove">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>`;
  }).join('');
}

function reSearch(topic) {
  closeHistory();
  document.getElementById('topicInput').value = topic;
  runSearch();
}

// ── DRAWER ─────────────────────────────
function openHistory() {
  document.getElementById('drawer').classList.add('open');
  document.getElementById('drawerOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeHistory() {
  document.getElementById('drawer').classList.remove('open');
  document.getElementById('drawerOverlay').classList.remove('open');
  document.body.style.overflow = '';
}

// ── UTIL ───────────────────────────────
function esc(s) {
  return String(s || '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}