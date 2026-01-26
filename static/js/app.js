/**
 * GitHub Clear - Main JavaScript
 */

// ==========================================
// Toast 通知系统
// ==========================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// ==========================================
// 标签页切换
// ==========================================

function initTabs() {
    document.querySelectorAll('.tabs').forEach(tabContainer => {
        const buttons = tabContainer.querySelectorAll('.tab-btn');
        const contents = tabContainer.parentElement.querySelectorAll('.tab-content');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.dataset.tab;
                
                buttons.forEach(b => b.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                
                btn.classList.add('active');
                document.getElementById(target)?.classList.add('active');
            });
        });
    });
}

// ==========================================
// 仓库列表
// ==========================================

let selectedRepos = new Set();
let allRepos = [];

async function loadRepos(platform) {
    const container = document.getElementById(`${platform}-repos`);
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    const visibility = document.getElementById(`${platform}-visibility`)?.value || 'all';
    const sort = document.getElementById(`${platform}-sort`)?.value || 'updated';
    const includeForks = document.getElementById(`${platform}-forks`)?.checked ?? true;
    
    try {
        const response = await fetch(
            `/api/repos/${platform}?visibility=${visibility}&sort=${sort}&include_forks=${includeForks}`
        );
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '加载失败');
        }
        
        const data = await response.json();
        allRepos = data.repos;
        renderRepos(platform, allRepos);
        updateSelectionInfo(platform);
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <span>❌</span>
                <span>${error.message}</span>
            </div>
        `;
    }
}

function renderRepos(platform, repos) {
    const container = document.getElementById(`${platform}-repos`);
    if (!container) return;
    
    if (repos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">📭</div>
                <h3>没有找到仓库</h3>
                <p>尝试调整筛选条件</p>
            </div>
        `;
        return;
    }
    
    const html = repos.map(repo => {
        const tags = [];
        if (repo.private) tags.push('<span class="tag" title="私有仓库" style="background: rgba(248, 81, 73, 0.2); color: #f85149;">🔒 私有</span>');
        if (repo.fork) tags.push('<span class="tag" title="Fork 仓库" style="background: rgba(88, 166, 255, 0.2); color: #58a6ff;">🍴 Fork</span>');
        if (repo.archived) tags.push('<span class="tag" title="已归档" style="background: rgba(210, 153, 34, 0.2); color: #d29922;">📁 归档</span>');
        
        // 统一使用 full_name 作为标识符，确保 Fork 仓库也能正确删除
        const identifier = repo.full_name;
        const isSelected = selectedRepos.has(identifier);
        
        return `
            <div class="repo-item ${isSelected ? 'selected' : ''}" data-repo="${identifier}">
                <div class="repo-checkbox">
                    <input type="checkbox" ${isSelected ? 'checked' : ''} 
                           onchange="toggleRepo('${platform}', '${identifier}', this.checked)">
                </div>
                <div class="repo-info">
                    <div class="repo-name">
                        <a href="${repo.html_url}" target="_blank">${repo.name}</a>
                        ${tags.join(' ')}
                    </div>
                    <div class="repo-desc">${repo.description || '暂无描述'}</div>
                </div>
                <div class="repo-meta">
                    <span>📝 ${repo.language || '-'}</span>
                    <span>⭐ ${repo.stars}</span>
                    <span>🍴 ${repo.forks}</span>
                    <span>📅 ${formatDate(repo.updated_at)}</span>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `<div class="repo-list">${html}</div>`;
}

function toggleRepo(platform, repoId, checked) {
    if (checked) {
        selectedRepos.add(repoId);
    } else {
        selectedRepos.delete(repoId);
    }
    
    const item = document.querySelector(`[data-repo="${repoId}"]`);
    if (item) {
        item.classList.toggle('selected', checked);
    }
    
    updateSelectionInfo(platform);
}

function selectAllRepos(platform) {
    allRepos.forEach(repo => {
        const identifier = platform === 'github' ? repo.name : repo.full_name;
        selectedRepos.add(identifier);
    });
    renderRepos(platform, allRepos);
    updateSelectionInfo(platform);
}

function deselectAllRepos(platform) {
    selectedRepos.clear();
    renderRepos(platform, allRepos);
    updateSelectionInfo(platform);
}

function updateSelectionInfo(platform) {
    const info = document.getElementById(`${platform}-selection-info`);
    const actions = document.getElementById(`${platform}-batch-actions`);
    
    if (info) {
        info.textContent = selectedRepos.size > 0 
            ? `已选择 ${selectedRepos.size} 个仓库`
            : '';
    }
    
    if (actions) {
        actions.style.display = selectedRepos.size > 0 ? 'flex' : 'none';
    }
}

function searchRepos(platform, query) {
    const filtered = allRepos.filter(repo => 
        repo.name.toLowerCase().includes(query.toLowerCase()) ||
        (repo.description || '').toLowerCase().includes(query.toLowerCase())
    );
    renderRepos(platform, filtered);
}

// ==========================================
// 协作仓库管理
// ==========================================

let selectedCollabRepos = new Set();
let allCollabRepos = [];

async function loadCollaboratorRepos() {
    const container = document.getElementById('collab-repos');
    if (!container) return;
    
    container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        const response = await fetch('/api/repos/github/collaborator');
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '加载失败');
        }
        
        const data = await response.json();
        allCollabRepos = data.repos;
        renderCollaboratorRepos(allCollabRepos);
        updateCollabSelectionInfo();
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <span>❌</span>
                <span>${error.message}</span>
            </div>
        `;
    }
}

