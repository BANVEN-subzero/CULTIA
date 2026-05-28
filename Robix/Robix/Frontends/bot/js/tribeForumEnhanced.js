/**
 * Tribe Forum Improved JavaScript
 * Enhanced functionality for tribe search and storytelling experience
 */

document.addEventListener('DOMContentLoaded', function() {
    // Element references
    const tribeNameInput = document.getElementById('tribeName');
    const tribeRegionSelect = document.getElementById('tribeRegion');
    const tribePopulationSelect = document.getElementById('tribePopulation');
    const tribeSortSelect = document.getElementById('tribeSort');
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
    let allTribes = [];
    
    // Load tribe data from API endpoint
    fetch('/api/tribes')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Tribe data loaded successfully:', data);
            tribeData = data.tribes;
            allTribes = Object.values(tribeData);
            // Display all tribes
            displayAllTribes(allTribes);
            
            // Apply tribe color scheme when a tribe is selected
            if (window.EnhancedDesign) {
                // Add event listener to tribe cards for color scheme changes
                document.addEventListener('click', function(e) {
                    if (e.target.closest('.tribe-card')) {
                        const tribeCard = e.target.closest('.tribe-card');
                        const tribeName = tribeCard.querySelector('h3').textContent.toLowerCase();
                        // Apply tribe-specific color scheme
                        window.EnhancedDesign.applyTribeColorScheme(tribeName);
                    }
                });
            }
        })
        .catch(error => {
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
            
            // Add error message before the tribe grid
            if (allTribesGrid && allTribesGrid.parentNode) {
                allTribesGrid.parentNode.insertBefore(errorMessage, allTribesGrid);
            }
            
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
                },
                'bassa': {
                    name: 'Bassa',
                    location: { region: 'Littoral Region of Cameroon' },
                    overview: 'The Bassa people are primarily found in the coastal regions of Cameroon and are known for their fishing traditions, rich oral literature, and agricultural skills.',
                    history: { origin: 'The Bassa people are among the earliest inhabitants of the Cameroon coast, with settlements dating back several centuries.', colonial_impact: 'The Bassa were involved in the early palm oil trade and later became prominent in the colonial administration.' },
                    culture: { social_structure: 'Bassa society is organized around extended family units and village councils of elders.', values: ['Community solidarity and mutual support', 'Respect for elders and tradition', 'Importance of fishing and agricultural skills'] },
                    traditions: { ceremonies: [{ name: 'Ngondo Festival', description: 'Annual water festival celebrating the Sawa people\'s connection to the sea.' }] },
                    arts_and_crafts: { textiles: 'Known for their traditional cloth weaving and decorative patterns.', pottery: 'Renowned for distinctive pottery and basketry with traditional designs.' },
                    population: 'Approximately 300,000',
                    languages: ['Basaa'],
                    governance: { traditional: 'Traditional Bassa governance was based on village councils of elders, with decisions made through consensus.', modern: 'Integration with Cameroon\'s national administrative system while maintaining traditional councils for cultural matters.' },
                    notable_figures: ['Charles Atangana (early collaborator with German colonial administration)'],
                    challenges: ['Environmental pressures on fishing resources', 'Urbanization and cultural change']
                }
            };
            allTribes = Object.values(tribeData);
            // Display all tribes
            displayAllTribes(allTribes);
        });
    
    // Initialize tab functionality
    function initializeTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
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
    
    // Search for tribe information
    function searchTribe(tribeName) {
        console.log('Searching for tribe:', tribeName);
        if (tribeNameInput) {
            tribeNameInput.value = tribeName;
        }
        displayTribeInfo(tribeName);
    }
    
    // Enhanced storytelling content generation with more engaging narrative
    function generateStorytellingContent(tribe) {
        let story = `<p>My dear child, come closer and listen carefully, for I have wonderful stories to tell you about the magnificent ${tribe.name} people. Sit comfortably, as I take you on a journey through time to learn about your ancestors.</p>`;
        
        story += `<p>Let me tell you, child, that the ${tribe.name} people are truly special. ${tribe.overview}</p>`;
        
        // Add origin story with more engaging language
        if (tribe.history && tribe.history.origin) {
            story += `<p>Long, long ago, even before your great-great-grandparents were born, your ancestors ${tribe.history.origin.toLowerCase()}. Can you imagine that, my dear? Such a rich history flowing through your veins!</p>`;
        }
        
        // Add more detailed colonial impact with emotional context
        if (tribe.history && tribe.history.colonial_impact) {
            story += `<p>During those difficult times when strangers came to our lands, seeking to change our ways, ${tribe.history.colonial_impact.toLowerCase()}. But our people, your ancestors, were strong and resilient. They held onto their traditions and values, passing them down to the next generation, just as I'm passing them to you now.</p>`;
        }
        
        // Add cultural values with personal connection
        if (tribe.culture && tribe.culture.values) {
            const values = Array.isArray(tribe.culture.values) ? tribe.culture.values.slice(0, 3).join(', ') : 'strong cultural values';
            story += `<p>The ${tribe.name} people have always been known for their ${values}. These precious values were carefully guarded and passed down from parent to child, from elder to youth, for many, many generations. And now, my dear, these same values live within you!</p>`;
        }
        
        // Add traditions and ceremonies with more vivid descriptions
        if (tribe.traditions && tribe.traditions.ceremonies && tribe.traditions.ceremonies.length > 0) {
            const ceremony = tribe.traditions.ceremonies[0];
            story += `<p>Every year, our people celebrate the beautiful ${ceremony.name}, where ${ceremony.description.toLowerCase()}. Oh, what joy fills our hearts during this special time! The whole community comes together, sharing stories, dancing, singing, and strengthening the bonds that tie us all together as one family.</p>`;
        }
        
        // Add information about daily life with more personal touch
        if (tribe.economy && tribe.economy.traditional) {
            const activities = Array.isArray(tribe.economy.traditional) ? tribe.economy.traditional.slice(0, 3).join(', ') : 'traditional activities';
            story += `<p>In our daily lives, our people engaged in ${activities}. These weren't just ways to earn a living, my dear. They were opportunities to teach young ones important life skills, to build character, and to understand the deep connection we have with the land and with each other.</p>`;
        }
        
        // Add information about arts and crafts if available
        if (tribe.arts_and_crafts) {
            const artForms = Object.keys(tribe.arts_and_crafts);
            if (artForms.length > 0) {
                const primaryArt = artForms[0];
                story += `<p>Our people are also known for their incredible skill in ${primaryArt.toLowerCase()}. The beautiful ${primaryArt.toLowerCase()} created by our ancestors wasn't just for decoration, child. Each piece told a story, carried meaning, and connected us to our heritage in ways that words alone never could.</p>`;
            }
        }
        
        // Add information about social structure if available
        if (tribe.culture && tribe.culture.social_structure) {
            story += `<p>Our society was organized in a special way, my dear. ${tribe.culture.social_structure} This structure helped ensure that everyone had a role to play and that wisdom was shared from the elders to the young ones like you.</p>`;
        }
        
        // Add a more emotional closing
        story += `<p>These are the precious stories that have been lovingly passed down through countless generations, my dear child. Hold them close to your heart, for they are not just stories about the past - they are part of who you are today. The spirit, strength, and wisdom of the ${tribe.name} people lives on in you, and through you, will continue to shine for generations to come.</p>`;
        
        story += `<p>Now, my dear, do you understand why we must never forget where we come from? These stories are your inheritance, more precious than any treasure in the world.</p>`;
        
        return story;
    }
    
    // Display tribe information
    function displayTribeInfo(tribeName) {
        console.log('Displaying tribe info for:', tribeName);
        
        // Apply tribe color scheme
        if (window.EnhancedDesign) {
            window.EnhancedDesign.applyTribeColorScheme(tribeName);
        }
        const normalizedTribeName = tribeName.toLowerCase().trim();
        let tribe = null;
        
        // Try to find exact match first
        if (tribeData[normalizedTribeName]) {
            tribe = tribeData[normalizedTribeName];
        } else {
            // Try to find partial match
            const tribeKeys = Object.keys(tribeData);
            for (const key of tribeKeys) {
                if (key.includes(normalizedTribeName) || 
                    (tribeData[key].name && tribeData[key].name.toLowerCase().includes(normalizedTribeName))) {
                    tribe = tribeData[key];
                    break;
                }
            }
        }
        
        if (tribe) {
            console.log('Found tribe data:', tribe);
            // Show loading state
            if (tribeInfoSection) {
                tribeInfoSection.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <div class="loading-text">Gathering stories from your ancestors...</div>
                    </div>
                `;
                tribeInfoSection.classList.add('active');
            }
            
            // Simulate loading delay for better UX
            setTimeout(() => {
                // Update tribe information
                if (tribeInfoSection) {
                    tribeInfoSection.innerHTML = `
                        <div class="tribe-detail-header">
                            <h2 id="tribeTitle">${tribe.name}</h2>
                            <p id="tribeSubtitle">Location: ${tribe.location.region}</p>
                        </div>
                        <div class="tribe-return-button">
                            <button class="learn-btn" onclick="document.getElementById('tribeInfo').classList.remove('active'); window.scrollTo({top: 0, behavior: 'smooth'});">
                                <i class="fas fa-arrow-left"></i> Back to All Tribes
                            </button>
                        </div>
                        <div class="tribe-tabs">
                            <!-- Grandparent Storytelling Section -->
                            <div class="storytelling-section">
                                <div class="storyteller-header">
                                    <i class="fas fa-user-circle fa-2x"></i>
                                    <h4>As Told by Your Grandparent</h4>
                                </div>
                                <div class="storytelling-content">
                                    <p id="grandparentStory">${generateStorytellingContent(tribe)}</p>
                                </div>
                            </div>
                            
                            <!-- Tribe Details Tabs -->
                            <div class="tab-buttons">
                                <button class="tab-btn active" data-tab="overview"><i class="fas fa-eye"></i> Overview</button>
                                <button class="tab-btn" data-tab="history"><i class="fas fa-history"></i> History</button>
                                <button class="tab-btn" data-tab="culture"><i class="fas fa-users"></i> Culture</button>
                                <button class="tab-btn" data-tab="traditions"><i class="fas fa-om"></i> Traditions</button>
                                <button class="tab-btn" data-tab="arts"><i class="fas fa-paint-brush"></i> Arts & Crafts</button>
                                <button class="tab-btn" data-tab="governance"><i class="fas fa-gavel"></i> Governance</button>
                            </div>
                            
                            <div class="tab-content active" id="overview-tab">
                                <div class="grid-2">
                                    <div>
                                        <h3><i class="fas fa-map-marker-alt"></i> Location</h3>
                                        <p id="locationContent">${tribe.location.region}${tribe.location.countries ? ', ' + tribe.location.countries.join(', ') : ''}</p>
                                    </div>
                                    <div>
                                        <h3><i class="fas fa-users"></i> Population</h3>
                                        <p id="populationContent">${tribe.population || 'Information not available'}</p>
                                    </div>
                                    <div>
                                        <h3><i class="fas fa-language"></i> Languages</h3>
                                        <p id="languageContent">${tribe.languages ? tribe.languages.join(', ') : 'Information not available'}</p>
                                    </div>
                                    <div>
                                        <h3><i class="fas fa-star"></i> Key Facts</h3>
                                        <p id="factsContent">${tribe.overview || 'Information not available'}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="tab-content" id="history-tab">
                                <h3><i class="fas fa-landmark"></i> Historical Origins</h3>
                                <p id="historyContent">${tribe.history ? (tribe.history.origin || '') + ' ' + (tribe.history.colonial_impact || '') : 'Information not available'}</p>
                                
                                <h3 class="mt-3"><i class="fas fa-calendar-alt"></i> Key Historical Events</h3>
                                <ul id="eventsContent">
                                    ${tribe.history && tribe.history.key_events ? 
                                        tribe.history.key_events.map(event => `<li>${event}</li>`).join('') : 
                                        '<li>Information not available</li>'}
                                </ul>
                            </div>
                            
                            <div class="tab-content" id="culture-tab">
                                <h3><i class="fas fa-users"></i> Social Structure</h3>
                                <p id="socialStructureContent">${tribe.culture && tribe.culture.social_structure ? tribe.culture.social_structure : 'Information not available'}</p>
                                
                                <h3 class="mt-3"><i class="fas fa-pray"></i> Beliefs and Values</h3>
                                <div class="grid-2">
                                    <div>
                                        <h4>Beliefs</h4>
                                        <ul id="beliefsContent">
                                            ${tribe.culture && tribe.culture.beliefs ? 
                                                tribe.culture.beliefs.map(belief => `<li>${belief}</li>`).join('') : 
                                                '<li>Information not available</li>'}
                                        </ul>
                                    </div>
                                    <div>
                                        <h4>Values</h4>
                                        <ul id="valuesContent">
                                            ${tribe.culture && tribe.culture.values ? 
                                                tribe.culture.values.map(value => `<li>${value}</li>`).join('') : 
                                                '<li>Information not available</li>'}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="tab-content" id="traditions-tab">
                                <h3><i class="fas fa-om"></i> Ceremonies and Festivals</h3>
                                <div id="ceremoniesContent">
                                    ${tribe.traditions && tribe.traditions.ceremonies ? 
                                        tribe.traditions.ceremonies.map(ceremony => `
                                            <div class="mb-3">
                                                <h4>${ceremony.name}</h4>
                                                <p>${ceremony.description}</p>
                                            </div>
                                        `).join('') : 
                                        '<p>Information not available</p>'}
                                </div>
                                
                                <h3 class="mt-3"><i class="fas fa-ring"></i> Marriage and Rites of Passage</h3>
                                <div class="grid-2">
                                    <div>
                                        <h4>Marriage Customs</h4>
                                        <p id="marriageContent">${tribe.traditions && tribe.traditions.marriage ? tribe.traditions.marriage : 'Information not available'}</p>
                                    </div>
                                    <div>
                                        <h4>Rites of Passage</h4>
                                        <ul id="ritesContent">
                                            ${tribe.traditions && tribe.traditions.rites_of_passage ? 
                                                tribe.traditions.rites_of_passage.map(rite => `<li>${rite}</li>`).join('') : 
                                                '<li>Information not available</li>'}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="tab-content" id="arts-tab">
                                <h3><i class="fas fa-paint-brush"></i> Artistic Expressions</h3>
                                <div class="grid-2" id="artsContent">
                                    ${tribe.arts_and_crafts ? 
                                        Object.entries(tribe.arts_and_crafts).map(([key, value]) => `
                                            <div class="mb-3">
                                                <h4>${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                                                <p>${value}</p>
                                            </div>
                                        `).join('') : 
                                        '<p>Information not available</p>'}
                                </div>
                            </div>
                            
                            <div class="tab-content" id="governance-tab">
                                <h3><i class="fas fa-gavel"></i> Traditional Governance</h3>
                                <p id="governanceContent">${tribe.governance ? (tribe.governance.traditional || '') + ' ' + (tribe.governance.modern || '') : 'Information not available'}</p>
                                
                                <h3 class="mt-3"><i class="fas fa-user-tie"></i> Notable Figures</h3>
                                <ul id="figuresContent">
                                    ${tribe.notable_figures ? 
                                        tribe.notable_figures.map(figure => `<li>${figure}</li>`).join('') : 
                                        '<li>Information not available</li>'}
                                </ul>
                                
                                <h3 class="mt-3"><i class="fas fa-exclamation-triangle"></i> Contemporary Challenges</h3>
                                <ul id="challengesContent">
                                    ${tribe.challenges ? 
                                        tribe.challenges.map(challenge => `<li>${challenge}</li>`).join('') : 
                                        '<li>Information not available</li>'}
                                </ul>
                            </div>
                        </div>
                    `;
                    
                    // Initialize tabs after content is loaded
                    setTimeout(initializeTabs, 100);
                    
                    // Scroll to tribe info
                    tribeInfoSection.scrollIntoView({ behavior: 'smooth' });
                }
            }, 800);
        } else {
            console.log('Tribe not found:', tribeName);
            // Show not found message
            if (tribeInfoSection) {
                tribeInfoSection.innerHTML = `
                    <div class="error-message" style="background: #f8d7da; color: #721c24; padding: 2rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #f5c6cb;">
                        <h3><i class="fas fa-exclamation-triangle"></i> Tribe Not Found</h3>
                        <p>Sorry, information about the "${tribeName}" tribe is not available in our database. Please try another tribe name.</p>
                        <button class="learn-btn" onclick="document.getElementById('tribeInfo').classList.remove('active'); window.scrollTo({top: 0, behavior: 'smooth'});">
                            <i class="fas fa-arrow-left"></i> Back to All Tribes
                        </button>
                    </div>
                `;
                tribeInfoSection.classList.add('active');
                tribeInfoSection.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }
    
    // Display all tribes with enhanced cards
    function displayAllTribes(tribesToShow) {
        console.log('Displaying tribes:', tribesToShow.length);
        
        // Check if tribesToShow is valid
        if (!tribesToShow || !Array.isArray(tribesToShow)) {
            console.error('Invalid tribes data provided to displayAllTribes');
            return;
        }
        
        // Sort tribes based on selected criteria
        const sortBy = tribeSortSelect ? tribeSortSelect.value : 'name';
        let sortedTribes = [...tribesToShow];
        
        switch (sortBy) {
            case 'name':
                sortedTribes.sort((a, b) => a.name.localeCompare(b.name));
                break;
            case 'population':
                sortedTribes.sort((a, b) => {
                    // Extract population numbers for comparison
                    const getPopulationNumber = (tribe) => {
                        if (!tribe.population) return 0;
                        const populationText = tribe.population.toLowerCase();
                        if (populationText.includes('million')) {
                            const match = populationText.match(/([0-9.]+)\s*million/);
                            return match ? parseFloat(match[1]) * 1000000 : 0;
                        } else if (populationText.includes('thousand')) {
                            const match = populationText.match(/([0-9.]+)\s*thousand/);
                            return match ? parseFloat(match[1]) * 1000 : 0;
                        } else {
                            const match = populationText.match(/([0-9,]+)/);
                            return match ? parseInt(match[1].replace(/,/g, '')) : 0;
                        }
                    };
                    return getPopulationNumber(b) - getPopulationNumber(a);
                });
                break;
            case 'region':
                sortedTribes.sort((a, b) => {
                    if (!a.location || !b.location) return 0;
                    return a.location.region.localeCompare(b.location.region);
                });
                break;
        }
        
        // Check if allTribesGrid exists
        if (!allTribesGrid) {
            console.error('allTribesGrid element not found');
            return;
        }
        
        allTribesGrid.innerHTML = '';
        
        // Show a message if no tribes found
        if (sortedTribes.length === 0) {
            allTribesGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 8px;">
                    <h3><i class="fas fa-search"></i> No Tribes Found</h3>
                    <p>Try adjusting your search or filter criteria</p>
                </div>
            `;
            return;
        }
        
        sortedTribes.forEach((tribe, index) => {
            // Validate tribe data
            if (!tribe || !tribe.name) {
                console.warn('Skipping invalid tribe data at index:', index);
                return;
            }
            
            const tribeCard = document.createElement('div');
            tribeCard.className = 'tribe-card';
            tribeCard.onclick = () => {
                console.log('Tribe card clicked:', tribe.name);
                searchTribe(tribe.name);
            };
            tribeCard.innerHTML = `
                <div class="tribe-card-image">
                    <i class="fas fa-users"></i>
                </div>
                <div class="tribe-card-content">
                    <h3>${tribe.name}</h3>
                    <p>${tribe.overview ? tribe.overview.substring(0, 120) + '...' : 'Explore the rich heritage of this tribe'}</p>
                    <span class="tribe-region">${tribe.location ? tribe.location.region : 'Location not available'}</span>
                </div>
            `;
            allTribesGrid.appendChild(tribeCard);
        });
        
        console.log('Finished displaying', sortedTribes.length, 'tribes');
    }
    
    // Filter tribes based on search input
    function filterTribes() {
        if (!tribeFilterInput || !allTribes) return;
        
        const filterValue = tribeFilterInput.value.toLowerCase();
        const filteredTribes = allTribes.filter(tribe => 
            tribe.name.toLowerCase().includes(filterValue) ||
            (tribe.location && tribe.location.region.toLowerCase().includes(filterValue)) ||
            (tribe.overview && tribe.overview.toLowerCase().includes(filterValue))
        );
        displayAllTribes(filteredTribes);
    }
    
    // Advanced search function
    function advancedSearch() {
        console.log('Advanced search initiated');
        if (!allTribes) {
            console.log('No tribe data available');
            return;
        }
        
        const tribeName = tribeNameInput ? tribeNameInput.value.trim() : '';
        const region = tribeRegionSelect ? tribeRegionSelect.value : '';
        const population = tribePopulationSelect ? tribePopulationSelect.value : '';
        const frenchChecked = frenchLanguageCheckbox ? frenchLanguageCheckbox.checked : false;
        const englishChecked = englishLanguageCheckbox ? englishLanguageCheckbox.checked : false;
        
        console.log('Search parameters:', { tribeName, region, population, frenchChecked, englishChecked });
        
        // If searching for a specific tribe name, display its info directly
        if (tribeName && tribeName.length > 0) {
            console.log('Searching for specific tribe:', tribeName);
            displayTribeInfo(tribeName);
            return;
        }
        
        let filteredTribes = [...allTribes]; // Create a copy of all tribes
        
        // Filter by region with enhanced matching
        if (region) {
            filteredTribes = filteredTribes.filter(tribe => {
                if (!tribe.location) return false;
                
                // Handle different region matching patterns
                const tribeRegion = tribe.location.region.toLowerCase();
                const filterRegion = region.toLowerCase();
                
                // Enhanced matching for various region patterns
                // Check for exact match, partial match, or if the tribe region contains any part of the filter
                return tribeRegion.includes(filterRegion) || 
                       filterRegion.includes(tribeRegion) ||
                       tribeRegion.split(' ').some(word => filterRegion.includes(word)) ||
                       filterRegion.split(' ').some(word => tribeRegion.includes(word)) ||
                       // Special handling for common region variations
                       (filterRegion === 'north' && (tribeRegion.includes('northern') || tribeRegion.includes('north region'))) ||
                       (filterRegion === 'west' && (tribeRegion.includes('western') || tribeRegion.includes('west region'))) ||
                       (filterRegion === 'south' && (tribeRegion.includes('southern') || tribeRegion.includes('south region'))) ||
                       (filterRegion === 'east' && (tribeRegion.includes('eastern') || tribeRegion.includes('east region'))) ||
                       (filterRegion === 'center' && (tribeRegion.includes('central') || tribeRegion.includes('centre')));
            });
        }
        
        // Filter by population size
        if (population) {
            filteredTribes = filteredTribes.filter(tribe => {
                if (!tribe.population) return false;
                
                // Extract numeric value from population string
                const populationText = tribe.population.toLowerCase();
                let populationNumber = 0;
                
                // Handle different population formats
                if (populationText.includes('million')) {
                    const match = populationText.match(/([0-9.]+)\s*million/);
                    if (match) {
                        populationNumber = parseFloat(match[1]) * 1000000;
                    }
                } else if (populationText.includes('thousand')) {
                    const match = populationText.match(/([0-9.]+)\s*thousand/);
                    if (match) {
                        populationNumber = parseFloat(match[1]) * 1000;
                    }
                } else {
                    // Try to extract any numeric value
                    const match = populationText.match(/([0-9,]+)/);
                    if (match) {
                        populationNumber = parseInt(match[1].replace(/,/g, ''));
                    }
                }
                
                // Apply population filters
                switch (population) {
                    case 'small':
                        return populationNumber < 100000;
                    case 'medium':
                        return populationNumber >= 100000 && populationNumber < 500000;
                    case 'large':
                        return populationNumber >= 500000 && populationNumber < 1000000;
                    case 'very-large':
                        return populationNumber >= 1000000;
                    default:
                        return true;
                }
            });
        }
        
        // Filter by language preference with enhanced detection
        if (frenchChecked || englishChecked) {
            filteredTribes = filteredTribes.filter(tribe => {
                if (!tribe.languages || tribe.languages.length === 0) return false;
                
                const hasFrench = tribe.languages.some(lang => {
                    const lowerLang = lang.toLowerCase();
                    return lowerLang.includes('french') || 
                           lowerLang.includes('français') || 
                           lowerLang.includes('francais') || 
                           lowerLang.includes('fr') ||
                           lowerLang.includes('français') ||
                           lowerLang.includes('camfranglais') ||
                           (lowerLang.includes('fr') && !lowerLang.includes('english'));
                });
                
                const hasEnglish = tribe.languages.some(lang => {
                    const lowerLang = lang.toLowerCase();
                    return lowerLang.includes('english') || 
                           lowerLang.includes('anglais') || 
                           lowerLang.includes('en') ||
                           lowerLang.includes('pidgin') ||
                           lowerLang.includes('cameroonian english') ||
                           lowerLang.includes('cameroonian pidgin english') ||
                           (lowerLang.includes('en') && !lowerLang.includes('french'));
                });
                
                // If both checkboxes are checked, show tribes with either language
                if (frenchChecked && englishChecked) {
                    return hasFrench || hasEnglish;
                } 
                // If only French is checked
                else if (frenchChecked) {
                    return hasFrench;
                } 
                // If only English is checked
                else if (englishChecked) {
                    return hasEnglish;
                }
                return false;
            });
        }
        
        console.log('Filtered tribes count:', filteredTribes.length);
        displayAllTribes(filteredTribes);
    }
    
    // Handle search button click
    if (searchTribeBtn) {
        console.log('Search button found, attaching event listener');
        searchTribeBtn.addEventListener('click', function(e) {
            console.log('Search button clicked');
            e.preventDefault();
            console.log('Calling advancedSearch');
            advancedSearch();
        });
    } else {
        console.error('Search button not found');
    }
    
    // Handle Enter key in search input
    if (tribeNameInput) {
        tribeNameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                console.log('Enter key pressed in search input');
                advancedSearch();
            }
        });
    } else {
        console.error('Tribe name input not found');
    }
    
    // Add event listener for filter input
    if (tribeFilterInput) {
        tribeFilterInput.addEventListener('input', filterTribes);
    } else {
        console.error('Tribe filter input not found');
    }
    
    // Add event listeners for checkboxes
    if (frenchLanguageCheckbox) {
        frenchLanguageCheckbox.addEventListener('change', advancedSearch);
    } else {
        console.error('French language checkbox not found');
    }
    
    if (englishLanguageCheckbox) {
        englishLanguageCheckbox.addEventListener('change', advancedSearch);
    } else {
        console.error('English language checkbox not found');
    }
    
    // Add event listener for region select
    if (tribeRegionSelect) {
        tribeRegionSelect.addEventListener('change', advancedSearch);
    } else {
        console.error('Tribe region select not found');
    }
    
    // Add event listener for population select
    if (tribePopulationSelect) {
        tribePopulationSelect.addEventListener('change', advancedSearch);
    } else {
        console.error('Tribe population select not found');
    }
    
    // Add event listener for sort select
    if (tribeSortSelect) {
        tribeSortSelect.addEventListener('change', function() {
            console.log('Sort option changed');
            // Re-display all tribes with new sorting
            displayAllTribes(allTribes);
        });
    } else {
        console.error('Tribe sort select not found');
    }
    
    // Make searchTribe function globally available
    window.searchTribe = searchTribe;
    
    // Add global function for external access
    window.TribeForum = {
        searchTribe: searchTribe,
        displayTribeInfo: displayTribeInfo
    };
});