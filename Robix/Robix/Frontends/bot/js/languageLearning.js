/**
 * Interactive Language Learning Module (Enhanced)
 * - Increased number of tribes to 18 with authentic phrases.
 * - Verified and corrected phrases using reliable sources (Omniglot, Wikivoyage, Polyglot Club, etc.).
 * - Ensured all translations include English, French, and Pidgin without undefined values.
 * - Added new tribes: Hausa, Bamum, Tikar, Basaa (distinct from Bassa), Gbaya, Maka, Mundang.
 * - Lessons expanded where authentic data available: Greetings, Numbers 1-5, Foods, Family.
 *
 * NOTE: This file keeps your original class structure but updates data + rendering
 */
/**
 * Interactive Language Learning Module
 * Gamified learning system for 18 Cameroonian tribal languages
 */

class LanguageLearningSystem {
    constructor() {
        this.currentTribe = null;
        this.currentLesson = 0;
        this.score = 0;
        this.streak = 0;
        this.completedLessons = new Set();
        this.userProgress = this.loadProgress();
        this.customAudio = this.loadCustomAudio();
        this.useGlobalVoice = this.loadGlobalVoiceSetting();
        // Initialize language data service only if available
        try {
            this.languageDataService = typeof LanguageDataService !== 'undefined' ? new LanguageDataService() : null;
        } catch (error) {
            console.warn('LanguageDataService not available, using local data only');
            this.languageDataService = null;
        }
        this.init();
    }

    async init() {
        try {
            // Initialize voices for better pronunciation
            this.initializeVoices();
            
            await this.loadTribes();
            this.setupEventListeners();
            
            // Ensure the container exists before rendering
            const container = document.getElementById('languageLearningContainer');
            if (container) {
                this.renderDashboard();
            } else {
                console.warn('languageLearningContainer not found during init, waiting for window.onload');
            }
            
            // No automatic points for just visiting dashboard
        } catch (error) {
            console.error('Error initializing language learning system:', error);
            // Fallback: still try to render dashboard
            this.renderDashboard();
        }
    }
    
    /**
     * Initialize and load available voices for speech synthesis
     */
    initializeVoices() {
        if ('speechSynthesis' in window) {
            // Store voices loaded flag
            this.voicesLoaded = false;
            
            // Function to load and log voices
            const loadVoices = () => {
                const voices = speechSynthesis.getVoices();
                if (voices.length > 0) {
                    this.voicesLoaded = true;
                    console.log(`🎤 Loaded ${voices.length} voices`);
                    this.logAvailableVoices(voices);
                    return true;
                }
                return false;
            };
            
            // Try to load voices immediately
            if (!loadVoices()) {
                // Chrome loads voices asynchronously
                console.log('⏳ Waiting for voices to load...');
                speechSynthesis.addEventListener('voiceschanged', () => {
                    loadVoices();
                }, { once: true });
                
                // Also try after a short delay as fallback
                setTimeout(() => {
                    if (!this.voicesLoaded) {
                        loadVoices();
                    }
                }, 500);
            }
        } else {
            console.error('❌ Speech synthesis not supported in this browser');
        }
    }
    
    /**
     * Log available voices for debugging and user information
     */
    logAvailableVoices(voices) {
        console.log('📋 Available voices for African pronunciation:');
        
        // Filter and display African/French voices
        const africanVoices = voices.filter(v => 
            v.lang.includes('fr') || 
            v.lang.includes('ha') || 
            v.lang.includes('sw') ||
            v.name.toLowerCase().includes('african')
        );
        
        if (africanVoices.length > 0) {
            console.log('✅ African/French voices found:');
            africanVoices.forEach(v => {
                console.log(`  - ${v.name} (${v.lang}) ${v.localService ? '[Local]' : '[Remote]'}`);
            });
        } else {
            console.warn('⚠️ No African/French voices found. Using default voices.');
            console.log('💡 Tip: Install additional language packs in your OS for better pronunciation.');
        }
    }

    /**
     * Get authentic Cameroonian Tribes Language Data
     */
    getTribesData() {
        // Use the expanded data from languageData.js if available
        if (typeof TRIBAL_LANGUAGE_DATA !== 'undefined') {
            return TRIBAL_LANGUAGE_DATA;
        }
        
        // Fallback to basic data if TRIBAL_LANGUAGE_DATA is not loaded
        return {
            bamileke: {
                name: "Bamiléké",
                region: "West Region",
                speakers: "3.2 million",
                difficulty: "intermediate",
                lessons: [
                    {
                        title: "Basic Greetings",
                        phrases: [
                            { phrase: "Mbɔ̀ŋ", pronunciation: "mbong", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                            { phrase: "Ŋwà'à", pronunciation: "ngwa-a", translations: {en: "Good morning", fr: "Bon matin", pid: "Gud monin"} },
                            { phrase: "M̀mɛ m̀mɛ", pronunciation: "mmeh mmeh", translations: {en: "How are you?", fr: "Comment ça va?", pid: "How na"} },
                            { phrase: "M̀mɛ m̀mɛ pə̀p", pronunciation: "mmeh mmeh pup", translations: {en: "I am fine", fr: "Ça va bien", pid: "A de fine"} },
                            { phrase: "Ndɛ̀ŋ", pronunciation: "ndeng", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} }
                        ]
                    }
                ]
            }
        };
    }

