// Theme Manager - Loads theme before CSS paints and updates light mode card dynamically
(function() {
    'use strict';
    
    const ThemeManager = {
        init() {
            this.loadTheme();
            this.applyColors();
            this.updateLightModeCard(); // NEW: Update light mode card on load
        },
        
        loadTheme() {
            const body = document.body;
            const savedTheme = body.dataset.themeMode || 'light';
            body.setAttribute('data-theme', savedTheme);
        },
        
        applyColors() {
            const body = document.body;
            const primary = body.dataset.primaryColor || '#3b82f6';
            const secondary = body.dataset.secondaryColor || '#8b5cf6';
            const accent = body.dataset.accentColor || '#ec4899';
            
            document.documentElement.style.setProperty('--primary-color', primary);
            document.documentElement.style.setProperty('--secondary-color', secondary);
            document.documentElement.style.setProperty('--accent-color', accent);
        },
        
        updateLightModeCard() {
            // Update light mode card background to match current colors
            const lightModeCard = document.querySelector('.light-mode-card');
            if (lightModeCard) {
                const primary = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
                const secondary = getComputedStyle(document.documentElement).getPropertyValue('--secondary-color').trim();
                lightModeCard.style.background = `linear-gradient(135deg, ${primary}, ${secondary})`;
            }
        },
        
        update(themeMode, colors) {
            const body = document.body;
            
            if (themeMode) {
                body.setAttribute('data-theme', themeMode);
                body.dataset.themeMode = themeMode;
            }
            
            if (colors) {
                if (colors.primary) {
                    document.documentElement.style.setProperty('--primary-color', colors.primary);
                    body.dataset.primaryColor = colors.primary;
                }
                if (colors.secondary) {
                    document.documentElement.style.setProperty('--secondary-color', colors.secondary);
                    body.dataset.secondaryColor = colors.secondary;
                }
                if (colors.accent) {
                    document.documentElement.style.setProperty('--accent-color', colors.accent);
                    body.dataset.accentColor = colors.accent;
                }
                
                // Update light mode card whenever colors change
                this.updateLightModeCard();
            }
        }
    };
    
    // Run immediately on script load (before DOM ready)
    ThemeManager.init();
    
    // Re-run when DOM is fully loaded (for dynamically added elements)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
    }
    
    // Make globally accessible
    window.ThemeManager = ThemeManager;
})();