/**
 * Storyteller Logic - Immersive Campfire Experience
 */

document.addEventListener('DOMContentLoaded', async () => {
    const tribeGrid = document.getElementById('tribeGrid');
    const regionTabs = document.getElementById('regionTabs');
    const storyDisplay = document.getElementById('storyDisplay');
    const typingIndicator = document.getElementById('typingIndicator');
    const viewHistoryBtn = document.getElementById('viewHistoryBtn');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const selectionPanel = document.querySelector('.selection-panel');
    const showSelectionBtn = document.getElementById('showSelectionBtn');

    let allTribes = [];
    let selectedTribe = null;

    // Region mapping
    const regionMap = {
        'Grassfields': ['North West Region', 'West Region'],
        'Coastal': ['Littoral Region', 'South West Region'],
        'Forest': ['Centre Region', 'South Region', 'East Region'],
        'Sahel': ['Adamawa Region', 'North Region', 'Far North Region']
    };

    /**
     * Load Tribes from Backend
     */
    async function loadTribes() {
        try {
            const response = await fetch('/api/tribes');
            const data = await response.json();
            allTribes = Object.values(data.tribes);
            renderTribeGrid('all');
        } catch (error) {
            console.error('Error loading tribes:', error);
        }
    }

    /**
     * Render Tribe Grid based on Region
     */
    function renderTribeGrid(region) {
        tribeGrid.innerHTML = '';
        
        const filtered = region === 'all' 
            ? allTribes 
            : allTribes.filter(t => regionMap[region].includes(t.location.region));

        filtered.forEach(tribe => {
            const item = document.createElement('div');
            item.className = 'tribe-item';
            if (selectedTribe && selectedTribe.name === tribe.name) item.classList.add('selected');
            
            item.innerHTML = `
                <i class="fas fa-landmark"></i>
                <span>${tribe.name}</span>
            `;
            
            item.onclick = () => {
                // Update selection UI
                document.querySelectorAll('.tribe-item').forEach(el => el.classList.remove('selected'));
                item.classList.add('selected');
                selectedTribe = tribe;
                
                // Hide selection panel and show the trigger button
                selectionPanel.classList.add('hidden');
                showSelectionBtn.style.display = 'block';
                
                // Trigger Story
                requestStory(tribe.name);
            };
            
            tribeGrid.appendChild(item);
        });
    }

    /**
     * Handle Story Request
     */
    async function requestStory(tribeName) {
        // Clear previous story/welcome message
        storyDisplay.innerHTML = '';
        
        // Show typing indicator
        typingIndicator.style.display = 'block';
        
        // Scroll to bottom to see indicator
        storyDisplay.scrollTop = storyDisplay.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: tribeName,
                    mode: 'storyteller'
                })
            });

            const data = await response.json();
            typingIndicator.style.display = 'none';

            if (data.response) {
                addStoryCard(data.tribe || tribeName, data.response);
                
                // Save to history using AICore
                AICore.addMessage('user', `The legend of ${tribeName}`, 'storyteller');
                AICore.addMessage('bot', data.response, data.source);
            }
        } catch (error) {
            console.error('Story error:', error);
            typingIndicator.style.display = 'none';
            addStoryCard('System', "The fire flickers... I'm having trouble recalling that legend right now. Please try again, traveler.");
        }
    }

    /**
     * Add a beautiful story card
     */
    function addStoryCard(tribe, content, animate = true) {
        const card = document.createElement('div');
        card.className = 'story-card mb-5';
        
        // Extract title if it's in the **Title** format
        let title = 'A Tale of Old';
        let body = content;
        
        const titleMatch = content.match(/\*\*(.*?)\*\*/);
        if (titleMatch) {
            title = titleMatch[1];
            body = content.replace(/\*\*(.*?)\*\*/, '').trim();
        }

        // Clean up common "Ah, gather 'round..." prefixes for history
        if (!animate) {
             body = body.split('\n\n').slice(0).join('\n\n');
        }

        card.innerHTML = `
            <div class="story-meta">
                <span class="tribe-badge">${tribe}</span>
            </div>
            <h2 class="story-title">${title}</h2>
            <div class="story-content">${body}</div>
            <div class="text-center mt-4 opacity-50">
                <i class="fas fa-fire-alt"></i>
            </div>
        `;
        
        storyDisplay.appendChild(card);
        
        if (animate && window.AOS) {
            card.setAttribute('data-aos', 'fade-up');
            AOS.refresh();
        }

        // Scroll to new content
        setTimeout(() => {
            storyDisplay.scrollTo({
                top: storyDisplay.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    /**
     * Load initial history from storage
     */
    function loadStoryHistory() {
        const history = AICore.getHistory();
        const stories = history.filter(m => m.role === 'bot' && (m.source === 'local_story' || m.source === 'gemini_story'));
        
        if (stories.length > 0) {
            if (welcomeMessage) welcomeMessage.style.display = 'none';
            stories.forEach(msg => {
                // Try to find the tribe name from the history message or content
                const tribeMatch = msg.content.match(/\*\*(.*?)\*\*/);
                const tribe = tribeMatch ? tribeMatch[1].split(' ')[0] : 'Legend';
                addStoryCard(tribe, msg.content, false);
            });
        }
    }

    /**
     * Clear Story History
     */
    function clearHistory() {
        if (confirm("Are you sure you want to silence the ancestors? This will clear all story history.")) {
            AICore.clearHistory();
            storyDisplay.innerHTML = '';
            
            // Show selection panel again
            selectionPanel.classList.remove('hidden');
            showSelectionBtn.style.display = 'none';

            if (welcomeMessage) {
                welcomeMessage.style.display = 'block';
                storyDisplay.appendChild(welcomeMessage);
            }
            alert("History cleared.");
        }
    }

    // Event Listeners
    regionTabs.addEventListener('click', (e) => {
        if (e.target.classList.contains('region-btn')) {
            document.querySelectorAll('.region-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            renderTribeGrid(e.target.dataset.region);
        }
    });

    viewHistoryBtn.addEventListener('click', () => {
        storyDisplay.scrollTo({ top: 0, behavior: 'smooth' });
    });

    showSelectionBtn.addEventListener('click', () => {
        selectionPanel.classList.remove('hidden');
        showSelectionBtn.style.display = 'none';
        
        // Refresh AOS to ensure animations work if needed
        if (window.AOS) AOS.refresh();
    });

    clearHistoryBtn.addEventListener('click', clearHistory);

    // Initial Load
    await loadTribes();
    loadStoryHistory();
});
