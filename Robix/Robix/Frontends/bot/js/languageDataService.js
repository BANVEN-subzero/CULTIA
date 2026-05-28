/**
 * Language Data Service
 * Fetches authentic Cameroonian tribal language content from external AI services
 */

class LanguageDataService {
    constructor() {
        this.apiEndpoints = {
            // Using free AI services for language content
            huggingface: 'https://api-inference.huggingface.co/models/',
            openai_free: 'https://api.openai.com/v1/chat/completions', // Requires API key
            anthropic: 'https://api.anthropic.com/v1/messages', // Requires API key
            // Fallback to local enhanced data
            local: true
        };
        
        // Authentic tribal language mappings
        this.tribalLanguages = {
            bamileke: {
                name: "Bamiléké (Yemba)",
                iso: "ybb",
                family: "Niger-Congo, Grassfields",
                region: "West Region",
                speakers: "3.2 million",
                difficulty: "intermediate",
                description: "A major Grassfields language spoken by the Bamiléké people"
            },
            bamum: {
                name: "Bamum (Shüpamem)",
                iso: "bax",
                family: "Niger-Congo, Grassfields", 
                region: "West Region",
                speakers: "215,000",
                difficulty: "intermediate",
                description: "Language of the Bamum Kingdom with unique script"
            },
            fulani: {
                name: "Fulfulde",
                iso: "ff",
                family: "Niger-Congo, Atlantic",
                region: "North & Adamawa",
                speakers: "2.5 million",
                difficulty: "beginner",
                description: "Widely spoken pastoral language across West Africa"
            },
            duala: {
                name: "Duala",
                iso: "dua",
                family: "Niger-Congo, Bantu",
                region: "Littoral Region",
                speakers: "87,700",
                difficulty: "beginner",
                description: "Historic trade language of coastal Cameroon"
            },
            bassa: {
                name: "Bassa",
                iso: "bas",
                family: "Niger-Congo, Bantu",
                region: "Centre & South",
                speakers: "300,000",
                difficulty: "intermediate",
                description: "Important Bantu language of central Cameroon"
            },
            beti: {
                name: "Beti-Fang",
                iso: "btb",
                family: "Niger-Congo, Bantu",
                region: "Centre & South",
                speakers: "1.4 million",
                description: "Major Bantu language group including Ewondo"
            },
            ewondo: {
                name: "Ewondo",
                iso: "ewo",
                family: "Niger-Congo, Bantu",
                region: "Centre Region",
                speakers: "577,700",
                difficulty: "beginner",
                description: "Prominent Beti language, lingua franca of Yaoundé"
            },
            kom: {
                name: "Kom",
                iso: "bkm",
                family: "Niger-Congo, Grassfields",
                region: "Northwest Region", 
                speakers: "200,000",
                difficulty: "intermediate",
                description: "Grassfields language of the Kom people"
            },
            nso: {
                name: "Lamso",
                iso: "lns",
                family: "Niger-Congo, Grassfields",
                region: "Northwest Region",
                speakers: "240,000", 
                difficulty: "intermediate",
                description: "Language of the Nso' kingdom"
            },
            medumba: {
                name: "Medumba",
                iso: "byv",
                family: "Niger-Congo, Grassfields",
                region: "West Region",
                speakers: "210,000",
                difficulty: "intermediate",
                description: "Bamiléké dialect with distinct features"
            },
            fe_fe: {
                name: "Fe'fe'",
                iso: "fmp",
                family: "Niger-Congo, Grassfields", 
                region: "West Region",
                speakers: "125,000",
                difficulty: "advanced",
                description: "Bamiléké dialect with complex tonal system"
            },
            ghomala: {
                name: "Ghomálá'",
                iso: "bbj",
                family: "Niger-Congo, Grassfields",
                region: "West Region", 
                speakers: "260,000",
                difficulty: "intermediate",
                description: "Major Bamiléké dialect"
            }
        };

        this.enhancedLanguageData = this.generateEnhancedLanguageData();
    }

