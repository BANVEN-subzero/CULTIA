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
        'Grassfields': ['Northwest Region', 'West Region'],
        'Coastal': ['Littoral Region', 'Southwest Region'],
        'Forest': ['Centre Region', 'South Region', 'East Region'],
        'Sahel': ['Adamawa Region', 'North Region', 'Far North Region']
    };

    // Mock Data: Exact user data
    const mockTribesData = {
        tribes: {
            // 1. West Region
            bamileke: {
                name: "Bamileke",
                location: { region: "West Region" },
                overview: "Nyang Nyang festival dancers marching in Bafoussam.",
                traditions: "Nyang Nyang festival dancers marching in Bafoussam.",
                traditional_meals: ["Ndolé", "Koki", "Eru"],
                image_url: "https://www.shutterstock.com/shutterstock/photos/2261864835/display_1500/stock-photo-bafoussam-west-cameroon-february-youthis-painted-in-festival-colors-parade-at-nyang-2261864835.jpg"
            },
            bamun: {
                name: "Bamun",
                location: { region: "West Region" },
                overview: "Biannual Nguon cultural festival outside the Foumban Royal Palace.",
                traditions: "Biannual Nguon cultural festival outside the Foumban Royal Palace.",
                traditional_meals: ["Fufu corn", "Koki", "Vegetable soups"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/b/b3/Parade_au_Ngouon_2018.jpg"
            },
            menoua: {
                name: "Menoua",
                location: { region: "West Region" },
                overview: "Intricate, hand-woven royal Ndop fabric from Dschang.",
                traditions: "Intricate, hand-woven royal Ndop fabric from Dschang.",
                traditional_meals: ["Ndolé", "Plantains", "Vegetable dishes"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/e/e0/Ndop_Fabric_Cameroon.jpg"
            },
            // 2. Centre Region
            "beti-bassa": {
                name: "Beti-Bassa (Ewondo/Bulu)",
                location: { region: "Centre Region" },
                overview: "Traditional forest region festive wear woven from local plant materials.",
                culture: "Traditional forest region festive wear woven from local plant materials.",
                traditional_meals: ["Poulet DG", "Plantains with groundnuts", "Mbongo tchobi"],
                image_url: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhw2HQG5pmj2-8Nc9HC0mWt2RyWqGf7CO2AIkiTcjlM0CGJOmbsxrFlyjSF6HOe-tqvLxBdNJ6agjaetnE5E-gXwkrplHDTdVHE1pbhLioKzfS85atHgSyxUOxFk7zleVA4txEJ2rEwv8M/s1600/pulch%25C3%25A9rie+en+pied-nzoubou.jpg"
            },
            fang: {
                name: "Fang",
                location: { region: "Centre Region" },
                overview: "Museum documentary image of an antique hand-carved wood ancestral mask.",
                traditions: "Museum documentary image of an antique hand-carved wood ancestral mask.",
                traditional_meals: ["Poulet DG", "Yam dishes", "Vegetable soups"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/0/07/Fang_mask_tellem.jpg"
            },
            ewondo: {
                name: "Ewondo",
                location: { region: "Centre Region" },
                overview: "Traditional elders performing using instruments inside local community chiefdoms.",
                traditions: "Traditional elders performing using instruments inside local community chiefdoms.",
                traditional_meals: ["Plantain dishes", "Vegetable soups", "Local staples"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/a/ab/Ewondo_Elders_Gathering.jpg"
            },
            // 3. Littoral Region
            sawa: {
                name: "Sawa (Coastal Peoples)",
                location: { region: "Littoral Region" },
                overview: "Traditional Sawa paddlers racing across the Wouri River during the Ngondo festival.",
                traditions: "Traditional Sawa paddlers racing across the Wouri River during the Ngondo festival.",
                traditional_meals: ["Fresh fish with plantains", "Coconut-based dishes", "Njangi"],
                image_url: "https://www.shutterstock.com/shutterstock/photos/2397750711/display_1500/stock-photo-douala-littoral-region-cameroon-december-paddlers-parade-on-the-wouri-river-in-douala-2397750711.jpg"
            },
            duala: {
                name: "Duala",
                location: { region: "Littoral Region" },
                overview: "Sawa women processing in their grand, flowing traditional Kaba Ngondo silk gowns.",
                traditions: "Sawa women processing in their grand, flowing traditional Kaba Ngondo silk gowns.",
                traditional_meals: ["Fresh fish", "Coconut rice", "Plantain dishes"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/a/a2/Femmes_Sawa_en_Kaba.jpg"
            },
            bassa: {
                name: "Bassa",
                location: { region: "Littoral Region" },
                overview: "Energetic Assiko dance performance featuring acoustic guitars and rhythmic precision.",
                traditions: "Energetic Assiko dance performance featuring acoustic guitars and rhythmic precision.",
                traditional_meals: ["Cassava-based dishes", "Smoked fish", "Bitterleaf soup"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/e/e9/Assiko_Dance_Littoral.jpg"
            },
            // 4. Northwest Region
            kom: {
                name: "Kom",
                location: { region: "Northwest Region" },
                overview: "Structural architecture of the royal palace thatch-work compound in Laikom.",
                traditions: "Structural architecture of the royal palace thatch-work compound in Laikom.",
                traditional_meals: ["Fufu corn", "Eru", "Koki"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/e/eb/Palais_du_Fon_de_Kom.jpg"
            },
            nso: {
                name: "Nso",
                location: { region: "Northwest Region" },
                overview: "Nso citizens adorned in authentic hand-stitched geometric Toghu garments.",
                traditions: "Nso citizens adorned in authentic hand-stitched geometric Toghu garments.",
                traditional_meals: ["Abacha", "Fufu", "Bitterleaf soup"],
                image_url: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhSmD27Ri87vChX7rJcarfXGwy-rK1A0RNUgjitMy_g3kU1bbLWfY1Y80zJZOIdmxO00eKJllT2zg3Xt-MbyWq24KHHyOTm7nX2CUvmcTXou_nZ2yw9uHUZxeiE4CCS6ZnicZQXeDI-R3UN/s1600/15777048_10209905030934154_7406994988728947858_o+nso.jpg"
            },
            bali: {
                name: "Bali",
                location: { region: "Northwest Region" },
                overview: "Annual Lela royal festival featuring warriors in traditional feathered headdresses.",
                traditions: "Annual Lela royal festival featuring warriors in traditional feathered headdresses.",
                traditional_meals: ["Fufu corn", "Koki", "Vegetable soup"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/1/14/Lela_Festival_Bali_Nyonga.jpg"
            },
            // 5. Southwest Region
            bakweri: {
                name: "Bakweri",
                location: { region: "Southwest Region" },
                overview: "Famous elephant dance Male society members clad in traditional environmental fibers.",
                traditions: "Famous elephant dance Male society members clad in traditional environmental fibers.",
                traditional_meals: ["Eru with waterfufu", "Koki beans", "Fish stew"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/4/4b/Male_Dance_Bakweri.jpg"
            },
            bakossi: {
                name: "Bakossi",
                location: { region: "Southwest Region" },
                overview: "The sacred twin crater lakes of Mount Manenguba, deeply revered by the Bakossi.",
                traditions: "The sacred twin crater lakes of Mount Manenguba, deeply revered by the Bakossi.",
                traditional_meals: ["Eru", "Waterfufu", "Vegetable stews"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/5/52/Lac_m%C3%A2le_et_lac_femelle_du_Mont_Manenguba.jpg"
            },
            tiv: {
                name: "Tiv",
                location: { region: "Southwest Region" },
                overview: "Distinct black-and-white striped Anger textile traditional wraps unique to this community.",
                traditions: "Distinct black-and-white striped Anger textile traditional wraps unique to this community.",
                traditional_meals: ["Yam-based dishes", "Vegetable soups", "Local staples"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/2/23/Tiv_Traditional_Anger_Fabric.jpg"
            },
            // 6. Adamawa Region
            fulani: {
                name: "Fulani (Fulbe)",
                location: { region: "Adamawa Region" },
                overview: "Majestic Northern equestrian culture with riders clad in flowing grand boubous.",
                culture: "Majestic Northern equestrian culture with riders clad in flowing grand boubous.",
                traditional_meals: ["Milk and dairy products", "Grilled meat", "Fura da nono"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/d/da/Fantasia_Cameroun.jpg"
            },
            tikar: {
                name: "Tikar",
                location: { region: "Adamawa Region" },
                overview: "Tikar bronze-smithing artisans pouring molten metal using ancestral clay molds.",
                traditions: "Tikar bronze-smithing artisans pouring molten metal using ancestral clay molds.",
                traditional_meals: ["Corn dishes", "Soup-based meals", "Local vegetables"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/9/90/Artisanat_Tikar_Foumban.jpg"
            },
            mbum: {
                name: "Mbum",
                location: { region: "Adamawa Region" },
                overview: "Traditional regional grain storage architecture built out of local clay and thatch roofs.",
                traditions: "Traditional regional grain storage architecture built out of local clay and thatch roofs.",
                traditional_meals: ["Local staples", "Traditional dishes", "Vegetables"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/2/28/Greniers_traditionnels_Mbum.jpg"
            },
            // 7. Far North Region
            kanuri: {
                name: "Kanuri",
                location: { region: "Far North Region" },
                overview: "Long white Sahelian turbans and embroidery styles worn during regional court parades.",
                traditions: "Long white Sahelian turbans and embroidery styles worn during regional court parades.",
                traditional_meals: ["Tuwo", "Miyan kuka", "Kosai"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/6/66/Chefferie_Kanuri_Far_North.jpg"
            },
            mandara: {
                name: "Mandara",
                location: { region: "Far North Region" },
                overview: "Grand sultanate structural walls and historic guard armor styles found inside Mora.",
                traditions: "Grand sultanate structural walls and historic guard armor styles found inside Mora.",
                traditional_meals: ["Sorghum-based dishes", "Local stews", "Dairy products"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/3/30/Sultanat_de_Mora_Mandara.jpg"
            },
            mafa: {
                name: "Mafa",
                location: { region: "Far North Region" },
                overview: "Dry-stone agricultural terraced hillsides running across the Mandara Mountains.",
                traditions: "Dry-stone agricultural terraced hillsides running across the Mandara Mountains.",
                traditional_meals: ["Sorghum", "Millet", "Local vegetables"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/4/4c/Paysage_Mafa_Monts_Mandara.jpg"
            },
            // 8. East Region
            sara: {
                name: "Sara",
                location: { region: "East Region" },
                overview: "Savanna-edge fishing communities operating handmade canoes across local rivers.",
                traditions: "Savanna-edge fishing communities operating handmade canoes across local rivers.",
                traditional_meals: ["Local staples", "Vegetable dishes", "Soups"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/0/01/Pirogues_Sara_Est.jpg"
            },
            gbaya: {
                name: "Gbaya",
                location: { region: "East Region" },
                overview: "Unique architecture of traditional oval earthen homes native to East Cameroon.",
                traditions: "Unique architecture of traditional oval earthen homes native to East Cameroon.",
                traditional_meals: ["Cassava dishes", "Vegetable soups", "Local staples"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/4/47/Case_traditionnelle_Gbaya.jpg"
            },
            mandjia: {
                name: "Mandjia",
                location: { region: "East Region" },
                overview: "Savanna transition farming community processing agricultural crops using hand-woven trays.",
                traditions: "Savanna transition farming community processing agricultural crops using hand-woven trays.",
                traditional_meals: ["Local staples", "Vegetable dishes", "Soups"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/3/3a/Recolte_Mandjia_Est.jpg"
            },
            // 9. North Region
            mada: {
                name: "Mada",
                location: { region: "North Region" },
                overview: "Traditional musicians performing outdoors using beautifully crafted, long wooden horns.",
                traditions: "Traditional musicians performing outdoors using beautifully crafted, long wooden horns.",
                traditional_meals: ["Sorghum dishes", "Local stews", "Dairy products"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/5/5e/Musiciens_Mada_Nord.jpg"
            },
            guiziga: {
                name: "Guiziga",
                location: { region: "North Region" },
                overview: "Community members dancing in unison inside local clay-walled compounds during harvest time.",
                traditions: "Community members dancing in unison inside local clay-walled compounds during harvest time.",
                traditional_meals: ["Local staples", "Vegetable dishes", "Soups"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/d/df/Danse_Guiziga.jpg"
            },
            dagara: {
                name: "Dagara",
                location: { region: "North Region" },
                overview: "Artisan hands shaping regional patterned earthenware pottery using open fires.",
                traditions: "Artisan hands shaping regional patterned earthenware pottery using open fires.",
                traditional_meals: ["Sorghum dishes", "Local staples", "Vegetable soups"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/b/b8/Poterie_Dagara_Nord.jpg"
            },
            // 10. South Region
            bulu: {
                name: "Bulu",
                location: { region: "South Region" },
                overview: "Deep-forest musical instruments including carved log drums used to pass messages.",
                traditions: "Deep-forest musical instruments including carved log drums used to pass messages.",
                traditional_meals: ["Plantain dishes", "Vegetable soups", "Local staples"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/b/ba/Tambour_d_avertissement_Bulu.jpg"
            },
            "fang-south": {
                name: "Fang (South)",
                location: { region: "South Region" },
                overview: "An elder carrying the traditional stringed Mvet harp-lute instrument.",
                traditions: "An elder carrying the traditional stringed Mvet harp-lute instrument.",
                traditional_meals: ["Yam dishes", "Plantain dishes", "Vegetable soups"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/2/24/Joueur_de_Mvet_Fang.jpg"
            },
            pov: {
                name: "Pov",
                location: { region: "South Region" },
                overview: "Thick, dense equatorial primary jungle paths typical of native Pov territories.",
                traditions: "Thick, dense equatorial primary jungle paths typical of native Pov territories.",
                traditional_meals: ["Local staples", "Vegetable dishes", "Soups"],
                image_url: "https://upload.wikimedia.org/wikipedia/commons/1/1d/Foret_Equatoriale_Sud_Cameroun.jpg"
            }
        }
    };

    /**
     * Load Tribes - Directly use mock data
     */
    async function loadTribes() {
        allTribes = Object.values(mockTribesData.tribes).map(tribe => {
            return {
                ...tribe,
                name: tribe.name,
                overview: tribe.overview,
                location: tribe.location,
                customs_and_traditions: (() => {
                    let val = tribe.customs_and_traditions || (tribe.traditions ? (typeof tribe.traditions === 'string' ? [tribe.traditions] : tribe.traditions) : (tribe.culture ? (typeof tribe.culture === 'string' ? [tribe.culture] : tribe.culture) : []));
                    return Array.isArray(val) ? val : (val ? [val] : []);
                })(),
                meals_and_cuisine_list: (() => {
                    let val = tribe.meals_and_cuisine_list || tribe.traditional_meals || [];
                    return Array.isArray(val) ? val : (val ? [val] : []);
                })(),
                festivals_list: (() => {
                    let val = tribe.festivals_list || [];
                    return Array.isArray(val) ? val : (val ? [val] : []);
                })()
            };
        });
        renderTribeGrid('all');
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
            // For this version, we'll use the same API fallback as before, but we'll prioritize local legends
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
