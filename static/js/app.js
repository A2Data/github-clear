/** GitHub Clear - shared UI and repository management. */

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[char]));
}

function safeUrl(value) {
    try {
        const url = new URL(value);
        return ['https:', 'http:'].includes(url.protocol) ? url.href : '#';
    } catch {
        return '#';
    }
}

async function requestJSON(url, options) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        const detail = Array.isArray(data.detail)
            ? data.detail.map(item => item.msg).join('；')
            : data.detail;
        throw new Error(detail || `请求失败（HTTP ${response.status}）`);
    }
    return data;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    const icon = document.createElement('span');
    icon.className = 'icon';
    icon.textContent = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    const text = document.createElement('span');
    text.textContent = Array.isArray(message) ? message.map(item => item.msg || String(item)).join('；') : message;
    toast.append(icon, text);
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('is-leaving');
        setTimeout(() => toast.remove(), 180);
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function uiIcon(name) {
    const symbols = ['repo', 'star', 'fork', 'calendar', 'lock', 'archive', 'copy'];
    const symbol = symbols.includes(name) ? name : 'repo';
    return `<svg class="ui-icon icon-${symbol}" data-icon="${symbol}" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><use href="/static/icons.svg?v=7#${symbol}"></use></svg>`;
}

function initNavigation() {
    const trigger = document.getElementById('mobile-menu');
    const sidebar = document.getElementById('sidebar');
    const scrim = document.getElementById('nav-scrim');
    if (!trigger || !sidebar || !scrim) return;
    const mobile = window.matchMedia('(max-width: 720px)');
    function setOpen(open, returnFocus = false) {
        const expanded = mobile.matches && open;
        document.body.classList.toggle('navigation-open', expanded);
        trigger.setAttribute('aria-expanded', String(expanded));
        sidebar.inert = mobile.matches && !expanded;
        if (expanded) sidebar.querySelector('.nav-item.active')?.focus();
        else if (returnFocus) trigger.focus();
    }
    trigger.addEventListener('click', () => setOpen(trigger.getAttribute('aria-expanded') !== 'true'));
    scrim.addEventListener('click', () => setOpen(false, true));
    sidebar.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setOpen(false)));
    document.addEventListener('keydown', event => {
        if (!document.body.classList.contains('navigation-open')) return;
        if (event.key === 'Escape') setOpen(false, true);
        if (event.key === 'Tab') {
            const controls = sidebar.querySelectorAll('a[href], button:not(:disabled)');
            const first = controls[0], last = controls[controls.length - 1];
            if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        }
    });
    mobile.addEventListener('change', () => setOpen(false));
    setOpen(false);
}

function initTabs() {
    document.querySelectorAll('.tabs').forEach(tabContainer => {
        const buttons = tabContainer.querySelectorAll('.tab-btn');
        const contents = Array.from(buttons, button => document.getElementById(button.dataset.tab)).filter(Boolean);
        const updateIndicator = () => {
            const active = tabContainer.querySelector('.tab-btn.active');
            if (!active) return;
            tabContainer.style.setProperty('--tab-offset', `${active.offsetLeft}px`);
            tabContainer.style.setProperty('--tab-width', `${active.offsetWidth}px`);
        };
        tabContainer.classList.add('motion-tabs');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById(btn.dataset.tab)?.classList.add('active');
                updateIndicator();
            });
        });
        updateIndicator();
        if (typeof ResizeObserver !== 'undefined') {
            const observer = new ResizeObserver(updateIndicator);
            observer.observe(tabContainer);
            buttons.forEach(button => observer.observe(button));
        }
    });
}

