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
                    this.showLogoutModal();
                });
            }
        });
    }

    /**
     * Show custom beautiful logout confirmation modal
     */
    showLogoutModal() {
        // Create modal if it doesn't exist
        let modal = document.getElementById('logoutModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'logoutModal';
            modal.className = 'custom-modal-overlay';
            modal.innerHTML = `
                <div class="custom-modal-card">
                    <div class="custom-modal-icon">
                        <i class="fas fa-sign-out-alt"></i>
                    </div>
                    <h2>Confirm Logout</h2>
                    <p>Are you sure you want to log out of your session? You will need to sign in again to access your saved progress and achievements.</p>
                    <div class="custom-modal-actions">
                        <button class="modal-btn modal-btn-cancel" id="cancelLogout">Cancel</button>
                        <button class="modal-btn modal-btn-confirm" id="confirmLogout">Logout</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            // Add event listeners for the new buttons
            document.getElementById('cancelLogout').addEventListener('click', () => this.hideLogoutModal());
            document.getElementById('confirmLogout').addEventListener('click', () => this.logout());
            
            // Close on overlay click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.hideLogoutModal();
            });
        }

        // Show modal
        setTimeout(() => modal.classList.add('active'), 10);
    }

    /**
     * Hide the logout modal
     */
    hideLogoutModal() {
        const modal = document.getElementById('logoutModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    /**
     * Clear user data and logout
     */
    async logout() {
        const confirmBtn = document.getElementById('confirmLogout');
        if (confirmBtn) {
            confirmBtn.textContent = 'Logging out...';
            confirmBtn.disabled = true;
        }

        try {
            const response = await fetch('/api/logout', { 
                method: 'POST', 
                credentials: 'include' 
            });
            
            // Clear user-specific local storage
            this.clearUserSessionData();
            
            // Hide modal
            this.hideLogoutModal();
            
            // Redirect to index.html
            window.location.href = '../index.html';
        } catch (error) {
            console.error('Logout failed:', error);
            // Fallback: still clear data and redirect
            this.clearUserSessionData();
            this.hideLogoutModal();
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
