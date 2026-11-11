const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

const source = fs.readFileSync(require('node:path').join(__dirname, '../static/js/app.js'), 'utf8');

function element() {
    return {
        innerHTML: '', textContent: '', style: {}, children: [], dataset: {},
        classList: { toggle() {}, add() {}, remove() {} },
        setAttribute() {}, querySelectorAll() { return []; }, focus() {}, remove() {},
        append(...children) { this.children.push(...children); },
        appendChild(child) { this.children.push(child); }
    };
}

function setup(fetch) {
    const elements = new Map();
    for (const platform of ['github', 'gitee', 'collab']) {
        for (const suffix of ['repos', 'selection-info', 'batch-actions']) {
            elements.set(`${platform}-${suffix}`, element());
        }
    }
    elements.set('toast-container', element());
    const body = element();
    body.insertAdjacentHTML = (_, html) => { body.innerHTML = html; };
    const document = {
        body, activeElement: null,
        getElementById: id => elements.get(id) || null,
        querySelectorAll: () => [], querySelector: () => null,
        createElement: element, addEventListener() {}, removeEventListener() {}
    };
    const context = vm.createContext({
        document, fetch, AbortController, URLSearchParams, URL,
        window: {}, console, setTimeout() {}, clearTimeout() {}
    });
    vm.runInContext(source, context);
    return { context, elements, body, run: code => vm.runInContext(code, context) };
}

function repo(name, description = '') {
    return { name, full_name: `alice/${name}`, description, html_url: `https://github.com/alice/${name}`, updated_at: '2026-01-01', stars: 0, forks: 0 };
}
function ok(data) { return { ok: true, json: async () => data }; }
function deferred() {
    let resolve;
    const promise = new Promise(r => { resolve = r; });
    return { promise, resolve };
}

function seed(app, platform, repos) {
    app.run(`repoStates.${platform}.repos = ${JSON.stringify(repos)}`);
}

test('GitHub and Gitee selections and repository lists stay independent', () => {
    const app = setup();
    seed(app, 'github', [repo('github-only')]);
    seed(app, 'gitee', [repo('gitee-only')]);
    app.run("selectAllRepos('github'); selectAllRepos('gitee'); deselectAllRepos('gitee')");
    assert.equal(app.run("Array.from(repoStates.github.selected).join(',')"), 'alice/github-only');
    assert.equal(app.run('repoStates.gitee.selected.size'), 0);
    assert.match(app.elements.get('github-repos').innerHTML, /checked/);
});

test('search then select-all only selects visible full names', () => {
    const app = setup();
    seed(app, 'github', [repo('visible'), repo('hidden')]);
    app.run("searchRepos('github', 'visible'); selectAllRepos('github')");
    assert.equal(app.run("Array.from(repoStates.github.selected).join(',')"), 'alice/visible');
    assert.doesNotMatch(app.elements.get('github-repos').innerHTML, /alice\/hidden/);
    app.run("searchRepos('github', 'hidden')");
    assert.equal(app.run('repoStates.github.selected.size'), 0);
});

test('refresh preserves search and removes vanished selections', async () => {
    const app = setup(async () => ok({ repos: [repo('keep'), repo('other')] }));
    seed(app, 'github', [repo('keep'), repo('keep-gone')]);
    app.run("searchRepos('github', 'keep'); selectAllRepos('github')");
    await app.run("loadRepos('github')");
    assert.equal(app.run("Array.from(repoStates.github.selected).join(',')"), 'alice/keep');
    assert.doesNotMatch(app.elements.get('github-repos').innerHTML, /alice\/other/);
});

test('late responses cannot replace a newer filter result', async () => {
    const first = deferred(), second = deferred();
    let calls = 0;
    const app = setup(() => ++calls === 1 ? first.promise : second.promise);
    const oldRequest = app.run("loadRepos('github')");
    const newRequest = app.run("loadRepos('github')");
    second.resolve(ok({ repos: [repo('new')] }));
    await newRequest;
    first.resolve(ok({ repos: [repo('old')] }));
    await oldRequest;
    assert.match(app.elements.get('github-repos').innerHTML, /alice\/new/);
    assert.doesNotMatch(app.elements.get('github-repos').innerHTML, /alice\/old/);
});

test('empty successful lists count as loaded', async () => {
    const app = setup(async () => ok({ repos: [] }));
    await app.run("loadRepos('gitee')");
    assert.equal(app.run("reposLoaded('gitee')"), true);
});

test('failed refresh clears stale selections and renders errors as text', async () => {
    const app = setup(async () => ({ ok: false, status: 401, json: async () => ({ detail: '<img src=x onerror=alert(1)>' }) }));
    seed(app, 'github', [repo('old')]);
    app.run("selectAllRepos('github')");
    await app.run("loadRepos('github')");
    assert.equal(app.run('repoStates.github.selected.size'), 0);
    assert.equal(app.run("reposLoaded('github')"), false);
    assert.match(app.elements.get('github-repos').innerHTML, /&lt;img/);
    assert.doesNotMatch(app.elements.get('github-repos').innerHTML, /<img/);
});

test('repository metadata is escaped and unsafe link protocols are rejected', () => {
    const app = setup();
    const data = repo('sample', '<img src=x onerror=alert(1)>');
    data.html_url = 'javascript:alert(1)';
    seed(app, 'github', [data]);
    app.run("renderRepos('github', repoStates.github.repos)");
    const html = app.elements.get('github-repos').innerHTML;
    assert.match(html, /&lt;img/);
    assert.doesNotMatch(html, /<img|javascript:/);
    assert.match(html, /rel="noopener noreferrer"/);
});

