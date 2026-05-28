/**
 * Educator Mode JavaScript
 * Handles sidebar navigation, voice input functionality, and page interactions
 */

document.addEventListener('DOMContentLoaded', function () {

    // ===== ELEMENT REFERENCES =====
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const voiceBtn = document.getElementById('voiceBtn');
    const voiceModal = document.getElementById('voiceModal');
    const closeVoiceBtn = document.getElementById('closeVoiceBtn');

    // Theme Toggle Logic
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            document.body.classList.remove('theme-light', 'theme-dark');
            document.body.classList.add(`theme-${newTheme}`);
            localStorage.setItem('culturalAI_theme', newTheme);
            localStorage.setItem('themePreference', newTheme);
            
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        });
    }

    // Restore Theme State
    const savedTheme = localStorage.getItem('culturalAI_theme') || localStorage.getItem('themePreference') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.body.classList.add(`theme-${savedTheme}`);
    const themeIcon = themeToggle?.querySelector('i');
    if (themeIcon) {
        themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    // ===== STATE VARIABLES =====
    let isListening = false;
    let recognition = null;

    // Back button functionality
    const backButtons = document.querySelectorAll('.back-button');
    backButtons.forEach(button => {
        // If the button doesn't have an explicit href, use history.back()
        if (!button.hasAttribute('href')) {
            button.addEventListener('click', function (e) {
                e.preventDefault();
                window.history.back();
            });
        }
    });

    // ===== SIDEBAR FUNCTIONALITY =====

    /**
     * Toggle sidebar expanded state
     */
    function toggleSidebar() {
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
            const isCollapsed = sidebar.classList.contains('collapsed');
            // Save state to localStorage
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        }
    }

    /**
     * Toggle mobile sidebar
     */
    function toggleMobileSidebar() {
        if (sidebar) {
            sidebar.classList.toggle('mobile-open');
            console.log('Mobile sidebar toggled:', sidebar.classList.contains('mobile-open'));
        } else {
            console.warn('Sidebar element not found');
        }
    }

    /**
     * Initialize sidebar state from localStorage
     */
    function initializeSidebarState() {
        if (sidebar) {
            const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
            if (isCollapsed) {
                sidebar.classList.add('collapsed');
            }
        }
    }

    // Event listeners for sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Sidebar toggle button clicked!');
            toggleSidebar();
        });
        console.log('Sidebar toggle button found and event listener added');
    } else {
        console.warn('Sidebar toggle button not found');
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Mobile menu button clicked!');
            toggleMobileSidebar();
        });
        console.log('Mobile menu button found and event listener added');
    } else {
        console.warn('Mobile menu button not found');
    }

    // Logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            e.preventDefault();
            showLogoutModal();
        });
    }

    /**
     * Show custom logout confirmation modal
     */
    function showLogoutModal() {
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
                    <p>Are you sure you want to log out of your session? You will need to sign in again to access your saved progress.</p>
                    <div class="custom-modal-actions">
                        <button class="modal-btn modal-btn-cancel" id="cancelLogout">Cancel</button>
                        <button class="modal-btn modal-btn-confirm" id="confirmLogout">Logout</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            // Add event listeners for the new buttons
            document.getElementById('cancelLogout').addEventListener('click', hideLogoutModal);
            document.getElementById('confirmLogout').addEventListener('click', performLogout);
            
            // Close on overlay click
            modal.addEventListener('click', function(e) {
                if (e.target === modal) hideLogoutModal();
            });
        }

        // Show modal
        setTimeout(() => modal.classList.add('active'), 10);
    }

    /**
     * Hide the logout modal
     */
    function hideLogoutModal() {
        const modal = document.getElementById('logoutModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    /**
     * Perform the actual logout operation
     */
    async function performLogout() {
        const confirmBtn = document.getElementById('confirmLogout');
        const originalText = confirmBtn.textContent;
        confirmBtn.textContent = 'Logging out...';
        confirmBtn.disabled = true;

        try {
            const response = await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Clear session/local storage
                sessionStorage.clear();
                localStorage.removeItem('user_id');
                localStorage.removeItem('first_name');
                
                // Redirect to login page
                window.location.href = '../login.html';
            } else {
                alert('Logout failed: ' + (data.message || 'Unknown error'));
                confirmBtn.textContent = originalText;
                confirmBtn.disabled = false;
            }
        } catch (error) {
            console.error('Logout error:', error);
            // Fallback: still clear storage and redirect if API fails
            sessionStorage.clear();
            localStorage.removeItem('user_id');
            localStorage.removeItem('first_name');
            window.location.href = '../login.html';
        }
    }

    // Close mobile sidebar when clicking outside
    document.addEventListener('click', function (event) {
        if (window.innerWidth <= 768 && sidebar) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnMenuBtn = mobileMenuBtn && mobileMenuBtn.contains(event.target);

            if (!isClickInsideSidebar && !isClickOnMenuBtn && sidebar.classList.contains('mobile-open')) {
                sidebar.classList.remove('mobile-open');
            }
        }
    });

    // ===== PAGE-SPECIFIC FUNCTIONALITY =====

    /**
     * Initialize page-specific features based on current page
     */
    function initializePageFeatures() {
        const currentPage = getCurrentPageName();

        switch (currentPage) {
            case 'languages':
                initializeLanguageTabs();
                break;
            case 'quizzes':
                // Quiz functionality is handled in the HTML file
                break;
            case 'settings':
                // Settings functionality is handled in the HTML file
                break;
        }
    }

    /**
     * Get current page name from URL
     * @returns {string} Current page name
     */
    function getCurrentPageName() {
        const path = window.location.pathname;
        const filename = path.split('/').pop();
        return filename.replace('.html', '') || 'dashboard';
    }

    /**
     * Initialize language tabs functionality
     */
    function initializeLanguageTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                const targetTab = this.getAttribute('data-tab');

                // Update active tab button
                tabBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                // Update active tab content
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === targetTab) {
                        content.classList.add('active');
                    }
                });
            });
        });

        // Initialize audio playback for phrases with a small delay to ensure DOM is ready
        setTimeout(() => {
            document.querySelectorAll('.play-btn').forEach(btn => {
                // Remove any existing event listeners to prevent duplicates
                const clone = btn.cloneNode(true);
                btn.parentNode.replaceChild(clone, btn);

                // Add click event listener
                clone.addEventListener('click', function () {
                    // Check if this is a language learning page button with data attributes
                    const dataText = this.getAttribute('data-text');
                    const dataLang = this.getAttribute('data-lang');

                    if (dataText && dataLang) {
                        // Use the data attributes for text-to-speech
                        speakText(dataText, dataLang);
                    } else {
                        // Fallback to the original method for pages without data attributes
                        const phraseItem = this.closest('.phrase-item');
                        if (phraseItem) {
                            const text = phraseItem.querySelector('.phrase-text').textContent;
                            const romanized = phraseItem.querySelector('.phrase-romanized').textContent;

                            // Use text-to-speech to play the phrase
                            speakText(text + '. ' + romanized);
                        }
                    }
                });
            });
        }, 100);
    }

    /**
     * Apply user settings from localStorage
     */
    function applyUserSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('educatorSettings') || '{}');

            // Apply theme
            if (settings.themeMode) {
                // Remove any existing theme classes
                document.body.className = document.body.className.replace(/theme-\w+/g, '');
                document.body.classList.add(`theme-${settings.themeMode}`);
            } else {
                // Apply system theme if no theme is set
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                document.body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
            }

            // Apply font size
            if (settings.fontSize) {
                // Remove any existing font size classes
                document.body.className = document.body.className.replace(/font-size-\w+/g, '');
                document.body.classList.add(`font-size-${settings.fontSize}`);
            }

            // Apply high contrast
            if (settings.highContrast) {
                document.body.classList.add('high-contrast');
            } else {
                document.body.classList.remove('high-contrast');
            }

            // Apply reduce motion
            if (settings.reduceMotion) {
                document.body.classList.add('reduce-motion');
            } else {
                document.body.classList.remove('reduce-motion');
            }

            console.log('User settings applied successfully');
        } catch (error) {
            console.error('Error applying user settings:', error);
            // Apply default theme if there's an error
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
        }
    }

    /**
     * Sync user profile data with backend
     */
    function syncUserProfile() {
        // Get user ID from session
        const userId = sessionStorage.getItem('user_id');

        if (userId) {
            // Fetch user profile from backend
            fetch('/api/profile')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update settings with user profile data
                        const settings = JSON.parse(localStorage.getItem('educatorSettings') || '{}');

                        // Update profile fields from backend
                        if (data.profile.first_name) {
                            settings.firstName = data.profile.first_name;
                        }

                        if (data.profile.last_name) {
                            settings.lastName = data.profile.last_name;
                        }

                        if (data.profile.email) {
                            settings.userEmail = data.profile.email;
                        }

                        if (data.profile.country) {
                            settings.userCountry = data.profile.country;
                        }

                        if (data.profile.interest) {
                            settings.userInterest = data.profile.interest;
                        }

                        // Save updated settings
                        localStorage.setItem('educatorSettings', JSON.stringify(settings));

                        // Apply the updated settings
                        applyUserSettings();

                        console.log('User profile synced successfully');
                    } else {
                        console.warn('Failed to fetch user profile:', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error fetching user profile:', error);
                });
        }
    }

    // ===== VOICE INPUT FUNCTIONALITY =====

    /**
     * Initialize speech recognition
     */
    function initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();

            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = function () {
                isListening = true;
                if (voiceModal) {
                    voiceModal.style.display = 'flex';
                }
                console.log('Voice recognition started');
            };

            recognition.onresult = function (event) {
                const transcript = event.results[0][0].transcript;
                console.log('Voice input received:', transcript);

                // Process the voice command
                processVoiceCommand(transcript);
                stopListening();
            };

            recognition.onerror = function (event) {
                console.error('Speech recognition error:', event.error);
                showNotification('Voice recognition error. Please try again.', 'error');
                stopListening();
            };

            recognition.onend = function () {
                stopListening();
            };
        } else {
            console.warn('Speech recognition not supported in this browser');
        }
    }

    /**
     * Start voice input
     */
    function startListening() {
        if (recognition && !isListening) {
            try {
                recognition.start();
            } catch (error) {
                console.error('Error starting voice recognition:', error);
                showNotification('Could not start voice input. Please try again.', 'error');
            }
        } else if (!recognition) {
            showNotification('Voice input not supported in this browser.', 'warning');
        }
    }

    /**
     * Stop voice input
     */
    function stopListening() {
        if (recognition && isListening) {
            recognition.stop();
        }
        isListening = false;
        if (voiceModal) {
            voiceModal.style.display = 'none';
        }
    }

    /**
     * Process voice commands
     * @param {string} command - The voice command to process
     */
    function processVoiceCommand(command) {
        const lowerCommand = command.toLowerCase();

        // Navigation commands
        if (lowerCommand.includes('dashboard') || lowerCommand.includes('home')) {
            window.location.href = 'dashboard.html';
        } else if (lowerCommand.includes('tribes') || lowerCommand.includes('ethnic')) {
            window.location.href = 'tribesAndEthnicGroups.html';
        } else if (lowerCommand.includes('timeline') || lowerCommand.includes('history')) {
            window.location.href = 'historicalTimelines.html';
        } else if (lowerCommand.includes('folklore') || lowerCommand.includes('myths')) {
            window.location.href = 'folkloreAndMyths.html';
        } else if (lowerCommand.includes('proverbs') || lowerCommand.includes('sayings')) {
            window.location.href = 'proverbs.html';
        } else if (lowerCommand.includes('language') || lowerCommand.includes('phrases')) {
            window.location.href = 'languages.html';
        } else if (lowerCommand.includes('quiz') || lowerCommand.includes('challenge')) {
            window.location.href = 'quizzes.html';
        } else if (lowerCommand.includes('settings')) {
            window.location.href = 'settings.html';
        } else if (lowerCommand.includes('assistant') || lowerCommand.includes('chat')) {
            window.location.href = 'assistant.html';
        } else {
            // General voice query - redirect to assistant mode
            localStorage.setItem('voiceQuery', command);
            window.location.href = 'assistant.html';
        }
    }

    /**
     * Speak text using text-to-speech
     * @param {string} text - The text to speak
     * @param {string} lang - The language code (optional)
     */
    function speakText(text, lang = 'en-US') {
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang;
            utterance.rate = 0.9;
            utterance.pitch = 1;

            // Try to find a matching voice
            const voices = speechSynthesis.getVoices();
            const voice = voices.find(v => v.lang.startsWith(lang)) || voices[0];
            if (voice) {
                utterance.voice = voice;
            }

            speechSynthesis.speak(utterance);
        } else {
            showNotification('Text-to-speech not supported in this browser.', 'warning');
        }
    }

    // ===== EVENT LISTENERS =====

    // Voice input button
    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => {
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        });
    }

    // Close voice modal
    if (closeVoiceBtn) {
        closeVoiceBtn.addEventListener('click', stopListening);
    }

    // Close voice modal when clicking outside
    if (voiceModal) {
        voiceModal.addEventListener('click', function (event) {
            if (event.target === voiceModal) {
                stopListening();
            }
        });
    }

    // Window resize handler
    window.addEventListener('resize', function () {
        // Close mobile sidebar on desktop
        if (window.innerWidth > 768 && sidebar) {
            sidebar.classList.remove('mobile-open');
        }
    });

    // ===== KEYBOARD SHORTCUTS =====

    document.addEventListener('keydown', function (event) {
        // Ctrl/Cmd + B: Toggle sidebar
        if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
            event.preventDefault();
            toggleSidebar();
        }

        // Ctrl/Cmd + Space: Voice input
        if ((event.ctrlKey || event.metaKey) && event.code === 'Space') {
            event.preventDefault();
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        }

        // Escape: Close voice modal
        if (event.key === 'Escape' && isListening) {
            stopListening();
        }

        // Number keys for quick navigation (1-9)
        if (event.altKey && event.key >= '1' && event.key <= '9') {
            event.preventDefault();
            const pageIndex = parseInt(event.key) - 1;
            const pages = [
                'dashboard.html',
                'tribesAndEthnicGroups.html',
                'historicalTimelines.html',
                'folkloreAndMyths.html',
                'proverbs.html',
                'languages.html',
                'quizzes.html',
                'settings.html',
                'assistant.html'
            ];

            if (pages[pageIndex]) {
                window.location.href = pages[pageIndex];
            }
        }
    });

    // ===== UTILITY FUNCTIONS =====

    /**
     * Show notification to user
     * @param {string} message - The notification message
     * @param {string} type - The notification type (success, error, warning, info)
     */
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
            background-color: ${type === 'success' ? '#27AE60' : type === 'error' ? '#C0392B' : type === 'warning' ? '#F39C12' : '#E67E22'};
        `;

        // Add to DOM
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after delay
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Handle window resize events
     */
    function handleResize() {
        // Close mobile sidebar on desktop
        if (window.innerWidth > 768 && sidebar) {
            sidebar.classList.remove('mobile-open');
        }
    }

    /**
     * Initialize theme toggle functionality
     */
    function initializeThemeToggle() {
        // Try different theme toggle IDs
        const themeToggle = document.getElementById('themeToggle') ||
            document.getElementById('dashboardThemeToggle') ||
            document.getElementById('settingsThemeToggle');
        if (!themeToggle) return;

        themeToggle.addEventListener('click', function () {
            // Use the global settingsManager instance if available
            if (typeof settingsManager !== 'undefined') {
                const currentTheme = settingsManager.get('themeMode', 'light');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

                // Update theme using SettingsManager
                settingsManager.set('themeMode', newTheme);
                settingsManager.applyTheme();

                console.log(`Theme switched to ${newTheme}`);
            } else {
                // Fallback if SettingsManager is not available
                const currentTheme = document.body.classList.contains('theme-dark') ? 'dark' : 'light';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

                // Apply new theme
                document.body.className = document.body.className.replace(/theme-\w+/g, '');
                document.body.classList.add(`theme-${newTheme}`);

                // Save preference
                const settings = JSON.parse(localStorage.getItem('educatorSettings') || '{}');
                settings.themeMode = newTheme;
                localStorage.setItem('educatorSettings', JSON.stringify(settings));

                // Dispatch event to notify other components
                window.dispatchEvent(new CustomEvent('settingsChanged', { detail: settings }));

                console.log(`Theme switched to ${newTheme}`);
            }
        });
    }

    // ===== INITIALIZATION =====

    /**
     * Initialize the application
     */
    function initializeApp() {
        // Initialize sidebar state from localStorage
        initializeSidebarState();

        // Initialize page features (once only)
        initializePageFeatures();

        // Initialize speech recognition
        initializeSpeechRecognition();

        // Apply user settings
        applyUserSettings();

        // Initialize theme toggle
        initializeThemeToggle();

        // Check for voice query from localStorage (from voice command navigation)
        const voiceQuery = localStorage.getItem('voiceQuery');
        if (voiceQuery && getCurrentPageName() === 'assistant') {
            localStorage.removeItem('voiceQuery');
        }
    }

    // Listen for settings changes from the settings page
    window.addEventListener('settingsChanged', function (event) {
        console.log('Settings changed, applying new settings...');
        applyUserSettings();
    });

    // Listen for system theme changes
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addListener(function (e) {
            // Only apply system theme if user has selected 'auto'
            const settings = JSON.parse(localStorage.getItem('educatorSettings') || '{}');
            if (!settings.themeMode || settings.themeMode === 'auto') {
                document.body.className = document.body.className.replace(/theme-\w+/g, '');
                document.body.classList.add(e.matches ? 'theme-dark' : 'theme-light');
            }
        });
    }

    // Start the application
    initializeApp();

    // Sync user profile on app start
    syncUserProfile();

    // ===== EXPORT FOR TESTING =====

    // Make functions available globally for testing (optional)
    window.EducatorMode = {
        toggleSidebar,
        startListening,
        stopListening,
        speakText,
        showNotification,
        processVoiceCommand,
        applyUserSettings,
        initializeThemeToggle
    };
});