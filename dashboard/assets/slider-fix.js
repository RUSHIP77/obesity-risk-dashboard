/**
 * Hide slider input boxes that Dash renders next to sliders.
 * These overlap with mark labels. The slider marks already show the value.
 * Uses MutationObserver to catch dynamically rendered elements.
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

    // Run on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(hideSliderInputs, 300);
            setTimeout(hideSliderInputs, 1000);
        });
    } else {
        setTimeout(hideSliderInputs, 300);
        setTimeout(hideSliderInputs, 1000);
    }

    // MutationObserver for dynamic content
    var observer = new MutationObserver(function() {
        hideSliderInputs();
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();
