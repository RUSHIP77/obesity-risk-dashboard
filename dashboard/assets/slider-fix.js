/**
 * Hide slider input boxes that Dash renders next to sliders.
 * These overlap with mark labels. The slider marks already show the value.
 * Uses a debounced MutationObserver to catch dynamically rendered elements.
 */
(function() {
    'use strict';

    function hideSliderInputs() {
        // Dash 4 renders an <input type="number"> next to each slider
        document.querySelectorAll('.dash-slider input[type="number"]').forEach(function(el) {
            el.style.display = 'none';
        });
        // Also target any input inside a slider wrapper that's not the search
        document.querySelectorAll('[data-dash-is-loading] input[type="number"]').forEach(function(el) {
            if (el.closest('.dash-slider') || el.closest('.rc-slider')) {
                el.style.display = 'none';
            }
        });
    }

    function setupObserver() {
        var timeout;
        var observer = new MutationObserver(function() {
            clearTimeout(timeout);
            timeout = setTimeout(hideSliderInputs, 100);
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Run on load — defer observer until DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(hideSliderInputs, 300);
            setTimeout(hideSliderInputs, 1000);
            setupObserver();
        });
    } else {
        setTimeout(hideSliderInputs, 300);
        setTimeout(hideSliderInputs, 1000);
        setupObserver();
    }
})();
