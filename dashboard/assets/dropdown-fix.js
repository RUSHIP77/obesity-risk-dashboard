/**
 * Nuclear dropdown dark-mode fix for Dash React-Select.
 * React-Select uses inline styles that CSS cannot override.
 * This MutationObserver watches for dropdown DOM changes and forces dark styles.
 */
(function() {
    'use strict';

    function getTheme() {
        return document.documentElement.getAttribute('data-theme') || 'dark';
    }

    function isDark() {
        return getTheme() === 'dark';
    }

    // Dark mode colors
    var DARK = {
        controlBg: '#1E2235',
        controlBorder: '#2A2F45',
        controlText: '#E2E8F0',
        menuBg: '#1E2235',
        menuBorder: '#2A2F45',
        optionBg: '#1E2235',
        optionHoverBg: 'rgba(59,154,232,0.25)',
        optionText: '#E2E8F0',
        inputBg: '#1E2235',
        inputText: '#E2E8F0',
        placeholder: '#7B8BA0',
    };

    // Light mode colors
    var LIGHT = {
        controlBg: '#FFFFFF',
        controlBorder: '#D1D1D6',
        controlText: '#1D1D1F',
        menuBg: '#FFFFFF',
        menuBorder: '#D1D1D6',
        optionBg: '#FFFFFF',
        optionHoverBg: 'rgba(0,122,255,0.12)',
        optionText: '#1D1D1F',
        inputBg: '#FFFFFF',
        inputText: '#1D1D1F',
        placeholder: '#86868B',
    };

    function getColors() {
        return isDark() ? DARK : LIGHT;
    }

    function styleAllDropdowns() {
        var c = getColors();

        // Style control containers (the visible dropdown bar)
        document.querySelectorAll('.Select-control').forEach(function(el) {
            el.style.setProperty('background-color', c.controlBg, 'important');
            el.style.setProperty('border-color', c.controlBorder, 'important');
            el.style.setProperty('color', c.controlText, 'important');
        });

        // Style the selected value text
        document.querySelectorAll('.Select-value-label, .Select--single > .Select-control .Select-value').forEach(function(el) {
            el.style.setProperty('color', c.controlText, 'important');
        });

        // Style placeholder
        document.querySelectorAll('.Select-placeholder').forEach(function(el) {
            el.style.setProperty('color', c.placeholder, 'important');
            el.style.setProperty('background-color', 'transparent', 'important');
        });

        // Style search input
        document.querySelectorAll('.Select-input input').forEach(function(el) {
            el.style.setProperty('color', c.inputText, 'important');
        });

        // Style the dropdown menu
        document.querySelectorAll('.Select-menu-outer').forEach(function(el) {
            el.style.setProperty('background-color', c.menuBg, 'important');
            el.style.setProperty('border-color', c.menuBorder, 'important');
            el.style.setProperty('z-index', '9999', 'important');
        });

        document.querySelectorAll('.Select-menu').forEach(function(el) {
            el.style.setProperty('background-color', c.menuBg, 'important');
        });

        // Style all options
        document.querySelectorAll('.VirtualizedSelectOption').forEach(function(el) {
            el.style.setProperty('background-color', c.optionBg, 'important');
            el.style.setProperty('color', c.optionText, 'important');
        });

        // Style focused option
        document.querySelectorAll('.VirtualizedSelectFocusedOption').forEach(function(el) {
            el.style.setProperty('background-color', c.optionHoverBg, 'important');
            el.style.setProperty('color', c.optionText, 'important');
        });

        // Style the search wrapper inside menu
        document.querySelectorAll('.Select-menu-outer input, .Select-input input').forEach(function(el) {
            el.style.setProperty('color', c.inputText, 'important');
            el.style.setProperty('background-color', 'transparent', 'important');
        });
    }

    // Run on initial load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(styleAllDropdowns, 500);
        });
    } else {
        setTimeout(styleAllDropdowns, 500);
    }

    // MutationObserver: re-style whenever DOM changes (dropdown opens, option hovers, etc.)
    var observer = new MutationObserver(function(mutations) {
        var shouldRestyle = false;
        for (var i = 0; i < mutations.length; i++) {
            var m = mutations[i];
            if (m.addedNodes.length > 0 || m.type === 'attributes') {
                shouldRestyle = true;
                break;
            }
        }
        if (shouldRestyle) {
            requestAnimationFrame(styleAllDropdowns);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'style']
    });

    // Also re-style when theme changes
    var themeObserver = new MutationObserver(function() {
        setTimeout(styleAllDropdowns, 100);
    });
    themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });

    // Expose for manual triggering
    window._styleDropdowns = styleAllDropdowns;
})();