function renderCollaboratorRepos(repos) {
    const container = document.getElementById('collab-repos');
    if (!container) return;
    
    if (repos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">🎉</div>
                <h3>没有协作仓库</h3>
                <p>你没有作为协作者参与其他人的仓库</p>
            </div>
        `;
        return;
    }
    
    const html = repos.map(repo => {
        const isSelected = selectedCollabRepos.has(repo.full_name);
        
        return `
            <div class="repo-item ${isSelected ? 'selected' : ''}" data-collab-repo="${repo.full_name}">
                <div class="repo-checkbox">
                    <input type="checkbox" ${isSelected ? 'checked' : ''} 
                           onchange="toggleCollabRepo('${repo.full_name}', this.checked)">
                </div>
                <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                    <img src="${repo.owner_avatar}" style="width: 32px; height: 32px; border-radius: 50%;">
                    <div class="repo-info">
                        <div class="repo-name">
                            <a href="${repo.html_url}" target="_blank">${repo.full_name}</a>
                            ${repo.private ? '<span class="tag" title="私有仓库" style="background: rgba(248, 81, 73, 0.2); color: #f85149;">🔒 私有</span>' : ''}
                        </div>
                        <div class="repo-desc">${repo.description || '暂无描述'}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `<div class="repo-list">${html}</div>`;
}

function toggleCollabRepo(repoFullName, checked) {
    if (checked) {
        selectedCollabRepos.add(repoFullName);
    } else {
        selectedCollabRepos.delete(repoFullName);
    }
    
    const item = document.querySelector(`[data-collab-repo="${repoFullName}"]`);
    if (item) {
        item.classList.toggle('selected', checked);
    }
    
    updateCollabSelectionInfo();
}

function updateCollabSelectionInfo() {
    const info = document.getElementById('collab-selection-info');
    const actions = document.getElementById('collab-batch-actions');
    
    if (info) {
        info.textContent = selectedCollabRepos.size > 0 
            ? `已选择 ${selectedCollabRepos.size} 个仓库`
            : '';
    }
    
    if (actions) {
        actions.style.display = selectedCollabRepos.size > 0 ? 'flex' : 'none';
    }
}

async function batchLeave() {
    if (selectedCollabRepos.size === 0) {
        showToast('请先选择仓库', 'error');
        return;
    }
    
    const repoList = Array.from(selectedCollabRepos);
    
    showModal(
        '🚪 确认退出协作',
        `确定要退出选中的 <strong>${selectedCollabRepos.size}</strong> 个协作仓库吗？<br>退出后你将无法访问这些私有仓库`,
        repoList,
        async () => {
            try {
                showToast('正在退出...', 'info');
                
                const response = await fetch('/api/repos/github/leave', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ repos: repoList })
                });
                
                const result = await response.json();
                
                if (result.success === result.total) {
                    showToast(`成功退出 ${result.success} 个仓库`, 'success');
                } else {
                    showToast(`退出完成: ${result.success}/${result.total} 成功`, 'error');
                }
                
                selectedCollabRepos.clear();
                loadCollaboratorRepos();
            } catch (error) {
                showToast(`退出失败: ${error.message}`, 'error');
            }
        },
        'warning'
    );
}

// ==========================================
// 模态框系统
// ==========================================

let currentModalCallback = null;

