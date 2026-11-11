/** Home overview. Provider failures are kept separate from empty repositories. */
(function () {
    const root = document.getElementById('workspace-overview');
    if (!root) return;
    const state = {
        filter: 'all', requestId: 0, controller: null,
        providers: Object.fromEntries(['github', 'gitee'].map(platform => [platform, {
            configured: root.dataset[platform] === 'true', status: 'unconfigured', repos: [], error: ''
        }]))
    };
    const text = (zh, en) => typeof currentLang !== 'undefined' && currentLang === 'en' ? en : zh;
    const allRepos = () => Object.entries(state.providers).flatMap(([platform, provider]) =>
        provider.status === 'ready' ? provider.repos.map(repo => ({ ...repo, platform })) : []
    );
    const currentProviders = () => Object.entries(state.providers).filter(([platform]) => state.filter === 'all' || platform === state.filter);
    const names = { github: 'GitHub', gitee: 'Gitee' };

    function render() {
        const providers = Object.values(state.providers);
        const repos = allRepos();
        const ready = providers.some(provider => provider.status === 'ready');
        const loading = providers.some(provider => provider.status === 'loading');
        const failed = Object.entries(state.providers).filter(([, provider]) => provider.status === 'error');
        document.getElementById('workspace-total').textContent = ready ? repos.length : '—';
        document.getElementById('workspace-public').textContent = ready ? repos.filter(repo => !repo.private).length : '—';
        document.getElementById('workspace-private').textContent = ready ? repos.filter(repo => repo.private).length : '—';
        document.getElementById('workspace-forks').textContent = ready ? repos.filter(repo => repo.fork).length : '—';
        const summary = document.getElementById('workspace-summary');
        summary.removeAttribute('data-i18n');
        summary.textContent = loading ? text('正在同步仓库…', 'Loading repositories…')
            : failed.length && ready ? text('当前统计包含已成功加载的平台。', 'Totals include the platforms loaded successfully.')
                : failed.length ? text('账户连接失败，请检查 Token。', 'Account connection failed. Check your tokens.')
                : ready ? text('把时间留给正在做的项目。', 'More time for the projects that matter.')
                    : text('连接账户后，在这里查看项目。', 'Connect an account to see your projects.');
        const notice = document.getElementById('workspace-load-notice');
        notice.hidden = failed.length === 0;
        notice.textContent = failed.map(([platform, provider]) => `${names[platform]}: ${provider.error}`).join(' · ');
        document.getElementById('workspace-refresh').disabled = loading;
        document.getElementById('workspace-load-status').textContent = loading ? text('正在加载', 'Loading')
            : failed.length ? text('部分平台加载失败，可刷新重试', 'Some platforms failed. Refresh to retry.')
                : ready ? text('已同步仓库信息', 'Repositories are up to date') : '';
        renderRepos();
    }

    function empty(title, description, configure = false) {
        return `<div class="workspace-list-empty">${uiIcon('repo')}<strong>${escapeHtml(title)}</strong><p>${escapeHtml(description)}</p>${configure ? `<a href="/settings#account-settings">${escapeHtml(text('配置账户', 'Configure account'))} →</a>` : ''}</div>`;
    }

    function renderRepos() {
        const list = document.getElementById('workspace-recent-list');
        const providers = currentProviders().map(([, provider]) => provider);
        const loading = providers.some(provider => provider.status === 'loading');
        list.setAttribute('aria-busy', String(loading));
        if (loading && !providers.some(provider => provider.status === 'ready')) {
            list.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
            return;
        }
        const repos = allRepos().filter(repo => state.filter === 'all' || repo.platform === state.filter)
            .sort((a, b) => (Date.parse(b.updated_at) || 0) - (Date.parse(a.updated_at) || 0)).slice(0, 4);
        if (!repos.length) {
            if (!providers.some(provider => provider.configured)) {
                list.innerHTML = empty(text('连接你的代码仓库', 'Connect your repositories'), text('配置 Token 后，最近更新的项目会显示在这里。', 'Your recently updated projects will appear here.'), true);
            } else if (providers.some(provider => provider.status === 'error')) {
                list.innerHTML = empty(text('仓库信息暂时无法加载', 'Repositories could not be loaded'), text('检查账户设置，或稍后刷新重试。', 'Check account settings or refresh to retry.'), true);
            } else {
                list.innerHTML = empty(text('还没有仓库', 'No repositories yet'), text('这个平台上的项目将显示在这里。', 'Projects from this platform will appear here.'));
            }
            return;
        }
        list.innerHTML = repos.map(repo => `
            <a class="workspace-repo-row" data-provider="${repo.platform}" href="${escapeHtml(safeUrl(repo.html_url))}" target="_blank" rel="noopener noreferrer">
                <span class="workspace-repo-icon">${uiIcon('repo')}</span>
                <div class="workspace-repo-copy"><strong>${escapeHtml(repo.name)}</strong><p>${escapeHtml(repo.description || `${names[repo.platform]} · ${repo.full_name}`)}</p></div>
                <span class="workspace-repo-language"><i></i>${escapeHtml(repo.language || '—')}</span>
                <span class="workspace-repo-stars" title="Stars">${uiIcon('star')}${escapeHtml(repo.stars ?? 0)}</span>
                <span class="workspace-repo-time">${escapeHtml(formatDate(repo.updated_at))}</span>
            </a>`).join('');
    }

    async function load() {
        state.controller?.abort();
        const controller = new AbortController();
        state.controller = controller;
        const requestId = ++state.requestId;
        const platforms = Object.keys(state.providers).filter(platform => state.providers[platform].configured);
        for (const platform of platforms) {
            state.providers[platform] = { configured: true, status: 'loading', repos: [], error: '' };
        }
        render();
        await Promise.all(platforms.map(async platform => {
            try {
                const data = await requestJSON(`/api/repos/${platform}?sort=updated`, { signal: controller.signal });
                if (requestId !== state.requestId) return;
                if (!Array.isArray(data.repos)) throw new Error(text('仓库数据格式无效', 'Invalid repository data'));
                state.providers[platform] = { configured: true, status: 'ready', repos: data.repos, error: '' };
            } catch (error) {
                if (requestId !== state.requestId || error.name === 'AbortError') return;
                state.providers[platform] = { configured: true, status: 'error', repos: [], error: error.message };
            }
            if (requestId === state.requestId) render();
        }));
    }
    root.querySelectorAll('[data-workspace-platform]').forEach(button => button.addEventListener('click', () => {
        state.filter = button.dataset.workspacePlatform;
        root.querySelectorAll('[data-workspace-platform]').forEach(item => {
            item.classList.toggle('active', item === button);
            item.setAttribute('aria-pressed', String(item === button));
        });
        renderRepos();
    }));
    document.getElementById('workspace-refresh').addEventListener('click', load);
    document.addEventListener('languagechange', render);
    load();
})();