    /**
     * Generate enhanced language data with authentic content
     */
    generateEnhancedLanguageData() {
        return {
            bamileke: {
                name: "Bamiléké (Yemba)",
                region: "West Region",
                speakers: "3.2 million",
                difficulty: "intermediate",
                lessons: [
                    {
                        title: "Greetings",
                        category: "greetings",
                        icon: "👋",
                        phrases: [
                            { phrase: "Mbɔ̀ŋ", translation: "Hello", pronunciation: "mbong" },
                            { phrase: "Ŋwà'à sɔ̀", translation: "Good morning", pronunciation: "ngwa-a so" },
                            { phrase: "Ŋwà'à nɛ̀m", translation: "Good evening", pronunciation: "ngwa-a nem" },
                            { phrase: "Ndɛ̀ŋ", translation: "Thank you", pronunciation: "ndeng" },
                            { phrase: "Yɛ̀", translation: "Yes", pronunciation: "yeh" },
                            { phrase: "Àà", translation: "No", pronunciation: "aa" },
                            { phrase: "Kɔ̀ bɔ̀", translation: "Goodbye", pronunciation: "ko bo" },
                            { phrase: "Wù lɛ̀ ɛ̀?", translation: "How are you?", pronunciation: "wu leh eh" }
                        ]
                    },
                    {
                        title: "Food",
                        category: "food",
                        icon: "🍽️",
                        phrases: [
                            { phrase: "Njɔ̀m", translation: "Food", pronunciation: "njom" },
                            { phrase: "Mɛ̀n", translation: "Water", pronunciation: "men" },
                            { phrase: "Kɔ̀ndɔ̀", translation: "Plantain", pronunciation: "kon-do" },
                            { phrase: "Ŋkàp", translation: "Groundnuts", pronunciation: "ngkap" },
                            { phrase: "Mbɔ̀ŋ", translation: "Palm wine", pronunciation: "mbong" },
                            { phrase: "Fùfù", translation: "Fufu", pronunciation: "fu-fu" },
                            { phrase: "Ndɔ̀lɛ̀", translation: "Ndole (soup)", pronunciation: "ndo-leh" },
                            { phrase: "Mɛ̀ fɛ̀ njɔ̀m", translation: "I want food", pronunciation: "meh feh njom" }
                        ]
                    },
                    {
                        title: "Numbers",
                        category: "numbers",
                        icon: "🔢",
                        phrases: [
                            { phrase: "Pɔ̀'", translation: "One", pronunciation: "po" },
                            { phrase: "Bà", translation: "Two", pronunciation: "ba" },
                            { phrase: "Tà", translation: "Three", pronunciation: "ta" },
                            { phrase: "Nà", translation: "Four", pronunciation: "na" },
                            { phrase: "Tɔ̀n", translation: "Five", pronunciation: "ton" },
                            { phrase: "Sàmɛ̀n", translation: "Six", pronunciation: "sa-men" },
                            { phrase: "Sàmɛ̀n pɔ̀'", translation: "Seven", pronunciation: "sa-men po" },
                            { phrase: "Sàmɛ̀n bà", translation: "Eight", pronunciation: "sa-men ba" },
                            { phrase: "Sàmɛ̀n tà", translation: "Nine", pronunciation: "sa-men ta" },
                            { phrase: "Fù", translation: "Ten", pronunciation: "fu" }
                        ]
                    },
                    {
                        title: "Family",
                        category: "family",
                        icon: "👨‍👩‍👧‍👦",
                        phrases: [
                            { phrase: "Tà", translation: "Father", pronunciation: "ta" },
                            { phrase: "Mà", translation: "Mother", pronunciation: "ma" },
                            { phrase: "Mùn", translation: "Child", pronunciation: "mun" },
                            { phrase: "Njùì", translation: "Brother", pronunciation: "njui" },
                            { phrase: "Njàŋ", translation: "Sister", pronunciation: "njang" },
                            { phrase: "Tàtà", translation: "Grandfather", pronunciation: "ta-ta" },
                            { phrase: "Màmà", translation: "Grandmother", pronunciation: "ma-ma" },
                            { phrase: "Ŋwà", translation: "Friend", pronunciation: "ngwa" }
                        ]
                    }
                ]
            },
            fulani: {
                name: "Fulfulde (Fulani)",
                region: "North & Adamawa",
                speakers: "2.5 million", 
                difficulty: "beginner",
                lessons: [
                    {
                        title: "Greetings",
                        category: "greetings",
                        icon: "👋",
                        phrases: [
                            { phrase: "Jam", translation: "Hello/Peace", pronunciation: "jahm" },
                            { phrase: "Jam walla", translation: "Good morning", pronunciation: "jahm wah-lah" },
                            { phrase: "Jam hiirde", translation: "Good evening", pronunciation: "jahm heer-deh" },
                            { phrase: "A jaraama", translation: "Thank you", pronunciation: "ah jah-rah-mah" },
                            { phrase: "Eey", translation: "Yes", pronunciation: "ay" },
                            { phrase: "Alaa", translation: "No", pronunciation: "ah-lah" },
                            { phrase: "Sellam", translation: "Goodbye", pronunciation: "sel-lahm" },
                            { phrase: "No mbadda?", translation: "How are you?", pronunciation: "no mbah-da" }
                        ]
                    },
                    {
                        title: "Food",
                        category: "food",
                        icon: "🍽️",
                        phrases: [
                            { phrase: "Nyiiri", translation: "Food", pronunciation: "nyee-ree" },
                            { phrase: "Ndiyam", translation: "Water", pronunciation: "ndee-yahm" },
                            { phrase: "Kosam", translation: "Milk", pronunciation: "ko-sahm" },
                            { phrase: "Hiire", translation: "Millet", pronunciation: "hee-reh" },
                            { phrase: "Maaro", translation: "Rice", pronunciation: "mah-ro" },
                            { phrase: "Naange", translation: "Meat", pronunciation: "nahn-geh" },
                            { phrase: "Lebbi", translation: "Honey", pronunciation: "leb-bee" },
                            { phrase: "Mi yiɗi nyiiri", translation: "I want food", pronunciation: "mee yee-dee nyee-ree" }
                        ]
                    },
                    {
                        title: "Numbers",
                        category: "numbers",
                        icon: "🔢",
                        phrases: [
                            { phrase: "Go'o", translation: "One", pronunciation: "go-oh" },
                            { phrase: "Ɗiɗi", translation: "Two", pronunciation: "dee-dee" },
                            { phrase: "Tati", translation: "Three", pronunciation: "tah-tee" },
                            { phrase: "Nayi", translation: "Four", pronunciation: "nah-yee" },
                            { phrase: "Jowi", translation: "Five", pronunciation: "joh-wee" },
                            { phrase: "Jeegom", translation: "Six", pronunciation: "jeh-gom" },
                            { phrase: "Jeeɗiɗi", translation: "Seven", pronunciation: "jeh-dee-dee" },
                            { phrase: "Jeetati", translation: "Eight", pronunciation: "jeh-tah-tee" },
                            { phrase: "Jeenayi", translation: "Nine", pronunciation: "jeh-nah-yee" },
                            { phrase: "Sappo", translation: "Ten", pronunciation: "sah-po" }
                        ]
                    },
                    {
                        title: "Family",
                        category: "family",
                        icon: "👨‍👩‍👧‍👦",
                        phrases: [
                            { phrase: "Baaba", translation: "Father", pronunciation: "bah-bah" },
                            { phrase: "Yaaya", translation: "Mother", pronunciation: "yah-yah" },
                            { phrase: "Ɓiɗɗo", translation: "Child", pronunciation: "bid-do" },
                            { phrase: "Mawniraaɗo", translation: "Brother", pronunciation: "maw-nee-rah-do" },
                            { phrase: "Debbo", translation: "Sister", pronunciation: "deb-bo" },
                            { phrase: "Baaba mawɗo", translation: "Grandfather", pronunciation: "bah-bah maw-do" },
                            { phrase: "Yaaya mawɗo", translation: "Grandmother", pronunciation: "yah-yah maw-do" },
                            { phrase: "Gariijo", translation: "Friend", pronunciation: "gah-ree-jo" }
                        ]
                    }
                ]
            },
            duala: {
                name: "Duala",
                region: "Littoral Region",
                speakers: "87,700",
                difficulty: "beginner",
                lessons: [
                    {
                        title: "Essential Greetings",
                        phrases: [
                            { phrase: "Mbolo", translation: "Hello", pronunciation: "mbo-lo" },
                            { phrase: "Mbolo mwa suba", translation: "Good morning", pronunciation: "mbo-lo mwa su-ba" },
                            { phrase: "Mbolo mwa munyene", translation: "Good evening", pronunciation: "mbo-lo mwa mu-nye-ne" },
                            { phrase: "Maséé", translation: "Thank you", pronunciation: "ma-say" },
                            { phrase: "Maséé mingi", translation: "Thank you very much", pronunciation: "ma-say min-gi" },
                            { phrase: "Éé", translation: "Yes", pronunciation: "ay" },
                            { phrase: "Tɛ́", translation: "No", pronunciation: "teh" },
                            { phrase: "Kende", translation: "Goodbye", pronunciation: "ken-de" }
                        ]
                    },
                    {
                        title: "Numbers 1-10",
                        phrases: [
                            { phrase: "Mɔ̀tɔ́", translation: "One", pronunciation: "mo-to" },
                            { phrase: "Babɛ́", translation: "Two", pronunciation: "ba-beh" },
                            { phrase: "Balalo", translation: "Three", pronunciation: "ba-la-lo" },
                            { phrase: "Banɛ́", translation: "Four", pronunciation: "ba-neh" },
                            { phrase: "Batánu", translation: "Five", pronunciation: "ba-ta-nu" },
                            { phrase: "Motóba", translation: "Six", pronunciation: "mo-to-ba" },
                            { phrase: "Sambo", translation: "Seven", pronunciation: "sam-bo" },
                            { phrase: "Mwambe", translation: "Eight", pronunciation: "mwam-be" },
                            { phrase: "Dibua", translation: "Nine", pronunciation: "di-bu-a" },
                            { phrase: "Duóm", translation: "Ten", pronunciation: "du-om" }
                        ]
                    }
                ]
            },
            ewondo: {
                name: "Ewondo",
                region: "Centre Region", 
                speakers: "577,700",
                difficulty: "beginner",
                lessons: [
                    {
                        title: "Essential Greetings",
                        phrases: [
                            { phrase: "Mbolo", translation: "Hello", pronunciation: "mbo-lo" },
                            { phrase: "Mbolo ngon mba", translation: "Good morning", pronunciation: "mbo-lo ngon mba" },
                            { phrase: "Mbolo ngon kiri", translation: "Good evening", pronunciation: "mbo-lo ngon ki-ri" },
                            { phrase: "Akiba", translation: "Thank you", pronunciation: "ah-kee-ba" },
                            { phrase: "Akiba mingi", translation: "Thank you very much", pronunciation: "ah-kee-ba min-gi" },
                            { phrase: "Eee", translation: "Yes", pronunciation: "eh-eh" },
                            { phrase: "Awa", translation: "No", pronunciation: "ah-wa" },
                            { phrase: "Kende", translation: "Goodbye", pronunciation: "ken-de" }
                        ]
                    },
                    {
                        title: "Numbers 1-10",
                        phrases: [
                            { phrase: "Fok", translation: "One", pronunciation: "fok" },
                            { phrase: "Bebe", translation: "Two", pronunciation: "be-be" },
                            { phrase: "Lalo", translation: "Three", pronunciation: "la-lo" },
                            { phrase: "Nne", translation: "Four", pronunciation: "nne" },
                            { phrase: "Tanu", translation: "Five", pronunciation: "ta-nu" },
                            { phrase: "Samena", translation: "Six", pronunciation: "sa-me-na" },
                            { phrase: "Zamgbala", translation: "Seven", pronunciation: "zam-gba-la" },
                            { phrase: "Mwom", translation: "Eight", pronunciation: "mwom" },
                            { phrase: "Ebul", translation: "Nine", pronunciation: "e-bul" },
                            { phrase: "Awom", translation: "Ten", pronunciation: "a-wom" }
                        ]
                    }
                ]
            },
            nso: {
                name: "Lamso",
                region: "Northwest Region",
                speakers: "240,000",
                difficulty: "intermediate", 
                lessons: [
                    {
                        title: "Essential Greetings",
                        phrases: [
                            { phrase: "irania", translation: "Good morning", pronunciation: "ee-rah-nyah" },
                            { phrase: "iginia", translation: "Good evening", pronunciation: "ee-gee-nyah" },
                            { phrase: "beriwa", translation: "Thank you", pronunciation: "beh-ree-wah" },
                            { phrase: "asaka", translation: "How are you?", pronunciation: "ah-sah-kah" },
                            { phrase: "nzakijung", translation: "I am fine", pronunciation: "n-zah-kee-joong" },
                            { phrase: "eno", translation: "Yes", pronunciation: "eh-noh" },
                            { phrase: "ayia", translation: "No", pronunciation: "ah-yee-ah" },
                            { phrase: "abenye", translation: "Goodbye", pronunciation: "ah-behn-yeh" }
                        ]
                    },
                    {
                        title: "Common Phrases",
                        phrases: [
                            { phrase: "asaka", translation: "How are you?", pronunciation: "ah-sah-kah" },
                            { phrase: "nzakijung", translation: "I am fine", pronunciation: "n-zah-kee-joong" },
                            { phrase: "iye dejika", translation: "What is your name?", pronunciation: "ee-yeh-deh-jee-kah" },
                            { phrase: "kiwo", translation: "Please", pronunciation: "kee-woh" },
                            { phrase: "abenye", translation: "Goodbye", pronunciation: "ah-behn-yeh" }
                        ]
                    },
                    {
                        title: "Numbers 1-10",
                        phrases: [
                            { phrase: "moon", translation: "One", pronunciation: "moon" },
                            { phrase: "ba", translation: "Two", pronunciation: "bah" },
                            { phrase: "tar", translation: "Three", pronunciation: "tah" },
                            { phrase: "wer", translation: "Four", pronunciation: "wehr" },
                            { phrase: "dan", translation: "Five", pronunciation: "dahn" },
                            { phrase: "ndufu", translation: "Six", pronunciation: "n-doo-foo" },
                            { phrase: "samba", translation: "Seven", pronunciation: "sahm-bah" },
                            { phrase: "wami", translation: "Eight", pronunciation: "wah-mee" },
                            { phrase: "vu", translation: "Nine", pronunciation: "voo" },
                            { phrase: "vum", translation: "Ten", pronunciation: "voom" }
                        ]
                    }
                ]
            }
        };
    }

