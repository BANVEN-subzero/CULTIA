/**
 * Authentic Cameroonian Tribal Language Data
 * Optimized for the 4 main languages: Lamnso', Bamiléké, Bamum (Foumban), and Hausa.
 * Each has at least 3 lessons with authentic phrases and pronunciations.
 */

const TRIBAL_LANGUAGE_DATA = {
    nso: {
        name: "Lamso",
        region: "Northwest Region",
        speakers: "280,000",
        difficulty: "intermediate",
        description: "The language of the Nso people, known for their powerful traditional kingdom (Bui Division).",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "irania", pronunciation: "ee-rah-nyah", translations: {en: "Good morning", fr: "Bon matin", pid: "Gud monin"} },
                    { phrase: "iginia", pronunciation: "ee-gee-nyah", translations: {en: "Good evening", fr: "Bonsoir", pid: "Gud ivnin"} },
                    { phrase: "beriwa", pronunciation: "beh-ree-wah", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} },
                    { phrase: "asaka", pronunciation: "ah-sah-kah", translations: {en: "How are you?", fr: "Comment ça va?", pid: "How na?"} },
                    { phrase: "nzakijung", pronunciation: "n-zah-kee-joong", translations: {en: "I am fine", fr: "Je vais bien", pid: "A de fine"} },
                    { phrase: "eno", pronunciation: "eh-noh", translations: {en: "Yes", fr: "Oui", pid: "Yes"} },
                    { phrase: "ayia", pronunciation: "ah-yee-ah", translations: {en: "No", fr: "Non", pid: "No"} },
                    { phrase: "kiwo", pronunciation: "kee-woh", translations: {en: "Please", fr: "S'il vous plaît", pid: "Abeg"} },
                    { phrase: "iye dejika", pronunciation: "ee-yeh deh-jee-kah", translations: {en: "What is your name?", fr: "Comment t'appelles-tu?", pid: "Wetin be your name?"} },
                    { phrase: "abenye", pronunciation: "ah-behn-yeh", translations: {en: "Goodbye", fr: "Au revoir", pid: "Bai bai"} }
                ]
            },
            {
                title: "Numbers 1-10",
                icon: "🔢",
                phrases: [
                    { phrase: "moon", pronunciation: "moon", translations: {en: "One", fr: "Un", pid: "Wan"} },
                    { phrase: "ba", pronunciation: "bah", translations: {en: "Two", fr: "Deux", pid: "Tu"} },
                    { phrase: "tar", pronunciation: "tahr", translations: {en: "Three", fr: "Trois", pid: "Tri"} },
                    { phrase: "wer", pronunciation: "wehr", translations: {en: "Four", fr: "Quatre", pid: "Fo"} },
                    { phrase: "dan", pronunciation: "dahn", translations: {en: "Five", fr: "Cinq", pid: "Faiv"} },
                    { phrase: "ndufu", pronunciation: "n-doo-foo", translations: {en: "Six", fr: "Six", pid: "Siks"} },
                    { phrase: "samba", pronunciation: "sahm-bah", translations: {en: "Seven", fr: "Sept", pid: "Seven"} },
                    { phrase: "wami", pronunciation: "wah-mee", translations: {en: "Eight", fr: "Huit", pid: "Eight"} },
                    { phrase: "vu", pronunciation: "voo", translations: {en: "Nine", fr: "Neuf", pid: "Nain"} },
                    { phrase: "vum", pronunciation: "voom", translations: {en: "Ten", fr: "Dix", pid: "Ten"} }
                ]
            },
            {
                title: "Family & People",
                icon: "👨‍👩‍👧‍👦",
                phrases: [
                    { phrase: "ba", pronunciation: "bah", translations: {en: "Father", fr: "Père", pid: "Papa"} },
                    { phrase: "mami", pronunciation: "mah-mee", translations: {en: "Mother", fr: "Mère", pid: "Mama"} },
                    { phrase: "wan", pronunciation: "wahn", translations: {en: "Child", fr: "Enfant", pid: "Pikin"} },
                    { phrase: "ferr", pronunciation: "fehr", translations: {en: "Brother", fr: "Frère", pid: "Broda"} },
                    { phrase: "ferr", pronunciation: "fehr", translations: {en: "Sister", fr: "Soeur", pid: "Sista"} },
                    { phrase: "nyako", pronunciation: "nyah-koh", translations: {en: "Grandfather", fr: "Grand-père", pid: "Granpapa"} },
                    { phrase: "ya", pronunciation: "yah", translations: {en: "Grandmother", fr: "Grand-mère", pid: "Granmama"} },
                    { phrase: "wi", pronunciation: "wee", translations: {en: "Woman", fr: "Femme", pid: "Woman"} },
                    { phrase: "lomin", pronunciation: "loh-meen", translations: {en: "Husband", fr: "Mari", pid: "Husband"} },
                    { phrase: "nkar", pronunciation: "n-kahr", translations: {en: "Friend", fr: "Ami", pid: "Paldin"} }
                ]
            }
        ]
    },
    bamileke: {
        name: "Bamiléké",
        region: "West Region",
        speakers: "3.2 million",
        difficulty: "intermediate",
        description: "A major Grassfields language cluster spoken in the Western Highlands.",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "Mbɔ̀ŋ", pronunciation: "mbong", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Ŋwà'à", pronunciation: "ngwa-a", translations: {en: "Good morning", fr: "Bon matin", pid: "Gud monin"} },
                    { phrase: "M̀mɛ m̀mɛ", pronunciation: "mmeh mmeh", translations: {en: "How are you?", fr: "Comment ça va?", pid: "How na"} },
                    { phrase: "M̀mɛ m̀mɛ pə̀p", pronunciation: "mmeh mmeh pup", translations: {en: "I am fine", fr: "Ça va bien", pid: "A de fine"} },
                    { phrase: "Ndɛ̀ŋ", pronunciation: "ndeng", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} },
                    { phrase: "Yɛ̀", pronunciation: "yeh", translations: {en: "Yes", fr: "Oui", pid: "Yes"} },
                    { phrase: "Àà", pronunciation: "aa", translations: {en: "No", fr: "Non", pid: "No"} },
                    { phrase: "Kɔ̀ bɔ̀", pronunciation: "ko bo", translations: {en: "Goodbye", fr: "Au revoir", pid: "Bai bai"} },
                    { phrase: "Sɔ́'ɔ́", pronunciation: "so-o", translations: {en: "Excuse me", fr: "Excusez-moi", pid: "Sori"} },
                    { phrase: "Wù lɛ̀ ɛ̀?", pronunciation: "wu leh eh", translations: {en: "What is your name?", fr: "Comment t'appelles-tu?", pid: "Wetin be your name?"} }
                ]
            },
            {
                title: "Numbers 1-10",
                icon: "🔢",
                phrases: [
                    { phrase: "Pɔ̀'", pronunciation: "po", translations: {en: "One", fr: "Un", pid: "Wan"} },
                    { phrase: "Bà", pronunciation: "ba", translations: {en: "Two", fr: "Deux", pid: "Tu"} },
                    { phrase: "Tà", pronunciation: "ta", translations: {en: "Three", fr: "Trois", pid: "Tri"} },
                    { phrase: "Nà", pronunciation: "na", translations: {en: "Four", fr: "Quatre", pid: "Fo"} },
                    { phrase: "Tɔ̀n", pronunciation: "ton", translations: {en: "Five", fr: "Cinq", pid: "Faiv"} },
                    { phrase: "Sàmɛ̀n", pronunciation: "sa-men", translations: {en: "Six", fr: "Six", pid: "Siks"} },
                    { phrase: "Sàmɛ̀n pɔ̀'", pronunciation: "sa-men po", translations: {en: "Seven", fr: "Sept", pid: "Seven"} },
                    { phrase: "Sàmɛ̀n bà", pronunciation: "sa-men ba", translations: {en: "Eight", fr: "Huit", pid: "Eight"} },
                    { phrase: "Sàmɛ̀n tà", pronunciation: "sa-men ta", translations: {en: "Nine", fr: "Neuf", pid: "Nain"} },
                    { phrase: "Fù", pronunciation: "fu", translations: {en: "Ten", fr: "Dix", pid: "Ten"} }
                ]
            },
            {
                title: "Common Objects",
                icon: "🏠",
                phrases: [
                    { phrase: "Mà'à", pronunciation: "mah-ah", translations: {en: "Water", fr: "Eau", pid: "Wata"} },
                    { phrase: "Ndà", pronunciation: "ndah", translations: {en: "House", fr: "Maison", pid: "House"} },
                    { phrase: "Mùn", pronunciation: "moon", translations: {en: "Child", fr: "Enfant", pid: "Pikin"} },
                    { phrase: "Ŋwà'", pronunciation: "ngwah", translations: {en: "Book", fr: "Livre", pid: "Book"} },
                    { phrase: "Tà", pronunciation: "tah", translations: {en: "Chair", fr: "Chaise", pid: "Chair"} },
                    { phrase: "Nə̀", pronunciation: "nuh", translations: {en: "Eye", fr: "Oeil", pid: "Eye"} },
                    { phrase: "Tsì", pronunciation: "tsee", translations: {en: "Head", fr: "Tête", pid: "Head"} },
                    { phrase: "Pɔ̀k", pronunciation: "pok", translations: {en: "Bag", fr: "Sac", pid: "Bag"} },
                    { phrase: "Shì", pronunciation: "shee", translations: {en: "Tree", fr: "Arbre", pid: "Stick"} },
                    { phrase: "Ŋwà'à", pronunciation: "ngwah-ah", translations: {en: "Paper", fr: "Papier", pid: "Paper"} }
                ]
            }
        ]
    },
    bamum: {
        name: "Bamum",
        region: "West Region",
        speakers: "420,000",
        difficulty: "advanced",
        description: "Language of the Bamum Kingdom (Foumban), famous for its unique writing system.",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "M̀beu yie", pronunciation: "mbeh-oo yee-eh", translations: {en: "Good morning", fr: "Bon matin", pid: "Gud monin"} },
                    { phrase: "M̀beu nɛ̀m", pronunciation: "mbeh-oo nem", translations: {en: "Good evening", fr: "Bonsoir", pid: "Gud ivnin"} },
                    { phrase: "Ǹga'ane", pronunciation: "ngah-ah-neh", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} },
                    { phrase: "Ǹchu", pronunciation: "nchoo", translations: {en: "Welcome", fr: "Bienvenue", pid: "Welkom"} },
                    { phrase: "Ǹchu lə̀?", pronunciation: "nchoo leh", translations: {en: "How are you?", fr: "Comment ça va?", pid: "How na?"} },
                    { phrase: "Ǹchu m̀mɛ", pronunciation: "nchoo mmeh", translations: {en: "I am fine", fr: "Je vais bien", pid: "A de fine"} },
                    { phrase: "Yɛ̀", pronunciation: "yeh", translations: {en: "Yes", fr: "Oui", pid: "Yes"} },
                    { phrase: "Àà", pronunciation: "aa", translations: {en: "No", fr: "Non", pid: "No"} },
                    { phrase: "M̀fen", pronunciation: "mfen", translations: {en: "King", fr: "Roi", pid: "King"} },
                    { phrase: "Ǹgondog", pronunciation: "ngon-dog", translations: {en: "Palace", fr: "Palais", pid: "Palas"} }
                ]
            },
            {
                title: "Numbers 1-10",
                icon: "🔢",
                phrases: [
                    { phrase: "Mo", pronunciation: "mo", translations: {en: "One", fr: "Un", pid: "Wan"} },
                    { phrase: "Mba", pronunciation: "mba", translations: {en: "Two", fr: "Deux", pid: "Tu"} },
                    { phrase: "Mte", pronunciation: "mte", translations: {en: "Three", fr: "Trois", pid: "Tri"} },
                    { phrase: "Mkpue", pronunciation: "mkpue", translations: {en: "Four", fr: "Quatre", pid: "Fo"} },
                    { phrase: "Mten", pronunciation: "mten", translations: {en: "Five", fr: "Cinq", pid: "Faiv"} },
                    { phrase: "Mntu", pronunciation: "mntu", translations: {en: "Six", fr: "Six", pid: "Siks"} },
                    { phrase: "Msambà", pronunciation: "msamba", translations: {en: "Seven", fr: "Sept", pid: "Seven"} },
                    { phrase: "Mfam", pronunciation: "mfam", translations: {en: "Eight", fr: "Huit", pid: "Eight"} },
                    { phrase: "Mkovu", pronunciation: "mkovu", translations: {en: "Nine", fr: "Neuf", pid: "Nain"} },
                    { phrase: "Mvə̀m", pronunciation: "mvem", translations: {en: "Ten", fr: "Dix", pid: "Ten"} }
                ]
            },
            {
                title: "People & Places",
                icon: "🏛️",
                phrases: [
                    { phrase: "Pɔ̀", pronunciation: "poh", translations: {en: "Person", fr: "Personne", pid: "Person"} },
                    { phrase: "M̀fen", pronunciation: "mfen", translations: {en: "King/Sultan", fr: "Roi/Sultan", pid: "King"} },
                    { phrase: "Ǹchu", pronunciation: "nchoo", translations: {en: "House", fr: "Maison", pid: "House"} },
                    { phrase: "Ǹgondog", pronunciation: "ngon-dog", translations: {en: "Palace", fr: "Palais", pid: "Palas"} },
                    { phrase: "M̀fùm", pronunciation: "mfoom", translations: {en: "Market", fr: "Marché", pid: "Market"} },
                    { phrase: "Ǹshì", pronunciation: "nshee", translations: {en: "Water", fr: "Eau", pid: "Wata"} },
                    { phrase: "Ǹda", pronunciation: "ndah", translations: {en: "Road", fr: "Route", pid: "Road"} },
                    { phrase: "M̀bu", pronunciation: "mboo", translations: {en: "Town", fr: "Ville", pid: "Town"} },
                    { phrase: "M̀be", pronunciation: "mbeh", translations: {en: "Friend", fr: "Ami", pid: "Paldin"} },
                    { phrase: "Ǹkap", pronunciation: "nkap", translations: {en: "Money", fr: "Argent", pid: "Money"} }
                ]
            }
        ]
    },
    hausa: {
        name: "Hausa",
        region: "North Region",
        speakers: "3 million",
        difficulty: "beginner",
        description: "A major Chadic language spoken widely in northern Cameroon and across West Africa.",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "Sannu", pronunciation: "san-noo", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Ina kwana", pronunciation: "ee-nah kwah-nah", translations: {en: "Good morning", fr: "Bon matin", pid: "Gud monin"} },
                    { phrase: "Ina wuni", pronunciation: "ee-nah woo-nee", translations: {en: "Good afternoon", fr: "Bon après-midi", pid: "Gud aphternun"} },
                    { phrase: "Na gode", pronunciation: "nah goh-deh", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} },
                    { phrase: "Don Allah", pronunciation: "don al-lah", translations: {en: "Please", fr: "S'il vous plaît", pid: "Abeg"} },
                    { phrase: "I", pronunciation: "ee", translations: {en: "Yes", fr: "Oui", pid: "Yes"} },
                    { phrase: "A'a", pronunciation: "ah-ah", translations: {en: "No", fr: "Non", pid: "No"} },
                    { phrase: "Lafiya", pronunciation: "lah-fee-yah", translations: {en: "I am fine", fr: "Ça va bien", pid: "A de fine"} },
                    { phrase: "Ina gajiya?", pronunciation: "ee-nah gah-jee-yah", translations: {en: "How is the tiredness? (Greeting)", fr: "Comment va la fatigue?", pid: "How work?"} },
                    { phrase: "Sai anjima", pronunciation: "sai an-jee-mah", translations: {en: "Goodbye", fr: "Au revoir", pid: "Bai bai"} }
                ]
            },
            {
                title: "Numbers 1-10",
                icon: "🔢",
                phrases: [
                    { phrase: "Daya", pronunciation: "dah-yah", translations: {en: "One", fr: "Un", pid: "Wan"} },
                    { phrase: "Biyu", pronunciation: "bee-yoo", translations: {en: "Two", fr: "Deux", pid: "Tu"} },
                    { phrase: "Uku", pronunciation: "oo-koo", translations: {en: "Three", fr: "Trois", pid: "Tri"} },
                    { phrase: "Hudu", pronunciation: "hoo-doo", translations: {en: "Four", fr: "Quatre", pid: "Fo"} },
                    { phrase: "Biyar", pronunciation: "bee-yar", translations: {en: "Five", fr: "Cinq", pid: "Faiv"} },
                    { phrase: "Shida", pronunciation: "shee-dah", translations: {en: "Six", fr: "Six", pid: "Siks"} },
                    { phrase: "Bakwai", pronunciation: "bak-wai", translations: {en: "Seven", fr: "Sept", pid: "Seven"} },
                    { phrase: "Takwas", pronunciation: "tak-was", translations: {en: "Eight", fr: "Huit", pid: "Eight"} },
                    { phrase: "Tara", pronunciation: "tah-rah", translations: {en: "Nine", fr: "Neuf", pid: "Nain"} },
                    { phrase: "Goma", pronunciation: "goh-mah", translations: {en: "Ten", fr: "Dix", pid: "Ten"} }
                ]
            },
            {
                title: "Essential Questions",
                icon: "❓",
                phrases: [
                    { phrase: "Ina ne?", pronunciation: "ee-nah neh", translations: {en: "Where is it?", fr: "Où est-ce?", pid: "Wha side?"} },
                    { phrase: "Nawa ne?", pronunciation: "nah-wah neh", translations: {en: "How much?", fr: "Combien?", pid: "How much?"} },
                    { phrase: "Wa ne?", pronunciation: "wah neh", translations: {en: "Who is it?", fr: "Qui est-ce?", pid: "Na who?"} },
                    { phrase: "Yaushe?", pronunciation: "yau-sheh", translations: {en: "When?", fr: "Quand?", pid: "Wha time?"} },
                    { phrase: "Me ya faru?", pronunciation: "meh yah fah-roo", translations: {en: "What happened?", fr: "Qu'est-ce qui s'est passé?", pid: "Wetin happen?"} },
                    { phrase: "Kana jin Turanci?", pronunciation: "kah-nah jeen too-ran-chee", translations: {en: "Do you speak English?", fr: "Parles-tu anglais?", pid: "You de hear English?"} },
                    { phrase: "Ba na ji", pronunciation: "bah nah jee", translations: {en: "I don't understand", fr: "Je ne comprends pas", pid: "A no de hear"} },
                    { phrase: "Maimaita mana", pronunciation: "mai-mai-tah mah-nah", translations: {en: "Repeat please", fr: "Répétez s'il vous plaît", pid: "Talk am again"} },
                    { phrase: "Ina bandaki?", pronunciation: "ee-nah ban-dah-kee", translations: {en: "Where is the bathroom?", fr: "Où sont les toilettes?", pid: "Wha side toilet de?"} },
                    { phrase: "Taimaka min", pronunciation: "tai-mah-kah meen", translations: {en: "Help me", fr: "Aidez-moi", pid: "Help me"} }
                ]
            }
        ]
    },
    fulani: {
        name: "Fulfulde",
        region: "North & Adamawa",
        speakers: "4 million",
        difficulty: "beginner",
        description: "The language of the Fulani people, widely spoken across the Sahel regions.",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "A salaam alaikum", pronunciation: "ah sah-lahm ah-lay-koom", translations: {en: "Peace be upon you", fr: "Paix sur vous", pid: "How na"} },
                    { phrase: "Alaikum salaam", pronunciation: "ah-lay-koom sah-lahm", translations: {en: "And upon you peace", fr: "Et sur vous la paix", pid: "A de fine"} },
                    { phrase: "Jam tan", pronunciation: "jam tahn", translations: {en: "Good afternoon", fr: "Bon après-midi", pid: "Gud aphternun"} }
                ]
            }
        ]
    },
    duala: {
        name: "Duala",
        region: "Littoral Region",
        speakers: "1.2 million",
        difficulty: "beginner",
        description: "Historic trade language of coastal Cameroon, spoken by the Duala people.",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "Mônè", pronunciation: "moh-neh", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Mase", pronunciation: "mah-seh", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} }
                ]
            }
        ]
    },
    bassa: {
        name: "Bassa",
        region: "Centre & Littoral",
        speakers: "800,000",
        difficulty: "intermediate",
        description: "An important Bantu language of central Cameroon, spoken by the Bassa people.",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "Hé hé", pronunciation: "hey hey", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Akiba", pronunciation: "ah-kee-bah", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} }
                ]
            }
        ]
    },
    beti: {
        name: "Beti",
        region: "Centre & South",
        speakers: "3 million",
        difficulty: "beginner",
        description: "A major Bantu language cluster spoken in the forest zones of central Cameroon.",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "Mbolo", pronunciation: "mbo-lo", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Akiba", pronunciation: "ah-kee-bah", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} }
                ]
            }
        ]
    }
};

window.TRIBAL_LANGUAGE_DATA = TRIBAL_LANGUAGE_DATA;
