// Copyright (c) 2024-2026 Bryan Everly
// Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
// See the LICENSE file in the project root for the full terms.

// Documentation search.  The index (assets/search/<lang>.json, built by
// scripts/build_search_index.py at deploy time) is fetched on first use, in
// the reader's language, and searched here -- the site is static.
(function () {
    'use strict';

    const MAX_RESULTS = 12;
    let index = null;
    let loading = null;

    function language() {
        let lang = 'en';
        try {
            lang = localStorage.getItem('sysmanage-docs-language') || 'en';
        } catch {
            lang = 'en';
        }
        return lang;
    }

    function load() {
        if (index) {
            return Promise.resolve(index);
        }
        if (!loading) {
            const url = '/assets/search/' + language() + '.json';
            loading = fetch(url)
                .then(function (r) { return r.ok ? r.json() : fetch('/assets/search/en.json').then(function (e) { return e.json(); }); })
                .then(function (data) { index = data; return data; })
                .catch(function () { index = []; return index; });
        }
        return loading;
    }

    function terms(query) {
        return query.toLowerCase().split(/\s+/).filter(function (t) { return t.length > 1; });
    }

    function score(entry, words) {
        const title = entry.t.toLowerCase();
        const heads = entry.h.join(' ').toLowerCase();
        const text = entry.x.toLowerCase();
        let total = 0;
        for (const word of words) {
            let hit = 0;
            if (title.includes(word)) { hit += 10; }
            if (heads.includes(word)) { hit += 4; }
            if (text.includes(word)) { hit += 1; }
            if (!hit) { return 0; }
            total += hit;
        }
        return total;
    }

    function snippet(text, words) {
        const lower = text.toLowerCase();
        let at = -1;
        for (const word of words) {
            at = lower.indexOf(word);
            if (at >= 0) { break; }
        }
        if (at < 0) { return text.slice(0, 160); }
        let start = Math.max(0, at - 60);
        if (start > 0) {
            // Begin on a word, not in the middle of one.
            const space = text.indexOf(' ', start);
            start = space >= 0 && space < at ? space + 1 : start;
        }
        let end = Math.min(text.length, start + 180);
        const lastSpace = text.lastIndexOf(' ', end);
        end = end < text.length && lastSpace > at ? lastSpace : end;
        return (start > 0 ? '... ' : '') + text.slice(start, end) + (end < text.length ? ' ...' : '');
    }

    function render(list, results, words, empty) {
        list.textContent = '';
        if (!results.length) {
            const li = document.createElement('li');
            li.className = 'docs-search-empty';
            li.textContent = empty;
            list.appendChild(li);
            return;
        }
        for (const entry of results) {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = entry.u;
            a.textContent = entry.t;
            const p = document.createElement('p');
            p.textContent = snippet(entry.x, words);
            li.appendChild(a);
            li.appendChild(p);
            list.appendChild(li);
        }
    }

    function init() {
        const host = document.getElementById('docs-search');
        if (!host) {
            return;
        }
        // Read at use time: i18n.js may translate these after this runs.
        const textOf = function (cls, fallback) {
            const el = host.querySelector(cls);
            return (el && el.textContent.trim()) || fallback;
        };
        const label = textOf('.docs-search-label', 'Search the documentation');
        const input = document.createElement('input');
        input.type = 'search';
        input.className = 'docs-search-input';
        input.setAttribute('aria-label', label);
        input.placeholder = label;
        const list = document.createElement('ul');
        list.className = 'docs-search-results';
        list.setAttribute('aria-live', 'polite');
        host.appendChild(input);
        host.appendChild(list);
        input.addEventListener('focus', function () {
            input.placeholder = textOf('.docs-search-label', label);
            input.setAttribute('aria-label', input.placeholder);
            load();
        });
        let timer = null;
        input.addEventListener('input', function () {
            clearTimeout(timer);
            timer = setTimeout(function () {
                const words = terms(input.value);
                if (!words.length) { list.textContent = ''; return; }
                load().then(function (data) {
                    const ranked = data
                        .map(function (entry) { return { entry: entry, s: score(entry, words) }; })
                        .filter(function (r) { return r.s > 0; })
                        .sort(function (a, b) { return b.s - a.s; })
                        .slice(0, MAX_RESULTS)
                        .map(function (r) { return r.entry; });
                    render(list, ranked, words, textOf('.docs-search-none', 'No pages match.'));
                });
            }, 150);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