test('partial batch failure retains failed items and reports details', async () => {
    const posts = [];
    const app = setup(async (url, options) => {
        if (options?.method === 'POST') {
            posts.push(JSON.parse(options.body));
            return ok({ success: 1, total: 2, results: { 'alice/good': true, 'alice/bad': false }, errors: ['alice/bad: permission denied'] });
        }
        return ok({ repos: [repo('bad')] });
    });
    seed(app, 'github', [repo('good'), repo('bad')]);
    app.run("selectAllRepos('github')");
    await app.run("runRepoBatch('github', 'delete', Array.from(repoStates.github.selected))");
    assert.deepEqual(posts, [{ repos: ['alice/good', 'alice/bad'] }]);
    assert.equal(app.run("Array.from(repoStates.github.selected).join(',')"), 'alice/bad');
    assert.equal(app.run('repoStates.github.busy'), false);
    const messages = app.elements.get('toast-container').children.map(toast => toast.children[1].textContent);
    assert.match(messages.join(' '), /permission denied/);
});

test('batch operation prevents duplicate submissions while pending', async () => {
    const pending = deferred();
    let posts = 0;
    const app = setup(async (url, options) => {
        if (options?.method === 'POST') { posts++; return pending.promise; }
        return ok({ repos: [] });
    });
    const first = app.run("runRepoBatch('github', 'delete', ['alice/a'])");
    await app.run("runRepoBatch('github', 'delete', ['alice/a'])");
    assert.equal(posts, 1);
    pending.resolve(ok({ success: 1, total: 1, results: { 'alice/a': true } }));
    await first;
});

test('HTTP failures in archive and leave preserve selections', async () => {
    const app = setup(async () => ({ ok: false, status: 403, json: async () => ({ detail: 'denied' }) }));
    for (const [platform, action] of [['github', 'archive'], ['collab', 'leave']]) {
        seed(app, platform, [repo('failed')]);
        app.run(`selectAllRepos('${platform}')`);
        await app.run(`runRepoBatch('${platform}', '${action}', ['alice/failed'])`);
        assert.equal(app.run(`repoStates.${platform}.selected.size`), 1);
        assert.equal(app.run(`repoStates.${platform}.busy`), false);
    }
});

test('leave confirmation has the correct action label', () => {
    const app = setup();
    seed(app, 'collab', [repo('shared')]);
    app.run("selectAllRepos('collab'); batchLeave()");
    assert.match(app.body.innerHTML, /确认退出协作/);
    assert.doesNotMatch(app.body.innerHTML, /确认归档|确认删除/);
});

test('toast messages never interpret supplied HTML', () => {
    const app = setup();
    app.run("showToast('<img src=x onerror=alert(1)>', 'error')");
    const toast = app.elements.get('toast-container').children[0];
    assert.equal(toast.innerHTML, '');
    assert.equal(toast.children[1].textContent, '<img src=x onerror=alert(1)>');
});

function profileSetup(fetch) {
    const app = setup(fetch);
    const form = element();
    form.username = 'alice';
    app.elements.set('profile-form', form);
    app.elements.set('profile-preview', element());
    app.elements.set('profile-source', element());
    app.elements.set('preview-status', element());
    app.context.FormData = class {
        constructor(form) { this.form = form; }
        get(key) { return key === 'username' ? this.form.username : ''; }
        getAll() { return []; }
    };
    app.context.marked = { parse: text => `<p>${text}</p>` };
    return app;
}

test('profile preview ignores an older response after a newer update', async () => {
    const first = deferred(), second = deferred();
    let calls = 0;
    const app = profileSetup(() => ++calls === 1 ? first.promise : second.promise);
    const old = app.run('profileRequestId = 1; renderProfile(1)');
    const latest = app.run('profileRequestId = 2; renderProfile(2)');
    second.resolve(ok({ content: 'latest' }));
    await latest;
    first.resolve(ok({ content: 'stale' }));
    await old;
    assert.equal(app.context.window.profileContent, 'latest');
    assert.equal(app.elements.get('profile-source').textContent, 'latest');
    assert.equal(app.elements.get('profile-preview').innerHTML, '<p>latest</p>');
    assert.equal(app.elements.get('preview-status').dataset.state, 'ready');
});

test('rapid profile input coalesces into one render and invalidates old deploy content', () => {
    const app = profileSetup();
    const pending = new Map();
    let id = 0;
    app.context.setTimeout = callback => { pending.set(++id, callback); return id; };
    app.context.clearTimeout = timer => pending.delete(timer);
    app.context.window.profileContent = 'old';
    app.run('generateProfile(); generateProfile(); generateProfile()');
    assert.equal(pending.size, 1);
    assert.equal(app.context.window.profileContent, '');
});

test('clearing the username clears the markdown and resets preview status', async () => {
    const app = profileSetup();
    app.elements.get('profile-form').username = '';
    app.elements.get('profile-source').textContent = 'old';
    await app.run('profileRequestId = 1; renderProfile(1)');
    assert.equal(app.elements.get('profile-source').textContent, '');
    assert.equal(app.elements.get('preview-status').textContent, '等待输入');
});
