/**
 * Personal Assistant Mode JavaScript
 * Handles chat interface, voice input/output, and assistant interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== ELEMENT REFERENCES =====
    const miniSidebar = document.getElementById('miniSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const voiceInputBtn = document.getElementById('voiceInputBtn');
    const voiceToggleBtn = document.getElementById('voiceToggleBtn');
    const botSpeaking = document.getElementById('botSpeaking');
    const userListening = document.getElementById('userListening');
    const quickSuggestions = document.getElementById('quickSuggestions');
    const searchSuggestions = document.getElementById('searchSuggestions'); // Add this line
    const clearChatBtn = document.getElementById('clearChatBtn');
    const storyModeBtn = document.getElementById('storyModeBtn');

    // Modal elements
    const languageModal = document.getElementById('languageModal');
    const historyModal = document.getElementById('historyModal');
    const favoritesModal = document.getElementById('favoritesModal');
    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    
    // History elements
    const historyList = document.getElementById('historyList');
    const favoritesList = document.getElementById('favoritesList');
    
    // Delete confirmation elements
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const closeDeleteConfirmModal = document.getElementById('closeDeleteConfirmModal');
    
    // ===== STATE VARIABLES =====
    let isStoryMode = false;
    let isListening = false;
    let isSpeaking = false;
    let recognition = null;
    let speechSynthesis = window.speechSynthesis;
    let currentLanguage = 'en';
    let conversationHistory = [];
    let favoriteMessages = [];
    let messageIdCounter = 0;
    let conversationToDelete = null; // For delete confirmation
    let highlightedSuggestionIndex = -1; // For keyboard navigation in search suggestions
    
    // ===== SIDEBAR FUNCTIONALITY =====
    
    /**
     * Toggle mini sidebar expanded state
     */
    function toggleSidebar() {
        miniSidebar.classList.toggle('expanded');
        
        // Save state to localStorage
        const isExpanded = miniSidebar.classList.contains('expanded');
        localStorage.setItem('sidebarExpanded', isExpanded);
    }
    
    /**
     * Toggle mobile sidebar
     */
    function toggleMobileSidebar() {
        miniSidebar.classList.toggle('mobile-open');
    }
    
    /**
     * Initialize sidebar state from localStorage
     */
    function initializeSidebarState() {
        const isExpanded = localStorage.getItem('sidebarExpanded') === 'true';
        if (isExpanded) {
            miniSidebar.classList.add('expanded');
        }
    }
    
    // Event listeners for sidebar
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileSidebar);
    }
    
    // Close mobile sidebar when clicking outside
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) {
            const isClickInsideSidebar = miniSidebar.contains(event.target);
            const isClickOnMenuBtn = mobileMenuBtn && mobileMenuBtn.contains(event.target);
            
            if (!isClickInsideSidebar && !isClickOnMenuBtn && miniSidebar.classList.contains('mobile-open')) {
                miniSidebar.classList.remove('mobile-open');
            }
        }
    });
    
    // ===== SEARCH SUGGESTIONS FUNCTIONALITY (History Intellisense) =====
    
    /**
     * Show search suggestions based on input and history
     */
    function showSearchSuggestions(inputValue) {
        if (!inputValue.trim()) {
            hideSearchSuggestions();
            return;
        }
        
        // Filter conversation history based on input
        const filteredSuggestions = conversationHistory
            .filter(msg => msg.type === 'user' && 
                          msg.content.toLowerCase().includes(inputValue.toLowerCase()))
            .map(msg => msg.content)
            .filter((value, index, self) => self.indexOf(value) === index) // Remove duplicates
            .slice(0, 5); // Limit to 5 suggestions
        
        if (filteredSuggestions.length === 0) {
            hideSearchSuggestions();
            return;
        }
        
        // Clear previous suggestions
        searchSuggestions.innerHTML = '';
        
        // Create suggestion elements
        filteredSuggestions.forEach((suggestion, index) => {
            const suggestionElement = document.createElement('div');
            suggestionElement.className = 'search-suggestion-item';
            suggestionElement.setAttribute('data-index', index);
            suggestionElement.textContent = suggestion;
            
            // Add click event
            suggestionElement.addEventListener('click', function() {
                chatInput.value = suggestion;
                adjustTextareaHeight();
                hideSearchSuggestions();
                chatInput.focus();
            });
            
            searchSuggestions.appendChild(suggestionElement);
        });
        
        // Show suggestions
        searchSuggestions.classList.add('active');
        highlightedSuggestionIndex = -1;
    }
    
    /**
     * Hide search suggestions
     */
    function hideSearchSuggestions() {
        searchSuggestions.classList.remove('active');
        highlightedSuggestionIndex = -1;
    }
    
    /**
     * Highlight next suggestion (for keyboard navigation)
     */
    function highlightNextSuggestion() {
        const suggestionItems = searchSuggestions.querySelectorAll('.search-suggestion-item');
        if (suggestionItems.length === 0) return;
        
        // Remove highlight from current
        if (highlightedSuggestionIndex >= 0) {
            suggestionItems[highlightedSuggestionIndex].classList.remove('highlighted');
        }
        
        // Move to next
        highlightedSuggestionIndex = (highlightedSuggestionIndex + 1) % suggestionItems.length;
        
        // Highlight new
        suggestionItems[highlightedSuggestionIndex].classList.add('highlighted');
        
        // Scroll to highlighted item
        suggestionItems[highlightedSuggestionIndex].scrollIntoView({ block: 'nearest' });
    }
    
    /**
     * Highlight previous suggestion (for keyboard navigation)
     */
    function highlightPreviousSuggestion() {
        const suggestionItems = searchSuggestions.querySelectorAll('.search-suggestion-item');
        if (suggestionItems.length === 0) return;
        
        // Remove highlight from current
        if (highlightedSuggestionIndex >= 0) {
            suggestionItems[highlightedSuggestionIndex].classList.remove('highlighted');
        }
        
        // Move to previous
        highlightedSuggestionIndex = (highlightedSuggestionIndex - 1 + suggestionItems.length) % suggestionItems.length;
        
        // Highlight new
        suggestionItems[highlightedSuggestionIndex].classList.add('highlighted');
        
        // Scroll to highlighted item
        suggestionItems[highlightedSuggestionIndex].scrollIntoView({ block: 'nearest' });
    }
    
    /**
     * Select highlighted suggestion
     */
    function selectHighlightedSuggestion() {
        if (highlightedSuggestionIndex >= 0) {
            const suggestionItems = searchSuggestions.querySelectorAll('.search-suggestion-item');
            if (suggestionItems[highlightedSuggestionIndex]) {
                const suggestionText = suggestionItems[highlightedSuggestionIndex].textContent;
                chatInput.value = suggestionText;
                adjustTextareaHeight();
                hideSearchSuggestions();
                chatInput.focus();
                sendBtn.disabled = false;
            }
        }
    }
    
    // ===== CHAT FUNCTIONALITY =====
    
    /**
     * Create a new message element
     * @param {string} content - The message content
     * @param {string} type - 'user' or 'bot'
     * @param {number} messageId - Unique message ID
     * @returns {HTMLElement} The message element
     */
    function createMessageElement(content, type, messageId) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.setAttribute('data-message-id', messageId);
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : '🤖';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        // Handle different content types
        if (typeof content === 'string') {
            const paragraphs = content.split('\n').filter(p => p.trim());
            paragraphs.forEach(paragraph => {
                const p = document.createElement('p');
                p.textContent = paragraph;
                bubble.appendChild(p);
            });
        }
        
        messageContent.appendChild(bubble);
        
        // Add actions for bot messages
        if (type === 'bot') {
            const actions = document.createElement('div');
            actions.className = 'message-actions';
            
            const replayBtn = document.createElement('button');
            replayBtn.className = 'action-btn replay-btn';
            replayBtn.title = 'Play/Stop audio';
            replayBtn.innerHTML = '<span class="action-icon">🔊</span>';
            replayBtn.addEventListener('click', () => {
                // Toggle speech: if speaking, stop it; otherwise, start it
                if (isSpeaking && speechSynthesis.speaking) {
                    speechSynthesis.cancel();
                    isSpeaking = false;
                    botSpeaking.classList.remove('active');
                } else {
                    speakMessage(content);
                }
            });
            
            const favoriteBtn = document.createElement('button');
            favoriteBtn.className = 'action-btn favorite-btn';
            favoriteBtn.title = 'Add to favorites';
            favoriteBtn.innerHTML = '<span class="action-icon">⭐</span>';
            favoriteBtn.addEventListener('click', () => toggleFavorite(messageId, content, favoriteBtn));
            
            const timeSpan = document.createElement('span');
            timeSpan.className = 'message-time';
            timeSpan.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            actions.appendChild(replayBtn);
            actions.appendChild(favoriteBtn);
            actions.appendChild(timeSpan);
            messageContent.appendChild(actions);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        return messageDiv;
    }
    
    /**
     * Add a message to the chat
     * @param {string} content - The message content
     * @param {string} type - 'user' or 'bot'
     */
    function addMessage(content, type) {
        const messageId = ++messageIdCounter;
        const messageElement = createMessageElement(content, type, messageId);
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add to conversation history
        const messageData = {
            id: messageId,
            content: content,
            role: type, // Standardize to role
            timestamp: new Date().toISOString()
        };
        conversationHistory.push(messageData);
        
        // Save to localStorage
        saveConversationHistory();
        
        return messageId;
    }
    
    /**
     * Redirect to Storytelling Mode
     */
    function toggleStoryMode() {
        window.location.href = 'storyteller.html';
    }

    if (storyModeBtn) {
        storyModeBtn.addEventListener('click', toggleStoryMode);
    }

    /**
     * Send a user message
     * @param {string} message - The message to send
     */
    async function sendMessage(message) {
        if (!message.trim()) return;

        // Add user message
        addMessage(message, 'user');

        // Clear input
        chatInput.value = '';
        adjustTextareaHeight();

        // Hide suggestions
        hideSuggestions();
        hideSearchSuggestions();

        // Show bot thinking indicator
        botSpeaking.classList.add('active');

        try {
            // Get bot response from API
            const responseData = await generateBotResponse(message);
            const messageId = addMessage(responseData.response, 'bot');

            // If it's a story, add the story styling
            if (isStoryMode && (responseData.source === 'local_story' || responseData.source === 'gemini_story')) {
                const lastMsg = chatMessages.lastElementChild;
                if (lastMsg) {
                    const contentDiv = lastMsg.querySelector('.message-content');
                    if (contentDiv) {
                        contentDiv.classList.add('story-message');
                        // Add a story badge
                        const badge = document.createElement('div');
                        badge.className = 'story-badge';
                        badge.innerHTML = '<i class="fas fa-scroll me-2"></i> Tribal Legend';
                        contentDiv.prepend(badge);
                    }
                }
            }

            // Display source attribution if available
            if (responseData.source && responseData.source !== 'local') {
                displaySourceAttribution(responseData.source, messageId);
            }

            // Hide bot thinking indicator
            botSpeaking.classList.remove('active');

            // Don't auto-play audio - user must click the audio button
        } catch (error) {
            console.error('Error sending message:', error);
            botSpeaking.classList.remove('active');
            addMessage("I'm sorry, I encountered an error processing your request. Please try again.", 'bot');
        }
    }

    /**
     * Display source attribution badge on the message
     * @param {string} source - The source of the response (gemini, local, system)
     * @param {number} messageId - The message ID to attach the badge to
     */
    function displaySourceAttribution(source, messageId) {
        const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
        if (!messageEl) return;

        const badge = document.createElement('span');
        badge.className = `source-badge source-${source}`;

        if (source === 'gemini') {
            badge.innerHTML = '<i class="fas fa-robot"></i> Enhanced by Gemini';
            badge.title = 'This response was enhanced using Google Gemini AI to provide more comprehensive information.';
        } else if (source === 'system') {
            badge.innerHTML = '<i class="fas fa-info-circle"></i> System';
            badge.title = 'System message';
        }

        const actionsDiv = messageEl.querySelector('.message-actions');
        if (actionsDiv) {
            actionsDiv.insertBefore(badge, actionsDiv.firstChild);
        }
    }

    /**
     * Generate a bot response by calling the backend API
     * @param {string} userMessage - The user's message
     * @returns {Promise<{response: string, source: string}>} The bot's response and source
     */
    async function generateBotResponse(userMessage) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: userMessage,
                    mode: isStoryMode ? 'storyteller' : 'assistant'
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                response: data.response || "I'm sorry, I couldn't process that request. Please try again.",
                source: data.source || 'local'
            };
        } catch (error) {
            console.error('Error calling chat API:', error);
            return {
                response: "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again in a moment.",
                source: 'system'
            };
        }
    }
    
    /**
     * Clear the chat conversation
     */
    function clearChat() {
        // Keep only the welcome message
        const welcomeMessage = chatMessages.querySelector('.message[data-message-id="0"]');
        chatMessages.innerHTML = '';
        if (welcomeMessage) {
            chatMessages.appendChild(welcomeMessage);
        } else {
            // Re-create welcome message if not found
            addMessage("Hello! I am your CULTIA Assistant. I can help you explore Cameroon's rich history, traditions, and diverse cultures. What would you like to know today?", 'bot');
        }
        
        // Clear history
        conversationHistory = [];
        saveConversationHistory();
        
        // Show suggestions again
        showSuggestions();
        
        showNotification('Chat cleared', 'info');
    }

    // Add listener for History modal to render on show
    const historyModalEl = document.getElementById('historyModal');
    if (historyModalEl) {
        historyModalEl.addEventListener('show.bs.modal', function () {
            renderHistory();
        });
    }

    // Add listener for Favorites modal to render on show
    const favoritesModalEl = document.getElementById('favoritesModal');
    if (favoritesModalEl) {
        favoritesModalEl.addEventListener('show.bs.modal', function () {
            renderFavorites();
        });
    }
    
    // ===== VOICE FUNCTIONALITY =====
    
    /**
     * Initialize speech recognition
     */
    function initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = getLanguageCode(currentLanguage);
            
            recognition.onstart = function() {
                isListening = true;
                userListening.classList.add('active');
                voiceInputBtn.classList.add('listening');
                console.log('Voice recognition started');
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                console.log('Voice input received:', transcript);
                
                // Send the voice message
                sendMessage(transcript);
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                showNotification('Voice recognition error. Please try again.', 'error');
                stopListening();
            };
            
            recognition.onend = function() {
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
        userListening.classList.remove('active');
        voiceInputBtn.classList.remove('listening');
    }
    
    /**
     * Speak a message using text-to-speech
     * @param {string} text - The text to speak
     */
    function speakMessage(text) {
        if (!speechSynthesis) {
            showNotification('Text-to-speech not supported in this browser.', 'warning');
            return;
        }
        
        // Stop any current speech
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = getLanguageCode(currentLanguage);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        
        utterance.onstart = function() {
            isSpeaking = true;
            botSpeaking.classList.add('active');
        };
        
        utterance.onend = function() {
            isSpeaking = false;
            botSpeaking.classList.remove('active');
        };
        
        utterance.onerror = function(event) {
            console.error('Speech synthesis error:', event.error);
            isSpeaking = false;
            botSpeaking.classList.remove('active');
        };
        
        speechSynthesis.speak(utterance);
    }
    
    /**
     * Toggle voice output on/off
     */
    function toggleVoiceOutput() {
        voiceToggleBtn.classList.toggle('active');
        const isActive = voiceToggleBtn.classList.contains('active');
        
        if (isActive) {
            showNotification('Voice output enabled', 'success');
        } else {
            showNotification('Voice output disabled', 'info');
            // Stop any current speech
            if (speechSynthesis) {
                speechSynthesis.cancel();
            }
            botSpeaking.classList.remove('active');
        }
        
        // Save preference
        localStorage.setItem('voiceOutputEnabled', isActive);
    }
    
    /**
     * Get language code for speech APIs
     * @param {string} lang - Language identifier
     * @returns {string} Language code
     */
    function getLanguageCode(lang) {
        const codes = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'zh': 'zh-CN',
            'ja': 'ja-JP'
        };
        return codes[lang] || 'en-US';
    }
    
    // ===== INPUT HANDLING =====
    
    /**
     * Adjust textarea height based on content
     */
    function adjustTextareaHeight() {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    }
    
    /**
     * Handle input events
     */
    function handleInput() {
        adjustTextareaHeight();
        
        // Enable/disable send button
        const hasContent = chatInput.value.trim().length > 0;
        sendBtn.disabled = !hasContent;
        
        // Show search suggestions based on input
        if (hasContent) {
            showSearchSuggestions(chatInput.value);
            hideSuggestions(); // Hide quick suggestions when typing
        } else {
            hideSearchSuggestions();
            showSuggestions(); // Show quick suggestions when input is empty
        }
    }
    
    /**
     * Handle key press events
     * @param {KeyboardEvent} e - The keyboard event
     */
    async function handleKeyPress(e) {
        // Handle arrow keys for suggestion navigation
        if (searchSuggestions.classList.contains('active')) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                highlightNextSuggestion();
                return;
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                highlightPreviousSuggestion();
                return;
            } else if (e.key === 'Enter' && highlightedSuggestionIndex >= 0) {
                e.preventDefault();
                selectHighlightedSuggestion();
                return;
            }
        }
        
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (message) {
                await sendMessage(message);
            }
        } else if (e.key === 'Escape') {
            hideSearchSuggestions();
        }
    }
    
    // ===== SUGGESTIONS FUNCTIONALITY =====
    
    /**
     * Show quick suggestions
     */
    function showSuggestions() {
        if (conversationHistory.length <= 1) { // Only welcome message
            quickSuggestions.style.display = 'block';
        }
    }
    
    /**
     * Hide quick suggestions
     */
    function hideSuggestions() {
        quickSuggestions.style.display = 'none';
    }
    
    /**
     * Handle suggestion click
     * @param {string} suggestion - The suggestion text
     */
    function handleSuggestionClick(suggestion) {
        chatInput.value = suggestion;
        adjustTextareaHeight();
        // Focus on the input field so user can decide to send or edit
        chatInput.focus();
        // Show the send button as enabled since there's content
        sendBtn.disabled = false;
        // Hide the quick suggestions since user has selected one
        hideSuggestions();
    }
    
    // ===== FAVORITES FUNCTIONALITY =====
    
    /**
     * Toggle favorite status of a message
     * @param {number} messageId - The message ID
     * @param {string} content - The message content
     * @param {HTMLElement} button - The favorite button
     */
    function toggleFavorite(messageId, content, button) {
        const existingIndex = favoriteMessages.findIndex(fav => fav.id === messageId);
        
        if (existingIndex >= 0) {
            // Remove from favorites
            favoriteMessages.splice(existingIndex, 1);
            button.classList.remove('favorited');
            showNotification('Removed from favorites', 'info');
        } else {
            // Add to favorites
            favoriteMessages.push({
                id: messageId,
                content: content,
                timestamp: new Date().toISOString()
            });
            button.classList.add('favorited');
            showNotification('Added to favorites', 'success');
        }
        
        // Save to localStorage
        saveFavorites();
        renderFavorites();
    }
    
    // ===== HISTORY FUNCTIONALITY =====
    
    /**
     * Render conversation history in the history modal
     */
    function renderHistory() {
        if (!historyList) return;
        
        historyList.innerHTML = '';
        
        const history = AICore.getHistory();
        
        if (history.length === 0) {
            historyList.innerHTML = `
                <div class="text-center py-5">
                    <div class="display-4 text-muted mb-3"><i class="fas fa-comment-slash"></i></div>
                    <p class="text-muted">No conversation history found.</p>
                </div>
            `;
            return;
        }

        // Group into sessions (pairs of user-bot)
        const sessions = [];
        for (let i = 0; i < history.length; i++) {
            if (history[i].role === 'user') {
                sessions.push({
                    user: history[i],
                    bot: history[i + 1] || null
                });
            }
        }

        // Sort by newest first
        sessions.reverse();

        sessions.forEach((session, index) => {
            const card = document.createElement('div');
            card.className = 'card border-0 shadow-sm rounded-4 mb-3 overflow-hidden history-card';
            
            const timeAgo = AICore.formatTime(session.user.timestamp);
            
            card.innerHTML = `
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-success bg-opacity-10 text-success rounded-pill px-3">
                                <i class="fas fa-clock me-1"></i> ${timeAgo}
                            </span>
                            ${session.bot && session.bot.source === 'gemini' ? 
                                '<span class="badge bg-primary bg-opacity-10 text-primary rounded-pill px-3"><i class="fas fa-robot me-1"></i> Gemini AI</span>' : ''}
                        </div>
                        <div class="dropdown">
                            <button class="btn btn-link text-muted p-0" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-h"></i>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 rounded-3">
                                <li><a class="dropdown-item load-session" href="#" data-index="${index}"><i class="fas fa-external-link-alt me-2"></i> Load Chat</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger delete-session" href="#" data-id="${session.user.id}"><i class="fas fa-trash-alt me-2"></i> Delete</a></li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="user-query mb-3">
                        <div class="d-flex gap-3">
                            <div class="avatar-sm bg-light rounded-circle d-flex align-items-center justify-content-center flex-shrink-0" style="width: 32px; height: 32px;">
                                <i class="fas fa-user text-muted small"></i>
                            </div>
                            <p class="mb-0 fw-bold text-dark">${session.user.content}</p>
                        </div>
                    </div>
                    
                    ${session.bot ? `
                    <div class="bot-response ps-5 border-start border-2 border-light">
                        <p class="text-muted small mb-0 text-truncate-2">${session.bot.content}</p>
                    </div>
                    ` : ''}
                </div>
            `;
            
            historyList.appendChild(card);
        });

        // Add event listeners
        historyList.querySelectorAll('.load-session').forEach(btn => {
            btn.onclick = (e) => {
                e.preventDefault();
                const idx = parseInt(btn.dataset.index);
                const session = sessions[idx];
                loadSessionIntoChat(session);
            };
        });

        historyList.querySelectorAll('.delete-session').forEach(btn => {
            btn.onclick = (e) => {
                e.preventDefault();
                const id = parseInt(btn.dataset.id);
                deleteSessionFromHistory(id);
            };
        });
    }

    function loadSessionIntoChat(session) {
        chatMessages.innerHTML = '';
        // Add welcome
        addMessageToChat("Hello! I am your CULTIA Assistant. I can help you explore Cameroon's rich history, traditions, and diverse cultures. What would you like to know today?", 'bot');
        
        addMessageToChat(session.user.content, 'user');
        if (session.bot) {
            addMessageToChat(session.bot.content, 'bot');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('historyModal')).hide();
        showNotification('Conversation loaded', 'success');
    }

    function deleteSessionFromHistory(userId) {
        const history = AICore.getHistory();
        const userIdx = history.findIndex(m => m.id === userId);
        if (userIdx !== -1) {
            // Remove user message and the following bot message
            history.splice(userIdx, 2);
            AICore.saveHistory(history);
            renderHistory();
            showNotification('Deleted from history', 'info');
        }
    }
    
    /**
     * Add a message to the chat without saving to history
     * @param {string} content - The message content
     * @param {string} type - 'user' or 'bot'
     */
    function addMessageToChat(content, type) {
        const messageId = ++messageIdCounter;
        const messageElement = createMessageElement(content, type, messageId);
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // ===== FAVORITES RENDERING =====
    
    /**
     * Render favorites in the favorites modal
     */
    function renderFavorites() {
        if (!favoritesList) return;
        
        // Clear current favorites list
        favoritesList.innerHTML = '';
        
        if (favoriteMessages.length === 0) {
            favoritesList.innerHTML = '<p class="no-favorites">No favorite messages yet.</p>';
            return;
        }
        
        // Sort favorites by timestamp (newest first)
        const sortedFavorites = [...favoriteMessages].sort((a, b) => 
            new Date(b.timestamp) - new Date(a.timestamp));
        
        sortedFavorites.forEach(favorite => {
            const favoriteItem = document.createElement('div');
            favoriteItem.className = 'favorite-item';
            favoriteItem.setAttribute('data-favorite-id', favorite.id);
            
            favoriteItem.innerHTML = `
                <div class="favorite-content">
                    <p>"${favorite.content}"</p>
                </div>
                <div class="favorite-actions">
                    <button class="favorite-action copy-favorite" data-favorite-id="${favorite.id}">Copy</button>
                    <button class="favorite-action remove remove-favorite" data-favorite-id="${favorite.id}">Remove</button>
                </div>
            `;
            
            favoritesList.appendChild(favoriteItem);
        });
        
        // Add event listeners for copy and remove buttons
        document.querySelectorAll('.copy-favorite').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const favoriteId = parseInt(e.target.getAttribute('data-favorite-id'));
                copyFavorite(favoriteId);
            });
        });
        
        document.querySelectorAll('.remove-favorite').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const favoriteId = parseInt(e.target.getAttribute('data-favorite-id'));
                removeFavorite(favoriteId);
            });
        });
    }
    
    /**
     * Copy a favorite message to clipboard
     * @param {number} favoriteId - The favorite message ID
     */
    function copyFavorite(favoriteId) {
        const favorite = favoriteMessages.find(fav => fav.id === favoriteId);
        if (favorite) {
            navigator.clipboard.writeText(favorite.content)
                .then(() => showNotification('Copied to clipboard', 'success'))
                .catch(() => showNotification('Failed to copy', 'error'));
        }
    }
    
    /**
     * Remove a favorite message
     * @param {number} favoriteId - The favorite message ID
     */
    function removeFavorite(favoriteId) {
        const index = favoriteMessages.findIndex(fav => fav.id === favoriteId);
        if (index >= 0) {
            favoriteMessages.splice(index, 1);
            saveFavorites();
            renderFavorites();
            showNotification('Removed from favorites', 'info');
        }
    }
    
    // ===== MODAL FUNCTIONALITY =====
    
    /**
     * Open a modal
     * @param {HTMLElement} modal - The modal element
     */
    function openModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    /**
     * Close a modal
     * @param {HTMLElement} modal - The modal element
     */
    function closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    /**
     * Handle language selection
     * @param {string} langCode - The language code
     */
    function selectLanguage(langCode) {
        currentLanguage = langCode;
        
        // Update recognition language
        if (recognition) {
            recognition.lang = getLanguageCode(langCode);
        }
        
        // Update UI
        document.querySelectorAll('.language-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-lang="${langCode}"]`).classList.add('active');
        
        // Save preference
        localStorage.setItem('selectedLanguage', langCode);
        
        showNotification(`Language changed to ${getLanguageName(langCode)}`, 'success');
        closeModal(languageModal);
    }
    
    /**
     * Get language name
     * @param {string} code - Language code
     * @returns {string} Language name
     */
    function getLanguageName(code) {
        const names = {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'zh': '中文',
            'ja': '日本語'
        };
        return names[code] || 'English';
    }
    
    // ===== DATA PERSISTENCE =====
    
    /**
     * Save conversation history to localStorage
     */
    function saveConversationHistory() {
        AICore.saveHistory(conversationHistory);
    }
    
    /**
     * Load conversation history from localStorage
     */
    function loadConversationHistory() {
        conversationHistory = AICore.getHistory();
        messageIdCounter = conversationHistory.length > 0 ? 
            Math.max(...conversationHistory.map(msg => msg.id || 0), 0) : 0;
    }

    // Add storage listener for sync
    window.addEventListener('storage', (e) => {
        if (e.key === AICore.SYNC_KEY) {
            loadConversationHistory();
            if (document.getElementById('historyModal').classList.contains('show')) {
                renderHistory();
            }
        }
    });
    
    /**
     * Save favorites to localStorage
     */
    function saveFavorites() {
        try {
            localStorage.setItem('favoriteMessages', JSON.stringify(favoriteMessages));
        } catch (error) {
            console.error('Error saving favorites:', error);
        }
    }
    
    /**
     * Load favorites from localStorage
     */
    function loadFavorites() {
        try {
            const saved = localStorage.getItem('favoriteMessages');
            if (saved) {
                favoriteMessages = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Error loading favorites:', error);
            favoriteMessages = [];
        }
    }
    
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
        `;
        
        // Set background color based on type
        const colors = {
            success: '#27AE60',
            error: '#C0392B',
            warning: '#F39C12',
            info: '#E67E22'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
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
        if (window.innerWidth > 768) {
            miniSidebar.classList.remove('mobile-open');
        }
        
        // Adjust chat messages scroll
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // ===== EVENT LISTENERS =====
    
    // Chat input events
    if (chatInput) {
        chatInput.addEventListener('input', handleInput);
        chatInput.addEventListener('keypress', handleKeyPress);
    }
    
    // Send button
    if (sendBtn) {
        sendBtn.addEventListener('click', async () => {
            const message = chatInput.value.trim();
            if (message) {
                await sendMessage(message);
            }
        });
    }
    
    // Voice input button
    if (voiceInputBtn) {
        voiceInputBtn.addEventListener('click', () => {
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        });
    }
    
    // Voice toggle button
    if (voiceToggleBtn) {
        voiceToggleBtn.addEventListener('click', toggleVoiceOutput);
    }
    
    // Clear chat button
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', clearChat);
    }
    
    // Suggestion buttons
    if (quickSuggestions) {
        quickSuggestions.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-btn')) {
                const suggestion = e.target.getAttribute('data-suggestion');
                handleSuggestionClick(suggestion);
            }
        });
    }
    
    // Tool buttons
    document.addEventListener('click', (e) => {
        if (e.target.closest('.tool-btn')) {
            const tool = e.target.closest('.tool-btn').getAttribute('data-tool');
            switch (tool) {
                case 'history':
                    renderHistory();
                    openModal(historyModal);
                    break;
                case 'favorites':
                    renderFavorites();
                    openModal(favoritesModal);
                    break;
                case 'language':
                    openModal(languageModal);
                    break;
            }
        }
    });
    
    // Modal close buttons
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            closeModal(modal);
        });
    });
    
    // Modal backdrop clicks
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });
    
    // Language selection
    document.querySelectorAll('.language-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const langCode = e.target.closest('.language-btn').getAttribute('data-lang');
            selectLanguage(langCode);
        });
    });
    
    // Delete confirmation buttons
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', () => {
            closeModal(deleteConfirmModal);
            conversationToDelete = null;
        });
    }
    
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', deleteConversation);
    }
    
    if (closeDeleteConfirmModal) {
        closeDeleteConfirmModal.addEventListener('click', () => {
            closeModal(deleteConfirmModal);
            conversationToDelete = null;
        });
    }
    
    // Window resize
    window.addEventListener('resize', handleResize);
    
    // ===== KEYBOARD SHORTCUTS =====
    
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter: Send message
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const message = chatInput.value.trim();
            if (message) {
                sendMessage(message);
            }
        }
        
        // Ctrl/Cmd + Space: Voice input
        if ((e.ctrlKey || e.metaKey) && e.code === 'Space') {
            e.preventDefault();
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        }
        
        // Escape: Close modals or stop voice
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal);
            } else if (isListening) {
                stopListening();
            }
        }
        
        // Ctrl/Cmd + K: Clear chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            clearChat();
        }
    });
    
    // ===== INITIALIZATION =====
    
    /**
     * Initialize the application
     */
    function initializeApp() {
        console.log('Initializing Personal Assistant Mode...');
        
        // Initialize sidebar state
        initializeSidebarState();
        
        // Load saved data
        loadConversationHistory();
        loadFavorites();
        
        // Initialize speech recognition
        initializeSpeechRecognition();
        
        // Load saved preferences
        const savedLanguage = localStorage.getItem('selectedLanguage') || 'en';
        selectLanguage(savedLanguage);
        
        const voiceEnabled = localStorage.getItem('voiceOutputEnabled') === 'true';
        if (voiceEnabled) {
            voiceToggleBtn.classList.add('active');
        }
        
        // Initialize input
        adjustTextareaHeight();
        handleInput();
        
        // Show initial suggestions
        showSuggestions();
        
        // Focus on input
        if (chatInput) {
            chatInput.focus();
        }
        
        // Show welcome notification
        setTimeout(() => {
            showNotification('Welcome to Personal Assistant Mode! Ask me anything about cultures and traditions.', 'success');
        }, 1000);
        
        console.log('Personal Assistant Mode initialized successfully');
    }
    
    // Start the application
    initializeApp();
    
    // ===== EXPORT FOR TESTING =====
    
    // Make functions available globally for testing (optional)
    window.AssistantMode = {
        sendMessage,
        toggleSidebar,
        startListening,
        stopListening,
        speakMessage,
        showNotification,
        clearChat
    };
});
