const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');
const appSource = fs.readFileSync(path.join(__dirname, '../static/js/app.js'), 'utf8');
const workspaceSource = fs.readFileSync(path.join(__dirname, '../static/js/workspace.js'), 'utf8');

function element(dataset = {}) {
    const events = new Map();
    const classes = new Set();
    return {
        dataset, events, textContent: '', innerHTML: '', hidden: false, disabled: false,
        style: {}, attributes: {},
        classList: {
            add(value) { classes.add(value); }, remove(value) { classes.delete(value); },
            toggle(value, on) { on ? classes.add(value) : classes.delete(value); }
        },
        setAttribute(name, value) { this.attributes[name] = value; }, removeAttribute(name) { delete this.attributes[name]; },
        addEventListener(name, callback) { events.set(name, callback); },
        querySelectorAll() { return []; }
    };
}
function setup(fetch, configured = { github: true, gitee: true }) {
    const root = element(Object.fromEntries(Object.entries(configured).map(([key, value]) => [key, String(value)])));
    const buttons = ['all', 'github', 'gitee'].map(platform => element({ workspacePlatform: platform }));
    root.querySelectorAll = () => buttons;
    const fields = new Map([['workspace-overview', root]]);
    for (const id of ['total', 'public', 'private', 'forks', 'summary', 'load-notice', 'refresh', 'load-status', 'recent-list']) fields.set(`workspace-${id}`, element());
    const context = vm.createContext({
        document: { getElementById: id => fields.get(id), addEventListener() {} },
        window: {}, fetch, AbortController, URLSearchParams, URL, console, setTimeout() {}, clearTimeout() {}
    });
    vm.runInContext(appSource, context);
    vm.runInContext(workspaceSource, context);
    return { fields, buttons };
}
const ok = repos => ({ ok: true, json: async () => ({ repos }) });
const failure = { ok: false, status: 401, json: async () => ({ detail: 'Token expired' }) };
const settle = () => new Promise(resolve => setImmediate(resolve));
const repo = (name, options = {}) => ({ name, full_name: `owner/${name}`, html_url: 'https://example.com/repo', description: 'Description', language: 'Python', stars: 0, private: false, fork: false, updated_at: '2026-11-01', ...options });

test('no configured account shows setup state without making provider requests', async () => {
    let calls = 0;
    const app = setup(() => { calls++; }, { github: false, gitee: false });
    await settle();
    assert.equal(calls, 0);
    assert.equal(app.fields.get('workspace-total').textContent, '—');
    assert.match(app.fields.get('workspace-recent-list').innerHTML, /配置账户/);
    assert.equal(app.fields.get('workspace-refresh').disabled, false);
});

test('workspace aggregates real provider data and filters recent repositories', async () => {
    const app = setup(async url => url.includes('/github')
        ? ok([repo('public'), repo('private', { private: true })])
        : ok([repo('forked', { fork: true, updated_at: '2026-11-10' })]));
    await settle();
    assert.equal(app.fields.get('workspace-total').textContent, 3);
    assert.equal(app.fields.get('workspace-public').textContent, 2);
    assert.equal(app.fields.get('workspace-private').textContent, 1);
    assert.equal(app.fields.get('workspace-forks').textContent, 1);
    assert.equal(app.fields.get('workspace-load-notice').hidden, true);
    app.buttons[2].events.get('click')();
    const html = app.fields.get('workspace-recent-list').innerHTML;
    assert.match(html, /forked/);
    assert.doesNotMatch(html, /<strong>public<\/strong>/);
    assert.equal(app.fields.get('workspace-total').textContent, 3);
});

test('a failed provider does not erase successful data or appear as an empty account', async () => {
    const app = setup(async url => url.includes('/github') ? ok([repo('loaded')]) : failure);
    await settle();
    assert.equal(app.fields.get('workspace-total').textContent, 1);
    assert.match(app.fields.get('workspace-load-notice').textContent, /Gitee: Token expired/);
    assert.match(app.fields.get('workspace-summary').textContent, /成功加载/);
    app.buttons[2].events.get('click')();
    assert.match(app.fields.get('workspace-recent-list').innerHTML, /无法加载/);
    assert.doesNotMatch(app.fields.get('workspace-recent-list').innerHTML, /还没有仓库/);
});

test('all provider failures leave metrics unknown and can be retried', async () => {
    let failing = true;
    const app = setup(async () => failing ? failure : ok([]));
    await settle();
    assert.equal(app.fields.get('workspace-total').textContent, '—');
    failing = false;
    await app.fields.get('workspace-refresh').events.get('click')();
    assert.equal(app.fields.get('workspace-total').textContent, 0);
    assert.equal(app.fields.get('workspace-load-notice').hidden, true);
    assert.match(app.fields.get('workspace-recent-list').innerHTML, /还没有仓库/);
});

test('provider text is escaped and unsafe repository URLs are rejected', async () => {
    const app = setup(async () => ok([repo('<img src=x>', { description: '<script>alert(1)</script>', html_url: 'javascript:alert(1)' })]), { github: true, gitee: false });
    await settle();
    const html = app.fields.get('workspace-recent-list').innerHTML;
    assert.match(html, /&lt;img/);
    assert.match(html, /&lt;script/);
    assert.doesNotMatch(html, /<img|<script|javascript:/);
});
