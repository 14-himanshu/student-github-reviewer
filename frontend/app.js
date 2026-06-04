'use strict';

/* ================================================================
   STATE
   ================================================================ */
let currentUsername = '';
let currentMarkdown = '';
let chatMessages    = [];
let chatOpen        = false;

/* ================================================================
   ELEMENT REFS
   ================================================================ */
const $ = id => document.getElementById(id);

/* ================================================================
   THEME TOGGLE
   ================================================================ */
const savedTheme = localStorage.getItem('devreview-theme') || 'dark';
document.documentElement.setAttribute('data-theme', savedTheme);
$('theme-toggle').addEventListener('click', () => {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('devreview-theme', next);
});

/* ================================================================
   INTEGRATIONS TOGGLE
   ================================================================ */
$('show-integrations-btn').addEventListener('click', () => {
    const row = $('integrations-row');
    row.classList.toggle('hidden');
    $('show-integrations-btn').innerText = row.classList.contains('hidden')
        ? 'Add LeetCode & StackOverflow'
        : 'Hide integrations';
});

/* ================================================================
   ANALYZE
   ================================================================ */
$('github-username').addEventListener('keydown', e => { if (e.key === 'Enter') $('analyze-btn').click(); });

$('analyze-btn').addEventListener('click', () => {
    const user = $('github-username').value.trim();
    const lc   = ($('leetcode-username').value || '').trim();
    const so   = ($('stackoverflow-username').value || '').trim();
    if (!user) { $('github-username').focus(); return; }
    chatMessages = [];
    analyzePortfolio(user, lc, so);
});

async function analyzePortfolio(user, lc, so) {
    showLoading('Analyzing portfolio...');
    try {
        const data = await apiPost(`/review?username=${enc(user)}&leetcode=${enc(lc)}&stackoverflow=${enc(so)}`);
        currentUsername = data.username || user;
        renderDashboard(data);
    } catch(err) {
        showError('Could not retrieve the portfolio. ' + err.message);
    }
}

/* ================================================================
   SHARED REVIEW
   ================================================================ */
window.addEventListener('DOMContentLoaded', () => {
    const reviewId = new URLSearchParams(window.location.search).get('review_id');
    if (reviewId) loadSharedReview(reviewId);
});

async function loadSharedReview(id) {
    showLoading('Loading shared review...');
    try {
        const data = await apiGet(`/reviews/${id}`);
        currentUsername = data.username;
        renderDashboard(data);
    } catch { showError('Shared review not found or expired.'); }
}

/* ================================================================
   VIEW HELPERS
   ================================================================ */
function showHero() {
    ['hero-section', 'loading-state', 'error-state', 'dashboard', 'site-footer'].forEach(id => {
        $(id).classList.add('hidden');
    });
    $('hero-section').classList.remove('hidden');
    $('chat-fab').classList.add('hidden');
    $('open-chat-btn').classList.add('hidden');
}
function showLoading(label) {
    $('hero-section').classList.add('hidden');
    $('error-state').classList.add('hidden');
    $('dashboard').classList.add('hidden');
    $('site-footer').classList.add('hidden');
    $('chat-fab').classList.add('hidden');
    $('open-chat-btn').classList.add('hidden');
    $('loading-text').innerText = label || 'Analyzing...';
    $('loading-state').classList.remove('hidden');
}
function showError(msg) {
    $('loading-state').classList.add('hidden');
    $('dashboard').classList.add('hidden');
    $('hero-section').classList.add('hidden');
    $('error-message').innerText = msg;
    $('error-state').classList.remove('hidden');
}
function showDashboard() {
    $('loading-state').classList.add('hidden');
    $('error-state').classList.add('hidden');
    $('hero-section').classList.add('hidden');
    $('dashboard').classList.remove('hidden');
    $('site-footer').classList.remove('hidden');
    $('chat-fab').classList.remove('hidden');
    $('open-chat-btn').classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ================================================================
   RESET / RETRY
   ================================================================ */
$('reset-btn').addEventListener('click', () => { showHero(); $('github-username').value = ''; });
$('nav-logo-btn').addEventListener('click', e => { e.preventDefault(); showHero(); $('github-username').value = ''; });
$('error-retry-btn').addEventListener('click', showHero);

/* ================================================================
   API HELPERS
   ================================================================ */
async function apiPost(path) {
    const res = await fetch(path, { method: 'POST' });
    if (!res.ok) { const t = await res.text().catch(()=>''); throw new Error(`${res.status} — ${t||res.statusText}`); }
    return res.json();
}
async function apiGet(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`${res.status}`);
    return res.json();
}
function enc(s) { return encodeURIComponent(s||''); }

/* ================================================================
   RENDER DASHBOARD
   ================================================================ */
