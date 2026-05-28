/**
 * Global Theme Manager
 * Manages theme state across all pages with localStorage persistence
 * and cross-tab synchronization
 */

class ThemeManager {
    constructor() {
        this.STORAGE_KEY = 'culturalAI_theme';
        this.currentTheme = this.loadTheme();
        this.init();
    }

    init() {
        // Apply theme immediately
        this.applyTheme(this.currentTheme);
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.applyTheme(this.currentTheme);
                this.initUI();
            });
        } else {
            this.initUI();
        }
        
        // Listen for storage changes (cross-tab sync)
        window.addEventListener('storage', (e) => {
            if (e.key === this.STORAGE_KEY && e.newValue) {
                this.currentTheme = e.newValue;
                this.applyTheme(this.currentTheme);
            }
        });
        
        // Listen for system theme changes
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            if (this.currentTheme === 'auto') {
                this.applyTheme('auto');
            }
        });
    }

    initUI() {
        initThemeToggle();
        window.addEventListener('themeChanged', updateToggleIcon);
    }

    loadTheme() {
        const theme = localStorage.getItem(this.STORAGE_KEY);
        if (theme) return theme;

        const oldPref = localStorage.getItem('themePreference');
        const oldTheme = localStorage.getItem('theme');
        const migrated = oldPref || oldTheme || 'light';
        localStorage.setItem(this.STORAGE_KEY, migrated);
        return migrated;
    }

    saveTheme(theme) {
        localStorage.setItem(this.STORAGE_KEY, theme);
        localStorage.setItem('themePreference', theme);
        this.currentTheme = theme;
    }

    applyTheme(theme) {
        const body = document.body;
        const root = document.documentElement;
        
        let appliedTheme = theme;
        if (theme === 'auto') {
            appliedTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        
        if (body) {
            body.classList.remove('theme-light', 'theme-dark');
            body.classList.add(`theme-${appliedTheme}`);
        }
        root.setAttribute('data-theme', appliedTheme);
        
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = appliedTheme === 'dark' ? '#1a1a1a' : '#ffffff';
        
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: appliedTheme, originalTheme: theme } 
        }));
    }

    toggle() {
        const newTheme = this.getAppliedTheme() === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        if (['light', 'dark', 'auto'].includes(theme)) {
            this.saveTheme(theme);
            this.applyTheme(theme);
        }
    }

    getTheme() {
        return this.currentTheme;
    }

    getAppliedTheme() {
        if (this.currentTheme === 'auto') {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return this.currentTheme;
    }
}

window.themeManager = new ThemeManager();

function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', () => {
        window.themeManager.toggle();
    });
    
    updateToggleIcon();
}

function updateToggleIcon() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    const appliedTheme = window.themeManager.getAppliedTheme();
    
    if (appliedTheme === 'dark') {
        themeToggle.classList.add('dark-mode');
        themeToggle.setAttribute('aria-label', 'Switch to light mode');
    } else {
        themeToggle.classList.remove('dark-mode');
        themeToggle.setAttribute('aria-label', 'Switch to dark mode');
    }
}


// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