    async loadTribes() {
        try {
            console.log('Loading tribes data...');
            // Load authentic language data
            this.tribes = this.getTribesData();
            console.log('Raw tribes data:', this.tribes);
            console.log('Tribes loaded successfully:', Object.keys(this.tribes || {}).length, 'tribes');
            
            if (!this.tribes || Object.keys(this.tribes).length === 0) {
                console.error('No tribes data returned from getTribesData()');
                // Create minimal fallback data
                this.tribes = {
                    bamileke: {
                        name: "Bamiléké",
                        region: "West Region", 
                        speakers: "3.2 million",
                        difficulty: "intermediate",
                        lessons: [
                            {
                                title: "Basic Greetings",
                                phrases: [
                                    { phrase: "Mbɔ̀ŋ", pronunciation: "mbong", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} }
                                ]
                            }
                        ]
                    }
                };
                console.log('Using fallback tribes data');
            }
        } catch (error) {
            console.error('Error loading tribes data:', error);
            // Fallback to minimal tribes object
            this.tribes = {
                test: {
                    name: "Test Language",
                    region: "Test Region",
                    speakers: "1000",
                    difficulty: "beginner",
                    lessons: []
                }
            };
        }
    }

    loadProgress() {
        const saved = localStorage.getItem('languageLearningProgress');
        return saved ? JSON.parse(saved) : {
            completedLessons: [],
            scores: {},
            streak: 0,
            totalPoints: 0
        };
    }

    saveProgress() {
        if (!this.userProgress.tribeProgress) {
            this.userProgress.tribeProgress = {};
        }
        
        Object.keys(this.tribes).forEach(tribeKey => {
            const tribe = this.tribes[tribeKey];
            const completedForTribe = this.userProgress.completedLessons.filter(l => l.startsWith(tribeKey)).length;
            const totalLessons = tribe.lessons.length;
            const percentage = Math.round((completedForTribe / totalLessons) * 100);
            
            this.userProgress.tribeProgress[tribeKey] = {
                completed: completedForTribe,
                total: totalLessons,
                percentage: percentage
            };
        });
        
        localStorage.setItem('languageLearningProgress', JSON.stringify(this.userProgress));
        
        if (sessionStorage.getItem('user_id')) {
            this.syncProgressToBackend();
        }
    }

    async syncProgressToBackend() {
        try {
            await fetch('/api/progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    category: 'language_learning',
                    progress_data: this.userProgress
                }),
                credentials: 'include'
            });
        } catch (error) {
            console.error('Error syncing progress:', error);
        }
    }

    /**
     * Award points for quiz completion
     */
    awardQuizPoints(score, total) {
        if (window.gamification) {
            const percentage = (score / total) * 100;
            let points = 20; // Base points
            
            // Bonus points based on performance
            if (percentage >= 90) points += 30;
            else if (percentage >= 80) points += 20;
            else if (percentage >= 70) points += 10;
            
            // Correct signature: addPoints(points, reason)
            window.gamification.addPoints(points, `Quiz completed: ${this.currentLesson.tribeKey}`);
            
            // Record activity to trigger badges
            window.gamification.recordActivity('quiz', {
                quizId: `${this.currentLesson.tribeKey}_lesson_${this.currentLesson.lessonIndex}`,
                score: score,
                total: total,
                percentage: percentage,
                tribe: this.currentLesson.tribeKey
            });
            
            // Dispatch custom event for additional tracking
            document.dispatchEvent(new CustomEvent('quizCompleted', {
                detail: { score, total, quizId: `${this.currentLesson.tribeKey}_lesson_${this.currentLesson.lessonIndex}` }
            }));
        }
    }
    
    // Removed automatic lesson points - points are now awarded manually based on actual completion
    
    // Removed automatic exploration points - no points for just browsing
    
    /**
     * Get current user stats for display
     */
    getUserStats() {
        try {
            if (window.gamification) {
                return {
                    points: window.gamification.points || 0,
                    badges: window.gamification.badges ? window.gamification.badges.length : 0,
                    activities: window.gamification.activities ? window.gamification.activities.length : 0,
                    languageLessons: window.gamification.countActivities ? window.gamification.countActivities('lesson') : 0,
                    languageQuizzes: window.gamification.countActivities ? window.gamification.countActivities('quiz') : 0
                };
            }
        } catch (error) {
            console.warn('Error getting gamification stats:', error);
        }
        return { points: 0, badges: 0, activities: 0, languageLessons: 0, languageQuizzes: 0 };
    }
    
    async syncAchievementToBackend(achievement) {
        try {
            const response = await fetch('/api/achievements', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(achievement),
                credentials: 'include'
            });
            
            if (response.ok) {
                console.log('Achievement synced to backend');
            }
        } catch (error) {
            console.error('Error syncing achievement to backend:', error);
        }
    }

    setupEventListeners() {
        // Will be set up when rendering
    }

    /**
     * Set up real-time stats updates
     */
    setupStatsUpdates() {
        // Update stats every 3 seconds
        setInterval(() => {
            const pointsElement = document.getElementById('gamificationPoints');
            const badgesElement = document.getElementById('gamificationBadges');
            
            if (pointsElement && badgesElement) {
                const stats = this.getUserStats();
                pointsElement.textContent = stats.points;
                badgesElement.textContent = stats.badges;
            }
        }, 3000);
    }

    getTotalLessons() {
        let total = 0;
        if (!this.tribes) return 0;
        Object.values(this.tribes).forEach(tribe => {
            if (tribe.lessons) total += tribe.lessons.length;
        });
        return total;
    }

    renderDashboard() {
        const container = document.getElementById('languageLearningContainer');
        if (!container) {
            console.error('Language learning container not found!');
            return;
        }

        console.log('Rendering dashboard with', Object.keys(this.tribes || {}).length, 'tribes');
        
        this.renderFullDashboard();
    }

    renderFullDashboard() {
        const container = document.getElementById('languageLearningContainer');
        if (!container) return;

        const customAudioCount = Object.keys(this.customAudio || {}).length;

        const html = `
            <div class="dashboard-content-v3">
                <!-- Restored Theme Header -->
                <div class="mb-5 p-5 rounded-5 text-white" style="background: linear-gradient(135deg, #2d5a27 0%, #1a3a17 100%); position: relative; overflow: hidden;">
                    <div style="position: absolute; right: -50px; top: -50px; width: 300px; height: 300px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
                    <h1 class="display-4 fw-bold mb-3">Language Learning</h1>
                    <p class="lead opacity-75 mb-4" style="max-width: 600px;">Master authentic tribal languages from Cameroon's diverse ethnic groups. Start your linguistic journey today.</p>
                    <div class="d-flex gap-3 flex-wrap">
                        <div class="bg-white bg-opacity-10 p-3 rounded-4 backdrop-blur shadow-sm">
                            <div class="h3 fw-bold mb-0">${Object.keys(this.tribes).length}</div>
                            <div class="small opacity-75 text-uppercase fw-bold">Languages</div>
                        </div>
                        <div class="bg-white bg-opacity-10 p-3 rounded-4 backdrop-blur shadow-sm">
                            <div class="h3 fw-bold mb-0">${this.getTotalLessons()}</div>
                            <div class="small opacity-75 text-uppercase fw-bold">Lessons</div>
                        </div>
                        ${customAudioCount > 0 ? `
                        <div class="bg-white bg-opacity-10 p-3 rounded-4 backdrop-blur shadow-sm" id="customAudioStats">
                            <div class="h3 fw-bold mb-0">${customAudioCount}</div>
                            <div class="small opacity-75 text-uppercase fw-bold">Custom Voices</div>
                        </div>` : ''}
                    </div>
                </div>

                <!-- Global Voice Toggle -->
                <div class="mb-4 p-4 rounded-4 bg-white shadow-sm border border-opacity-10" style="border: 2px solid #f0f4f0;">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-3">
                            <div style="width:50px; height:50px; background:linear-gradient(135deg, #F39C12, #E67E22); border-radius:12px; display:flex; align-items:center; justify-content:center;">
                                <i class="fas fa-globe-americas text-white" style="font-size:1.5rem;"></i>
                            </div>
                            <div>
                                <h5 class="fw-bold mb-0">Global Custom Voice</h5>
                                <p class="text-muted mb-0 small">Use your custom recordings across all tribes (when no tribe-specific one exists)</p>
                            </div>
                        </div>
                        <label class="custom-switch mb-0" style="cursor:pointer;">
                            <input type="checkbox" id="globalVoiceToggle" ${this.useGlobalVoice ? 'checked' : ''} onchange="window.languageLearning.toggleGlobalVoice()">
                            <span class="slider"></span>
                        </label>
                    </div>
                </div>

                ${customAudioCount > 0 ? `
                <div class="mb-4 p-4 rounded-4 bg-white shadow-sm border border-opacity-10" style="border: 2px solid #f0f4f0;">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-3">
                            <div style="width:50px; height:50px; background:linear-gradient(135deg, #2d5a27, #863d08); border-radius:12px; display:flex; align-items:center; justify-content:center;">
                                <i class="fas fa-microphone-alt text-white" style="font-size:1.5rem;"></i>
                            </div>
                            <div>
                                <h5 class="fw-bold mb-0">Your Custom Recordings</h5>
                                <p class="text-muted mb-0 small">You have ${customAudioCount} custom pronunciation${customAudioCount !== 1 ? 's' : ''} saved.</p>
                            </div>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-light" onclick="window.languageLearning.showRecordingsManager()">
                                <i class="fas fa-cog me-2"></i>Manage
                            </button>
                            <button class="btn btn-outline-danger" onclick="window.languageLearning.confirmDeleteAllRecordings()">
                                <i class="fas fa-trash-alt me-2"></i>Delete All
                            </button>
                            <button class="btn btn-info text-white" onclick="window.languageLearning.showTtsInfo()">
                                <i class="fas fa-info-circle me-2"></i>TTS Training
                            </button>
                        </div>
                    </div>
                </div>` : `
                <div class="mb-4 p-4 rounded-4 bg-light">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-3">
                            <div style="width:50px; height:50px; background:#f0f4f0; border-radius:12px; display:flex; align-items:center; justify-content:center;">
                                <i class="fas fa-microphone-alt" style="font-size:1.5rem; color:#2d5a27;"></i>
                            </div>
                            <div>
                                <h5 class="fw-bold mb-0">Record Your Own Voice</h5>
                                <p class="text-muted mb-0 small">Record your own authentic pronunciations while learning.</p>
                            </div>
                        </div>
                        <div class="d-flex gap-2">
                            <span class="badge bg-success text-white">New Feature</span>
                            <button class="btn btn-info text-white" onclick="window.languageLearning.showTtsInfo()">
                                <i class="fas fa-info-circle me-2"></i>TTS Training
                            </button>
                        </div>
                    </div>
                </div>`}

                <div class="section-header-v3">
                    <h2 class="fw-bold h3">Choose a Language</h2>
                    <div class="tribe-filters">
                        <button class="filter-btn active">All</button>
                    </div>
                </div>

                <div class="tribes-grid-v3">
                    ${this.renderEnhancedTribesGrid()}
                </div>
            </div>

            <style>
                .dashboard-content-v3 {
                    animation: fadeIn 0.8s ease;
                }
                .section-header-v3 {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 30px;
                }
                .tribe-filters {
                    display: flex;
                    gap: 10px;
                }
                .filter-btn {
                    padding: 8px 18px;
                    border-radius: 10px;
                    border: 1px solid #eee;
                    background: white;
                    font-weight: 600;
                    font-size: 0.9rem;
                    color: #666;
                    transition: all 0.3s ease;
                }
                .filter-btn.active, .filter-btn:hover {
                    background: #2d5a27;
                    color: white;
                    border-color: #2d5a27;
                }
                
                .tribes-grid-v3 {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 25px;
                }
                
                .tribe-card-v3 {
                    background: white;
                    border-radius: 25px;
                    padding: 25px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
                    transition: all 0.3s ease;
                    border: 1px solid rgba(0,0,0,0.03);
                    display: flex;
                    flex-direction: column;
                    text-decoration: none;
                    color: inherit;
                }
                .tribe-card-v3:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
                    border-color: #2d5a27;
                }
                .tribe-icon-box {
                    width: 50px;
                    height: 50px;
                    background: #f0f4f0;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    color: #2d5a27;
                    margin-bottom: 15px;
                }
                .tribe-card-v3 h3 {
                    font-weight: 800;
                    font-size: 1.25rem;
                    margin-bottom: 8px;
                }
                .tribe-meta {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-bottom: 15px;
                    font-size: 0.8rem;
                    color: #888;
                    font-weight: 600;
                }
                .tribe-meta span {
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }
                .tribe-desc {
                    font-size: 0.85rem;
                    color: #666;
                    margin-bottom: 20px;
                    line-height: 1.5;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }
                .card-footer {
                    margin-top: auto;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .progress-mini {
                    flex: 1;
                    margin-right: 15px;
                }
                .mini-bar {
                    height: 5px;
                    background: #eee;
                    border-radius: 10px;
                    overflow: hidden;
                    margin-bottom: 4px;
                }
                .mini-fill {
                    height: 100%;
                    background: #2d5a27;
                }
                .mini-label {
                    font-size: 0.65rem;
                    font-weight: 700;
                    color: #aaa;
                }
                .btn-learn {
                    width: 35px;
                    height: 35px;
                    background: #2d5a27;
                    color: white;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: none;
                    transition: all 0.3s ease;
                }
                .btn-learn:hover {
                    background: #1a3a17;
                    transform: scale(1.1);
                }

                /* Custom Switch */
                .custom-switch {
                    position: relative;
                    display: inline-block;
                    width: 60px;
                    height: 30px;
                }
                .custom-switch input {
                    opacity: 0;
                    width: 0;
                    height: 0;
                }
                .slider {
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #ccc;
                    transition: .4s;
                    border-radius: 34px;
                }
                .slider:before {
                    position: absolute;
                    content: "";
                    height: 22px;
                    width: 22px;
                    left: 4px;
                    bottom: 4px;
                    background-color: white;
                    transition: .4s;
                    border-radius: 50%;
                }
                input:checked + .slider {
                    background-color: #2d5a27;
                }
                input:focus + .slider {
                    box-shadow: 0 0 1px #2d5a27;
                }
                input:checked + .slider:before {
                    transform: translateX(30px);
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
        `;

        container.innerHTML = html;
        this.setupStatsUpdates();
    }

    renderEnhancedTribesGrid() {
        if (!this.tribes || Object.keys(this.tribes).length === 0) {
            return '<div style="text-align: center; padding: 2rem; color: #666;"><p>Loading tribal languages...</p></div>';
        }
        
        return Object.entries(this.tribes).map(([key, tribe]) => {
            const progress = this.getTribeProgress(key);
            const iconMap = {
                bamileke: '🎭', bamum: '👑', fulani: '🐄', duala: '⚓', bassa: '🌳',
                beti: '🌿', ewondo: '🏙️', kom: '⛰️', nso: '🛡️', medumba: '🏘️',
                ghomala: '🎨', bakweri: '🌋', hausa: '🕌'
            };
            
            return `
                <div class="tribe-card-v3" data-tribe="${key}">
                    <div class="tribe-icon-box">
                        ${iconMap[key] || '🌍'}
                    </div>
                    <h3>${tribe.name}</h3>
                    <div class="tribe-meta">
                        <span><i class="fas fa-map-marker-alt"></i> ${tribe.region}</span>
                        <span><i class="fas fa-users"></i> ${tribe.speakers}</span>
                    </div>
                    <div class="tribe-desc">${tribe.description || 'Discover the rich linguistic heritage and unique cultural expressions of this vibrant Cameroonian community.'}</div>
                    <div class="card-footer">
                        <div class="progress-mini">
                            <div class="mini-bar">
                                <div class="mini-fill" style="width: ${progress}%"></div>
                            </div>
                            <div class="mini-label">${progress}% Mastery</div>
                        </div>
                        <button class="btn-learn" onclick="startTribeLearning('${key}')">
                            <i class="fas fa-arrow-right"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderSimpleTribesGrid() {
        // Keep the old method for backward compatibility
        return this.renderEnhancedTribesGrid();
    }

    renderTribesGrid() {
        return this.renderSimpleTribesGrid();
    }

    getTribeProgress(tribeKey) {
        const tribe = this.tribes[tribeKey];
        if (!tribe || !tribe.lessons) return 0;
        
        const totalLessons = tribe.lessons.length;
        const completed = this.userProgress.completedLessons?.filter(l => 
            l.startsWith(tribeKey)
        ).length || 0;
        
        return Math.round((completed / totalLessons) * 100);
    }


    startTribeLearning(tribeKey) {
        console.log('Starting tribe learning for:', tribeKey);
        this.currentTribe = tribeKey;
        
        // Check if tribe exists
        if (!this.tribes[tribeKey]) {
            console.error('Tribe not found:', tribeKey);
            return;
        }
        
        this.renderLessonsView(tribeKey);
    }

    renderLessonsView(tribeKey) {
        const tribe = this.tribes[tribeKey];
        const container = document.getElementById('languageLearningContainer');
        const progress = this.getTribeProgress(tribeKey);
        
        const html = `
            <div class="lessons-page-v3">
                <div class="page-header-v3">
                    <button class="btn-back-v3" onclick="renderDashboard()">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <div class="page-title-v3">
                        <h1 class="fw-bold">${tribe.name} Lessons</h1>
                        <p>${tribe.region} • ${tribe.speakers} Speakers</p>
                    </div>
                    <div class="mastery-pill-v3">
                        <div class="mastery-circle">
                            <svg viewBox="0 0 36 36">
                                <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                <path class="circle" stroke-dasharray="${progress}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                            </svg>
                            <span class="mastery-val">${progress}%</span>
                        </div>
                    </div>
                </div>

                <div class="lessons-list-v3">
                    ${tribe.lessons.map((lesson, index) => this.renderModernLessonCard(tribeKey, lesson, index)).join('')}
                </div>
            </div>

            <style>
                .lessons-page-v3 {
                    animation: slideIn 0.5s ease;
                }
                .page-header-v3 {
                    display: flex;
                    align-items: center;
                    gap: 25px;
                    margin-bottom: 40px;
                }
                .btn-back-v3 {
                    width: 45px;
                    height: 45px;
                    border-radius: 12px;
                    border: 1px solid #eee;
                    background: white;
                    color: #2d5a27;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s ease;
                }
                .btn-back-v3:hover {
                    background: #2d5a27;
                    color: white;
                }
                .page-title-v3 h1 {
                    font-size: 2rem;
                    margin: 0;
                    color: #333;
                }
                .page-title-v3 p {
                    margin: 5px 0 0 0;
                    color: #888;
                    font-weight: 600;
                    font-size: 0.9rem;
                }
                
                .mastery-pill-v3 {
                    margin-left: auto;
                }
                .mastery-circle {
                    position: relative;
                    width: 70px;
                    height: 70px;
                }
                .circle-bg {
                    fill: none;
                    stroke: #eee;
                    stroke-width: 3.5;
                }
                .circle {
                    fill: none;
                    stroke: #2d5a27;
                    stroke-width: 3.5;
                    stroke-linecap: round;
                    transition: stroke-dasharray 0.5s ease;
                }
                .mastery-val {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-weight: 800;
                    font-size: 0.9rem;
                    color: #2d5a27;
                }
                
                .lessons-list-v3 {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                    gap: 20px;
                }
                
                .lesson-row-v3 {
                    background: white;
                    border-radius: 20px;
                    padding: 20px;
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.03);
                    transition: all 0.3s ease;
                    border: 1px solid transparent;
                }
                .lesson-row-v3:hover {
                    transform: scale(1.02);
                    border-color: #2d5a27;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.06);
                }
                .lesson-icon-v3 {
                    width: 50px;
                    height: 50px;
                    background: #f8f9fa;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.25rem;
                }
                .lesson-info-v3 {
                    flex: 1;
                }
                .lesson-info-v3 h3 {
                    margin: 0 0 3px 0;
                    font-size: 1.1rem;
                    font-weight: 800;
                    color: #333;
                }
                .lesson-info-v3 p {
                    margin: 0;
                    font-size: 0.8rem;
                    color: #888;
                    font-weight: 600;
                }
                .lesson-btns-v3 {
                    display: flex;
                    gap: 8px;
                }
                .btn-action-v3 {
                    padding: 8px 14px;
                    border-radius: 10px;
                    border: none;
                    font-weight: 700;
                    font-size: 0.75rem;
                    transition: all 0.3s ease;
                }
                .btn-action-v3.read {
                    background: #f0f4f0;
                    color: #2d5a27;
                }
                .btn-action-v3.read:hover {
                    background: #2d5a27;
                    color: white;
                }
                .btn-action-v3.quiz {
                    background: #2d5a27;
                    color: white;
                }
                .btn-action-v3.quiz:hover {
                    background: #1a3a17;
                    transform: translateY(-2px);
                }
                
                @keyframes slideIn {
                    from { opacity: 0; transform: translateX(20px); }
                    to { opacity: 1; transform: translateX(0); }
                }
            </style>
        `;

        container.innerHTML = html;
    }

    renderModernLessonCard(tribeKey, lesson, index) {
        const lessonId = `${tribeKey}_lesson_${index}`;
        const isCompleted = this.userProgress.completedLessons?.includes(lessonId);
        
        return `
            <div class="lesson-row-v3 ${isCompleted ? 'completed' : ''}">
                <div class="lesson-icon-v3">
                    ${lesson.icon || '📚'}
                </div>
                <div class="lesson-info-v3">
                    <h3>${lesson.title}</h3>
                    <p>${lesson.phrases.length} Essential Phrases</p>
                </div>
                <div class="lesson-btns-v3">
                    <button class="btn-action-v3 read" onclick="startLesson('${tribeKey}', ${index})">
                        <i class="fas fa-book-open me-1"></i> Read
                    </button>
                    <button class="btn-action-v3 quiz" onclick="startQuiz('${tribeKey}', ${index})">
                        <i class="fas fa-vial me-1"></i> Quiz
                    </button>
                </div>
            </div>
        `;
    }

    renderLessonCard(tribeKey, lesson, index) {
        const lessonId = `${tribeKey}_lesson_${index}`;
        const isCompleted = this.userProgress.completedLessons?.includes(lessonId);
        const score = this.userProgress.scores?.[lessonId] || 0;

        return `
            <div class="lesson-card ${isCompleted ? 'completed' : ''}" data-lesson-id="${lessonId}">
                <div class="lesson-number">${index + 1}</div>
                <div class="lesson-content">
                    <h3>${lesson.title}</h3>
                    <p>${lesson.phrases.length} phrases to learn</p>
                    ${isCompleted ? `<p class="score">Best Score: ${score}%</p>` : ''}
                </div>
                <button class="lesson-btn" data-tribe="${tribeKey}" data-lesson="${index}">
                    ${isCompleted ? '<i class="fas fa-redo"></i> Practice Again' : '<i class="fas fa-play"></i> Start Lesson'}
                </button>
            </div>
        `;
    }

    attachLessonClickHandlers() {
        document.querySelectorAll('.lesson-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tribeKey = e.target.dataset.tribe;
                const lessonIndex = parseInt(e.target.dataset.lesson);
                this.startLesson(tribeKey, lessonIndex);
            });
        });
    }

    startLesson(tribeKey, lessonIndex) {
        console.log('Starting lesson:', tribeKey, lessonIndex);
        const tribe = this.tribes[tribeKey];
        if (!tribe || !tribe.lessons[lessonIndex]) {
            console.error('Lesson not found:', tribeKey, lessonIndex);
            return;
        }
        
        const lesson = tribe.lessons[lessonIndex];
        this.currentLesson = { tribeKey, lessonIndex, lesson };
        
        this.renderLearningInterface(lesson);
    }

    renderLearningInterface(lesson) {
        const container = document.getElementById('languageLearningContainer');
        const tribe = this.tribes[this.currentLesson.tribeKey];
        
        const html = `
            <div class="learning-page-v3">
                <div class="learning-header-v3">
                    <div class="header-left-v3">
                        <button class="btn-back-v3" onclick="startTribeLearning('${this.currentLesson.tribeKey}')">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        <div class="header-info-v3">
                            <span class="tribe-label-v3">${tribe.name}</span>
                            <h2 class="lesson-title-v3">${lesson.icon || '📚'} ${lesson.title}</h2>
                        </div>
                    </div>
                    <div class="progress-box-v3">
                        <div class="progress-stats-v3">
                            <span class="count-v3"><span id="currentPhrase">1</span> / ${lesson.phrases.length}</span>
                            <span class="label-v3">Phrases</span>
                        </div>
                        <div class="bar-v3">
                            <div id="studyProgressBar" class="fill-v3" style="width: ${(1/lesson.phrases.length)*100}%"></div>
                        </div>
                    </div>
                </div>

                <div class="flashcard-wrapper-v3">
                    <div class="flashcard-container-v3">
                        ${this.renderFlashcards(lesson.phrases)}
                    </div>
                </div>

                <div class="learning-footer-v3">
                    <div class="nav-controls-v3">
                        <button class="btn-nav-v3" id="prevBtn" disabled>
                            <i class="fas fa-arrow-left"></i>
                        </button>
                        <div class="tip-v3">Click card to reveal translation</div>
                        <button class="btn-nav-v3 primary" id="nextBtn">
                            <i class="fas fa-arrow-right"></i>
                        </button>
                    </div>
                    <button class="btn-start-quiz-v3" id="startQuizBtn" style="display:none;">
                        <span>Ready for Quiz?</span>
                        <i class="fas fa-bolt ms-2"></i>
                    </button>
                </div>
            </div>

            <style>
                .learning-page-v3 {
                    max-width: 900px;
                    margin: 0 auto;
                    animation: fadeIn 0.6s ease;
                }
                .learning-header-v3 {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 40px;
                    background: white;
                    padding: 20px 30px;
                    border-radius: 20px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.03);
                }
                .header-left-v3 {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }
                .tribe-label-v3 {
                    display: block;
                    font-size: 0.7rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    font-weight: 800;
                    color: #2d5a27;
                    margin-bottom: 2px;
                }
                .lesson-title-v3 {
                    margin: 0;
                    font-size: 1.5rem;
                    color: #333;
                    font-weight: 800;
                }
                .progress-box-v3 {
                    text-align: right;
                    min-width: 150px;
                }
                .progress-stats-v3 {
                    margin-bottom: 5px;
                }
                .count-v3 {
                    font-weight: 800;
                    font-size: 1.25rem;
                    color: #2d5a27;
                }
                .label-v3 {
                    font-size: 0.65rem;
                    color: #aaa;
                    font-weight: 700;
                    text-transform: uppercase;
                }
                .bar-v3 {
                    height: 5px;
                    background: #eee;
                    border-radius: 10px;
                    overflow: hidden;
                }
                .fill-v3 {
                    height: 100%;
                    background: #2d5a27;
                    transition: width 0.4s ease;
                }
                
                .flashcard-wrapper-v3 {
                    perspective: 1500px;
                    height: 400px;
                    margin-bottom: 40px;
                }
                .flashcard-container-v3 {
                    position: relative;
                    width: 100%;
                    height: 100%;
                }
                .flashcard {
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    display: none;
                    cursor: pointer;
                }
                .flashcard.active {
                    display: block;
                    animation: slideInUp 0.5s ease;
                }
                .flashcard-inner {
                    position: relative;
                    width: 100%;
                    height: 100%;
                    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                    transform-style: preserve-3d;
                }
                .flashcard.flipped .flashcard-inner {
                    transform: rotateY(180deg);
                }
                .flashcard-front, .flashcard-back {
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    backface-visibility: hidden;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    border-radius: 30px;
                    padding: 40px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
                    border: 1px solid rgba(0,0,0,0.02);
                }
                .flashcard-front {
                    background: white;
                }
                .flashcard-back {
                    background: linear-gradient(135deg, #2d5a27 0%, #1a3a17 100%);
                    color: white;
                    transform: rotateY(180deg);
                }
                .phrase-native {
                    font-size: 3rem;
                    font-weight: 800;
                    color: #863d08;
                    margin-bottom: 10px;
                }
                .pronunciation {
                    font-size: 1.25rem;
                    color: #888;
                    font-style: italic;
                    margin-bottom: 30px;
                }
                .flashcard-back .phrase-translation {
                    font-size: 1.75rem;
                    font-weight: 700;
                    text-align: center;
                }
                .translation-row {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    margin-bottom: 15px;
                }
                .lang-tag {
                    font-size: 0.65rem;
                    background: rgba(255,255,255,0.15);
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-weight: 800;
                }
                
                .learning-footer-v3 {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 20px;
                }
                .nav-controls-v3 {
                    display: flex;
                    align-items: center;
                    gap: 25px;
                    background: white;
                    padding: 10px 25px;
                    border-radius: 50px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.03);
                }
                .btn-nav-v3 {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    border: none;
                    background: #f8f9fa;
                    color: #333;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .btn-nav-v3:hover:not(:disabled) {
                    background: #863d08;
                    color: white;
                    transform: scale(1.1);
                }
                .btn-nav-v3.primary {
                    background: #863d08;
                    color: white;
                }
                .tip-v3 {
                    font-size: 0.8rem;
                    color: #ccc;
                    font-weight: 600;
                }
                .btn-start-quiz-v3 {
                    background: #2d5a27;
                    color: white;
                    border: none;
                    padding: 15px 40px;
                    border-radius: 15px;
                    font-weight: 800;
                    font-size: 1.1rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .btn-start-quiz-v3:hover {
                    transform: translateY(-3px) scale(1.02);
                    background: #1a3a17;
                }
                
                @keyframes slideInUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
        `;

        container.innerHTML = html;
        this.initializeFlashcards(lesson.phrases);
    }

    renderFlashcards(phrases) {
        return phrases.map((phrase, index) => {
            const hasTribeAudio = !!(this.getCustomAudioUrl(phrase.phrase, this.currentLesson.tribeKey));
            const hasGlobalOnly = !hasTribeAudio && this.isGlobalRecording(phrase.phrase);
            
            let statusHtml = '';
            if (hasTribeAudio) {
                statusHtml = `
                    <div style="font-size:0.8rem; color:#27AE60; font-weight:600; margin-bottom:0.5rem;">
                        <i class="fas fa-check-circle"></i> Tribe-specific custom voice active
                    </div>
                `;
            } else if (hasGlobalOnly) {
                statusHtml = `
                    <div style="font-size:0.8rem; color:#F39C12; font-weight:600; margin-bottom:0.5rem;">
                        <i class="fas fa-globe"></i> Your global custom voice active
                    </div>
                `;
            } else if (this.useGlobalVoice) {
                statusHtml = `
                    <div style="font-size:0.8rem; color:#666; font-weight:500; margin-bottom:0.5rem;">
                        <i class="fas fa-microphone-slash"></i> No custom voice yet
                    </div>
                `;
            } else {
                statusHtml = `
                    <div style="font-size:0.8rem; color:#666; font-weight:500; margin-bottom:0.5rem;">
                        <i class="fas fa-microphone-slash"></i> Global voice disabled
                    </div>
                `;
            }
            
            return `
            <div class="flashcard ${index === 0 ? 'active' : ''}" data-index="${index}">
                <div class="flashcard-inner">
                    <div class="flashcard-front">
                        <div class="phrase-native">${phrase.phrase}</div>
                        <div class="pronunciation">[${phrase.pronunciation}]</div>
                        ${statusHtml}
                        <div class="action-buttons">
                            <button class="audio-btn-v2 ${(hasTribeAudio || hasGlobalOnly) ? 'custom-audio' : ''}" onclick="event.stopPropagation(); window.languageLearning.playAudio('${this.escapeForOnclick(phrase.phrase)}', '${this.escapeForOnclick(this.currentLesson.tribeKey)}')" title="Listen">
                                <i class="fas fa-volume-up"></i>
                            </button>
                            <button class="audio-btn-v2 record-btn" onclick="event.stopPropagation(); window.languageLearning.openRecorderModal('${this.escapeForOnclick(phrase.phrase)}', '${this.escapeForOnclick(this.currentLesson.tribeKey)}')" title="Record your custom pronunciation">
                                <i class="fas fa-microphone-alt"></i>
                            </button>
                            <button class="audio-btn-v2 mic-btn" onclick="event.stopPropagation(); window.languageLearning.verifyPronunciation('${this.escapeForOnclick(phrase.phrase)}', this)" title="Practice Speaking">
                                <i class="fas fa-microphone"></i>
                            </button>
                        </div>
                        <div class="feedback-msg mt-3 fw-bold" style="display:none; height: 24px;"></div>
                    </div>
                    <div class="flashcard-back">
                        <div class="phrase-translation">
                            <div class="translation-row">
                                <span class="lang-tag">EN</span>
                                <span>${phrase.translations.en}</span>
                            </div>
                            <div class="translation-row">
                                <span class="lang-tag">FR</span>
                                <span>${phrase.translations.fr}</span>
                            </div>
                            <div class="translation-row">
                                <span class="lang-tag">PID</span>
                                <span>${phrase.translations.pid}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `}).join('') + `
            <style>
                .action-buttons {
                    display: flex;
                    gap: 15px;
                    flex-wrap: wrap;
                    justify-content: center;
                }
                .audio-btn-v2 {
                    width: 60px;
                    height: 60px;
                    border-radius: 20px;
                    border: none;
                    background: #f0f4f0;
                    color: #2d5a27;
                    font-size: 1.5rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .audio-btn-v2:hover {
                    background: #2d5a27;
                    color: white;
                    transform: translateY(-3px);
                }
                .audio-btn-v2.custom-audio {
                    background: linear-gradient(135deg, #2d5a27 0%, #863d08 100%);
                    color: white;
                    box-shadow: 0 4px 10px rgba(45,90,39,0.3);
                }
                .audio-btn-v2.record-btn {
                    background: linear-gradient(135deg, #F39C12 0%, #E67E22 100%);
                    color: white;
                }
                .audio-btn-v2.record-btn:hover {
                    background: linear-gradient(135deg, #E67E22 0%, #D35400 100%);
                }
                .audio-btn-v2.recording {
                    background: #ff4757;
                    color: white;
                    animation: pulse 1.5s infinite;
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
                .feedback-msg.success {
                    color: #2ecc71;
                    animation: bounceIn 0.5s ease;
                }
                .feedback-msg.error {
                    color: #e74c3c;
                }
                @keyframes bounceIn {
                    0% { transform: scale(0.3); opacity: 0; }
                    50% { transform: scale(1.05); opacity: 1; }
                    70% { transform: scale(0.9); }
                    100% { transform: scale(1); }
                }
            </style>
        `;
    }

    /**
     * Verify pronunciation using Speech Recognition
     */
    verifyPronunciation(targetText, btn) {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showNotification('Speech recognition not supported in this browser.', 'error');
            return;
        }

        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'fr-FR'; // French-style pronunciation works best for many tribal phrases
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        const icon = btn.querySelector('i');
        const card = btn.closest('.flashcard-front');
        const feedback = card.querySelector('.feedback-msg');

        btn.classList.add('recording');
        icon.className = 'fas fa-spinner fa-spin';
        feedback.style.display = 'none';

        recognition.start();

        recognition.onresult = (event) => {
            const result = event.results[0][0].transcript.toLowerCase();
            const target = targetText.toLowerCase();
            
            console.log('Recognized:', result, 'Target:', target);
            
            // Fuzzy matching: check if the recognized text is close to the target
            // Tribal phrases often contain special characters, so we compare simplified versions
            const simplifiedResult = result.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z]/g, '');
            const simplifiedTarget = target.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z]/g, '');

            if (simplifiedResult.includes(simplifiedTarget) || simplifiedTarget.includes(simplifiedResult) || this.calculateSimilarity(simplifiedResult, simplifiedTarget) > 0.7) {
                this.handlePronunciationSuccess(card, feedback);
            } else {
                this.handlePronunciationError(feedback, result);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.showNotification('Could not hear you clearly. Please try again.', 'warning');
            this.resetMicBtn(btn, icon);
        };

        recognition.onend = () => {
            this.resetMicBtn(btn, icon);
        };
    }

    handlePronunciationSuccess(card, feedback) {
        feedback.textContent = 'Excellent! 🎉';
        feedback.className = 'feedback-msg success mt-3 fw-bold';
        feedback.style.display = 'block';
        
        this.celebrateSuccess();
        
        // Auto-advance after 1.5s
        setTimeout(() => {
            const nextBtn = document.getElementById('nextBtn');
            if (nextBtn && nextBtn.style.visibility !== 'hidden') {
                nextBtn.click();
            }
        }, 1500);
    }

    handlePronunciationError(feedback, result) {
        feedback.textContent = `Try again! (You said: "${result}")`;
        feedback.className = 'feedback-msg error mt-3 fw-bold';
        feedback.style.display = 'block';
    }

    /**
     * Calculate string similarity (0 to 1)
     */
    calculateSimilarity(s1, s2) {
        if (!s1 || !s2) return 0;
        if (s1 === s2) return 1;
        
        const len1 = s1.length;
        const len2 = s2.length;
        const matrix = Array(len1 + 1).fill(null).map(() => Array(len2 + 1).fill(null));

        for (let i = 0; i <= len1; i++) matrix[i][0] = i;
        for (let j = 0; j <= len2; j++) matrix[0][j] = j;

        for (let i = 1; i <= len1; i++) {
            for (let j = 1; j <= len2; j++) {
                const cost = s1[i - 1] === s2[j - 1] ? 0 : 1;
                matrix[i][j] = Math.min(
                    matrix[i - 1][j] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j - 1] + cost
                );
            }
        }

        const distance = matrix[len1][len2];
        return 1 - distance / Math.max(len1, len2);
    }

    resetMicBtn(btn, icon) {
        btn.classList.remove('recording');
        icon.className = 'fas fa-microphone';
    }

    celebrateSuccess() {
        // Create simple confetti effect
        const colors = ['#2d5a27', '#863d08', '#f1c40f', '#e74c3c', '#3498db'];
        for (let i = 0; i < 30; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                left: ${Math.random() * 100}vw;
                top: -10px;
                border-radius: 50%;
                z-index: 10001;
                pointer-events: none;
                animation: fall ${1 + Math.random() * 2}s linear forwards;
            `;
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 3000);
        }

        // Add CSS for fall animation if not present
        if (!document.getElementById('confettiStyles')) {
            const style = document.createElement('style');
            style.id = 'confettiStyles';
            style.innerHTML = `
                @keyframes fall {
                    to {
                        transform: translateY(100vh) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    escapeForOnclick(value) {
        return (value ?? '')
            .toString()
            .replace(/\\/g, '\\\\')
            .replace(/'/g, "\\'")
            .replace(/\n/g, '\\n')
            .replace(/\r/g, '\\r');
    }

    loadGlobalVoiceSetting() {
        try {
            const saved = localStorage.getItem('languageLearningUseGlobalVoice');
            return saved ? JSON.parse(saved) : true;
        } catch (e) {
            return true;
        }
    }

    saveGlobalVoiceSetting() {
        try {
            localStorage.setItem('languageLearningUseGlobalVoice', JSON.stringify(this.useGlobalVoice));
        } catch (e) { /* ignore */ }
    }

    toggleGlobalVoice() {
        this.useGlobalVoice = !this.useGlobalVoice;
        this.saveGlobalVoiceSetting();
        this.renderDashboard();
        this.showNotification(`Global voice ${this.useGlobalVoice ? 'enabled' : 'disabled'}`, 'success');
    }

    loadCustomAudio() {
        try {
            const raw = localStorage.getItem('languageLearningCustomAudio');
            if (!raw) return {};
            const data = JSON.parse(raw) || {};
            // Convert old string format to new object format for backward compatibility
            Object.keys(data).forEach(key => {
                if (typeof data[key] === 'string') {
                    data[key] = { url: data[key], isGlobal: false };
                }
            });
            return data;
        } catch (e) {
            return {};
        }
    }

    saveCustomAudio() {
        try {
            localStorage.setItem('languageLearningCustomAudio', JSON.stringify(this.customAudio || {}));
        } catch (e) {
            // ignore
        }
    }

    getCustomAudioKey(text, tribeKey) {
        return `${(tribeKey || 'default').toString().toLowerCase()}::${(text || '').toString()}`;
    }

    getGlobalAudioKey(text) {
        return `global::${(text || '').toString()}`;
    }

    isGlobalRecording(text) {
        if (!this.useGlobalVoice) return false;
        const globalKey = this.getGlobalAudioKey(text);
        return !!(this.customAudio[globalKey] && this.customAudio[globalKey].url);
    }

    getCustomAudioUrl(text, tribeKey) {
        console.log('[getCustomAudioUrl] Checking for text:', text, 'tribeKey:', tribeKey, 'useGlobalVoice:', this.useGlobalVoice);
        console.log('[getCustomAudioUrl] customAudio:', this.customAudio);
        
        // First check for tribe-specific recording
        const tribeKeyFull = this.getCustomAudioKey(text, tribeKey);
        console.log('[getCustomAudioUrl] Checking tribe key:', tribeKeyFull);
        if (this.customAudio[tribeKeyFull] && this.customAudio[tribeKeyFull].url) {
            console.log('[getCustomAudioUrl] Found tribe-specific audio!');
            return this.customAudio[tribeKeyFull].url;
        }
        
        // If global is enabled, check for global recording
        if (this.useGlobalVoice) {
            const globalKey = this.getGlobalAudioKey(text);
            console.log('[getCustomAudioUrl] Checking global key:', globalKey);
            if (this.customAudio[globalKey] && this.customAudio[globalKey].url) {
                console.log('[getCustomAudioUrl] Found global audio!');
                return this.customAudio[globalKey].url;
            }
        }
        
        console.log('[getCustomAudioUrl] No custom audio found');
        // No custom recording found
        return null;
    }

    ensureRecorderModal() {
        let modal = document.getElementById('pronunciationRecorderModal');
        if (modal) return modal;

        modal = document.createElement('div');
        modal.id = 'pronunciationRecorderModal';
        modal.style.cssText = `
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.6);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100000;
        `;

        modal.innerHTML = `
            <div style="background: white; width: min(520px, 92vw); border-radius: 16px; padding: 1.25rem; box-shadow: 0 10px 30px rgba(0,0,0,0.25);">
                <div style="display:flex; justify-content: space-between; align-items:center; gap: 1rem;">
                    <h3 style="margin:0;">Record pronunciation</h3>
                    <button id="closePronunciationRecorderBtn" style="border:none; background:transparent; font-size:1.2rem; cursor:pointer;">✕</button>
                </div>
                <div style="margin-top: 0.75rem; color:#444;">
                    <div style="font-weight:600;">Phrase</div>
                    <div id="pronunciationRecorderPhrase" style="margin-top:0.25rem; padding:0.75rem; background:#f6f6f6; border-radius:10px; word-break: break-word;"></div>
                </div>
                <div style="margin-top: 1rem; padding: 0.75rem; background: #fffbf0; border: 1px solid #f0e7c5; border-radius: 8px;">
                    <label style="display:flex; gap: 0.5rem; align-items: center; cursor:pointer; margin:0;">
                        <input type="checkbox" id="useGlobalCheckbox">
                        <div style="flex:1;">
                            <div style="font-weight:600; font-size:0.9rem;">Use as global voice</div>
                            <div style="font-size:0.8rem; color:#666;">Apply this pronunciation to all tribes (when no tribe-specific one exists)</div>
                        </div>
                    </label>
                </div>
                <div style="display:flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1rem;">
                    <button id="startRecordingBtn" style="background:#863d08; color:white; border:none; padding:0.65rem 1rem; border-radius:10px; cursor:pointer;">Start</button>
                    <button id="stopRecordingBtn" disabled style="background:#999; color:white; border:none; padding:0.65rem 1rem; border-radius:10px; cursor:not-allowed;">Stop</button>
                    <button id="saveRecordingBtn" disabled style="background:#27AE60; color:white; border:none; padding:0.65rem 1rem; border-radius:10px; cursor:not-allowed;">Save</button>
                    <button id="playRecordingBtn" disabled style="background:#c85a17; color:white; border:none; padding:0.65rem 1rem; border-radius:10px; cursor:not-allowed;">Play</button>
                </div>
                <div style="margin-top: 0.75rem; font-size:0.9rem; color:#666;">
                    After saving, your voice will be used for this phrase.
                </div>
                <audio id="recordingPreview" controls style="width:100%; margin-top: 0.75rem; display:none;"></audio>
            </div>
        `;

        document.body.appendChild(modal);

        const closeBtn = modal.querySelector('#closePronunciationRecorderBtn');
        closeBtn.addEventListener('click', () => this.closeRecorderModal());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeRecorderModal();
        });

        return modal;
    }

    openRecorderModal(text, tribeKey) {
        const modal = this.ensureRecorderModal();
        modal.dataset.text = text || '';
        modal.dataset.tribeKey = tribeKey || '';

        const phraseBox = modal.querySelector('#pronunciationRecorderPhrase');
        phraseBox.textContent = text || '';

        const startBtn = modal.querySelector('#startRecordingBtn');
        const stopBtn = modal.querySelector('#stopRecordingBtn');
        const saveBtn = modal.querySelector('#saveRecordingBtn');
        const playBtn = modal.querySelector('#playRecordingBtn');
        const preview = modal.querySelector('#recordingPreview');
        const useGlobalCheckbox = modal.querySelector('#useGlobalCheckbox');

        // reset state
        saveBtn.disabled = true;
        playBtn.disabled = true;
        stopBtn.disabled = true;
        stopBtn.style.background = '#999';
        stopBtn.style.cursor = 'not-allowed';
        preview.style.display = 'none';
        preview.removeAttribute('src');
        preview.load();
        useGlobalCheckbox.checked = true; // Check "Use as global voice" by default

        startBtn.disabled = false;
        startBtn.style.cursor = 'pointer';

        // avoid stacking handlers
        startBtn.onclick = () => this.startRecording(modal);
        stopBtn.onclick = () => this.stopRecording(modal);
        saveBtn.onclick = () => this.saveRecording(modal);
        playBtn.onclick = () => {
            try { preview.play(); } catch (e) {}
        };

        modal.style.display = 'flex';
    }

    closeRecorderModal() {
        const modal = document.getElementById('pronunciationRecorderModal');
        if (!modal) return;
        modal.style.display = 'none';

        // stop stream if active
        if (this._recorder && this._recorder.state !== 'inactive') {
            try { this._recorder.stop(); } catch (e) {}
        }
        if (this._recordingStream) {
            this._recordingStream.getTracks().forEach(t => t.stop());
            this._recordingStream = null;
        }
        this._recorder = null;
        this._recordingChunks = [];
        this._recordedBlob = null;
    }

    async startRecording(modal) {
        const startBtn = modal.querySelector('#startRecordingBtn');
        const stopBtn = modal.querySelector('#stopRecordingBtn');
        const saveBtn = modal.querySelector('#saveRecordingBtn');
        const playBtn = modal.querySelector('#playRecordingBtn');
        const preview = modal.querySelector('#recordingPreview');

        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                this.showNotification('Recording not supported in this browser.', 'error');
                return;
            }

            this._recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this._recordingChunks = [];
            this._recordedBlob = null;

            const recorder = new MediaRecorder(this._recordingStream);
            this._recorder = recorder;

            recorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) this._recordingChunks.push(e.data);
            };

            recorder.onstop = () => {
                const blob = new Blob(this._recordingChunks, { type: 'audio/webm' });
                this._recordedBlob = blob;
                const url = URL.createObjectURL(blob);
                preview.src = url;
                preview.style.display = 'block';
                saveBtn.disabled = false;
                saveBtn.style.cursor = 'pointer';
                playBtn.disabled = false;
                playBtn.style.cursor = 'pointer';

                if (this._recordingStream) {
                    this._recordingStream.getTracks().forEach(t => t.stop());
                    this._recordingStream = null;
                }
            };

            recorder.start();

            startBtn.disabled = true;
            startBtn.style.cursor = 'not-allowed';
            stopBtn.disabled = false;
            stopBtn.style.background = '#E74C3C';
            stopBtn.style.cursor = 'pointer';
            saveBtn.disabled = true;
            saveBtn.style.cursor = 'not-allowed';
            playBtn.disabled = true;
            playBtn.style.cursor = 'not-allowed';
        } catch (e) {
            console.error('Recording error:', e);
            this.showNotification('Microphone permission denied or not available.', 'error');
        }
    }

    stopRecording(modal) {
        const startBtn = modal.querySelector('#startRecordingBtn');
        const stopBtn = modal.querySelector('#stopRecordingBtn');

        try {
            if (this._recorder && this._recorder.state !== 'inactive') {
                this._recorder.stop();
            }
        } catch (e) {
            console.error('Stop recording error:', e);
        }

        startBtn.disabled = false;
        startBtn.style.cursor = 'pointer';
        stopBtn.disabled = true;
        stopBtn.style.background = '#999';
        stopBtn.style.cursor = 'not-allowed';
    }

    saveRecording(modal) {
        if (!this._recordedBlob) {
            this.showNotification('No recording to save.', 'warning');
            return;
        }

        const text = modal.dataset.text || '';
        const tribeKey = modal.dataset.tribeKey || '';
        const useGlobalCheckbox = modal.querySelector('#useGlobalCheckbox');
        const isGlobal = useGlobalCheckbox.checked;

        const reader = new FileReader();
        reader.onload = () => {
            if (isGlobal) {
                const globalKey = this.getGlobalAudioKey(text);
                this.customAudio[globalKey] = { url: reader.result, isGlobal: true };
                this.showNotification('Saved as global voice! 🌍', 'success');
            } else {
                const tribeSpecificKey = this.getCustomAudioKey(text, tribeKey);
                this.customAudio[tribeSpecificKey] = { url: reader.result, isGlobal: false };
                this.showNotification('Saved for this tribe! 🎉', 'success');
            }
            this.saveCustomAudio();
            this.closeRecorderModal();
            if (this.currentLesson && this.currentLesson.lesson && this.renderLearningInterface) {
                this.renderLearningInterface(this.currentLesson.lesson);
            }
        };
        reader.onerror = () => {
            this.showNotification('Failed to save recording.', 'error');
        };
        reader.readAsDataURL(this._recordedBlob);
    }

    initializeFlashcards(phrases) {
        let currentIndex = 0;
        let viewedPhrases = new Set();
        viewedPhrases.add(0);
        
        const flashcards = document.querySelectorAll('.flashcard');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const startQuizBtn = document.getElementById('startQuizBtn');
        const currentPhraseSpan = document.getElementById('currentPhrase');
        const studyProgressBar = document.getElementById('studyProgressBar');

        flashcards.forEach(card => {
            card.addEventListener('click', () => {
                card.classList.toggle('flipped');
            });
        });

        prevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (currentIndex > 0) {
                flashcards[currentIndex].classList.remove('active');
                currentIndex--;
                flashcards[currentIndex].classList.add('active');
                viewedPhrases.add(currentIndex);
                updateControls();
            }
        });

        nextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (currentIndex < phrases.length - 1) {
                flashcards[currentIndex].classList.remove('active');
                currentIndex++;
                flashcards[currentIndex].classList.add('active');
                viewedPhrases.add(currentIndex);
                updateControls();
            }
        });

        startQuizBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const allPhrasesViewed = viewedPhrases.size === phrases.length;
            if (!allPhrasesViewed) {
                this.showNotification(`Please study all ${phrases.length} phrases first!`, 'warning');
                return;
            }
            
            if (window.gamification) {
                const lessonId = `${this.currentLesson.tribeKey}_lesson_${this.currentLesson.lessonIndex}`;
                window.gamification.addPoints('lesson', 10, {
                    lessonId: lessonId,
                    lessonTitle: this.currentLesson.lesson.title,
                    tribe: this.currentLesson.tribeKey
                });
            }
            
            this.startQuiz(phrases);
        });

        const updateControls = () => {
            prevBtn.disabled = currentIndex === 0;
            currentPhraseSpan.textContent = currentIndex + 1;
            
            // Update progress bar
            const progress = (viewedPhrases.size / phrases.length) * 100;
            if (studyProgressBar) {
                studyProgressBar.style.width = `${progress}%`;
            }
            
            if (currentIndex === phrases.length - 1) {
                nextBtn.style.visibility = 'hidden';
                if (viewedPhrases.size === phrases.length) {
                    startQuizBtn.style.display = 'flex';
                }
            } else {
                nextBtn.style.visibility = 'visible';
                startQuizBtn.style.display = 'none';
            }
        };

        updateControls();
    }

    playAudio(text, tribeKey = null) {
        console.log('[playAudio] Called with text:', text, 'tribeKey:', tribeKey);
        const customUrl = this.getCustomAudioUrl(text, tribeKey);
        console.log('[playAudio] customUrl:', customUrl);
        if (customUrl) {
            try {
                const audio = new Audio(customUrl);
                audio.play().catch(() => {
                    this.showNotification('Unable to play saved pronunciation. Please try again.', 'error');
                });
                return;
            } catch (e) {
                console.error('[playAudio] Error playing custom audio:', e);
                // fallback to TTS below
            }
        }

        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            speechSynthesis.cancel();
            
            // Wait a bit to ensure voices are loaded (Chrome issue)
            const speakWithVoice = () => {
                const utterance = new SpeechSynthesisUtterance(text);
                
                // Get language settings with African voice preferences
                const langSettings = this.getLanguageSettings(tribeKey);
                utterance.lang = langSettings.lang;
                utterance.rate = langSettings.rate;
                utterance.pitch = langSettings.pitch;
                utterance.volume = 1.0;
                
                // Try to select an African or French voice with better pronunciation
                let voices = speechSynthesis.getVoices();
                
                // If no voices loaded yet, try again after a short delay
                if (voices.length === 0) {
                    console.log('⏳ Waiting for voices to load...');
                    setTimeout(() => {
                        voices = speechSynthesis.getVoices();
                        const selectedVoice = this.selectBestVoice(voices, langSettings.lang, tribeKey);
                        if (selectedVoice) {
                            utterance.voice = selectedVoice;
                            console.log(`🎤 Using voice: ${selectedVoice.name} (${selectedVoice.lang})`);
                        } else {
                            console.log(`🎤 Using default voice for: ${langSettings.lang}`);
                        }
                        speechSynthesis.speak(utterance);
                    }, 100);
                    return;
                }
                
                const selectedVoice = this.selectBestVoice(voices, langSettings.lang, tribeKey);
                
                if (selectedVoice) {
                    utterance.voice = selectedVoice;
                    console.log(`🎤 Using voice: ${selectedVoice.name} (${selectedVoice.lang})`);
                } else {
                    console.log(`🎤 Using default voice for: ${langSettings.lang}`);
                }
                
                // Add event handlers for better control
                utterance.onstart = () => {
                    console.log('🔊 Audio playback started');
                };
                
                utterance.onerror = (event) => {
                    console.error('❌ Speech synthesis error:', event.error, event);
                    
                    // Provide more specific error messages
                    let errorMessage = 'Audio playback failed. ';
                    if (event.error === 'not-allowed') {
                        errorMessage += 'Please allow audio playback in your browser.';
                    } else if (event.error === 'network') {
                        errorMessage += 'Network error. Please check your connection.';
                    } else if (event.error === 'synthesis-failed') {
                        errorMessage += 'Speech synthesis failed. Trying with default voice...';
                        // Retry with simpler settings
                        const simpleUtterance = new SpeechSynthesisUtterance(text);
                        simpleUtterance.lang = 'fr-FR';
                        simpleUtterance.rate = 0.8;
                        speechSynthesis.speak(simpleUtterance);
                        return;
                    } else {
                        errorMessage += 'Please try again.';
                    }
                    
                    this.showNotification(errorMessage, 'error');
                };
                
                utterance.onend = () => {
                    console.log('✅ Audio playback completed');
                };
                
                // Speak with enhanced settings
                try {
                    speechSynthesis.speak(utterance);
                    console.log('🔊 Speech synthesis started');
                } catch (error) {
                    console.error('❌ Error starting speech:', error);
                    this.showNotification('Failed to start audio. Please try again.', 'error');
                }
            };
            
            speakWithVoice();
        } else {
            console.error('❌ Speech synthesis not supported');
            this.showNotification('Audio playback is not supported in your browser.', 'error');
        }
    }

    selectBestVoice(voices, targetLang, tribeKey) {
        if (!voices || voices.length === 0) {
            console.warn('⚠️ No voices available yet, will use default');
            return null;
        }

        console.log(`🔍 Searching for voice matching: ${targetLang} for tribe: ${tribeKey}`);
        console.log(`📋 Available voices: ${voices.length}`);

        // Priority 1: Exact match for Cameroon French (best for most tribal languages)
        const cmFrVoices = voices.filter(voice =>
            voice.lang === 'fr-CM' || voice.lang === 'fr-CA' || voice.lang === 'fr-FR'
        );

        if (cmFrVoices.length > 0) {
            // Prefer female voices for softer, clearer pronunciation
            const femaleVoice = cmFrVoices.find(v =>
                v.name.toLowerCase().includes('female') ||
                v.name.toLowerCase().includes('amelie') ||
                v.name.toLowerCase().includes('celine') ||
                v.name.toLowerCase().includes('marie') ||
                v.name.toLowerCase().includes('sophie') ||
                v.name.toLowerCase().includes('oceane') ||
                v.name.toLowerCase().includes('pauline')
            );

            if (femaleVoice) {
                console.log(`✅ Found female French voice: ${femaleVoice.name}`);
                return femaleVoice;
            }

            console.log(`✅ Found French voice: ${cmFrVoices[0].name}`);
            return cmFrVoices[0];
        }

        // Priority 2: Any African French voice
        const africanFrenchVoices = voices.filter(voice =>
            voice.lang.includes('fr') && (
                voice.lang.includes('CM') ||
                voice.lang.includes('SN') ||
                voice.lang.includes('CI') ||
                voice.lang.includes('BF') ||
                voice.name.toLowerCase().includes('african') ||
                voice.name.toLowerCase().includes('cameroon')
            )
        );

        if (africanFrenchVoices.length > 0) {
            console.log(`✅ Found African French voice: ${africanFrenchVoices[0].name}`);
            return africanFrenchVoices[0];
        }

        // Priority 3: Specific African language voices (for Hausa, Fulani, etc.)
        const hausaVoices = voices.filter(voice => voice.lang.includes('ha'));
        if (hausaVoices.length > 0 && tribeKey === 'hausa') {
            console.log(`✅ Found Hausa voice: ${hausaVoices[0].name}`);
            return hausaVoices[0];
        }

        // Priority 4: Standard French voices (France, Belgium, Canada)
        const frenchVoices = voices.filter(voice =>
            voice.lang.startsWith('fr') && voice.lang !== 'fr-CA'
        );

        if (frenchVoices.length > 0) {
            const femaleVoice = frenchVoices.find(v =>
                v.name.toLowerCase().includes('female') ||
                v.name.toLowerCase().includes('amelie') ||
                v.name.toLowerCase().includes('celine') ||
                v.name.toLowerCase().includes('marie')
            );

            if (femaleVoice) {
                console.log(`✅ Found French female voice: ${femaleVoice.name}`);
                return femaleVoice;
            }

            console.log(`✅ Found French voice: ${frenchVoices[0].name}`);
            return frenchVoices[0];
        }

        // Priority 5: Any voice matching the target language family
        const matchingVoices = voices.filter(voice => voice.lang.startsWith(targetLang.split('-')[0]));
        if (matchingVoices.length > 0) {
            console.log(`✅ Found matching voice: ${matchingVoices[0].name}`);
            return matchingVoices[0];
        }

        // Priority 6: Fallback to any French voice
        const anyFrenchVoice = voices.find(voice => voice.lang.startsWith('fr'));
        if (anyFrenchVoice) {
            console.log(`⚠️ Using fallback French voice: ${anyFrenchVoice.name}`);
            return anyFrenchVoice;
        }

        // Priority 7: Any English voice as last resort
        const anyEnglishVoice = voices.find(voice => voice.lang.startsWith('en'));
        if (anyEnglishVoice) {
            console.log(`⚠️ Using fallback English voice: ${anyEnglishVoice.name}`);
            return anyEnglishVoice;
        }

        console.warn('⚠️ No suitable voice found, using browser default');
        return null;
    }

    getLanguageSettings(tribeKey) {
        // Enhanced settings with slower rates and adjusted pitch for clearer African pronunciation
        const settings = {
            fulani: { 
                lang: 'fr-CM',  // Cameroon French
                rate: 0.65,     // Slower for clarity
                pitch: 1.0      // Natural pitch
            },
            duala: { 
                lang: 'fr-CM',  // Cameroon French
                rate: 0.7, 
                pitch: 1.05     // Slightly higher for tonal language
            },
            ewondo: { 
                lang: 'fr-CM',  // Cameroon French
                rate: 0.7, 
                pitch: 1.0 
            },
            bamileke: { 
                lang: 'fr-CM',  // Cameroon French
                rate: 0.65,     // Slower for tonal clarity
                pitch: 1.1      // Higher for tonal language
            },
            nso: {
                lang: 'en-GB',
                rate: 0.6,
                pitch: 1.05
            },
            hausa: { 
                lang: 'ha-NG',  // Hausa (Nigeria)
                rate: 0.75, 
                pitch: 0.95     // Slightly lower for Hausa
            },
            basaa: { 
                lang: 'fr-CM',  // Cameroon French
                rate: 0.7, 
                pitch: 1.0 
            },
            gbaya: { 
                lang: 'fr-CF',  // Central African French
                rate: 0.7, 
                pitch: 1.0 
            },
            mundang: { 
                lang: 'fr-TD',  // Chad French
                rate: 0.7, 
                pitch: 1.0 
            },
            default: { 
                lang: 'fr-CM',  // Default to Cameroon French
                rate: 0.7,      // Slower for clarity
                pitch: 1.0 
            }
        };
        
        return settings[tribeKey] || settings.default;
    }
    
    showNotification(message, type = 'info') {
        // Add CSS animations if not present
        if (!document.getElementById('notificationAnimations')) {
            const style = document.createElement('style');
            style.id = 'notificationAnimations';
            style.textContent = `
                @keyframes slideIn {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                @keyframes slideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        // Set background color based on type
        const colors = {
            success: '#27AE60',
            error: '#E74C3C',
            info: '#3498DB',
            warning: '#F39C12'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    showRecordingsManager() {
        const container = document.getElementById('languageLearningContainer');
        if (!container) return;

        const recordingsList = Object.entries(this.customAudio || {}).map(([key, data], index) => {
            const isGlobal = typeof data === 'object' && data.isGlobal;
            const dataUrl = typeof data === 'object' ? data.url : data;

            let tribeText = 'General';
            let phraseText = key;
            if (key.startsWith('global::')) {
                phraseText = key.replace('global::', '');
                tribeText = '🌍 Global';
            } else {
                const parts = key.split('::');
                tribeText = parts[0] ? `${parts[0][0].toUpperCase() + parts[0].slice(1)}` : 'General';
                phraseText = parts.slice(1).join('::');
            }

            return { index, key, tribeText, phraseText, dataUrl, isGlobal };
        });
        
        // Separate into global and tribe-specific
        const globalRecordings = recordingsList.filter(item => item.isGlobal);
        const tribeRecordings = recordingsList.filter(item => !item.isGlobal);

        const renderRecordingItem = (item) => `
            <div class="recording-item p-4 mb-3 bg-white rounded-4 shadow-sm border" data-key="${this.escapeForOnclick(item.key)}">
                <div class="d-flex justify-content-between align-items-start gap-4">
                    <div class="flex-1">
                        <h5 class="fw-bold mb-2">
                            ${item.phraseText}
                            ${item.isGlobal ? `<span class="badge bg-warning text-dark ms-2" style="font-size:0.7rem;">Global</span>` : ''}
                        </h5>
                        <p class="text-muted mb-0 small"><strong>Tribe:</strong> ${item.tribeText}</p>
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-light" onclick="window.languageLearning.playRecording('${this.escapeForOnclick(item.key)}')">
                            <i class="fas fa-play me-2"></i>Play
                        </button>
                        ${!item.isGlobal ? `
                        <button class="btn btn-warning text-dark" onclick="window.languageLearning.toggleRecordingGlobal('${this.escapeForOnclick(item.key)}')" title="Make global">
                            <i class="fas fa-globe"></i>
                        </button>
                        ` : ''}
                        <button class="btn btn-outline-danger" onclick="window.languageLearning.deleteRecording('${this.escapeForOnclick(item.key)}')">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        const html = `
            <div class="dashboard-content-v3">
                <div class="mb-5 d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center gap-3">
                        <button class="btn btn-light" onclick="window.languageLearning.renderDashboard()">
                            <i class="fas fa-arrow-left me-2"></i>Back
                        </button>
                        <div>
                            <h1 class="fw-bold mb-0">Manage Custom Recordings</h1>
                            <p class="text-muted mb-0">${recordingsList.length} custom pronunciation${recordingsList.length !== 1 ? 's' : ''} saved</p>
                        </div>
                    </div>
                    <button class="btn btn-outline-danger" onclick="window.languageLearning.confirmDeleteAllRecordings()">
                        <i class="fas fa-trash-alt me-2"></i>Delete All
                    </button>
                </div>
                
                <!-- Global Voices Section -->
                ${globalRecordings.length > 0 ? `
                    <div class="mb-5">
                        <h3 class="fw-bold mb-3">🌍 Global Voices (Used Across All Tribes)</h3>
                        <div class="recordings-list mb-4">
                            ${globalRecordings.map(renderRecordingItem).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Tribe-Specific Voices Section -->
                ${tribeRecordings.length > 0 ? `
                    <div class="mb-5">
                        <h3 class="fw-bold mb-3">🎭 Tribe-Specific Voices (Override Global)</h3>
                        <div class="recordings-list">
                            ${tribeRecordings.map(renderRecordingItem).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Empty State -->
                ${recordingsList.length === 0 ? `
                    <div class="text-center py-5">
                        <i class="fas fa-microphone-alt" style="font-size:4rem; color:#ddd; margin-bottom:1rem;"></i>
                        <p class="text-muted">No custom recordings yet.</p>
                    </div>
                ` : ''}
            </div>

            <style>
                .recordings-list {
                    animation: fadeIn 0.5s ease;
                }
                .recording-item {
                    transition: all 0.2s ease;
                }
                .recording-item:hover {
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
            </style>
        `;

        container.innerHTML = html;
    }

    toggleRecordingGlobal(key) {
        const data = this.customAudio[key];
        if (!data) return;

        if (key.startsWith('global::')) {
            // Move from global to tribe-general
            const phrase = key.replace('global::', '');
            const newKey = `default::${phrase}`;
            this.customAudio[newKey] = { url: typeof data === 'object' ? data.url : data, isGlobal: false };
            delete this.customAudio[key];
        } else {
            // Convert to global
            const phrase = key.split('::').slice(1).join('::');
            const globalKey = `global::${phrase}`;
            this.customAudio[globalKey] = { url: typeof data === 'object' ? data.url : data, isGlobal: true };
            delete this.customAudio[key];
        }

        this.saveCustomAudio();
        this.showNotification('Recording updated!', 'success');
        this.showRecordingsManager();
    }

    playRecording(key) {
        let dataUrl = this.customAudio[key];
        if (typeof dataUrl === 'object') {
            dataUrl = dataUrl.url;
        }

        if (!dataUrl) {
            this.showNotification('Recording not found.', 'error');
            return;
        }

        try {
            const audio = new Audio(dataUrl);
            audio.play().catch(() => {
                this.showNotification('Unable to play recording.', 'error');
            });
        } catch (e) {
            this.showNotification('Failed to play recording.', 'error');
        }
    }

    deleteRecording(key) {
        if (confirm('Are you sure you want to delete this recording?')) {
            delete this.customAudio[key];
            this.saveCustomAudio();
            this.showNotification('Recording deleted.', 'success');
            this.showRecordingsManager();
        }
    }

    confirmDeleteAllRecordings() {
        const count = Object.keys(this.customAudio || {}).length;
        if (count === 0) {
            this.showNotification('No recordings to delete.', 'info');
            return;
        }

        if (confirm(`Are you sure you want to delete all ${count} custom recording${count !== 1 ? 's' : ''}? This cannot be undone.`)) {
            this.customAudio = {};
            this.saveCustomAudio();
            this.showNotification('All recordings deleted.', 'success');
            this.renderDashboard();
        }
    }
    
    showTtsInfo() {
        const modalId = 'ttsInfoModal';
        let modal = document.getElementById(modalId);
        if (modal) modal.remove();
        
        modal = document.createElement('div');
        modal.id = modalId;
        modal.style.cssText = `
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100001;
            padding: 1rem;
        `;
        
        modal.innerHTML = `
            <div style="background: white; max-width: 600px; width: 100%; border-radius: 16px; padding: 2rem; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1.5rem;">
                    <h2 style="margin: 0; color: #2d5a27;">Custom TTS Training Options</h2>
                    <button onclick="document.getElementById('${modalId}').remove()" style="border: none; background: none; font-size: 1.5rem; cursor: pointer; color: #666;">&times;</button>
                </div>
                
                <div style="color: #444; line-height: 1.7;">
                    <p style="margin-bottom: 1rem;">
                        <strong>Option 1: Manual Recordings (Current)</strong><br>
                        Record individual phrases to create your custom voice. Perfect for authentic, personal pronunciations!
                    </p>
                    
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <h4 style="margin-top: 0; color: #2d5a27;">Option 2: AI TTS Model Training (Future)</h4>
                        <p style="margin-bottom: 0.5rem;">To train a full AI TTS model from your voice, you'd need:</p>
                        <ul style="margin: 0; padding-left: 1.25rem;">
                            <li>15-30 minutes of clean audio recordings</li>
                            <li>Services like ElevenLabs, Coqui, or AWS Polly</li>
                            <li>Export as WAV/MP3 and upload</li>
                        </ul>
                        <p style="margin-top: 1rem; margin-bottom: 0; font-size: 0.9rem; color: #666;">
                            <em>This feature isn't implemented yet, but your manual recordings are a great start!</em>
                        </p>
                    </div>
                    
                    <p style="margin: 0;">
                        <strong>Pro Tip:</strong> For now, just keep recording phrases you use often! Each recording helps make the app more authentic.
                    </p>
                </div>
                
                <div style="margin-top: 2rem; display: flex; justify-content: flex-end;">
                    <button onclick="document.getElementById('${modalId}').remove()" style="background: #2d5a27; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 10px; cursor: pointer; font-weight: 600;">
                        Got it!
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }

    startQuiz(phrases) {
        this.renderQuizInterface(phrases);
    }

    renderQuizInterface(phrases) {
        const container = document.getElementById('languageLearningContainer');
        const tribe = this.tribes[this.currentLesson.tribeKey];
        let currentQuestion = 0;
        let score = 0;
        const shuffledPhrases = this.shuffleArray([...phrases]);

        const renderQuestion = () => {
            if (currentQuestion >= shuffledPhrases.length) {
                this.showQuizResults(score, shuffledPhrases.length);
                return;
            }

            const phrase = shuffledPhrases[currentQuestion];
            const options = this.generateOptions(phrase, phrases);
            const progress = ((currentQuestion + 1) / shuffledPhrases.length) * 100;

            const html = `
                <div class="quiz-container-v3">
                    <div class="quiz-header-v3">
                        <div class="quiz-meta-v3">
                            <span class="quiz-tag-v3">${tribe.name} Challenge</span>
                            <h2 class="fw-bold h3">Translate the Phrase</h2>
                        </div>
                        <div class="quiz-stats-v3">
                            <div class="quiz-stat-box">
                                <span class="stat-label-v3">Progress</span>
                                <span class="stat-value-v3">${currentQuestion + 1}/${shuffledPhrases.length}</span>
                            </div>
                            <div class="quiz-stat-box">
                                <span class="stat-label-v3">Score</span>
                                <span class="stat-value-v3">${score * 10}</span>
                            </div>
                        </div>
                    </div>

                    <div class="quiz-progress-bar-v3">
                        <div class="quiz-progress-fill-v3" style="width: ${progress}%"></div>
                    </div>

                    <div class="quiz-main-v3">
                        <div class="question-card-v3">
                            <div class="question-phrase-v3">${phrase.phrase}</div>
                            <div class="question-hint-v3">"${phrase.pronunciation}"</div>
                            <button class="btn-audio-v3" onclick="window.languageLearning.playAudio('${this.escapeForOnclick(phrase.phrase)}', '${this.escapeForOnclick(this.currentLesson.tribeKey)}')">
                                <i class="fas fa-volume-up me-2"></i> Listen
                            </button>
                        </div>

                        <div class="quiz-options-v3">
                            ${options.map((opt, i) => `
                                <button class="quiz-opt-btn-v3" data-answer="${opt === phrase.translations.en}">
                                    <span class="opt-index-v3">${String.fromCharCode(65 + i)}</span>
                                    <span class="opt-text-v3">${opt}</span>
                                    <i class="fas fa-check-circle check-icon"></i>
                                    <i class="fas fa-times-circle cross-icon"></i>
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <style>
                    .quiz-container-v3 {
                        max-width: 800px;
                        margin: 0 auto;
                        animation: fadeIn 0.5s ease;
                    }
                    .quiz-header-v3 {
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-end;
                        margin-bottom: 25px;
                    }
                    .quiz-tag-v3 {
                        display: inline-block;
                        padding: 4px 10px;
                        background: #fdf2e9;
                        color: #863d08;
                        border-radius: 8px;
                        font-weight: 700;
                        font-size: 0.65rem;
                        text-transform: uppercase;
                        margin-bottom: 8px;
                    }
                    .quiz-meta-v3 h2 {
                        font-size: 1.75rem;
                        margin: 0;
                        color: #333;
                    }
                    .quiz-stats-v3 {
                        display: flex;
                        gap: 15px;
                    }
                    .quiz-stat-box {
                        text-align: right;
                    }
                    .stat-label-v3 {
                        display: block;
                        font-size: 0.6rem;
                        color: #aaa;
                        font-weight: 700;
                        text-transform: uppercase;
                    }
                    .stat-value-v3 {
                        font-size: 1.1rem;
                        font-weight: 800;
                        color: #333;
                    }
                    
                    .quiz-progress-bar-v3 {
                        height: 6px;
                        background: #eee;
                        border-radius: 10px;
                        margin-bottom: 30px;
                        overflow: hidden;
                    }
                    .quiz-progress-fill-v3 {
                        height: 100%;
                        background: #2d5a27;
                        transition: width 0.4s ease;
                    }
                    
                    .question-card-v3 {
                        background: white;
                        border-radius: 25px;
                        padding: 40px;
                        text-align: center;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.03);
                        margin-bottom: 30px;
                        border: 1px solid rgba(0,0,0,0.02);
                    }
                    .question-phrase-v3 {
                        font-size: 2.5rem;
                        font-weight: 800;
                        color: #863d08;
                        margin-bottom: 8px;
                    }
                    .question-hint-v3 {
                        font-size: 1.1rem;
                        color: #888;
                        font-style: italic;
                        margin-bottom: 20px;
                    }
                    .btn-audio-v3 {
                        background: #f8f9fa;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 10px;
                        font-weight: 700;
                        color: #863d08;
                        font-size: 0.9rem;
                        transition: all 0.3s ease;
                    }
                    .btn-audio-v3:hover {
                        background: #863d08;
                        color: white;
                    }
                    
                    .quiz-options-v3 {
                        display: grid;
                        grid-template-columns: repeat(2, 1fr);
                        gap: 15px;
                    }
                    .quiz-opt-btn-v3 {
                        background: white;
                        border: 2px solid #eee;
                        border-radius: 15px;
                        padding: 15px 20px;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        position: relative;
                        text-align: left;
                    }
                    .quiz-opt-btn-v3:hover:not(:disabled) {
                        border-color: #863d08;
                        transform: translateY(-3px);
                    }
                    .opt-index-v3 {
                        width: 30px;
                        height: 30px;
                        background: #f8f9fa;
                        border-radius: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 800;
                        color: #aaa;
                        font-size: 0.85rem;
                    }
                    .opt-text-v3 {
                        font-size: 1rem;
                        font-weight: 600;
                        color: #333;
                        flex: 1;
                    }
                    .check-icon, .cross-icon {
                        display: none;
                        font-size: 1.25rem;
                    }
                    
                    .quiz-opt-btn-v3.correct {
                        background: #f0fdf4;
                        border-color: #22c55e;
                    }
                    .quiz-opt-btn-v3.correct .opt-text-v3 { color: #15803d; }
                    .quiz-opt-btn-v3.correct .check-icon { display: block; color: #22c55e; }
                    
                    .quiz-opt-btn-v3.incorrect {
                        background: #fef2f2;
                        border-color: #ef4444;
                    }
                    .quiz-opt-btn-v3.incorrect .opt-text-v3 { color: #b91c1c; }
                    .quiz-opt-btn-v3.incorrect .cross-icon { display: block; color: #ef4444; }
                    
                    @media (max-width: 600px) {
                        .quiz-options-v3 { grid-template-columns: 1fr; }
                    }
                </style>
            `;

            container.innerHTML = html;

            document.querySelectorAll('.quiz-opt-btn-v3').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const optionBtn = e.currentTarget;
                    const isCorrect = optionBtn.dataset.answer === 'true';
                    
                    document.querySelectorAll('.quiz-opt-btn-v3').forEach(opt => {
                        opt.disabled = true;
                        if (opt.dataset.answer === 'true') {
                            opt.classList.add('correct');
                        }
                    });
                    
                    if (isCorrect) {
                        score++;
                        setTimeout(() => {
                            currentQuestion++;
                            renderQuestion();
                        }, 1000);
                    } else {
                        optionBtn.classList.add('incorrect');
                        setTimeout(() => {
                            currentQuestion++;
                            renderQuestion();
                        }, 1800);
                    }
                });
            });
        };

        renderQuestion();
    }

    generateOptions(correctPhrase, allPhrases) {
        const options = [correctPhrase.translations.en];
        const otherPhrases = allPhrases.filter(p => p.translations.en !== correctPhrase.translations.en);
        
        while (options.length < 4 && otherPhrases.length > 0) {
            const randomIndex = Math.floor(Math.random() * otherPhrases.length);
            options.push(otherPhrases[randomIndex].translations.en);
            otherPhrases.splice(randomIndex, 1);
        }

        return this.shuffleArray(options);
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    showQuizResults(score, total) {
        const percentage = Math.round((score / total) * 100);
        const lessonId = `${this.currentLesson.tribeKey}_lesson_${this.currentLesson.lessonIndex}`;
        
        if (!this.userProgress.completedLessons) {
            this.userProgress.completedLessons = [];
        }
        if (!this.userProgress.completedLessons.includes(lessonId)) {
            this.userProgress.completedLessons.push(lessonId);
        }
        
        if (!this.userProgress.scores) {
            this.userProgress.scores = {};
        }
        this.userProgress.scores[lessonId] = Math.max(
            this.userProgress.scores[lessonId] || 0,
            percentage
        );
        
        this.userProgress.totalPoints = (this.userProgress.totalPoints || 0) + score * 10;
        this.saveProgress();
        
        // Award points only for successful quiz completion (70% or higher)
        let pointsAwarded = 0;
        if (window.gamification && percentage >= 70) {
            pointsAwarded = Math.floor(10 + (percentage / 100) * 40); // 10-50 points based on score
            const quizId = `${this.currentLesson.tribeKey}_lesson_${this.currentLesson.lessonIndex}_quiz`;
            window.gamification.addPoints('quiz', pointsAwarded, {
                quizId: quizId,
                lessonId: lessonId,
                quizName: `${this.currentLesson.lesson.title} Quiz`,
                tribe: this.currentLesson.tribeKey,
                lessonTitle: this.currentLesson.lesson.title,
                score: score,
                total: total,
                percentage: percentage
            });
            
            // Bonus points for perfect score
            if (percentage === 100) {
                window.gamification.addPoints('quiz', 20, {
                    quizId: `${quizId}_perfect_bonus`,
                    lessonId: lessonId,
                    quizName: `${this.currentLesson.lesson.title} Perfect Bonus`,
                    tribe: this.currentLesson.tribeKey,
                    lessonTitle: this.currentLesson.lesson.title,
                    percentage: 100
                });
                pointsAwarded += 20;
            }
        }

        const container = document.getElementById('languageLearningContainer');
        const trophyColor = percentage >= 80 ? '#ffd700' : percentage >= 60 ? '#c0c0c0' : '#cd7f32';
        
        const html = `
            <div style="padding: 2rem; max-width: 800px; margin: 0 auto; font-family: Arial, sans-serif;">
                <!-- Results Header -->
                <div style="text-align: center; background: linear-gradient(135deg, #863d08 0%, #a0522d 100%); color: white; padding: 3rem; border-radius: 12px; margin-bottom: 2rem;">
                    <div style="font-size: 4rem; color: ${trophyColor}; margin-bottom: 1rem;">🏆</div>
                    <h2 style="margin: 0; font-size: 2.2rem;">${percentage >= 80 ? 'Excellent!' : percentage >= 60 ? 'Good Job!' : 'Keep Practicing!'}</h2>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Quiz completed for ${this.currentLesson.lesson.title}</p>
                </div>

                <!-- Stats Grid -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 3rem;">
                    <div style="background: white; padding: 2rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 4px solid #4caf50;">
                        <div style="font-size: 2.5rem; font-weight: bold; color: #4caf50;">${score}/${total}</div>
                        <div style="color: #666; margin-top: 0.5rem;">Correct Answers</div>
                    </div>
                    <div style="background: white; padding: 2rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 4px solid #2196f3;">
                        <div style="font-size: 2.5rem; font-weight: bold; color: #2196f3;">${percentage}%</div>
                        <div style="color: #666; margin-top: 0.5rem;">Score</div>
                    </div>
                    <div style="background: white; padding: 2rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 4px solid ${pointsAwarded > 0 ? '#4caf50' : '#ff9800'};">
                        <div style="font-size: 2.5rem; font-weight: bold; color: ${pointsAwarded > 0 ? '#4caf50' : '#ff9800'};">
                            ${pointsAwarded > 0 ? `+${pointsAwarded}` : '0'}
                        </div>
                        <div style="color: #666; margin-top: 0.5rem;">
                            ${pointsAwarded > 0 ? 'Points Earned' : 'No Points (Score < 70%)'}
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <button onclick="startQuiz('${this.currentLesson.tribeKey}', ${this.currentLesson.lessonIndex})" style="
                        background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%); 
                        color: white; 
                        border: none; 
                        padding: 1rem; 
                        border-radius: 8px; 
                        font-weight: bold; 
                        cursor: pointer;
                    ">
                        🔄 Retake Quiz
                    </button>
                    <button onclick="startTribeLearning('${this.currentLesson.tribeKey}')" style="
                        background: linear-gradient(135deg, #863d08 0%, #a0522d 100%); 
                        color: white; 
                        border: none; 
                        padding: 1rem; 
                        border-radius: 8px; 
                        font-weight: bold; 
                        cursor: pointer;
                    ">
                        📚 Back to Lessons
                    </button>
                    <button onclick="window.open('gamification.html', '_blank')" style="
                        background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); 
                        color: white; 
                        border: none; 
                        padding: 1rem; 
                        border-radius: 8px; 
                        font-weight: bold; 
                        cursor: pointer;
                    ">
                        🏆 View Achievements
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    async awardAchievement(name, description, points) {
        const achievements = JSON.parse(localStorage.getItem('userAchievements') || '[]');
        const newAchievement = {
            id: Date.now(),
            type: 'language_learning',
            name: name,
            description: description,
            points: points,
            earnedAt: new Date().toISOString()
        };
        achievements.push(newAchievement);
        localStorage.setItem('userAchievements', JSON.stringify(achievements));
        
        try {
            if (sessionStorage.getItem('user_id')) {
                await fetch('/api/achievements', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        type: 'language_learning',
                        name: name,
                        description: description,
                        points: points
                    })
                });
            }
        } catch (error) {
            console.error('Error syncing achievement to backend:', error);
        }
    }
}

// Test if script loads
console.log('✅ languageLearning.js script loaded successfully');

// Global test functions for debugging
window.testButtonClick = function(tribeKey) {
    console.log('🔧 Test button clicked for tribe:', tribeKey);
    if (window.languageLearning) {
        console.log('✅ window.languageLearning exists, calling startTribeLearning...');
        window.languageLearning.startTribeLearning(tribeKey);
    } else {
        console.error('❌ window.languageLearning not found!');
        alert('Language learning system not initialized. Please refresh the page.');
    }
};

window.testLessonClick = function(tribeKey, lessonIndex) {
    console.log('🔧 Lesson button clicked:', tribeKey, lessonIndex);
    if (window.languageLearning) {
        console.log('✅ window.languageLearning exists, calling startLesson...');
        window.languageLearning.startLesson(tribeKey, lessonIndex);
    } else {
        console.error('❌ window.languageLearning not found!');
        alert('Language learning system not initialized. Please refresh the page.');
    }
};

window.testQuizClick = function(tribeKey, lessonIndex) {
    console.log('🔧 Quiz button clicked:', tribeKey, lessonIndex);
    if (window.languageLearning) {
        console.log('✅ window.languageLearning exists, calling startQuiz...');
        // First start the lesson to set up context, then start quiz
        window.languageLearning.startLesson(tribeKey, lessonIndex);
        // Give it a moment to set up, then start quiz
        setTimeout(() => {
            if (window.languageLearning.currentLesson && window.languageLearning.currentLesson.lesson.phrases) {
                window.languageLearning.startQuiz(window.languageLearning.currentLesson.lesson.phrases);
            } else {
                console.error('❌ Lesson not properly loaded for quiz');
                alert('Unable to start quiz. Please try again.');
            }
        }, 100);
    } else {
        console.error('❌ window.languageLearning not found!');
        alert('Language learning system not initialized. Please refresh the page.');
    }
};

window.testDashboardClick = function() {
    console.log('🔧 Dashboard button clicked');
    if (window.languageLearning) {
        console.log('✅ window.languageLearning exists, calling renderDashboard...');
        window.languageLearning.renderDashboard();
    } else {
        console.error('❌ window.languageLearning not found!');
        alert('Language learning system not initialized. Please refresh the page.');
    }
};

window.testForceLoadData = function() {
    console.log('🔧 Force load data button clicked');
    if (window.languageLearning) {
        console.log('✅ window.languageLearning exists, calling forceLoadData...');
        window.languageLearning.forceLoadData();
    } else {
        console.error('❌ window.languageLearning not found!');
        alert('Language learning system not initialized. Please refresh the page.');
    }
};

// Initialize when DOM is ready
let languageLearning;
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing language learning system...');
    
    // First, test if container exists
    const container = document.getElementById('languageLearningContainer');
    if (!container) {
        console.error('❌ languageLearningContainer not found!');
        return;
    }
    
    console.log('✅ Container found, proceeding with initialization...');
    
    try {
        languageLearning = new LanguageLearningSystem();
        window.languageLearning = languageLearning; // Make it globally accessible
        
        // Global functions are now defined in HTML file
        
        console.log('✅ Language learning system initialized successfully');
        console.log('✅ Global functions set: startTribeLearning, startLesson, startQuiz, renderDashboard');
    } catch (error) {
        console.error('❌ Failed to initialize language learning system:', error);
        
        // Fallback: try to show a basic message
        container.innerHTML = `
            <div style="padding: 2rem; text-align: center; background: #ffe6e6; border: 2px solid #ff4444; margin: 2rem; border-radius: 8px;">
                <h2>❌ Language Learning System Error</h2>
                <p>There was an error loading the language learning system.</p>
                <p><strong>Error:</strong> ${error.message}</p>
                <button onclick="location.reload()" style="padding: 1rem 2rem; background: #863d08; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 0.5rem;">
                    Refresh Page
                </button>
                <button onclick="window.open('minimal-language-learning.html', '_blank')" style="padding: 1rem 2rem; background: #4caf50; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 0.5rem;">
                    Open Simple Version
                </button>
            </div>
        `;
    }
});

// Fallback initialization after 2 seconds
setTimeout(() => {
    if (!window.languageLearning) {
        console.log('🔄 Fallback initialization attempt...');
        const container = document.getElementById('languageLearningContainer');
        if (container && container.innerHTML.includes('Loading language learning system')) {
            try {
                languageLearning = new LanguageLearningSystem();
                window.languageLearning = languageLearning;
                
                // Global functions are now defined in HTML file
                
                console.log('✅ Fallback initialization successful');
                console.log('✅ Global functions set in fallback');
            } catch (error) {
                console.error('❌ Fallback initialization failed:', error);
            }
        }
    }
}, 2000);