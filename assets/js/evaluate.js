// Copyright (c) 2024-2026 Bryan Everly
// Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
// See the LICENSE file in the project root for the full terms.

// /evaluate/: copy the forwardable evaluation request, in the reader's
// language -- both texts are whatever i18n.js rendered into the page.
(function () {
    'use strict';

    function init() {
        const button = document.getElementById('copy-forward');
        const text = document.getElementById('forward-text');
        const status = document.getElementById('copy-done');
        const doneText = document.getElementById('copy-done-text');
        if (!button || !text || !status) {
            return;
        }
        button.addEventListener('click', function () {
            navigator.clipboard.writeText(text.textContent.trim()).then(function () {
                status.textContent = doneText ? doneText.textContent : 'Copied';
                setTimeout(function () { status.textContent = ''; }, 2500);
            }).catch(function () {
                // No clipboard permission: select the text so it can be copied by hand.
                const range = document.createRange();
                range.selectNodeContents(text);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