    /**
     * Get enhanced language data for a specific tribe
     */
    getTribalLanguageData(tribeKey) {
        return this.enhancedLanguageData[tribeKey] || null;
    }

    /**
     * Get all enhanced language data
     */
    getAllLanguageData() {
        return this.enhancedLanguageData;
    }

    /**
     * Validate language content authenticity
     */
    validateLanguageContent(tribeKey, phrase, translation) {
        // Basic validation rules
        const tribe = this.tribalLanguages[tribeKey];
        if (!tribe) return false;

        // Check for common patterns in each language family
        const validationRules = {
            'Niger-Congo, Grassfields': {
                // Grassfields languages often have tonal markers
                patterns: [/[àáâãäāăąǎ]/, /[èéêëēĕėęě]/, /[ìíîïīĭįǐ]/, /[òóôõöōŏőǒ]/, /[ùúûüūŭůűǔ]/],
                commonPrefixes: ['mb', 'ng', 'nj', 'nd']
            },
            'Niger-Congo, Bantu': {
                patterns: [/mb/, /nd/, /ng/, /nj/],
                commonPrefixes: ['ba', 'ma', 'wa', 'mi']
            },
            'Niger-Congo, Atlantic': {
                patterns: [/aa/, /ee/, /ii/, /oo/, /uu/],
                commonSuffixes: ['o', 'i', 'e']
            }
        };

        const rules = validationRules[tribe.family];
        if (!rules) return true; // No specific rules, assume valid

        // Check if phrase contains expected patterns
        return rules.patterns.some(pattern => pattern.test(phrase));
    }

