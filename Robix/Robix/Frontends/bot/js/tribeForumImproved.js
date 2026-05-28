/**
 * Tribe Forum JavaScript - Improved Version
 * Handles tribe search functionality and interactive storytelling experience
 */

document.addEventListener('DOMContentLoaded', function() {

    // Element references
    const tribeNameInput = document.getElementById('tribeName');
    const tribeRegionSelect = document.getElementById('tribeRegion');
    const frenchLanguageCheckbox = document.getElementById('frenchLanguage');
    const englishLanguageCheckbox = document.getElementById('englishLanguage');
    const searchTribeBtn = document.getElementById('searchTribeBtn');
    const tribeFilterInput = document.getElementById('tribeFilter');
    const tribeInfoSection = document.getElementById('tribeInfo');
    const allTribesGrid = document.getElementById('allTribesGrid');

    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Tribe data will be loaded from API
    let tribeData = {};

    const LANG_STORAGE_KEY = 'educatorSettings';

    function getSettings() {
        try {
            return JSON.parse(localStorage.getItem(LANG_STORAGE_KEY) || '{}') || {};
        } catch (e) {
            return {};
        }
    }

    function setLearningLanguage(lang) {
        const settings = getSettings();
        settings.learningLanguage = lang;
        localStorage.setItem(LANG_STORAGE_KEY, JSON.stringify(settings));
        window.dispatchEvent(new CustomEvent('settingsChanged', { detail: settings }));
    }

    function getLearningLanguage() {
        const settings = getSettings();
        return (settings.learningLanguage || 'en').toString().toLowerCase();
    }

    const translations = {
        en: {
            pageTitle: 'Tribe Forum',
            discoverHeader: "Discover Cameroon's Rich Tribal Heritage",
            discoverSub: 'Explore the stories, traditions, arts, and governance of over 50 major tribes across Cameroon',
            findYourTribe: 'Find Your Tribe',
            searchByName: 'Search by Tribe Name',
            placeholderName: 'e.g., Bamileke, Bamum, Bassa...',
            filterByRegion: 'Filter by Region',
            allRegions: 'All Regions',
            filterByPopulation: 'Filter by Population Size',
            allSizes: 'All Sizes',
            languagePreference: 'Language Preference',
            frenchSpeaking: 'French-Speaking Tribes',
            englishSpeaking: 'English-Speaking Tribes',
            exploreTribes: 'Explore Tribes',
            exploreAll: 'Explore All Tribes',
            sortBy: 'Sort By',
            filterPlaceholder: 'Filter tribes by name, region, or description...',
            switchAssistant: 'Switch to Assistant'
        },
        fr: {
            pageTitle: 'Forum des tribus',
            discoverHeader: 'Découvrez le riche patrimoine tribal du Cameroun',
            discoverSub: "Explorez les histoires, traditions, arts et gouvernance de plus de 50 grandes tribus du Cameroun",
            findYourTribe: 'Trouvez votre tribu',
            searchByName: 'Rechercher par nom de tribu',
            placeholderName: 'ex. Bamileke, Bamum, Bassa...',
            filterByRegion: 'Filtrer par région',
            allRegions: 'Toutes les régions',
            filterByPopulation: 'Filtrer par taille de population',
            allSizes: 'Toutes les tailles',
            languagePreference: 'Préférence de langue',
            frenchSpeaking: 'Tribus francophones',
            englishSpeaking: 'Tribus anglophones',
            exploreTribes: 'Explorer les tribus',
            exploreAll: 'Explorer toutes les tribus',
            sortBy: 'Trier par',
            filterPlaceholder: 'Filtrer les tribus par nom, région ou description...',
            switchAssistant: "Basculer vers l'assistant"
        }
    };

    function applyTranslations(lang) {
        const dict = translations[lang] || translations.en;

        const pageTitle = document.querySelector('.page-title');
        if (pageTitle) pageTitle.textContent = dict.pageTitle;

        const switchLabel = document.querySelector('.switch-mode-btn .switch-label');
        if (switchLabel) switchLabel.textContent = dict.switchAssistant;

        const forumHeaderTitle = document.querySelector('.tribe-forum-header h1');
        if (forumHeaderTitle) forumHeaderTitle.textContent = dict.discoverHeader;
        const forumHeaderSub = document.querySelector('.tribe-forum-header p');
        if (forumHeaderSub) forumHeaderSub.textContent = dict.discoverSub;

        const findYourTribeTitle = document.querySelector('.search-filter-section .card-header h3');
        if (findYourTribeTitle) {
            findYourTribeTitle.innerHTML = `<i class="fas fa-search"></i> ${dict.findYourTribe}`;
        }

        const cardHeaderP = document.querySelector('.search-filter-section .card-header p');
        if (cardHeaderP) cardHeaderP.textContent = lang === 'fr'
            ? 'Recherchez une tribu spécifique ou parcourez par région'
            : 'Search for a specific tribe or browse by region';

        const searchByNameLabel = document.querySelector('label[for="tribeName"]');
        if (searchByNameLabel) searchByNameLabel.textContent = dict.searchByName;
        if (tribeNameInput) tribeNameInput.placeholder = dict.placeholderName;

        const filterByRegionLabel = document.querySelector('label[for="tribeRegion"]');
        if (filterByRegionLabel) filterByRegionLabel.textContent = dict.filterByRegion;
        if (tribeRegionSelect) {
            const opt = tribeRegionSelect.querySelector('option[value=""]');
            if (opt) opt.textContent = dict.allRegions;
        }

        const filterByPopulationLabel = document.querySelector('label[for="tribePopulation"]');
        if (filterByPopulationLabel) filterByPopulationLabel.textContent = dict.filterByPopulation;
        const tribePopulationSelect = document.getElementById('tribePopulation');
        if (tribePopulationSelect) {
            const opt = tribePopulationSelect.querySelector('option[value=""]');
            if (opt) opt.textContent = dict.allSizes;
        }

        const langPrefLabel = document.querySelector('.search-filter-section .form-group .form-label:not([for])');
        if (langPrefLabel && langPrefLabel.textContent.trim().toLowerCase().includes('language')) {
            langPrefLabel.textContent = dict.languagePreference;
        }

        const frenchLabel = document.querySelector('label.checkbox-label[for]');
        if (frenchLanguageCheckbox && frenchLanguageCheckbox.parentElement) {
            const label = frenchLanguageCheckbox.parentElement;
            label.childNodes.forEach(node => {
                if (node.nodeType === Node.TEXT_NODE) node.textContent = ` ${dict.frenchSpeaking}`;
            });
        }
        if (englishLanguageCheckbox && englishLanguageCheckbox.parentElement) {
            const label = englishLanguageCheckbox.parentElement;
            label.childNodes.forEach(node => {
                if (node.nodeType === Node.TEXT_NODE) node.textContent = ` ${dict.englishSpeaking}`;
            });
        }

        if (searchTribeBtn) {
            searchTribeBtn.innerHTML = `<i class="fas fa-search"></i> ${dict.exploreTribes}`;
        }

        const exploreAllTitle = document.querySelector('.content-section h3');
        if (exploreAllTitle) {
            exploreAllTitle.innerHTML = `<i class="fas fa-atlas"></i> ${dict.exploreAll}`;
        }

        const sortByLabel = document.querySelector('label[for="tribeSort"]');
        if (sortByLabel) sortByLabel.textContent = dict.sortBy;

        if (tribeFilterInput) tribeFilterInput.placeholder = dict.filterPlaceholder;

        document.documentElement.setAttribute('lang', lang);
    }

    function syncLanguageUI(lang) {
        if (!frenchLanguageCheckbox || !englishLanguageCheckbox) return;
        frenchLanguageCheckbox.checked = lang === 'fr';
        englishLanguageCheckbox.checked = lang === 'en';
    }

    function initializeLanguagePreference() {
        const lang = getLearningLanguage() === 'fr' ? 'fr' : 'en';
        syncLanguageUI(lang);
        applyTranslations(lang);

        if (frenchLanguageCheckbox) {
            frenchLanguageCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    if (englishLanguageCheckbox) englishLanguageCheckbox.checked = false;
                    setLearningLanguage('fr');
                    applyTranslations('fr');
                } else {
                    setLearningLanguage('en');
                    if (englishLanguageCheckbox) englishLanguageCheckbox.checked = true;
                    applyTranslations('en');
                }
            });
        }

        if (englishLanguageCheckbox) {
            englishLanguageCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    if (frenchLanguageCheckbox) frenchLanguageCheckbox.checked = false;
                    setLearningLanguage('en');
                    applyTranslations('en');
                } else {
                    setLearningLanguage('fr');
                    if (frenchLanguageCheckbox) frenchLanguageCheckbox.checked = true;
                    applyTranslations('fr');
                }
            });
        }

        window.addEventListener('settingsChanged', function(event) {
            const next = (event.detail && event.detail.learningLanguage) ? event.detail.learningLanguage : getLearningLanguage();
            const normalized = next === 'fr' ? 'fr' : 'en';
            syncLanguageUI(normalized);
            applyTranslations(normalized);
        });
    }

    function getSelectedTribeKey() {
        return (localStorage.getItem('selectedTribe') || '').toString().trim().toLowerCase();
    }

    function userHasTribeRestriction() {
        return !!getSelectedTribeKey();
    }

    initializeLanguagePreference();

    // Load tribe data from API endpoint with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    fetch('/api/tribes', { signal: controller.signal })
        .then(response => {

            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            tribeData = data.tribes;
            const selectedTribe = getSelectedTribeKey();
            if (selectedTribe && tribeData && tribeData[selectedTribe]) {
                displayAllTribes(selectedTribe);
                displayTribeInfo(selectedTribe);
            } else {
                displayAllTribes();
            }
        })

        .catch(error => {

            clearTimeout(timeoutId);
            console.error('Error loading tribe data:', error);
            // Show error message to user
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.innerHTML = `
                <div style="background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #f5c6cb;">
                    <h3><i class="fas fa-exclamation-triangle"></i> Data Loading Error</h3>
                    <p>Unable to load tribe data. Displaying sample tribes instead.</p>
                    <p>Error: ${error.message}</p>
                </div>
            `;
            document.querySelector('.content-body').prepend(errorMessage);

            // Fallback to sample data if API fails to load
            tribeData = {
                'bamileke': {
                    name: 'Bamileke',
                    location: { region: 'Western Highlands of Cameroon' },
                    overview: 'The Bamileke people are one of the largest ethnic groups in Cameroon, known for their rich cultural heritage and traditional kingdoms.',
                    history: { origin: 'The Bamileke people trace their origins to the Grassfields region of western Cameroon.', colonial_impact: 'The arrival of German colonizers in the late 19th century significantly impacted their traditional governance systems.' },
                    culture: { social_structure: 'Bamileke society is organized into numerous chiefdoms and kingdoms.', values: ['Respect for elders', 'Importance of education', 'Community solidarity'] },
                    traditions: { ceremonies: [{ name: 'Lem Festival', description: 'Annual celebration of the new yam harvest.' }] },
                    arts_and_crafts: { textiles: 'Famous for Toghu cloth', metalwork: 'Renowned for bronze casting' },
                    population: 'Approximately 3.2 million',
                    languages: ['Shüpamom', 'Ménzìm', 'Nda\'nda\''],
                    governance: { traditional: 'Each kingdom is ruled by a Fon.', modern: 'Integration with national administration.' },
                    notable_figures: ['Ahmadou Ahidjo', 'Paul Biya'],
                    challenges: ['Balancing tradition with modernization', 'Land disputes']
                },
                'bamum': {
                    name: 'Bamum',
                    location: { region: 'West-Central Cameroon' },
                    overview: 'The Bamum people are known for their ancient kingdom and rich written tradition.',
                    history: { origin: 'The Bamum established their kingdom in the 17th century.', colonial_impact: 'The kingdom was conquered by German forces in 1901.' },
                    culture: { social_structure: 'Historically organized around the monarchy.', values: ['Respect for tradition', 'Importance of literacy'] },
                    traditions: { ceremonies: [{ name: 'Nguon Festival', description: 'Celebrates the installation of Sultan Njoya.' }] },
                    arts_and_crafts: { metalwork: 'Renowned for bronze sculptures', literature: 'Development of indigenous writing system' },
                    population: 'Approximately 350,000',
                    languages: ['Aghem', 'Ngyem'],
                    governance: { traditional: 'Ruled by a Sultan with council of nobles.', modern: 'Traditional Sultan holds cultural authority.' },
                    notable_figures: ['Sultan Njoya'],
                    challenges: ['Preserving writing system', 'Balancing traditional authority']
                }
            };
            // Display all tribes
            displayAllTribes();
        });

    // Initialize tab functionality
    function initializeTabs() {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');

                // Update active tab button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                // Update active tab content
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === `${tabId}-tab`) {
                        content.classList.add('active');
                    }
                });
            });
        });
    }

    // Display all tribes
    function displayAllTribes() {
        // Check if tribeData is valid
        if (!tribeData || typeof tribeData !== 'object') {
            console.error('Invalid tribe data provided to displayAllTribes');
            return;
        }

        const selectedTribe = getSelectedTribeKey();

        allTribesGrid.innerHTML = '';

        const entries = Object.entries(tribeData);
        const filteredEntries = selectedTribe
            ? entries.filter(([key]) => key.toString().toLowerCase() === selectedTribe)
            : entries;

        filteredEntries.forEach(([key, tribe]) => {
            const tribeCard = document.createElement('div');
            tribeCard.className = 'tribe-card';
            tribeCard.onclick = () => searchTribe(tribe.name);
            tribeCard.innerHTML = `
                <div class="tribe-card-image">
                    <i class="fas fa-users"></i>
                </div>
                <div class="tribe-card-content">
                    <h3>${tribe.name}</h3>
                    <p>${tribe.overview ? tribe.overview.substring(0, 100) + '...' : 'Explore the rich heritage of this tribe'}</p>
                    <span class="tribe-region">${tribe.location.region}</span>
                </div>
            `;
            allTribesGrid.appendChild(tribeCard);
        });

        // Add event listener for filter input
        if (tribeFilterInput) {
            tribeFilterInput.addEventListener('input', filterTribes);
        }
    }

    // Search for tribe information
    function searchTribe(tribeName) {
        const selectedTribe = getSelectedTribeKey();
        const normalized = (tribeName || '').toString().trim().toLowerCase();

        if (selectedTribe && normalized && normalized !== selectedTribe) {
            alert(`You are currently viewing only: ${selectedTribe}. Click "All Tribes" on the dashboard to view others.`);
            tribeNameInput.value = selectedTribe;
            displayTribeInfo(selectedTribe);
            return;
        }

        tribeNameInput.value = tribeName;
        displayTribeInfo(tribeName);
    }

    // Display tribe information
    function displayTribeInfo(tribeName) {
        console.log('🔍 displayTribeInfo called for:', tribeName);
        
        const selectedTribe = getSelectedTribeKey();
        const normalizedTribeName = (tribeName || '').toString().toLowerCase().trim();

        if (selectedTribe && normalizedTribeName && normalizedTribeName !== selectedTribe) {
            alert(`You are currently viewing only: ${selectedTribe}. Click "All Tribes" on the dashboard to view others.`);
            return displayTribeInfo(selectedTribe);
        }

        let tribe = tribeData ? tribeData[normalizedTribeName] : null;
        if (!tribe && tribeData && normalizedTribeName) {
            const keys = Object.keys(tribeData);
            for (const key of keys) {
                const t = tribeData[key];
                const name = (t && t.name) ? t.name.toString().toLowerCase() : '';
                if (key.toString().toLowerCase() === normalizedTribeName || name === normalizedTribeName) {
                    tribe = t;
                    break;
                }
                if (name.includes(normalizedTribeName) || key.toString().toLowerCase().includes(normalizedTribeName)) {
                    tribe = t;
                    break;
                }
            }
        }

        if (!tribe) {
            console.error('❌ Tribe not found:', tribeName);
            alert(`Sorry, information about the ${tribeName} tribe is not available in our database. Please try another tribe name.`);
            return;
        }

        console.log('✅ Found tribe:', tribe.name);

        // Build the complete tribe info HTML dynamically
        const overview = tribe.overview || '';
        const origin = tribe.history && tribe.history.origin ? tribe.history.origin : '';
        const colonial = tribe.history && tribe.history.colonial_impact ? tribe.history.colonial_impact : '';
        const valuesText = (tribe.culture && Array.isArray(tribe.culture.values) && tribe.culture.values.length > 0)
            ? tribe.culture.values.slice(0, 2).join(' and ')
            : 'strong cultural values';
        const ceremony = (tribe.traditions && Array.isArray(tribe.traditions.ceremonies) && tribe.traditions.ceremonies.length > 0)
            ? tribe.traditions.ceremonies[0]
            : null;
        
        const region = tribe.location && tribe.location.region ? tribe.location.region : 'Information not available';
        const countries = tribe.location && tribe.location.countries ? tribe.location.countries.join(', ') : '';
        
        // Build richer, more "wise" storytelling HTML
        const customs = (tribe.customs_and_traditions || []).slice(0, 3).join(', ');
        const meals = (tribe.meals_and_cuisine_list || []).slice(0, 3).join(', ');
        const festivals = (tribe.festivals_list || []).slice(0, 2).join(' and ');
        
        let storytellingHTML = `
            <p><i class="fas fa-quote-left me-2" style="color: var(--primary-orange); opacity: 0.5;"></i> Come closer, my child. Sit by my side and let the winds of the past whisper to you. Today, I shall share the sacred story of the <strong>${tribe.name}</strong>, a people whose roots run as deep as the ancient mahogany trees of our great land.</p>
            
            <p>You see, the ${tribe.name} are not just any people; they are the heart of the ${region}. ${overview}</p>
        `;

        if (origin) {
            storytellingHTML += `<p>In the times of the old ones, long before the maps were drawn as they are now, your ancestors ${origin.toLowerCase()}. They carried their dreams across the plains and through the forests, seeking a place where their children could flourish.</p>`;
        }

        if (customs) {
            storytellingHTML += `<p>Listen well, for our strength lies in our ways. The ${tribe.name} have always walked with dignity, upheld by their traditions of ${customs.toLowerCase()}. These are the threads that weave our community together, stronger than any iron chain.</p>`;
        }

        if (meals) {
            storytellingHTML += `<p>And when the sun begins to set and the fires are lit, the air fills with the aroma of home. Our tables are blessed with the bounty of the earth—${meals.toLowerCase()}. Each bite is a memory, a taste of the love our mothers poured into every pot.</p>`;
        }

        if (festivals) {
            storytellingHTML += `<p>When the moon is full and the drums begin to speak, we gather for the ${festivals}. Oh, the joy! The dances tell the stories of our victories, and the songs reach the very ears of the ancestors themselves.</p>`;
        }

        if (colonial) {
            storytellingHTML += `<p>There were shadows, yes. During the seasons of change and colonization, ${colonial.toLowerCase()}. But like the grass that bends but never breaks in the storm, the ${tribe.name} spirit remained unyielding. We remember the struggle so that we may cherish the peace.</p>`;
        }

        storytellingHTML += `
            <p>The world is wide and changing, my child, but never forget who you are. The ${tribe.name} people have always been known for their ${valuesText}. Carry this wisdom in your heart like a precious gem, and you will never be lost, no matter how far you wander. <i class="fas fa-quote-right ms-2" style="color: var(--primary-orange); opacity: 0.5;"></i></p>
        `;

        // Build the complete HTML structure
        const heroImg = tribe.image_url || `image/download (${(Math.floor(Math.random() * 8) + 1)}).jpeg`;
        
        tribeInfoSection.innerHTML = `
            <div class="tribe-return-button">
                <button class="learn-btn" id="backToTribesBtn">
                    <i class="fas fa-arrow-left"></i> Back to All Tribes
                </button>
            </div>

            <div class="tribe-detail-header" style="background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('${heroImg}'); background-size: cover; background-position: center; min-height: 300px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white;">
                <h2 id="tribeTitle" style="font-size: 3.5rem; text-shadow: 2px 2px 10px rgba(0,0,0,0.5);">${tribe.name || 'Tribe'}</h2>
                <p id="tribeSubtitle" style="font-size: 1.5rem; opacity: 1; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);">${region}${countries ? ' • ' + countries : ''}</p>
            </div>
            
            <!-- Grandparent Storytelling Section -->
            <div class="storytelling-section">
                <div class="storyteller-header">
                    <i class="fas fa-user-circle fa-3x" style="color: var(--primary-orange);"></i>
                    <div>
                        <h4 style="margin: 0; color: var(--primary-brown);">Wisdom of the Elders</h4>
                        <small class="text-muted">Oral Tradition & Heritage</small>
                    </div>
                </div>
                <div class="storytelling-content" id="grandparentStory" style="font-size: 1.25rem; line-height: 2;">
                    ${storytellingHTML}
                </div>
            </div>
            
            <!-- Tribe Details Tabs -->
            <div class="tribe-tabs">
                <div class="tab-buttons">
                    <button class="tab-btn active" data-tab="overview"><i class="fas fa-eye"></i> Quick Facts</button>
                    <button class="tab-btn" data-tab="history"><i class="fas fa-history"></i> History</button>
                    <button class="tab-btn" data-tab="culture"><i class="fas fa-users"></i> Culture</button>
                    <button class="tab-btn" data-tab="traditions"><i class="fas fa-om"></i> Traditions</button>
                    <button class="tab-btn" data-tab="arts"><i class="fas fa-paint-brush"></i> Arts & Crafts</button>
                </div>
                
                <div class="tab-content active" id="overview-tab">
                    <div class="grid-2">
                        <div class="content-section">
                            <h3><i class="fas fa-map-marker-alt" style="color: #e74c3c;"></i> Location</h3>
                            <p>${region}${countries ? ', ' + countries : ''}</p>
                        </div>
                        <div class="content-section">
                            <h3><i class="fas fa-users" style="color: #3498db;"></i> Population</h3>
                            <p>${tribe.population || 'Information not available'}</p>
                        </div>
                        <div class="content-section">
                            <h3><i class="fas fa-language" style="color: #2ecc71;"></i> Languages</h3>
                            <p>${tribe.languages ? tribe.languages.join(', ') : (tribe.language || 'Information not available')}</p>
                        </div>
                        <div class="content-section">
                            <h3><i class="fas fa-info-circle" style="color: #f1c40f;"></i> Summary</h3>
                            <p>${overview || 'Information not available'}</p>
                        </div>
                    </div>
                </div>
                
                <div class="tab-content" id="history-tab">
                    <div class="content-section">
                        <h3><i class="fas fa-landmark"></i> Historical Origins</h3>
                        <p>${tribe.history ? (tribe.history.origin || tribe.history || '') + ' ' + (tribe.history.colonial_impact || '') : 'Information not available'}</p>
                        
                        ${tribe.history && tribe.history.key_events ? `
                        <h4 class="mt-4"><i class="fas fa-calendar-alt"></i> Key Historical Events</h4>
                        <ul class="list-group list-group-flush">
                            ${tribe.history.key_events.map(event => `<li class="list-group-item bg-transparent border-0 ps-0"><i class="fas fa-check-circle text-success me-2"></i> ${event}</li>`).join('')}
                        </ul>
                        ` : ''}
                    </div>
                </div>
                
                <div class="tab-content" id="culture-tab">
                    <div class="content-section">
                        <h3><i class="fas fa-users"></i> Social Structure</h3>
                        <p>${tribe.culture && tribe.culture.social_structure ? tribe.culture.social_structure : (tribe.culture || 'Information not available')}</p>
                        
                        <div class="row mt-4">
                            <div class="col-md-6">
                                <div class="p-3 rounded bg-light">
                                    <h4 class="mt-0"><i class="fas fa-pray"></i> Beliefs</h4>
                                    <ul class="list-unstyled">
                                        ${tribe.culture && tribe.culture.beliefs ? tribe.culture.beliefs.map(belief => `<li class="mb-2"><i class="fas fa-star text-warning me-2"></i> ${belief}</li>`).join('') : '<li>Information not available</li>'}
                                    </ul>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="p-3 rounded bg-light">
                                    <h4 class="mt-0"><i class="fas fa-heart"></i> Values</h4>
                                    <ul class="list-unstyled">
                                        ${tribe.culture && tribe.culture.values ? tribe.culture.values.map(value => `<li class="mb-2"><i class="fas fa-heart text-danger me-2"></i> ${value}</li>`).join('') : '<li>Information not available</li>'}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-content" id="traditions-tab">
                    <div class="content-section">
                        <h3><i class="fas fa-om"></i> Ceremonies and Festivals</h3>
                        <div class="row g-4">
                            ${tribe.traditions && tribe.traditions.ceremonies ? tribe.traditions.ceremonies.map(ceremony => `
                                <div class="col-md-6">
                                    <div class="card h-100 border-0 shadow-sm rounded-4">
                                        <div class="card-body">
                                            <h4 class="card-title text-success">${ceremony.name}</h4>
                                            <p class="card-text">${ceremony.description}</p>
                                        </div>
                                    </div>
                                </div>
                            `).join('') : '<div class="col-12"><p>Information not available</p></div>'}
                        </div>
                        
                        <h3 class="mt-5"><i class="fas fa-ring"></i> Marriage and Rites</h3>
                        <div class="p-4 rounded-4" style="background: #fdfaf5; border-left: 5px solid var(--primary-orange);">
                            <p class="mb-0"><strong>Marriage:</strong> ${tribe.traditions && tribe.traditions.marriage ? tribe.traditions.marriage : (tribe.marriage || 'Information not available')}</p>
                            ${tribe.traditions && tribe.traditions.rites_of_passage ? `
                                <hr>
                                <p class="mb-0"><strong>Rites of Passage:</strong> ${tribe.traditions.rites_of_passage.join(', ')}</p>
                            ` : ''}
                        </div>
                    </div>
                </div>
                
                <div class="tab-content" id="arts-tab">
                    <div class="content-section">
                        <h3><i class="fas fa-paint-brush"></i> Artistic Expressions</h3>
                        <div class="grid-2">
                            ${tribe.arts_and_crafts ? Object.entries(tribe.arts_and_crafts).map(([key, value]) => `
                                <div class="p-3 border-bottom">
                                    <h4 class="mt-0 text-capitalize">${key.replace(/_/g, ' ')}</h4>
                                    <p class="mb-0">${value}</p>
                                </div>
                            `).join('') : '<p>Information not available</p>'}
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Show tribe info section with animation
        tribeInfoSection.classList.add('active');

        // Scroll to tribe info
        tribeInfoSection.scrollIntoView({ behavior: 'smooth' });

        // Add back button listener
        document.getElementById('backToTribesBtn').addEventListener('click', () => {
            tribeInfoSection.classList.remove('active');
            window.scrollTo({top: 0, behavior: 'smooth'});
        });

        // Initialize tabs after content is loaded
        initializeTabs();
        
        console.log('✅ Tribe info displayed successfully');
    }

    // Filter tribes based on search input
    function filterTribes() {
        const filterValue = tribeFilterInput.value.toLowerCase();
        const tribeCards = allTribesGrid.querySelectorAll('.tribe-card');
        
        tribeCards.forEach(card => {
            const tribeName = card.querySelector('h3').textContent.toLowerCase();
            if (tribeName.includes(filterValue)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Handle search button click with error handling
    if (searchTribeBtn) {
        searchTribeBtn.addEventListener('click', function() {
            const tribeName = tribeNameInput.value;
            if (tribeName && tribeName.trim()) {
                displayTribeInfo(tribeName);
            } else {
                displayAllTribes();
            }
        });
    }
    
    // Make searchTribe function globally available
    window.searchTribe = searchTribe;
    
    // Add global function for external access
    window.TribeForum = {
        searchTribe: searchTribe,
        displayTribeInfo: displayTribeInfo
    };
});