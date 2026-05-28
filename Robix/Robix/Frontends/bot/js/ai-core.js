/**
 * AI Core Logic - Shared across Assistant page and Chatbot widget
 * Handles unified history storage, API communication, and sync
 */

const AICore = {
    STORAGE_KEY: 'cultia_ai_history',
    SYNC_KEY: 'cultia_ai_update',

    /**
     * Get unified conversation history
     */
    getHistory() {
        try {
            const saved = localStorage.getItem(this.STORAGE_KEY);
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            console.error('Error loading AI history:', e);
            return [];
        }
    },

    /**
     * Save unified conversation history
     */
    saveHistory(history) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(history));
            localStorage.setItem(this.SYNC_KEY, Date.now());
        } catch (e) {
            console.error('Error saving AI history:', e);
        }
    },

    /**
     * Add a message to the unified history
     */
    addMessage(role, content, source = 'local') {
        const history = this.getHistory();
        const newMessage = {
            id: Date.now(),
            role: role,
            content: content,
            timestamp: new Date().toISOString(),
            source: source
        };
        history.push(newMessage);
        this.saveHistory(history);
        return newMessage;
    },

    /**
     * Clear unified history
     */
    clearHistory() {
        this.saveHistory([]);
    },

    /**
     * Generate bot response from API
     */
    async generateResponse(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            return {
                response: data.response || "I'm sorry, I couldn't process that.",
                source: data.source || 'local'
            };
        } catch (error) {
            console.error('AI Response error:', error);
            return {
                response: "I'm having trouble connecting right now. Please try again later.",
                source: 'system'
            };
        }
    },

    /**
     * Format time for display
     */
    formatTime(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const diff = (now - date) / 1000;

        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }
};

window.AICore = AICore;