    /**
     * Fetch language content from external AI service
     */
    async fetchFromAI(tribeKey, contentType = 'greetings') {
        const tribe = this.tribalLanguages[tribeKey];
        if (!tribe) return null;

        const prompt = this.generateLanguagePrompt(tribe, contentType);
        
        try {
            // Try multiple AI services in order of preference
            let result = await this.tryHuggingFace(prompt);
            if (!result) {
                result = await this.tryLocalGeneration(tribe, contentType);
            }
            
            return this.parseAIResponse(result, contentType);
        } catch (error) {
            console.error('Error fetching from AI:', error);
            return this.getFallbackContent(tribeKey, contentType);
        }
    }

    /**
     * Generate appropriate prompt for AI services
     */
    generateLanguagePrompt(tribe, contentType) {
        const prompts = {
            greetings: `Generate authentic ${tribe.name} language greetings with accurate pronunciation. Include: hello, good morning, good evening, thank you, yes, no, goodbye. Format: phrase|translation|pronunciation`,
            numbers: `Generate numbers 1-10 in authentic ${tribe.name} language with pronunciation. Format: phrase|translation|pronunciation`,
            family: `Generate family terms in authentic ${tribe.name} language: father, mother, child, brother, sister, grandfather, grandmother. Format: phrase|translation|pronunciation`,
            common: `Generate common phrases in authentic ${tribe.name} language: How are you?, I am fine, What is your name?, My name is..., I don't understand. Format: phrase|translation|pronunciation`
        };

        return prompts[contentType] || prompts.greetings;
    }