function showModal(title, message, repoList, onConfirm, type = 'danger') {
    // 创建模态框 HTML
    const modalHTML = `
        <div class="modal-overlay active" id="confirm-modal">
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-${type === 'danger' ? 'danger' : 'warning'}" style="margin-bottom: 16px;">
                        <span>${type === 'danger' ? '⚠️' : '📁'}</span>
                        <span>${message}</span>
                    </div>
                    <div style="max-height: 200px; overflow-y: auto; background: var(--bg-primary); border-radius: 8px; padding: 12px;">
                        <div style="font-family: monospace; font-size: 13px; color: var(--text-secondary);">
                            ${repoList.map(r => `<div style="padding: 4px 0;">• ${r}</div>`).join('')}
                        </div>
                    </div>
                </div>
                <div class="modal-footer" style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px;">
                    <button class="btn btn-secondary" onclick="closeModal()">
                        <span>❌</span>
                        <span>取消</span>
                    </button>
                    <button class="btn btn-${type === 'danger' ? 'danger' : 'primary'}" onclick="confirmModal()">
                        <span>${type === 'danger' ? '🗑️' : '📁'}</span>
                        <span>${type === 'danger' ? '确认删除' : '确认归档'}</span>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existing = document.getElementById('confirm-modal');
    if (existing) existing.remove();
    
    // 添加到 DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 保存回调
    currentModalCallback = onConfirm;
    
    // ESC 键关闭
    document.addEventListener('keydown', handleModalEsc);
}

function closeModal() {
    const modal = document.getElementById('confirm-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
    document.removeEventListener('keydown', handleModalEsc);
    currentModalCallback = null;
}

function confirmModal() {
    if (currentModalCallback) {
        currentModalCallback();
    }
    closeModal();
}

function handleModalEsc(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
}

// ==========================================
// 批量操作
// ==========================================

async function batchDelete(platform) {
    if (selectedRepos.size === 0) {
        showToast('请先选择仓库', 'error');
        return;
    }
    
    const repoList = Array.from(selectedRepos);
    
    showModal(
        '🗑️ 确认删除仓库',
        `确定要删除选中的 <strong>${selectedRepos.size}</strong> 个仓库吗？<br><strong style="color: var(--danger);">此操作不可恢复！</strong>`,
        repoList,
        async () => {
            try {
                showToast('正在删除...', 'info');
                
                const response = await fetch(`/api/repos/${platform}/delete`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ repos: repoList })
                });
                
                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.detail || '删除失败');
                }
                
                if (result.success === result.total) {
                    showToast(`成功删除 ${result.success} 个仓库`, 'success');
                } else {
                    // 显示失败详情
                    const failed = Object.entries(result.results)
                        .filter(([_, success]) => !success)
                        .map(([name]) => name);
                    showToast(`删除完成: ${result.success}/${result.total} 成功，失败: ${failed.join(', ')}`, 'error');
                }
                
                selectedRepos.clear();
                loadRepos(platform);
            } catch (error) {
                showToast(`删除失败: ${error.message}`, 'error');
            }
        },
        'danger'
    );
}

async function batchArchive(platform) {
    if (selectedRepos.size === 0) {
        showToast('请先选择仓库', 'error');
        return;
    }
    
    if (platform !== 'github') {
        showToast('Gitee 暂不支持归档', 'error');
        return;
    }
    
    const repoList = Array.from(selectedRepos);
    
    showModal(
        '📁 确认归档仓库',
        `确定要归档选中的 <strong>${selectedRepos.size}</strong> 个仓库吗？<br>归档后仓库将变为只读状态`,
        repoList,
        async () => {
            try {
                showToast('正在归档...', 'info');
                
                const response = await fetch(`/api/repos/${platform}/archive`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ repos: repoList })
                });
                
                const result = await response.json();
                
                if (result.success === result.total) {
                    showToast(`成功归档 ${result.success} 个仓库`, 'success');
                } else {
                    showToast(`归档完成: ${result.success}/${result.total} 成功`, 'error');
                }
                
                selectedRepos.clear();
                loadRepos(platform);
            } catch (error) {
                showToast(`归档失败: ${error.message}`, 'error');
            }
        },
        'warning'
    );
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
        <div class="error-icon">📊</div>
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

async function generateProfile() {
    const form = document.getElementById('profile-form');
    if (!form) return;

    const formData = new FormData(form);
    const username = formData.get('username')?.trim();

    // 如果用户名为空，显示提示而不是发送请求
    const preview = document.getElementById('profile-preview');
    if (!username) {
        if (preview) {
            preview.innerHTML = `
                <div class="empty-state" style="padding: 60px 20px; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 16px;">👤</div>
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
    };

    // 清理空的社交链接
    Object.keys(config.socials).forEach(key => {
        if (!config.socials[key]) delete config.socials[key];
    });
    
    // 显示加载状态
    if (preview) {
        preview.innerHTML = `
            <div class="loading" style="padding: 60px;">
                <div class="spinner"></div>
            </div>
        `;
    }
    
    try {
        const response = await fetch('/api/profile/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        // 更新预览
        const preview = document.getElementById('profile-preview');
        const source = document.getElementById('profile-source');

        if (preview) {
            preview.innerHTML = marked.parse(result.content);

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
        
        showToast('Profile 已生成', 'success');
    } catch (error) {
        showToast(`生成失败: ${error.message}`, 'error');
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

