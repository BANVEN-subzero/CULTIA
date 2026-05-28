/**
 * settingsManager.js - Global Theme and User Settings Management
 * Ensures consistency across the entire CULTIA platform.
 */

class SettingsManager {
    constructor() {
        this.UNIFIED_THEME_KEY = 'culturalAI_theme';
        this.init();
    }

    init() {
        // Apply saved theme immediately
        this.applyTheme();
        
        // Listen for storage changes (sync across tabs)
        window.addEventListener('storage', (e) => {
            if (e.key === this.UNIFIED_THEME_KEY) {
                this.applyTheme();
            }
        });
    }

    get(key, defaultValue) {
        return localStorage.getItem(key) || defaultValue;
    }

    set(key, value) {
        localStorage.setItem(key, value);
        // If theme is set, broadcast it
        if (key === 'themeMode') {
            localStorage.setItem(this.UNIFIED_THEME_KEY, value);
        }
    }

    /**
     * Apply theme settings to the entire document
     */
    applyTheme() {
        const theme = localStorage.getItem(this.UNIFIED_THEME_KEY) || 'light';
        document.documentElement.setAttribute('data-theme', theme);
        document.body.classList.toggle('dark-mode', theme === 'dark');
        
        // Update header buttons if they exist
        this.updateHeaderThemeButtons(theme);
    }

    /**
     * Update header theme toggle buttons appearance
     */
    updateHeaderThemeButtons(theme) {
        const wrapper = document.getElementById('headerThemeToggle');
        if (wrapper) {
            const buttons = wrapper.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn.dataset.theme === theme) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }
    }

    /**
     * Initialize the theme toggle in the shared header
     */
    initHeaderThemeToggle() {
        const wrapper = document.getElementById('headerThemeToggle');
        if (!wrapper) {
            console.warn('headerThemeToggle not found, theme toggle will not work');
            return;
        }

        const buttons = wrapper.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const newTheme = btn.dataset.theme;
                this.set('themeMode', newTheme);
                this.applyTheme();
            });
        });

        // Set initial state based on current theme
        const currentTheme = localStorage.getItem(this.UNIFIED_THEME_KEY) || 'light';
        this.updateHeaderThemeButtons(currentTheme);
        this.applyTheme();

        // Initialize Logout buttons
        this.initLogoutButtons();
    }

    /**
     * Initialize logout buttons across the app
     */
    initLogoutButtons() {
        const logoutButtons = [
            document.getElementById('headerLogoutBtn'),
            document.getElementById('sidebarLogoutBtn'),
            document.getElementById('footerLogoutBtn')
        ];

        logoutButtons.forEach(btn => {
            if (btn) {
                // Remove existing listeners if any
                const newBtn = btn.cloneNode(true);
                btn.parentNode.replaceChild(newBtn, btn);
                
                newBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.logout();
                });
            }
        });
    }

    /**
     * Clear user data and logout
     */
    async logout() {
        try {
            const response = await fetch('/api/logout', { 
                method: 'POST', 
                credentials: 'include' 
            });
            
            // Clear user-specific local storage
            this.clearUserSessionData();
            
            // Redirect to index
            window.location.href = '../index.html';
        } catch (error) {
            console.error('Logout failed:', error);
            // Fallback: still clear data and redirect
            this.clearUserSessionData();
            window.location.href = '../index.html';
        }
    }

    /**
     * Clear all user-related local storage
     */
    clearUserSessionData() {
        const keysToRemove = [
            'userId', 
            'userPoints', 
            'userBadges', 
            'userActivities', 
            'gamificationUpdate',
            'languageLearningProgress'
        ];
        keysToRemove.forEach(key => localStorage.removeItem(key));
        
        // Clear session storage if used
        sessionStorage.clear();
        
        console.log('User session data cleared from local storage');
    }
}

// Global instance
window.settingsManager = new SettingsManager();
