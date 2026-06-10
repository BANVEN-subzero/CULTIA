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
                    { phrase: "beriwo", pronunciation: "beh-ree-woh", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} },
                    { phrase: "asaka", pronunciation: "ah-sah-kah", translations: {en: "How are you?", fr: "Comment ça va?", pid: "How na?"} },
                    { phrase: "nzakijung", pronunciation: "n-zah-kee-joong", translations: {en: "I am fine", fr: "Je vais bien", pid: "A de fine"} },
                    { phrase: "eno", pronunciation: "eh-noh", translations: {en: "Yes", fr: "Oui", pid: "Yes"} },
                    { phrase: "ayia", pronunciation: "ah-yee-ah", translations: {en: "No", fr: "Non", pid: "No"} },
                    { phrase: "kiwo", pronunciation: "kee-woh", translations: {en: "Please", fr: "S'il vous plaît", pid: "Abeg"} },
                    { phrase: "yiye dejika", pronunciation: "yee-yeh deh-jee-kah", translations: {en: "What is your name?", fr: "Comment t'appelles-tu?", pid: "Wetin be your name?"} },
                    { phrase: "abenye", pronunciation: "ah-behn-yeh", translations: {en: "Goodbye", fr: "Au revoir", pid: "Bai bai"} }
                ]
            },
            {
                title: "Numbers 1-10",
                icon: "🔢",
                phrases: [
                    { phrase: "moon", pronunciation: "moon", translations: {en: "One", fr: "Un", pid: "Wan"} },
                    { phrase: "baa", pronunciation: "baah", translations: {en: "Two", fr: "Deux", pid: "Tu"} },
                    { phrase: "tar", pronunciation: "tahr", translations: {en: "Three", fr: "Trois", pid: "Tri"} },
                    { phrase: "qwer", pronunciation: "qwehr", translations: {en: "Four", fr: "Quatre", pid: "Fo"} },
                    { phrase: "tan", pronunciation: "tahn", translations: {en: "Five", fr: "Cinq", pid: "Faiv"} },
                    { phrase: "ntufu", pronunciation: "n-too-foo", translations: {en: "Six", fr: "Six", pid: "Siks"} },
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
        name: "Bamiléké (Fe'fe')",
        region: "West Region",
        speakers: "3.2 million",
        difficulty: "intermediate",
        description: "A major Grassfields language cluster spoken in the Western Highlands (Fe'fe' / Nufi).",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "Shwama / A-o", pronunciation: "shwah-mah / ah-oh", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Lòh sǐə̀ / O mbuen", pronunciation: "loh see-ah / oh m-bwen", translations: {en: "Good morning", fr: "Bon matin", pid: "Gud monin"} },
                    { phrase: "O mbyā nâ?", pronunciation: "oh mbyah nah", translations: {en: "How are you?", fr: "Comment ça va?", pid: "How na"} },
                    { phrase: "Mě mbyā", pronunciation: "meh mbyah", translations: {en: "I am fine", fr: "Ça va bien", pid: "A de fine"} },
                    { phrase: "Sǐə̀ sǐə̀", pronunciation: "see-ah see-ah", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} },
                    { phrase: "Éé / Ǒo", pronunciation: "eh-eh / oh-oh", translations: {en: "Yes", fr: "Oui", pid: "Yes"} },
                    { phrase: "Ghǎ / Gà’", pronunciation: "gah / gah", translations: {en: "No", fr: "Non", pid: "No"} },
                    { phrase: "Ngà’ mbuen / Ndʉ̀’ lēē", pronunciation: "ngah m-bwen / ndoo lay", translations: {en: "Goodbye", fr: "Au revoir", pid: "Bai bai"} },
                    { phrase: "Cō pū’ / Khù’ ngò", pronunciation: "coh poo / khoo ngoh", translations: {en: "Excuse me", fr: "Excusez-moi", pid: "Sori"} },
                    { phrase: "Lǐn lēē nâ wō?", pronunciation: "leen lay nah woh", translations: {en: "What is your name?", fr: "Comment t'appelles-tu?", pid: "Wetin be your name?"} }
                ]
            },
            {
                title: "Numbers 1-10",
                icon: "🔢",
                phrases: [
                    { phrase: "Nshʉ̀’", pronunciation: "nshoo", translations: {en: "One", fr: "Un", pid: "Wan"} },
                    { phrase: "Pʉ́á", pronunciation: "pwa", translations: {en: "Two", fr: "Deux", pid: "Tu"} },
                    { phrase: "Tāā", pronunciation: "tah", translations: {en: "Three", fr: "Trois", pid: "Tri"} },
                    { phrase: "Kwà", pronunciation: "kwah", translations: {en: "Four", fr: "Quatre", pid: "Fo"} },
                    { phrase: "Tǐi", pronunciation: "tee", translations: {en: "Five", fr: "Cinq", pid: "Faiv"} },
                    { phrase: "Ntóho", pronunciation: "n-toh-hoh", translations: {en: "Six", fr: "Six", pid: "Siks"} },
                    { phrase: "Sə̀ə̀mbʉ́á", pronunciation: "suh-suh-mbwa", translations: {en: "Seven", fr: "Sept", pid: "Seven"} },
                    { phrase: "Hǎa", pronunciation: "hah", translations: {en: "Eight", fr: "Huit", pid: "Eight"} },
                    { phrase: "Vʉ̀’ʉ̄", pronunciation: "voo-voo", translations: {en: "Nine", fr: "Neuf", pid: "Nain"} },
                    { phrase: "Ghám", pronunciation: "gam", translations: {en: "Ten", fr: "Dix", pid: "Ten"} }
                ]
            },
            {
                title: "Common Objects",
                icon: "🏠",
                phrases: [
                    { phrase: "Nshǐ", pronunciation: "n-shee", translations: {en: "Water", fr: "Eau", pid: "Wata"} },
                    { phrase: "Ndá", pronunciation: "ndah", translations: {en: "House", fr: "Maison", pid: "House"} },
                    { phrase: "Môn", pronunciation: "mohn", translations: {en: "Child", fr: "Enfant", pid: "Pikin"} },
                    { phrase: "Ghà’ lǎ’ / Nà’ wà’", pronunciation: "gah lah / nah wah", translations: {en: "Book", fr: "Livre", pid: "Book"} },
                    { phrase: "Kwà’", pronunciation: "kwah", translations: {en: "Chair", fr: "Chaise", pid: "Chair"} },
                    { phrase: "Lǐghə̀", pronunciation: "lee-guh", translations: {en: "Eye", fr: "Oeil", pid: "Eye"} },
                    { phrase: "Tʉ̄", pronunciation: "too", translations: {en: "Head", fr: "Tête", pid: "Head"} },
                    { phrase: "Kà’", pronunciation: "kah", translations: {en: "Bag", fr: "Sac", pid: "Bag"} },
                    { phrase: "Tī", pronunciation: "tee", translations: {en: "Tree", fr: "Arbre", pid: "Stick"} },
                    { phrase: "Wà’", pronunciation: "wah", translations: {en: "Paper", fr: "Papier", pid: "Paper"} }
                ]
            }
        ]
    },
    bamum: {
        name: "Bamum (Shüpamom)",
        region: "West Region",
        speakers: "420,000",
        difficulty: "advanced",
        description: "Language of the Bamum Kingdom (Foumban), famous for its unique writing system (Shüpamom).",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "Me nshat shu / O tanzie", pronunciation: "meh n-shat shoo / oh tan-zee", translations: {en: "Good morning", fr: "Bon matin", pid: "Gud monin"} },
                    { phrase: "Me nshat mbiye", pronunciation: "meh n-shat m-bee-yeh", translations: {en: "Good evening", fr: "Bonsoir", pid: "Gud ivnin"} },
                    { phrase: "Mengwet / Nshat", pronunciation: "meng-wet / n-shat", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} },
                    { phrase: "Kwansha / Shwama", pronunciation: "kwahn-shah / shwah-mah", translations: {en: "Welcome", fr: "Bienvenue", pid: "Welkom"} },
                    { phrase: "O lere na?", pronunciation: "oh leh-reh nah", translations: {en: "How are you?", fr: "Comment ça va?", pid: "How na?"} },
                    { phrase: "Me lere mben", pronunciation: "meh leh-reh m-ben", translations: {en: "I am fine", fr: "Je vais bien", pid: "A de fine"} },
                    { phrase: "Éé", pronunciation: "eh-eh", translations: {en: "Yes", fr: "Oui", pid: "Yes"} },
                    { phrase: "Ngat", pronunciation: "ngat", translations: {en: "No", fr: "Non", pid: "No"} },
                    { phrase: "Mfon", pronunciation: "m-fon", translations: {en: "King", fr: "Roi", pid: "King"} },
                    { phrase: "Ndji mfon / Nda mfon", pronunciation: "n-jee m-fon / ndah m-fon", translations: {en: "Palace", fr: "Palais", pid: "Palas"} }
                ]
            },
            {
                title: "Numbers 1-10",
                icon: "🔢",
                phrases: [
                    { phrase: "Mò’", pronunciation: "moh", translations: {en: "One", fr: "Un", pid: "Wan"} },
                    { phrase: "Pàa", pronunciation: "pah", translations: {en: "Two", fr: "Deux", pid: "Tu"} },
                    { phrase: "Tēt", pronunciation: "tayt", translations: {en: "Three", fr: "Trois", pid: "Tri"} },
                    { phrase: "Kpà", pronunciation: "kpah", translations: {en: "Four", fr: "Quatre", pid: "Fo"} },
                    { phrase: "Tēn", pronunciation: "tayn", translations: {en: "Five", fr: "Cinq", pid: "Faiv"} },
                    { phrase: "Ntuon", pronunciation: "n-too-on", translations: {en: "Six", fr: "Six", pid: "Siks"} },
                    { phrase: "Sàatpàa", pronunciation: "saa-t-pah", translations: {en: "Seven", fr: "Sept", pid: "Seven"} },
                    { phrase: "Fám", pronunciation: "fam", translations: {en: "Eight", fr: "Huit", pid: "Eight"} },
                    { phrase: "Kovù", pronunciation: "koh-voo", translations: {en: "Nine", fr: "Neuf", pid: "Nain"} },
                    { phrase: "Ghome", pronunciation: "goh-meh", translations: {en: "Ten", fr: "Dix", pid: "Ten"} }
                ]
            },
            {
                title: "People & Places",
                icon: "🏛️",
                phrases: [
                    { phrase: "Ghu / Mut", pronunciation: "goo / moot", translations: {en: "Person", fr: "Personne", pid: "Person"} },
                    { phrase: "Mfon / Fon", pronunciation: "m-fon / fon", translations: {en: "King/Sultan", fr: "Roi/Sultan", pid: "King"} },
                    { phrase: "Nda", pronunciation: "ndah", translations: {en: "House", fr: "Maison", pid: "House"} },
                    { phrase: "Ndji mfon", pronunciation: "n-jee m-fon", translations: {en: "Palace", fr: "Palais", pid: "Palas"} },
                    { phrase: "Gbét / Chié", pronunciation: "g-beht / chay", translations: {en: "Market", fr: "Marché", pid: "Market"} },
                    { phrase: "Nshǐ", pronunciation: "n-shee", translations: {en: "Water", fr: "Eau", pid: "Wata"} },
                    { phrase: "Ndie", pronunciation: "n-dee-eh", translations: {en: "Road", fr: "Route", pid: "Road"} },
                    { phrase: "La’", pronunciation: "lah", translations: {en: "Town", fr: "Ville", pid: "Town"} },
                    { phrase: "Shwá", pronunciation: "shwah", translations: {en: "Friend", fr: "Ami", pid: "Paldin"} },
                    { phrase: "Nkap", pronunciation: "n-kap", translations: {en: "Money", fr: "Argent", pid: "Money"} }
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
                    { phrase: "Ina kwana?", pronunciation: "ee-nah kwah-nah", translations: {en: "Good morning", fr: "Bon matin", pid: "Gud monin"} },
                    { phrase: "Ina wuni?", pronunciation: "ee-nah woo-nee", translations: {en: "Good afternoon", fr: "Bon après-midi", pid: "Gud aphternun"} },
                    { phrase: "Na gode", pronunciation: "nah goh-deh", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} },
                    { phrase: "Don Allah", pronunciation: "don al-lah", translations: {en: "Please", fr: "S'il vous plaît", pid: "Abeg"} },
                    { phrase: "Iiyay / E", pronunciation: "ee-yay / eh", translations: {en: "Yes", fr: "Oui", pid: "Yes"} },
                    { phrase: "A'a", pronunciation: "ah-ah", translations: {en: "No", fr: "Non", pid: "No"} },
                    { phrase: "Lafiya lau", pronunciation: "lah-fee-yah lah-oo", translations: {en: "I am fine", fr: "Ça va bien", pid: "A de fine"} },
                    { phrase: "Sannu da gajiya", pronunciation: "san-noo dah gah-jee-yah", translations: {en: "How is the tiredness? (Greeting)", fr: "Comment va la fatigue?", pid: "How work?"} },
                    { phrase: "Sai an jima / Sai wata rana", pronunciation: "sai ahn jee-mah / sai wah-tah rah-nah", translations: {en: "Goodbye", fr: "Au revoir", pid: "Bai bai"} }
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
                    { phrase: "Ina yake?", pronunciation: "ee-nah yah-keh", translations: {en: "Where is it?", fr: "Où est-ce?", pid: "Wha side?"} },
                    { phrase: "Nawa ne?", pronunciation: "nah-wah neh", translations: {en: "How much?", fr: "Combien?", pid: "How much?"} },
                    { phrase: "Wane ne? (m) / Wace ce? (f)", pronunciation: "wah-neh neh / wah-cheh cheh", translations: {en: "Who is it?", fr: "Qui est-ce?", pid: "Na who?"} },
                    { phrase: "Yaushe?", pronunciation: "yau-sheh", translations: {en: "When?", fr: "Quand?", pid: "Wha time?"} },
                    { phrase: "Me ya faru?", pronunciation: "meh yah fah-roo", translations: {en: "What happened?", fr: "Qu'est-ce qui s'est passé?", pid: "Wetin happen?"} },
                    { phrase: "Kana jin Turanci?", pronunciation: "kah-nah jeen too-ran-chee", translations: {en: "Do you speak English?", fr: "Parles-tu anglais?", pid: "You de hear English?"} },
                    { phrase: "Ban gane ba", pronunciation: "bah-n gah-neh bah", translations: {en: "I don't understand", fr: "Je ne comprends pas", pid: "A no de hear"} },
                    { phrase: "Da Allah sake faɗa", pronunciation: "dah al-lah sah-keh fah-dah", translations: {en: "Repeat please", fr: "Répétez s'il vous plaît", pid: "Talk am again"} },
                    { phrase: "Ina banɗaki yake?", pronunciation: "ee-nah bah-n-dah-kee yah-keh", translations: {en: "Where is the bathroom?", fr: "Où sont les toilettes?", pid: "Wha side toilet de?"} },
                    { phrase: "Taimake ni", pronunciation: "tai-mah-keh nee", translations: {en: "Help me", fr: "Aidez-moi", pid: "Help me"} }
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
                    { phrase: "As-salamu alaykum", pronunciation: "as-sah-lah-moo ah-lay-koom", translations: {en: "Peace be upon you", fr: "Paix sur vous", pid: "How na"} },
                    { phrase: "Wa alaykumus-salam", pronunciation: "wah ah-lay-koo-moo-s sah-lam", translations: {en: "And upon you peace", fr: "Et sur vous la paix", pid: "A de fine"} },
                    { phrase: "Jam weeti (Jam nyalli)", pronunciation: "jahm wee-tee (jahm nyah-lee)", translations: {en: "Good afternoon", fr: "Bon après-midi", pid: "Gud aphternun"} }
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
                    { phrase: "A tété / Idiba bwam", pronunciation: "ah teh-teh / ee-dee-bah bwahm", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Na som / Na som jita", pronunciation: "nah sohm / nah sohm jee-tah", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} }
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
                    { phrase: "Me boti / Me salgi we", pronunciation: "meh boh-tee / meh sahl-gee weh", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Me boti / Syé syé", pronunciation: "meh boh-tee / shay shay", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} }
                ]
            }
        ]
    },
    beti: {
        name: "Beti (Ewondo)",
        region: "Centre & South",
        speakers: "3 million",
        difficulty: "beginner",
        description: "A major Bantu language cluster spoken in the forest zones of central Cameroon (Ewondo).",
        lessons: [
            {
                title: "Greetings & Basics",
                icon: "👋",
                phrases: [
                    { phrase: "Mbolo", pronunciation: "mbo-loh", translations: {en: "Hello", fr: "Bonjour", pid: "How na"} },
                    { phrase: "Wa boga / Akiba", pronunciation: "wah boh-gah / ah-kee-bah", translations: {en: "Thank you", fr: "Merci", pid: "Tank yu"} }
                ]
            }
        ]
    }
};
// Attach to window for use in languageLearning.js
window.TRIBAL_LANGUAGE_DATA = TRIBAL_LANGUAGE_DATA;

window.TRIBAL_LANGUAGE_DATA = TRIBAL_LANGUAGE_DATA;