function renderDashboard(data) {
    const ext      = data.extracted_data  || {};
    const feedback = data.mentor_feedback || '';

    /* Profile bar */
    $('profile-avatar').src = ext.avatar_url || 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
    $('profile-name').innerText = currentUsername;
    $('profile-followers-chip').innerText = `${(ext.followers||0).toLocaleString()} followers`;

    /* Stats */
    $('metric-repos').innerText     = (ext.public_repos_count||0).toLocaleString();
    $('metric-languages').innerText = (ext.primary_languages||[]).length;
    $('metric-recent').innerText    = (ext.recent_repos||[]).length;

    /* Grade & Badges */
    const gradeMatch  = feedback.match(/\[GRADE:\s*(.*?)\]/);
    const badgesMatch = feedback.match(/\[BADGES:\s*(.*?)\]/);
    $('feedback-grade').innerText = gradeMatch ? gradeMatch[1].trim() : '—';

    const badgesSection = $('badges-section');
    const badgesRow     = $('feedback-badges');
    badgesRow.innerHTML = '';
    if (badgesMatch) {
        badgesMatch[1].split(',').forEach(b => {
            const chip = document.createElement('span');
            chip.className = 'badge-chip';
            chip.innerText = b.trim();
            badgesRow.appendChild(chip);
        });
        badgesSection.classList.remove('hidden');
    } else {
        badgesSection.classList.add('hidden');
    }

    /* Mentor Feedback */
    let clean = feedback.replace(/\[GRADE:\s*.*?\]/g,'').replace(/\[BADGES:\s*.*?\]/g,'').trim();
    currentMarkdown = clean;
    $('feedback-markdown').innerHTML = marked.parse(clean);

    /* Languages */
    const langs     = ext.primary_languages || [];
    const langList  = $('languages-list');
    langList.innerHTML = '';
    if (langs.length) {
        langs.slice(0,8).forEach((lang,i) => {
            const pct = Math.max(8, 100 - i*13);
            const item = document.createElement('div');
            item.className = 'lang-item';
            item.innerHTML = `<span class="lang-name">${escHtml(lang)}</span><div class="lang-bar-track"><div class="lang-bar-fill" style="width:0" data-pct="${pct}%"></div></div><span class="lang-pct">${pct}%</span>`;
            langList.appendChild(item);
        });
        requestAnimationFrame(() => {
            langList.querySelectorAll('.lang-bar-fill').forEach(b => { b.style.width = b.dataset.pct; });
        });
    } else {
        langList.innerHTML = '<p style="font-size:0.85rem;color:var(--text-secondary)">No data</p>';
    }

    /* Repos */
    const repos      = ext.recent_repos || [];
    const reposList  = $('repos-list');
    reposList.innerHTML = '';
    repos.forEach(repo => {
        const li = document.createElement('li');
        li.className = 'repo-item';
        li.innerHTML = `<span class="repo-name" title="${escHtml(repo)}">${escHtml(repo)}</span><a class="repo-link" href="https://github.com/${enc(currentUsername)}/${enc(repo)}" target="_blank" rel="noopener"><svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg></a>`;
        reposList.appendChild(li);
    });

    /* Deep Dive select */
    const ddSel = $('tool-dd-select');
    ddSel.innerHTML = '';
    repos.forEach(repo => {
        const opt = document.createElement('option');
        opt.value = repo; opt.innerText = repo;
        ddSel.appendChild(opt);
    });

    /* Reset tool outputs + collapse buttons */
    ['cl','rm','pi','iq','dd'].forEach(key => {
        const result  = $(`tool-${key}-result`);
        if (result) { result.innerHTML = ''; result.classList.add('hidden'); }
        const colBtn = document.querySelector(`[data-target="tool-${key}-result"]`);
        if (colBtn) { colBtn.classList.add('hidden'); colBtn.classList.remove('expanded'); }
    });

    /* Reset share link */
    $('share-link-result').classList.add('hidden');

    /* Reset chat */
    chatMessages = [];
    $('chat-messages').innerHTML = '';

    showDashboard();
}

function escHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

/* ================================================================
   COLLAPSE / EXPAND — tool results
   ================================================================ */
document.addEventListener('click', e => {
    const colBtn = e.target.closest('.tool-collapse-btn');
    if (!colBtn) return;
    const targetId = colBtn.dataset.target;
    const result   = $(targetId);
    if (!result) return;
    const isExpanded = !result.classList.contains('hidden');
    if (isExpanded) {
        result.classList.add('hidden');
        colBtn.classList.remove('expanded');
        colBtn.title = 'Show result';
    } else {
        result.classList.remove('hidden');
        colBtn.classList.add('expanded');
        colBtn.title = 'Collapse';
    }
});

/* ================================================================
   SHARE LINK
   ================================================================ */
$('share-link-btn').addEventListener('click', async () => {
    const btn    = $('share-link-btn');
    const result = $('share-link-result');
    btn.disabled = true; btn.innerText = 'Saving...';
    try {
        const data = await apiPost(`/reviews/save?username=${enc(currentUsername)}`);
        const url  = `${location.origin}/?review_id=${data.review_id}`;
        result.innerHTML = `Link ready: <a href="${url}">${url}</a>`;
        result.classList.remove('hidden');
    } catch(e) {
        result.innerHTML = 'Failed to create link. ' + e.message;
        result.classList.remove('hidden');
    } finally { btn.disabled = false; btn.innerText = 'Share'; }
});

/* ================================================================
   EXPORT MARKDOWN + PDF
   ================================================================ */
