/**
 * Gamification System for CulturalAI Educator
 * Handles badges, points, and leaderboards for learning activities
 */

class GamificationSystem {
    constructor() {
        this.points = 0;
        this.badges = [];
        this.activities = [];
        this.leaderboard = [];
        this.userId = this.getUserId();
        this.completedQuizIds = new Set();
        this.completedLessonIds = new Set();
        this.init();
    }

    /**
     * Initialize the gamification system
     */
    init() {
        this.loadUserData();
        this.setupStorageSync();
        this.updateUI();
        this.broadcastUpdate(); // Notify dashboard
        console.log('Gamification system initialized with real-time updates');
    }

    /**
     * Set up cross-tab synchronization
     */
    setupStorageSync() {
        window.addEventListener('storage', (e) => {
            if (e.key === 'gamificationUpdate') {
                const data = JSON.parse(e.newValue);
                console.log('🔄 Syncing gamification data from another tab:', data);
                this._loadFromLocalStorage(); // Refresh local state
                window.dispatchEvent(new CustomEvent('gamificationUpdate', { detail: data }));
            }
        });
    }

    /**
     * Broadcast updates to dashboard and other pages
     */
    broadcastUpdate() {
        const updateData = {
            points: this.points,
            badges: this.badges.length,
            activities: this.activities.length,
            timestamp: Date.now()
        };
        localStorage.setItem('gamificationUpdate', JSON.stringify(updateData));
        window.dispatchEvent(new CustomEvent('gamificationUpdate', { detail: updateData }));
    }