function initMotion() {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    document.addEventListener('pointerdown', event => {
        if (reducedMotion.matches || event.button !== 0 || event.isPrimary === false) return;
        const button = event.target.closest?.('.btn, .btn-action, .btn-demo, .btn-save');
        if (!button || button.disabled) return;
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 2;
        const ripple = document.createElement('span');
        ripple.className = 'click-ripple';
        ripple.setAttribute('aria-hidden', 'true');
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left}px`;
        ripple.style.top = `${event.clientY - rect.top}px`;
        button.appendChild(ripple);
        ripple.addEventListener('animationend', () => ripple.remove(), { once: true });
    });
}

// Keep account selections, searches and pending requests isolated by platform.
const repoStates = Object.fromEntries(['github', 'gitee', 'collab'].map(platform => [platform, {
    repos: [], selected: new Set(), query: '', loaded: false,
    loading: false, busy: false, controller: null, requestId: 0
}]));

function visibleRepos(platform) {
    const state = repoStates[platform];
    const query = state.query.trim().toLowerCase();
    return state.repos.filter(repo =>
        [repo.full_name, repo.name, repo.description].some(value =>
            String(value || '').toLowerCase().includes(query))
    );
}

function reconcileSelection(platform) {
    const state = repoStates[platform];
    const visible = new Set(visibleRepos(platform).map(repo => repo.full_name));
    state.selected.forEach(name => {
        if (!visible.has(name)) state.selected.delete(name);
    });
}

function reposLoaded(platform) {
    return repoStates[platform].loaded || repoStates[platform].loading;
}

async function loadRepos(platform, afterMutation = false) {
    const container = document.getElementById(`${platform}-repos`);
    const state = repoStates[platform];
    if (!container || (state.busy && !afterMutation)) return;
    state.controller?.abort();
    const controller = new AbortController();
    const requestId = ++state.requestId;
    state.controller = controller;
    state.loading = true;
    container.setAttribute('aria-busy', 'true');
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    updateSelectionInfo(platform);
    const params = new URLSearchParams({
        visibility: document.getElementById(`${platform}-visibility`)?.value || 'all',
        sort: document.getElementById(`${platform}-sort`)?.value || 'updated',
        include_forks: document.getElementById(`${platform}-forks`)?.checked ?? true
    });
    const url = platform === 'collab' ? '/api/repos/github/collaborator' : `/api/repos/${platform}?${params}`;
    try {
        const data = await requestJSON(url, { signal: controller.signal });
        if (requestId !== state.requestId) return;
        if (!Array.isArray(data.repos)) throw new Error('仓库列表格式无效，请刷新重试');
        state.repos = data.repos;
        state.loaded = true;
        reconcileSelection(platform);
        renderRepos(platform, visibleRepos(platform), true);
    } catch (error) {
        if (requestId !== state.requestId || error.name === 'AbortError') return;
        state.repos = [];
        state.selected.clear();
        state.loaded = false;
        container.innerHTML = `<div class="alert alert-danger" role="alert">${escapeHtml(error.message)}</div>`;
    } finally {
        if (requestId === state.requestId) {
            state.loading = false;
            container.setAttribute('aria-busy', 'false');
            updateSelectionInfo(platform);
        }
    }
}

function renderRepos(platform, repos, animate = false) {
    const container = document.getElementById(`${platform}-repos`);
    if (!container) return;
    const state = repoStates[platform];
    if (repos.length === 0) {
        container.innerHTML = `<div class="empty-state"><div class="icon">${uiIcon('repo')}</div><h3>没有找到仓库</h3><p>尝试调整筛选条件</p></div>`;
        return;
    }
    container.innerHTML = `<div class="repo-list">${repos.map((repo, index) => {
        const selected = state.selected.has(repo.full_name);
        const identifier = escapeHtml(repo.full_name);
        const tags = [];
        if (repo.private) tags.push(`<span class="tag">${uiIcon('lock')}私有</span>`);
        if (repo.fork) tags.push('<span class="tag">Fork</span>');
        if (repo.archived) tags.push('<span class="tag">已归档</span>');
        return `
            <div class="repo-item ${selected ? 'selected' : ''} ${animate && index < 10 ? 'repo-enter' : ''}" style="--row-order:${Math.min(index, 8)}" data-repo="${identifier}">
                <div class="repo-checkbox">
                    <input type="checkbox" ${selected ? 'checked' : ''} ${state.busy ? 'disabled' : ''}
                        aria-label="选择 ${identifier}" data-repo="${identifier}"
                        onchange="toggleRepo('${platform}', this.dataset.repo, this.checked)">
                </div>
                <div class="repo-info">
                    <div class="repo-name">
                        <a href="${escapeHtml(safeUrl(repo.html_url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(platform === 'collab' ? repo.full_name : repo.name)}</a>
                        ${tags.join(' ')}
                    </div>
                    <div class="repo-desc">${escapeHtml(repo.description || '暂无描述')}</div>
                </div>
                ${platform === 'collab' ? '' : `<div class="repo-meta">
                    <span><i class="language-dot" aria-hidden="true"></i> ${escapeHtml(repo.language || '-')}</span>
                    <span title="Stars">${uiIcon('star')} ${escapeHtml(repo.stars)}</span>
                    <span title="Forks">${uiIcon('fork')} ${escapeHtml(repo.forks)}</span>
                    <span>${uiIcon('calendar')} ${escapeHtml(formatDate(repo.updated_at))}</span>
                </div>`}
            </div>`;
    }).join('')}</div>`;
}

function toggleRepo(platform, repoId, checked) {
    const state = repoStates[platform];
    if (state.loading || state.busy) return;
    if (checked && visibleRepos(platform).some(repo => repo.full_name === repoId)) {
        state.selected.add(repoId);
    } else {
        state.selected.delete(repoId);
    }
    document.getElementById(`${platform}-repos`)?.querySelectorAll('.repo-item').forEach(item => {
        if (item.dataset.repo === repoId) item.classList.toggle('selected', checked);
    });
    updateSelectionInfo(platform);
}

function selectAllRepos(platform) {
    const state = repoStates[platform];
    if (state.loading || state.busy) return;
    visibleRepos(platform).forEach(repo => state.selected.add(repo.full_name));
    renderRepos(platform, visibleRepos(platform));
    updateSelectionInfo(platform);
}

function deselectAllRepos(platform) {
    const state = repoStates[platform];
    if (state.loading || state.busy) return;
    state.selected.clear();
    renderRepos(platform, visibleRepos(platform));
    updateSelectionInfo(platform);
}

function updateSelectionInfo(platform) {
    const state = repoStates[platform];
    const info = document.getElementById(`${platform}-selection-info`);
    const actions = document.getElementById(`${platform}-batch-actions`);
    if (info) info.textContent = state.loading ? '正在加载仓库…' : `${visibleRepos(platform).length} 个仓库 · 已选择 ${state.selected.size} 个`;
    if (actions) {
        actions.style.display = state.selected.size > 0 ? 'flex' : 'none';
        actions.querySelectorAll('button').forEach(button => {
            button.disabled = state.loading || state.busy;
        });
    }
    document.getElementById(`${platform}-tab`)?.querySelectorAll('.toolbar input, .toolbar select, .toolbar button').forEach(control => {
        control.disabled = state.busy || (state.loading && control.tagName === 'BUTTON');
        if (control.tagName === 'BUTTON') {
            control.classList.toggle('is-busy', state.loading && (control.getAttribute('onclick') || '').includes('loadRepos'));
        }
    });
    document.getElementById(`${platform}-repos`)?.querySelectorAll('input[type="checkbox"]').forEach(input => {
        input.disabled = state.loading || state.busy;
    });
}

function searchRepos(platform, query) {
    const state = repoStates[platform];
    if (state.busy) return;
    state.query = query;
    reconcileSelection(platform);
    if (!state.loading) renderRepos(platform, visibleRepos(platform));
    updateSelectionInfo(platform);
}

function loadCollaboratorRepos() {
    return loadRepos('collab');
}

let currentModalCallback = null;
let modalTrigger = null;

function showModal(title, message, repoList, onConfirm, type = 'danger', confirmLabel = '确认删除') {
    modalTrigger = document.activeElement;
    document.getElementById('confirm-modal')?.remove();
    document.body.insertAdjacentHTML('beforeend', `
        <div class="modal-overlay active" id="confirm-modal">
            <div class="modal" role="dialog" aria-modal="true" aria-labelledby="confirm-modal-title">
                <div class="modal-header">
                    <h3 class="modal-title" id="confirm-modal-title">${escapeHtml(title)}</h3>
                    <button class="modal-close" onclick="closeModal()" aria-label="关闭">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-${type}" style="margin-bottom: 16px;"><span>${message}</span></div>
                    <div style="max-height: 200px; overflow-y: auto; background: var(--bg-primary); border-radius: 8px; padding: 12px;">
                        ${repoList.map(name => `<div style="padding: 4px 0;">• ${escapeHtml(name)}</div>`).join('')}
                    </div>
                </div>
                <div class="modal-footer" style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px;">
                    <button class="btn btn-secondary" onclick="closeModal()">取消</button>
                    <button class="btn btn-${type === 'danger' ? 'danger' : 'primary'}" onclick="confirmModal()">${escapeHtml(confirmLabel)}</button>
                </div>
            </div>
        </div>`);
    currentModalCallback = onConfirm;
    document.addEventListener('keydown', handleModalEsc);
    document.querySelector('#confirm-modal .btn-secondary')?.focus();
}

function closeModal() {
    document.getElementById('confirm-modal')?.remove();
    document.removeEventListener('keydown', handleModalEsc);
    currentModalCallback = null;
    modalTrigger?.focus();
}

async function confirmModal() {
    const callback = currentModalCallback;
    closeModal();
    if (callback) await callback();
}

function handleModalEsc(event) {
    if (event.key === 'Escape') closeModal();
    if (event.key === 'Tab') {
        const buttons = document.querySelectorAll('#confirm-modal button');
        if (!buttons.length) return;
        const first = buttons[0], last = buttons[buttons.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }
}

function confirmBatch(platform, action) {
    const state = repoStates[platform];
    if (state.loading || state.busy) return;
    if (!state.selected.size) return showToast('请先选择仓库', 'error');
    if (state.selected.size > 1000) return showToast('单次最多操作 1000 个仓库，请缩小筛选范围', 'error');
    const labels = { delete: '删除', archive: '归档', leave: '退出协作' };
    const label = labels[action];
    const names = Array.from(state.selected);
    const hint = action === 'delete' ? '此操作不可恢复！' : action === 'archive' ? '归档后仓库将变为只读状态。' : '退出后将无法访问这些私有仓库。';
    showModal(`确认${label}`, `确定要${label}选中的 <strong>${names.length}</strong> 个仓库吗？<br>${hint}`,
        names, () => runRepoBatch(platform, action, names), action === 'delete' ? 'danger' : 'warning', `确认${label}`);
}

async function runRepoBatch(platform, action, names) {
    const state = repoStates[platform];
    if (state.busy) return;
    state.busy = true;
    updateSelectionInfo(platform);
    const label = { delete: '删除', archive: '归档', leave: '退出' }[action];
    try {
        showToast(`正在${label}…`, 'info');
        const provider = platform === 'collab' ? 'github' : platform;
        const result = await requestJSON(`/api/repos/${provider}/${action}`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repos: names })
        });
        if (!result.results || typeof result.results !== 'object') throw new Error('操作结果格式无效，请刷新确认仓库状态');
        names.forEach(name => {
            if (result.results[name]) state.selected.delete(name);
        });
        const complete = result.success === result.total;
        const details = complete ? '' : `；${(result.errors || ['失败项已保留选中，可重试']).join('；')}`;
        showToast(`${label}完成：${result.success}/${result.total} 成功${details}`, complete ? 'success' : 'error');
        await loadRepos(platform, true);
    } catch (error) {
        showToast(`${label}失败：${error.message}`, 'error');
    } finally {
        state.busy = false;
        updateSelectionInfo(platform);
    }
}

function batchDelete(platform) {
    confirmBatch(platform, 'delete');
}

function batchArchive(platform) {
    if (platform !== 'github') return showToast('Gitee 暂不支持归档', 'error');
    confirmBatch(platform, 'archive');
}

function batchLeave() {
    confirmBatch('collab', 'leave');
}

// ==========================================
// Token 配置
// ==========================================

async function saveToken(platform) {
    const input = document.getElementById(`${platform}-token`);
    const token = input?.value.trim();
    
    if (!token) {
        showToast('请输入 Token', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/settings/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform, token })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Token 已保存', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(result.detail || '保存失败', 'error');
        }
    } catch (error) {
        showToast(`保存失败: ${error.message}`, 'error');
    }
}

async function testToken(platform) {
    const input = document.getElementById(`${platform}-token`);
    const token = input?.value.trim();
    
    if (!token) {
        showToast('请输入 Token', 'error');
        return;
    }
    
    try {
        showToast('测试连接中...', 'info');
        
        const response = await fetch('/api/settings/test-token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform, token })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast(`连接成功！欢迎，${result.user.name}`, 'success');
        } else {
            showToast(result.detail || '连接失败', 'error');
        }
    } catch (error) {
        showToast(`连接失败: ${error.message}`, 'error');
    }
}

// ==========================================
// Profile 生成器
// ==========================================

// 预设 Emoji 列表
const INTRO_EMOJIS = [
    '👋', '👀', '🚀', '💖', '📫', '🌐', '💡', '🔭',
    '🌱', '👯', '🤔', '💬', '📝', '⚡', '🎯', '🔥'
];

// 添加介绍项
function addIntroItem(emoji = '👋', text = '') {
    const container = document.getElementById('intro-items-container');
    if (!container) return;

    const itemDiv = document.createElement('div');
    itemDiv.className = 'intro-item';

    // Emoji 选择器
    const emojiSelect = document.createElement('select');
    emojiSelect.className = 'intro-emoji';
    INTRO_EMOJIS.forEach(e => {
        const option = document.createElement('option');
        option.value = e;
        option.textContent = e;
        if (e === emoji) option.selected = true;
        emojiSelect.appendChild(option);
    });
    emojiSelect.onchange = () => generateProfile();

    // 文本输入
    const textInput = document.createElement('input');
    textInput.type = 'text';
    textInput.className = 'intro-text';
    textInput.placeholder = 'e.g., Currently learning Rust';
    textInput.value = text;
    textInput.oninput = () => generateProfile();

    // 删除按钮
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'btn-remove';
    deleteBtn.textContent = '×';
    deleteBtn.onclick = function() { removeIntroItem(this); };

    itemDiv.appendChild(emojiSelect);
    itemDiv.appendChild(textInput);
    itemDiv.appendChild(deleteBtn);
    container.appendChild(itemDiv);

    // 聚焦到新输入框
    textInput.focus();
    generateProfile();
}

// 删除介绍项
function removeIntroItem(btn) {
    const item = btn.closest('.intro-item');
    if (item) {
        item.remove();
        generateProfile();
    }
}

// 收集介绍项数据
function collectIntroItems() {
    const items = [];
    const container = document.getElementById('intro-items-container');
    if (!container) return items;

    container.querySelectorAll('.intro-item').forEach(item => {
        const emoji = item.querySelector('.intro-emoji')?.value || '👋';
        const text = item.querySelector('.intro-text')?.value?.trim() || '';
        if (text) {
            items.push({ emoji, text });
        }
    });

    return items;
}

// 保存服务 URL（从 Profile 页面）
async function saveStatsUrlFromProfile() {
    const statsUrl = document.getElementById('stats-url-input')?.value?.trim() || '';
    const streakUrl = document.getElementById('streak-url-input')?.value?.trim() || '';

    try {
        const response = await fetch('/api/settings/stats-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                stats_url: statsUrl,
                streak_url: streakUrl
            })
        });

        const result = await response.json();

        if (response.ok) {
            showToast('服务 URL 已保存，重新生成预览...', 'success');
            // 刷新页面以加载新的服务 URL
            setTimeout(() => location.reload(), 500);
        } else {
            showToast(result.detail || '保存失败', 'error');
        }
    } catch (error) {
        showToast(`保存失败: ${error.message}`, 'error');
    }
}

// 处理图片加载错误
function handleImageError(img) {
    img.classList.remove('img-loading');

    // 判断是哪种类型的图片
    const src = img.src || '';
    let serviceName = '外部服务';
    let suggestion = '';

    if (src.includes('github-readme-stats')) {
        serviceName = 'GitHub Stats';
        suggestion = '尝试使用镜像: github-readme-stats-git-masterrstaa-rickstaa.vercel.app';
    } else if (src.includes('streak-stats') || src.includes('github-readme-streak')) {
        serviceName = 'GitHub Streak';
        suggestion = '官方服务: streak-stats.demolab.com';
    } else if (src.includes('shields.io')) {
        serviceName = 'Shields.io 徽章';
        suggestion = '请检查网络连接后重试';
    } else if (src.includes('github-profile-trophy')) {
        serviceName = 'GitHub Trophy';
        suggestion = '请自部署 Trophy 服务';
    } else if (src.includes('readme-typing-svg') || src.includes('capsule-render')) {
        serviceName = '动态头图';
        suggestion = '请检查网络后重试';
    }

    // 创建简洁的错误提示
    const errorDiv = document.createElement('div');
    errorDiv.className = 'img-error-placeholder';
    errorDiv.innerHTML = `
        <div class="error-icon">${uiIcon('repo')}</div>
        <div class="error-text">${serviceName}</div>
        <div class="error-hint">${suggestion || '服务暂时不可用'}</div>
    `;

    // 替换图片
    if (img.parentNode) {
        img.parentNode.replaceChild(errorDiv, img);
    }
}

// 添加自定义社交链接
function addCustomSocial(label = '', url = '') {
    const container = document.getElementById('custom-social-container');
    if (!container) return;

    const itemDiv = document.createElement('div');
    itemDiv.className = 'custom-social-item';

    // 标签输入
    const labelInput = document.createElement('input');
    labelInput.type = 'text';
    labelInput.className = 'custom-social-label';
    labelInput.placeholder = '标签名';
    labelInput.value = label;
    labelInput.oninput = () => generateProfile();

    // URL 输入
    const urlInput = document.createElement('input');
    urlInput.type = 'text';
    urlInput.className = 'custom-social-url';
    urlInput.placeholder = 'https://example.com/profile';
    urlInput.value = url;
    urlInput.oninput = () => generateProfile();

    // 删除按钮
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'btn-remove';
    deleteBtn.textContent = '×';
    deleteBtn.onclick = function() {
        itemDiv.remove();
        generateProfile();
    };

    itemDiv.appendChild(labelInput);
    itemDiv.appendChild(urlInput);
    itemDiv.appendChild(deleteBtn);
    container.appendChild(itemDiv);

    labelInput.focus();
    generateProfile();
}

// 收集自定义社交链接
function collectCustomSocials() {
    const items = [];
    const container = document.getElementById('custom-social-container');
    if (!container) return items;

    container.querySelectorAll('.custom-social-item').forEach(item => {
        const label = item.querySelector('.custom-social-label')?.value?.trim() || '';
        const url = item.querySelector('.custom-social-url')?.value?.trim() || '';
        if (label && url) {
            items.push({ label, url });
        }
    });

    return items;
}

// 添加自定义技能
function addCustomSkill(name = '', color = '', logo = '') {
    const container = document.getElementById('custom-skill-container');
    if (!container) return;

    const itemDiv = document.createElement('div');
    itemDiv.className = 'custom-skill-item';

    // 技能名称
    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.className = 'custom-skill-name';
    nameInput.placeholder = '技能名称 (如 FastAPI)';
    nameInput.value = name;
    nameInput.oninput = () => generateProfile();

    // 颜色
    const colorInput = document.createElement('input');
    colorInput.type = 'text';
    colorInput.className = 'custom-skill-color';
    colorInput.placeholder = '颜色 (如 009688)';
    colorInput.value = color;
    colorInput.oninput = () => generateProfile();

    // Logo (可选)
    const logoInput = document.createElement('input');
    logoInput.type = 'text';
    logoInput.className = 'custom-skill-logo';
    logoInput.placeholder = 'Logo名 (可选, 如 fastapi)';
    logoInput.value = logo;
    logoInput.oninput = () => generateProfile();

    // 删除按钮
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'btn-remove';
    deleteBtn.textContent = '×';
    deleteBtn.onclick = function() {
        itemDiv.remove();
        generateProfile();
    };

    itemDiv.appendChild(nameInput);
    itemDiv.appendChild(colorInput);
    itemDiv.appendChild(logoInput);
    itemDiv.appendChild(deleteBtn);
    container.appendChild(itemDiv);

    nameInput.focus();
    generateProfile();
}

// 添加项目组件
function addComponent(name = '', url = '', status = 'release', version = '', description = '') {
    const container = document.getElementById('components-container');
    if (!container) return;

    const itemDiv = document.createElement('div');
    itemDiv.className = 'component-item';

    // 项目名
    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.className = 'component-name';
    nameInput.placeholder = t('profile.component_name') || 'Project Name';
    nameInput.value = name;
    nameInput.oninput = () => generateProfile();

    // 项目链接
    const urlInput = document.createElement('input');
    urlInput.type = 'text';
    urlInput.className = 'component-url';
    urlInput.placeholder = 'https://github.com/...';
    urlInput.value = url;
    urlInput.oninput = () => generateProfile();

    // 状态选择
    const statusSelect = document.createElement('select');
    statusSelect.className = 'component-status';
    const statuses = [
        { value: 'release', label: 'Release' },
        { value: 'private', label: 'Private' },
        { value: 'beta', label: 'Beta' },
        { value: 'alpha', label: 'Alpha' },
        { value: 'dev', label: 'Dev' }
    ];
    statuses.forEach(s => {
        const option = document.createElement('option');
        option.value = s.value;
        option.textContent = s.label;
        if (s.value === status) option.selected = true;
        statusSelect.appendChild(option);
    });
    statusSelect.onchange = () => generateProfile();

    // 版本号
    const versionInput = document.createElement('input');
    versionInput.type = 'text';
    versionInput.className = 'component-version';
    versionInput.placeholder = 'v1.0.0';
    versionInput.value = version;
    versionInput.oninput = () => generateProfile();

    // 描述
    const descInput = document.createElement('input');
    descInput.type = 'text';
    descInput.className = 'component-desc';
    descInput.placeholder = t('profile.component_desc') || 'Description';
    descInput.value = description;
    descInput.oninput = () => generateProfile();

    // 删除按钮
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'btn-remove';
    deleteBtn.textContent = '×';
    deleteBtn.onclick = function() {
        itemDiv.remove();
        generateProfile();
    };

    itemDiv.appendChild(nameInput);
    itemDiv.appendChild(urlInput);
    itemDiv.appendChild(statusSelect);
    itemDiv.appendChild(versionInput);
    itemDiv.appendChild(descInput);
    itemDiv.appendChild(deleteBtn);
    container.appendChild(itemDiv);

    nameInput.focus();
    generateProfile();
}

// 收集自定义技能
function collectCustomSkills() {
    const items = [];
    const container = document.getElementById('custom-skill-container');
    if (!container) return items;

    container.querySelectorAll('.custom-skill-item').forEach(item => {
        const name = item.querySelector('.custom-skill-name')?.value?.trim() || '';
        const color = item.querySelector('.custom-skill-color')?.value?.trim() || '000000';
        const logo = item.querySelector('.custom-skill-logo')?.value?.trim() || '';
        if (name) {
            items.push({ name, color, logo });
        }
    });

    return items;
}

// 收集项目组件
function collectComponents() {
    const items = [];
    const container = document.getElementById('components-container');
    if (!container) return items;

    container.querySelectorAll('.component-item').forEach(item => {
        const name = item.querySelector('.component-name')?.value?.trim() || '';
        const url = item.querySelector('.component-url')?.value?.trim() || '';
        const status = item.querySelector('.component-status')?.value || 'release';
        const version = item.querySelector('.component-version')?.value?.trim() || '';
        const description = item.querySelector('.component-desc')?.value?.trim() || '';
        if (name) {
            items.push({ name, url, status, version, description });
        }
    });

    return items;
}

let profileDebounce = null;
let profileRequestId = 0;
let profileController = null;

function setPreviewStatus(message, state = '') {
    const status = document.getElementById('preview-status');
    if (status) {
        status.textContent = message;
        status.dataset.state = state;
    }
}

function generateProfile() {
    if (!document.getElementById('profile-form')) return;
    clearTimeout(profileDebounce);
    profileController?.abort();
    const requestId = ++profileRequestId;
    window.profileContent = '';
    profileDebounce = setTimeout(() => renderProfile(requestId), 200);
}

async function renderProfile(requestId) {
    const form = document.getElementById('profile-form');
    if (!form) return;

    const formData = new FormData(form);
    const username = formData.get('username')?.trim();

    // 如果用户名为空，显示提示而不是发送请求
    const preview = document.getElementById('profile-preview');
    const panel = document.querySelector('.preview-panel');
    if (!username) {
        panel?.classList.remove('is-updating');
        setPreviewStatus('等待输入');
        const source = document.getElementById('profile-source');
        if (source) source.textContent = '';
        if (preview) {
            preview.innerHTML = `
                <div class="empty-state">
                    <div class="icon">${uiIcon('repo')}</div>
                    <h3 style="margin-bottom: 8px; color: var(--text-primary);">请先输入 GitHub 用户名</h3>
                    <p style="color: var(--text-secondary);">输入你的 GitHub 用户名后，预览会自动生成</p>
                </div>
            `;
        }
        return;
    }

    const config = {
        username: username,
        name: formData.get('name') || username,
        bio: formData.get('bio'),
        greeting: formData.get('greeting'),
        skills: formData.getAll('skills'),
        custom_skills: collectCustomSkills(),
        socials: {
            github: formData.get('github_url'),
            twitter: formData.get('twitter_url'),
            linkedin: formData.get('linkedin_url'),
            email: formData.get('email'),
            blog: formData.get('blog_url'),
            youtube: formData.get('youtube_url'),
        },
        custom_socials: collectCustomSocials(),
        show_stats: formData.get('show_stats') === 'on',
        show_streak: formData.get('show_streak') === 'on',
        show_languages: formData.get('show_languages') === 'on',
        show_trophy: formData.get('show_trophy') === 'on',
        show_activity: formData.get('show_activity') === 'on',
        show_quote: formData.get('show_quote') === 'on',
        show_joke: formData.get('show_joke') === 'on',
        show_snake: formData.get('show_snake') === 'on',
        theme: formData.get('theme'),
        header_style: formData.get('header_style'),
        intro_items: collectIntroItems(),
        layout: formData.get('layout') || 'single',
        streak_locale: formData.get('streak_locale') || 'en',
        badge_layout: formData.get('badge_layout') || 'inline',
        components: collectComponents(),
        components_title: formData.get('components_title') || 'Components',
    };

    // 清理空的社交链接
    Object.keys(config.socials).forEach(key => {
        if (!config.socials[key]) delete config.socials[key];
    });
    
    panel?.classList.add('is-updating');
    preview?.classList.remove('is-updated');
    setPreviewStatus('更新中…', 'loading');
    profileController = new AbortController();

    try {
        const result = await requestJSON('/api/profile/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
            signal: profileController.signal
        });
        if (requestId !== profileRequestId) return;

        // 更新预览
        const preview = document.getElementById('profile-preview');
        const source = document.getElementById('profile-source');

        if (preview) {
            preview.innerHTML = marked.parse(result.content);
            preview.classList.add('is-updated');

            // 处理图片加载
            const images = preview.querySelectorAll('img');
            images.forEach(img => {
                // 检查图片是否已经加载完成（从缓存）
                if (img.complete && img.naturalWidth > 0) {
                    // 已加载成功
                    return;
                }

                img.classList.add('img-loading');

                // 设置超时检测 (15秒)
                const timeout = setTimeout(() => {
                    if (img.classList.contains('img-loading')) {
                        handleImageError(img);
                    }
                }, 15000);

                img.onload = () => {
                    clearTimeout(timeout);
                    img.classList.remove('img-loading');
                };

                img.onerror = () => {
                    clearTimeout(timeout);
                    handleImageError(img);
                };

                // 如果图片已完成但失败（naturalWidth 为 0）
                if (img.complete && img.naturalWidth === 0) {
                    clearTimeout(timeout);
                    handleImageError(img);
                }
            });
        }
        if (source) {
            source.textContent = result.content;
        }
        
        // 保存到全局变量供下载/部署使用
        window.profileContent = result.content;
        
        setPreviewStatus('已更新', 'ready');
    } catch (error) {
        if (requestId !== profileRequestId || error.name === 'AbortError') return;
        setPreviewStatus('更新失败', 'error');
        showToast(`生成失败: ${error.message}`, 'error');
    } finally {
        if (requestId === profileRequestId) panel?.classList.remove('is-updating');
    }
}

function downloadProfile() {
    if (!window.profileContent) {
        showToast('请先生成 Profile', 'error');
        return;
    }
    
    const blob = new Blob([window.profileContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'README.md';
    a.click();
    URL.revokeObjectURL(url);
    
    showToast('下载成功', 'success');
}

async function deployProfile() {
    if (!window.profileContent) {
        showToast('请先生成 Profile', 'error');
        return;
    }
    
    try {
        showToast('部署中...', 'info');
        
        const response = await fetch('/api/profile/deploy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: window.profileContent })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('部署成功！', 'success');
            window.open(result.profile_url, '_blank');
        } else {
            showToast(result.detail || '部署失败', 'error');
        }
    } catch (error) {
        showToast(`部署失败: ${error.message}`, 'error');
    }
}

// ==========================================
// 工具函数
// ==========================================

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('已复制到剪贴板', 'success');
    }).catch(() => {
        showToast('复制失败', 'error');
    });
}

// ==========================================
// 初始化
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initNavigation();
    initMotion();
    
    // 自动加载仓库列表（如果在仓库页面）
    if (document.getElementById('github-repos')) {
        loadRepos('github');
    }
    
    // 自动生成 Profile（如果在 Profile 页面）
    if (document.getElementById('profile-form')) {
        generateProfile();
    }
});

// 重置 Profile 选项并恢复 GitHub 默认状态
async function resetProfileConfig() {
    if (!confirm('确定要恢复 GitHub 默认 Profile 吗？\n\n此操作将：\n1. 删除你的自定义 Profile README\n2. 恢复表单为默认配置')) {
        return;
    }

    try {
        showToast('正在恢复默认...', 'info');

        // 调用恢复 API
        const response = await fetch('/api/profile/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const result = await response.json();

        if (response.ok) {
            showToast('已恢复为 GitHub 默认样式！', 'success');

            // 重置表单配置
            const form = document.querySelector('form');
            if (form) {
                // 重置主题 (Tokyo Night)
                const themeSelect = form.querySelector('select[name="theme"]');
                if (themeSelect) {
                    themeSelect.value = 'tokyonight';
                }

                // 重置 Header Style (Capsule Render)
                const headerRadios = form.querySelectorAll('input[name="header_style"]');
                headerRadios.forEach(radio => {
                    if (radio.value === 'capsule') radio.checked = true;
                });

                // 重置 Checkbox
                const defaults = {
                    'show_stats': true,
                    'show_streak': true,
                    'show_languages': true,
                    'show_trophy': false,
                    'show_activity': true,
                    'show_calendar': true,
                    'show_quote': false,
                    'show_joke': false,
                    'show_snake': false
                };

                Object.entries(defaults).forEach(([name, checked]) => {
                    const checkbox = form.querySelector(`input[name="${name}"]`);
                    if (checkbox) {
                        checkbox.checked = checked;
                    }
                });

                // 自动触发生成预览
                generateProfile();
            }

            // 打开 GitHub Profile 页面
            setTimeout(() => {
                window.open(result.profile_url, '_blank');
            }, 1000);
        } else {
            showToast(result.detail || '恢复失败', 'error');
        }
    } catch (error) {
        showToast(`恢复失败: ${error.message}`, 'error');
    }
}



function filterGitCommands() {
    const query = (document.getElementById('git-command-search')?.value || '').trim().toLowerCase();
    const category = document.getElementById('git-command-category')?.value || 'all';
    let count = 0;
    document.querySelectorAll('.command-group').forEach(group => {
        let matches = 0;
        group.querySelectorAll('.command-item').forEach(item => {
            const visible = (category === 'all' || category === group.dataset.category)
                && item.dataset.search.toLowerCase().includes(query);
            item.hidden = !visible;
            if (visible) matches++;
        });
        group.hidden = matches === 0;
        count += matches;
    });
    document.getElementById('command-count').textContent = `${count} 条命令`;
    document.getElementById('command-empty').hidden = count > 0;
}