$('download-md-btn').addEventListener('click', () => {
    downloadBlob(new Blob([currentMarkdown], {type:'text/markdown'}), `${currentUsername}_review.md`);
});
$('generate-pdf-btn').addEventListener('click', async () => {
    const btn = $('generate-pdf-btn');
    btn.disabled = true; btn.innerText = 'Generating...';
    try {
        const res = await fetch(`/generate-pdf?username=${enc(currentUsername)}`, {method:'POST'});
        if (!res.ok) throw new Error(res.status);
        downloadBlob(await res.blob(), `${currentUsername}_resume.pdf`);
    } catch(e) { alert('PDF failed: '+e.message); }
    finally { btn.disabled = false; btn.innerText = 'Export PDF'; }
});
function downloadBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const a   = Object.assign(document.createElement('a'), {href:url, download:name});
    a.click(); URL.revokeObjectURL(url);
}

/* ================================================================
   CAREER TOOL BINDINGS
   ================================================================ */
function bindTool(btnId, resultId, urlFn) {
    $(btnId).addEventListener('click', async () => {
        const btn     = $(btnId);
        const out     = $(resultId);
        const colBtn  = document.querySelector(`[data-target="${resultId}"]`);
        const orig    = btn.innerText;
        btn.disabled  = true; btn.innerText = 'Generating...';
        out.classList.add('hidden');
        if (colBtn) { colBtn.classList.add('hidden'); colBtn.classList.remove('expanded'); }

        try {
            const data    = await apiPost(urlFn());
            const content = Object.values(data).find(v => typeof v === 'string') || '';
            out.innerHTML = marked.parse(content);
            out.classList.remove('hidden');
            if (colBtn) { colBtn.classList.remove('hidden'); colBtn.classList.add('expanded'); colBtn.title = 'Collapse'; }
        } catch(e) {
            out.innerHTML = `<p style="color:var(--error-text)">Error: ${escHtml(e.message)}</p>`;
            out.classList.remove('hidden');
        } finally { btn.disabled = false; btn.innerText = orig; }
    });
}
bindTool('tool-cl-btn','tool-cl-result',()=>`/cover-letter?username=${enc(currentUsername)}`);
bindTool('tool-rm-btn','tool-rm-result',()=>`/roadmap?username=${enc(currentUsername)}`);
bindTool('tool-pi-btn','tool-pi-result',()=>`/project-ideas?username=${enc(currentUsername)}`);
bindTool('tool-iq-btn','tool-iq-result',()=>`/interview-prep?username=${enc(currentUsername)}`);
bindTool('tool-dd-btn','tool-dd-result',()=>`/repo-deep-dive?username=${enc(currentUsername)}&repo_name=${enc($('tool-dd-select').value)}`);

/* ================================================================
   FLOATING CHAT DRAWER
   ================================================================ */
function openChat() {
    chatOpen = true;
    $('chat-drawer').classList.add('open');
    $('chat-overlay').classList.remove('hidden');
    $('chat-fab').classList.add('hidden');
    setTimeout(() => $('chat-input').focus(), 320);
}
function closeChat() {
    chatOpen = false;
    $('chat-drawer').classList.remove('open');
    $('chat-overlay').classList.add('hidden');
    $('chat-fab').classList.remove('hidden');
}
$('chat-fab').addEventListener('click', openChat);
$('open-chat-btn').addEventListener('click', openChat);
$('close-chat-btn').addEventListener('click', closeChat);
$('chat-overlay').addEventListener('click', closeChat);

$('chat-input').addEventListener('keydown', e => { if (e.key === 'Enter') $('chat-send-btn').click(); });

$('chat-send-btn').addEventListener('click', async () => {
    const input = $('chat-input');
    const text  = input.value.trim();
    if (!text || !currentUsername) return;
    input.value = '';
    appendBubble('user', text);
    chatMessages.push({role:'user', content:text});
    const thinking = appendBubble('assistant','Thinking...', true);
    try {
        const res = await fetch('/chat', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({username: currentUsername, messages: chatMessages})
        });
        if (!res.ok) throw new Error(res.status);
        const data  = await res.json();
        const reply = data.response || '';
        chatMessages.push({role:'assistant', content:reply});
        thinking.classList.remove('thinking');
        thinking.innerHTML = marked.parse(reply);
        thinking.style.fontStyle = '';
    } catch(e) { thinking.innerText = 'Error: '+e.message; }
    scrollChat();
});

function appendBubble(role, text, isThinking=false) {
    const c = $('chat-messages');
    const b = document.createElement('div');
    b.className = `chat-bubble chat-${role}${isThinking ? ' thinking' : ''}`;
    if (role==='user') b.innerText = text;
    else b.innerHTML = isThinking ? text : marked.parse(text);
    c.appendChild(b);
    scrollChat();
    return b;
}
function scrollChat() { const c=$('chat-messages'); c.scrollTop = c.scrollHeight; }

/* ================================================================
   INIT
   ================================================================ */
$('dashboard').classList.add('hidden');
$('site-footer').classList.add('hidden');
$('chat-fab').classList.add('hidden');