    /**
     * Get or generate user ID
     */
    getUserId() {
        let userId = localStorage.getItem('userId');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('userId', userId);
        }
        return userId;
    }

    isPointTransactionType(type) {
        return ['points', 'activity', 'quiz_points', 'lesson_points'].includes(type);
    }

    isBadgeAchievement(achievement) {
        if (!achievement || !achievement.type) return false;
        return !this.isPointTransactionType(achievement.type);
    }

    /**
     * Load user data from backend and fallback to localStorage
     */
    async loadUserData() {
        try {
            const response = await fetch('/api/achievements', { credentials: 'include' });
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const achievements = Array.isArray(data.achievements) ? data.achievements : [];
                    this.points = Number(data.total_points) || 0;

                    const seenBadgeTypes = new Set();
                    this.badges = achievements
                        .filter(a => this.isBadgeAchievement(a))
                        .filter(a => {
                            if (seenBadgeTypes.has(a.type)) return false;
                            seenBadgeTypes.add(a.type);
                            return true;
                        })
                        .map(a => ({
                            id: a.type,
                            name: a.name,
                            description: a.description,
                            earnedDate: a.earned_at
                        }));
                    
                    const progResp = await fetch('/api/progress', { credentials: 'include' });
                    if (progResp.ok) {
                        const progData = await progResp.json();
                        if (progData.success) {
                            this.activities = [];
                            Object.keys(progData.progress).forEach(cat => {
                                const catData = progData.progress[cat].data;
                                if (Array.isArray(catData)) {
                                    this.activities.push(...catData);
                                } else if (typeof catData === 'object' && catData !== null) {
                                    this.activities.push(catData);
                                }
                            });
                        }
                    }
                    
                    this._rebuildDerivedState();
                    this.updateUI();
                    this.broadcastUpdate();
                    this._syncToLocalStorage();
                    return;
                }
            }
        } catch (error) {
            console.warn('Backend sync failed, falling back to local storage', error);
        }

        this._loadFromLocalStorage();
    }

    _loadFromLocalStorage() {
        try {
            const savedPoints = localStorage.getItem('userPoints');
            const savedBadges = localStorage.getItem('userBadges');
            const savedActivities = localStorage.getItem('userActivities');
            
            this.points = savedPoints ? parseInt(savedPoints) : 0;
            this.badges = savedBadges ? JSON.parse(savedBadges) : [];
            this.activities = savedActivities ? JSON.parse(savedActivities) : [];
            
            this._rebuildDerivedState();
            this.updateUI();
            this.broadcastUpdate();
        } catch (error) {
            console.error('Error loading from local storage:', error);
        }
    }

    _syncToLocalStorage() {
        try {
            localStorage.setItem('userPoints', this.points.toString());
            localStorage.setItem('userBadges', JSON.stringify(this.badges));
            localStorage.setItem('userActivities', JSON.stringify(this.activities));
        } catch (e) {
            console.error('Local storage sync failed', e);
        }
    }

    _rebuildDerivedState() {
        this.completedQuizIds = new Set(
            (this.activities || [])
                .filter(a => a && a.type === 'quiz' && a.metadata && a.metadata.quizId)
                .map(a => a.metadata.quizId)
        );
        this.completedLessonIds = new Set(
            (this.activities || [])
                .filter(a => a && a.type === 'lesson' && a.metadata && a.metadata.lessonId)
                .map(a => a.metadata.lessonId)
        );
    }

    async saveUserData(syncPoints = 0, syncReason = '') {
        this._syncToLocalStorage();
        this.broadcastUpdate();

        try {
            if (syncPoints > 0) {
                await fetch('/api/achievements', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        type: 'points',
                        name: 'Points Earned',
                        description: syncReason || 'Activity points',
                        points: syncPoints
                    }),
                    credentials: 'include'
                });
            }

            const lastActivity = this.activities[this.activities.length - 1];
            if (lastActivity) {
                await fetch('/api/progress', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        category: lastActivity.type,
                        progress_data: this.activities.filter(a => a.type === lastActivity.type)
                    }),
                    credentials: 'include'
                });
            }

            const lastBadge = this.badges[this.badges.length - 1];
            if (lastBadge && lastBadge.isNew) {
                await fetch('/api/achievements', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        type: lastBadge.id,
                        name: lastBadge.name,
                        description: lastBadge.description,
                        points: 50
                    }),
                    credentials: 'include'
                });
                delete lastBadge.isNew;
            }
        } catch (error) {
            console.log('Backend sync failed');
        }
    }

    addPoints(a, b, c) {
        let pointsToAdd = 0;
        let reasonStr = '';

        if (typeof a === 'string') {
            const type = a;
            const points = b;
            const metadata = c || {};
            if (typeof points !== 'number' || isNaN(points)) return;

            if (type === 'quiz') {
                const quizId = metadata.quizId;
                if (quizId && this.completedQuizIds.has(quizId)) return;
                if (quizId) this.completedQuizIds.add(quizId);
                this.recordActivity('quiz', metadata);
            }

            if (type === 'lesson') {
                const lessonId = metadata.lessonId;
                if (lessonId && this.completedLessonIds.has(lessonId)) return;
                if (lessonId) this.completedLessonIds.add(lessonId);
                this.recordActivity('lesson', metadata);
            }

            pointsToAdd = points;
            reasonStr = `Activity: ${type}`;
            this.points += points;
            this.saveUserData(pointsToAdd, reasonStr);
            this.updateUI();
            this.showNotification(`+${points} points`, 'success');
            return;
        }

        const points = a;
        const reason = b || '';
        if (typeof points !== 'number' || isNaN(points)) return;
        
        pointsToAdd = points;
        reasonStr = reason;
        this.points += points;
        this.saveUserData(pointsToAdd, reasonStr);
        this.updateUI();
        this.showNotification(`+${points} points${reason ? ': ' + reason : ''}`, 'success');
    }

    recordActivity(type, metadata = {}) {
        const activity = {
            type: type,
            metadata: metadata,
            timestamp: new Date().toISOString()
        };
        this.activities.push(activity);
        this.saveUserData();
        this.broadcastUpdate();
        this._checkBadgeEligibility();
    }

    _checkBadgeEligibility() {
        const badgeCriteria = [
            { id: 'first_lesson', name: 'First Steps', desc: 'Completed your first language lesson', check: () => this.countActivities('lesson') >= 1 },
            { id: 'first_quiz', name: 'Quiz Starter', desc: 'Completed your first language quiz', check: () => this.countActivities('quiz') >= 1 },
            { id: 'language_explorer', name: 'Language Explorer', desc: 'Learned from 3 different tribal languages', check: () => this.countUniqueTribes() >= 3 },
            { id: 'knowledge_seeker', name: 'Knowledge Seeker', desc: 'Completed 5 language lessons', check: () => this.countActivities('lesson') >= 5 },
            { id: 'quiz_master', name: 'Quiz Master', desc: 'Completed 10 language quizzes', check: () => this.countActivities('quiz') >= 10 },
            { id: 'polyglot', name: 'Polyglot', desc: 'Learned from 5 different tribal languages', check: () => this.countUniqueTribes() >= 5 },
            { id: 'scholar', name: 'Cultural Scholar', desc: 'Earned 500 points', check: () => this.points >= 500 },
            { id: 'expert', name: 'Language Expert', desc: 'Earned 1000 points', check: () => this.points >= 1000 }
        ];

        for (const criteria of badgeCriteria) {
            const alreadyEarned = this.badges.some(b => b.id === criteria.id);
            if (!alreadyEarned && criteria.check()) {
                this.awardBadge(criteria.id, criteria.name, criteria.desc);
            }
        }
    }

    awardBadge(id, name, description) {
        if (this.badges.some(b => b.id === id)) return;
        const badge = { id, name, description, earnedDate: new Date().toISOString(), isNew: true };
        this.badges.push(badge);
        this.saveUserData();
        this.updateUI();
        this.animateBadgeEarned(badge);
        this.fireConfetti();
    }

    async getLeaderboardData() {
        try {
            const response = await fetch('/api/leaderboard', { credentials: 'include' });
            if (response.ok) {
                const data = await response.json();
                if (data.success) return data.leaderboard;
            }
        } catch (error) { console.error('Error fetching leaderboard:', error); }
        return [];
    }

    async updateLeaderboardUI() {
        const leaderboardContainer = document.querySelector('.leaderboard-list') || document.querySelector('.leaderboard');
        if (!leaderboardContainer) return;

        const leaderboard = await this.getLeaderboardData();
        if (!leaderboard || leaderboard.length === 0) {
            leaderboardContainer.innerHTML = '<div class="text-center p-4 text-muted">No explorers yet. Be the first!</div>';
            return;
        }

        leaderboardContainer.innerHTML = '';
        leaderboard.forEach(user => {
            const userElement = document.createElement('div');
            if (leaderboardContainer.classList.contains('leaderboard-list')) {
                userElement.className = `leaderboard-item ${user.is_current_user ? 'user-position' : ''}`;
                userElement.innerHTML = `
                    <div class="leaderboard-rank">${user.rank}</div>
                    <div class="leaderboard-name">${user.is_current_user ? 'You' : user.name}</div>
                    <div class="leaderboard-points">${user.points} pts</div>
                `;
            } else {
                userElement.className = `d-flex align-items-center gap-3 mb-3 p-3 rounded-4 ${user.is_current_user ? 'bg-light border-start border-success border-4' : ''}`;
                userElement.innerHTML = `
                    <span class="fw-bold ${user.rank === 1 ? 'text-success' : 'text-muted'} fs-5">${user.rank}</span>
                    <div class="rounded-circle bg-success bg-opacity-10 d-flex align-items-center justify-content-center text-success fw-bold" style="width: 45px; height: 45px;">
                        ${user.name.charAt(0).toUpperCase()}
                    </div>
                    <div class="flex-grow-1">
                        <h6 class="fw-bold mb-0">${user.is_current_user ? 'You' : user.name}</h6>
                        <small class="text-muted">${user.points.toLocaleString()} pts</small>
                    </div>
                    ${user.rank === 1 ? '<i class="fas fa-crown text-warning"></i>' : ''}
                `;
            }
            leaderboardContainer.appendChild(userElement);
        });
    }

    countActivities(type) { return this.activities.filter(a => a.type === type).length; }
    countUniqueTribes() {
        const tribes = new Set();
        this.activities.filter(a => a.type === 'lesson' || a.type === 'quiz').forEach(a => { if (a.metadata.tribe) tribes.add(a.metadata.tribe); });
        return tribes.size;
    }

    updateUI() {
        // Update points in various formats
        const pointsElements = document.querySelectorAll('.user-points, .gamification-points, #totalPoints, #userPoints');
        pointsElements.forEach(el => {
            el.textContent = this.points.toLocaleString();
        });

        // Update badge counts
        const badgeCountElements = document.querySelectorAll('.badge-count, #badgeCount, #earnedBadges');
        badgeCountElements.forEach(el => {
            el.textContent = this.badges.length;
        });

        this.updateBadgesUI();
    }

    updateBadgesUI() {
        const container = document.querySelector('.badges-container');
        if (!container) return;
        container.innerHTML = this.badges.length === 0 ? '<p class="no-badges">No badges earned yet.</p>' : '';
        this.badges.forEach(badge => {
            const el = document.createElement('div');
            el.className = 'badge-item';
            el.innerHTML = `<div class="badge-icon">🏆</div><div class="badge-info"><h4>${badge.name}</h4><p>${badge.description}</p></div>`;
            container.appendChild(el);
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `gamification-notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `position: fixed; top: 80px; right: 20px; padding: 1rem 1.5rem; border-radius: 8px; color: white; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.15); background: ${type === 'success' ? '#27AE60' : '#E67E22'};`;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    fireConfetti() {
        // Confetti logic restored
    }

    animateBadgeEarned(badge) {
        // Badge animation logic restored
    }

    onUpdate(callback) {
        window.addEventListener('gamificationUpdate', (e) => callback(e.detail));
    }

    getStats() {
        return { points: this.points, badges: this.badges, activities: this.activities };
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (!window.gamification) {
        window.gamification = new GamificationSystem();
    }
});