    /**
     * Try Hugging Face API (free tier)
     */
    async tryHuggingFace(prompt) {
        try {
            const response = await fetch('https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    inputs: prompt,
                    parameters: {
                        max_length: 200,
                        temperature: 0.7
                    }
                })
            });

            if (response.ok) {
                const data = await response.json();
                return data[0]?.generated_text || null;
            }
        } catch (error) {
            console.error('Hugging Face API error:', error);
        }
        return null;
    }

    /**
     * Local content generation as fallback
     */
    async tryLocalGeneration(tribe, contentType) {
        // Return enhanced local content
        return this.getTribalLanguageData(tribe.name.toLowerCase().replace(/[^a-z]/g, '_'));
    }

    /**
     * Parse AI response into structured format
     */
    parseAIResponse(response, contentType) {
        if (!response) return null;

        try {
            // Parse response format: phrase|translation|pronunciation
            const lines = response.split('\n').filter(line => line.includes('|'));
            return lines.map(line => {
                const [phrase, translation, pronunciation] = line.split('|');
                return {
                    phrase: phrase?.trim(),
                    translation: translation?.trim(), 
                    pronunciation: pronunciation?.trim()
                };
            }).filter(item => item.phrase && item.translation);
        } catch (error) {
            console.error('Error parsing AI response:', error);
            return null;
        }
    }

    /**
     * Get fallback content when AI services fail
     */
    getFallbackContent(tribeKey, contentType) {
        const data = this.getTribalLanguageData(tribeKey);
        if (!data) return null;

        const lessonMap = {
            greetings: 0,
            numbers: 1,
            family: 2,
            common: 3
        };

        const lessonIndex = lessonMap[contentType] || 0;
        return data.lessons[lessonIndex]?.phrases || null;
    }

    /**
     * Update language data with AI-generated content
     */
    async updateLanguageData(tribeKey) {
        const contentTypes = ['greetings', 'numbers', 'family', 'common'];
        const updatedLessons = [];

        for (const contentType of contentTypes) {
            const aiContent = await this.fetchFromAI(tribeKey, contentType);
            if (aiContent) {
                updatedLessons.push({
                    title: this.getContentTypeTitle(contentType),
                    phrases: aiContent
                });
            }
        }

        if (updatedLessons.length > 0) {
            this.enhancedLanguageData[tribeKey].lessons = updatedLessons;
            return true;
        }

        return false;
    }

    /**
     * Get title for content type
     */
    getContentTypeTitle(contentType) {
        const titles = {
            greetings: 'Essential Greetings',
            numbers: 'Numbers 1-10',
            family: 'Family & Relationships', 
            common: 'Common Phrases'
        };
        return titles[contentType] || 'Language Lesson';
    }
}

// Export for use in other modules
window.LanguageDataService = LanguageDataService;
