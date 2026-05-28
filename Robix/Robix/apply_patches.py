
import json
import os

def update_tribes_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data = {
        "comprehensive_profiles": {
            "Bamoun": {
                "location": "Centered in the Noun Division of the West Region, Cameroon, with their historical and administrative capital at Foumban.",
                "population": "Approximately 400,000 to 500,000 individuals.",
                "languages": "Shu-mom (or Bamun), a Benue-Congo language of the Grassfields Bantu subgroup. Notably possesses its own historic indigenous writing system (the Bamum script).",
                "social_organization": "A highly centralized, stratified, and multi-layered society. It utilizes a lineage-based kinship system linked vertically to the royal court via Nji (honorific titles granted by the monarch to lineage heads and nobles).",
                "governance": "A centralized monarchical system that transformed into an influential Islamic Sultanate. The king coordinates with a council of nobles (Nji) and influential secret/regulatory societies.",
                "modern_governance": "Functions dynamically as a legally recognized traditional chiefdom (First-Class Fondom/Sultanate) under Cameroonian administrative law, bridging formal state authority with customary law.",
                "leadership": "Headed by the Sultan King of Foumban (Mfon). The palace hierarchy includes royal ministers, titled lineage heads (Nji), and the heads of institutional secret societies.",
                "culture": "A blend of deep-rooted Grassfields monarchical traditions and Islamic influences, marked by a highly sophisticated material civilization, historic literature preservation, and architectural prestige.",
                "traditions": "Celebrated through the biennial Nguon Festival, a 600-year-old ritual of governance and accountability where the rigid social hierarchy dissolves temporarily, allowing ritual leaders to publicly critique and trial the Mfon's governance.",
                "spiritual_beliefs": "Dominated by Islam (the majority faith since the early 20th century), practiced alongside deeply rooted ancestral veneration, royal cults, and traditional cosmic beliefs.",
                "oral_traditions": "Rich historical chronicles, royal geneologies, and folk narratives. Crucially, these oral traditions were systematically committed to writing using the indigenous script invented by Sultan Njoya.",
                "music_dance": "Features royal court music played on long bronze horns, ivory trumpets, and large royal drums (Mbaya). Dances are highly choreographic and performed during state ceremonies and festivals.",
                "arts_and_crafts": "Renowned globally for high-level mastery in bronze casting (using the lost-wax method), delicate woodworking (carved royal stools, pillars), textile artistry, and ancestral sculptures fully embroidered with multicolored glass beads.",
                "history": "Established in the late 14th century by Nchare Yen from the Tikar lineage. The kingdom expanded drastically through strategic conquests and assimilation of over 40 independent chiefdoms in the Noun valley.",
                "pre_contact_history": "Characterized by centuries of steady sovereign expansion, defensive architectural ditch building around the capital, and economic domination of regional trade routes under successive Mfons.",
                "colonial_impact": "Navigated German colonization smoothly via diplomatic negotiation by Sultan Njoya. Faced heavy suppression under French mandatory rule, which temporarily dismantled the formal administrative power of the monarchy and exiled the King.",
                "cultural_revitalization": "Maintained through the modern revival of the Nguon Festival, active preservation efforts at the Foumban Royal Museum, and community projects to teach the historic Bamum script to younger generations.",
                "economy": "A prosperous regional market economy driven by intensive agriculture, artisanal production, and historic positioning as a trade hub connecting the Grassfields to northern and southern Cameroon networks.",
                "subsistence_patterns": "Intensive agricultural cultivation, featuring staple food crops alongside cash crops like coffee, heavily reliant on the rich volcanic soils of the Noun division.",
                "traditional_technology": "Advanced metallurgy (highly specialized iron smelting and bronze casting), architectural brick manufacturing, sophisticated textile looms, and the historic Raphia palm and oil palm cultivation/processing complex.",
                "traditional_meals": "Kpen (a dense paste made of maize flour) served with a rich, dark traditional vegetable or groundnut soup cooked with smoked fish or game meat."
            },
            "Wimbum": {
                "location": "Located predominantly on the Nkambe Plateau within the Donga-Mantung Division of the Northwest Region, Cameroon.",
                "population": "Approximately 150,000 to 200,000 individuals.",
                "languages": "Limbum, a Grassfields Bantu language belonging to the Mbam-Nkam subgroup.",
                "social_organization": "Composed of three primary localized clans: the Warr (headquartered at Mbot), the Tang (headquartered at Tallah), and the Wiya (headquartered at Ndu). Society is organized around extended familial compounds led by a Tarlah (extended family head).",
                "governance": "Divided into highly sovereign independent fondoms. Each fondom is governed by a Nkfu (Fon) who works closely with the Kwifor (the powerful, male-only regulatory secret society that executes judicial and legislative orders).",
                "modern_governance": "Governed under the Cameroonian state framework as Second-Class or Third-Class traditional chiefdoms, where Fons serve as administrative auxiliaries to the divisional officers.",
                "leadership": "Led by the Fons (Nkfu) of the respective sovereign fondoms (e.g., Fon of Ndu, Fon of Mbot). Kingmakers hold the hereditary authority to select and install heirs, while the Tarlah manages localized lineage groups.",
                "culture": "Deeply anchored in Bamenda Grassfields values, highlighting communal solidarity, land preservation, and institutionalized conflict resolution based on social trust.",
                "traditions": "Regulated by community-wide cycles of agricultural festivals, funeral celebrations (cry-dies), and reciprocal network rituals designed to foster communal peace and relational balance.",
                "spiritual_beliefs": "A harmonious blend of Christianity and indigenous spiritual practices centered on ancestral communication, land spirits, and a supreme creator.",
                "oral_traditions": "Transmitted through rich folktales, complex riddles, and proverbs designed to pass down moral codes and the history of migration to the Nkambe plateau.",
                "music_dance": "Celebrated through highly rhythmic communal dances such as the Njang, performed using traditional wooden xylophones (Njangs), drums, and metal shakers.",
                "arts_and_crafts": "Notable for utilitarian and ritual arts, including intricate bamboo weaving, clay pottery, specialized ironwork, and embroidered traditional garments (Toghu).",
                "history": "Originated from a series of migratory movements passing through the Tikar/Ntem areas before settling permanently on the high-altitude Nkambe plateau to escape external threats and conflicts.",
                "pre_contact_history": "Formed strong socio-economic networks based on communal land tenure systems and established trading relations with both northern savanna merchants and neighboring Grassfields groups.",
                "colonial_impact": "Encountered German military excursions, followed by British administrative control under the Southern Cameroons mandate, which introduced intensive tea plantations (Ndu Tea Estate) and introduced Western education.",
                "cultural_revitalization": "Fueled by elite homecoming festivals, development associations, and specific language initiatives like the Wimbum Sign Language Project to promote inclusivity and save the native language from urban erosion.",
                "economy": "Dominated by smallholder agricultural commerce, small-scale livestock rearing, and trade inside major local highland markets.",
                "subsistence_patterns": "High-altitude agro-pastoral cultivation. Notably features a progressive customary inheritance system where women historically hold direct cultivation rights over farmlands to grow food crops.",
                "traditional_technology": "Terraced farming methods adapted to rolling high-plateau hills, bamboo construction for traditional architectures, and local iron smithing for farming tools.",
                "traditional_meals": "Cornchaff (a hearty, slow-cooked mixture of corn and beans stewed with palm oil, fish, and local spices) and pounded cocoyams served with yellow soup."
            },
            "Yebekolo": {
                "location": "Located primarily in the Haute-Sanaga and Méfou-et-Afamba divisions of the Center Region, Cameroon, lying along the forest-savanna transition zones south of the Sanaga River.",
                "population": "Approximately 40,000 to 60,000 individuals.",
                "languages": "A distinct dialect of the Beti language cluster, belonging to the North-West Bantu family.",
                "social_organization": "Traditionally segmentary and patrilineal. Society is organized around decentralized, autonomous lineages (Mvok) where authority is horizontal rather than highly centralized or monarchical.",
                "governance": "Managed historically through a council of elders and lineage heads. Unlike the Grassfields tribes, power is decentralized, relying on the Palaver system—collective deliberation and consensus-seeking among family heads.",
                "modern_governance": "Integrated into the national governance framework as Third-Class traditional chiefdoms under the Ministry of Territorial Administration, answering to the sub-divisional state officers.",
                "leadership": "Vested in lineage elders, family heads, and modern designated village chiefs (Chefs de village). Leadership is based on age, accumulated wisdom, oratorical skill, and consensus.",
                "culture": "Deeply embedded within the larger Beti-Pahuin cultural continuum of the equatorial rainforest, focusing heavily on kinship bonds, forest-lore, and generational balance.",
                "traditions": "Expressed through community life-cycle rites (birth, marriage, death), seasonal forest gatherings, and historical purification rituals designed to cleanse the lineage of internal discord.",
                "spiritual_beliefs": "Largely Roman Catholic, heavily integrated with traditional Beti cosmologies, ancestor respect, and a belief in the spiritual energy residing within the sacred equatorial forest ecosystem.",
                "oral_traditions": "Comprises historical migration narratives across the Sanaga River, genealogical recitations, and animal fables used to teach societal ethics.",
                "music_dance": "Dominated by the heavy use of the Balafon (wooden xylophone with gourd resonators) and drums, executing fast-paced, rhythmic dances common to the Beti people (such as Bikutsi roots).",
                "arts_and_crafts": "Specialized in practical rainforest crafts: palm-frond weaving, functional basketry, wooden tool sculpting, and traditional hunting trap configurations.",
                "history": "Part of the historic southward migration of the Beti-Pahuin peoples. They crossed the Sanaga River under pressure from northern groups (Vute/Mbum) and local geopolitical shifts in the 18th and 19th centuries.",
                "pre_contact_history": "Developed fluid, mobile forest communities based on shifting agriculture, hunting networks, and regional trade of forest commodities along the Sanaga waterways.",
                "colonial_impact": "Strongly affected by French colonial administrative restructuring, forced labor systems for infrastructure development, and highly aggressive Catholic missionary campaigns that dismantled many traditional institutions.",
                "cultural_revitalization": "Sustained through rural-urban elite development associations, participation in regional Beti cultural festivals, and the intentional usage of the native dialect in local church liturgy.",
                "economy": "Primarily agrarian and rural, focused heavily on food production for personal consumption and shipping surpluses to the larger urban markets of Yaoundé.",
                "subsistence_patterns": "Shifting slash-and-burn agriculture in the rainforest zone. Major crops cultivated include cassava, plantains, groundnuts, and local varieties of yams, supplemented by small-scale hunting and fishing.",
                "traditional_technology": "Specialized agricultural tools tailored for heavy forest clearing, traditional traps for game management, and mud-and-wattle home construction using local timber.",
                "traditional_meals": "Sangah (a traditional Beti dish made of fresh corn, palm nut juice, and finely shredded bitter leaf vegetables, boiled together into a thick, sweet stew)."
            }
        },
        "big_five_patches": {
            "bamileke": {
                "leadership": "Governed by the Fon (Fo/Fo'o), an absolute traditional monarch who inherits power patrilineally. The Fon rules alongside a powerful kingmaking council of nine elders (Kamveu) and regulatory secret societies (Ku'ngang, Maigari)."
            },
            "beti": {
                "leadership": "Historically decentralized and horizontal. Leadership is held by Lineage Heads (Mbombog / Mbok / Elders) who rule by consensus, age wisdom, and oratorical mastery. In the modern era, Third-Class village chiefs act as administrative leaders."
            },
            "duala": {
                "leadership": "Headed by the Paramount Chiefs (Kings) of the major royal lineages (the Bell and Akwa royal houses). Leadership is dynastic, supported by titled notables (Bona) and the Ngondo traditional council."
            },
            "fulani": {
                "leadership": "Structured under a centralized religious and political leader known as the Lamido, who rules over an Lamidat. The Lamido is assisted by a council of traditional ministers (Galdima, Sarkin), while nomadic groups look to the Ardo (lineage leader)."
            },
            "nsaw": {
                "leadership": "Led by the Fon of Nso (the paramount traditional ruler residing at the Kovifem/Kumbo palace). The Fon exercises power in tandem with the Vibai (great lords of the court) and the Ngwerong and Nggiri secret regulatory societies."
            }
        },
        "standard_group_patches": {
            "babungo": {
                "leadership": "Led by the Fon of Babungo, supported by the Tifuan (council of elders) and judicial secret societies.",
                "traditional_meals": "Pounded cocoyams served with a rich, dark bitterleaf and smoked fish soup."
            },
            "bafang": {
                "leadership": "Led by localized Fons, ruling via lineage-based titles and regulatory village councils.",
                "traditional_meals": "Koki corn (steamed fresh corn paste wrapped in banana leaves with palm oil)."
            },
            "bafanji": {
                "leadership": "Headed by the Fon of Bafanji, working in tandem with the Kwifon secret regulatory society.",
                "traditional_meals": "Achou (pounded taro coco-yam served with a bright yellow limestone-palm oil soup)."
            },
            "bafia": {
                "leadership": "Governed by Lineage Elders and modern village chiefs; historically lacked rigid, centralized kings.",
                "traditional_meals": "Kidjan (a rich groundnut paste soup cooked with local wild vegetables and served with cassava)."
            },
            "bafoussam": {
                "leadership": "Governed by the Fon (Fo'o) of Bafoussam, assisted by the Kamveu (council of nine).",
                "traditional_meals": "Kondre (a highly seasoned, slow-cooked pot of plantains, spices, and goat meat)."
            },
            "bafut": {
                "leadership": "Led by the Paramount Fon of Bafut, ruling from the historic royal palace with the Kwifor.",
                "traditional_meals": "Achou (smoothly pounded taro paste paired with a rich, yellow palm-oil and limestone soup)."
            },
            "baka": {
                "leadership": "Completely decentralized; led horizontally by Gbanzas (wise elders) and expert hunting guides.",
                "traditional_meals": "Wild forest yams roasted over open flames, paired with gathered forest mushrooms and game."
            },
            "baki": {
                "leadership": "Handled by Family Heads and local lineage elders via consensus-driven village councils.",
                "traditional_meals": "Pounded cassava served with a thick, savory leaf soup cooked with wild seeds."
            },
            "bakoko": {
                "leadership": "Headed by Clan Chiefs (Mbombog) and lineage elders within the littoral forest zone.",
                "traditional_meals": "Miondo (fermented, thinly wrapped cassava sticks) served with fresh, spicy fish soup."
            },
            "bakola": {
                "leadership": "Semi-nomadic structure led by Senior Hunters and elder gatherers via group consensus.",
                "traditional_meals": "Roasted plantains served with bushmeat stew and gathered wild forest roots."
            },
            "bakossi": {
                "leadership": "Headed by the Clan Council of Elders and traditional chiefs holding ritual land authority.",
                "traditional_meals": "Esubag (pounded cocoyams) eaten with a highly seasoned wild bush-vegetable soup."
            },
            "bakundu": {
                "leadership": "Led by Village Chiefs and traditional councilors within the Oroko cultural union.",
                "traditional_meals": "Ambandi (pounded plantains or cassava) served with a rich, dark leaf and bushmeat broth."
            },
            "bakweri": {
                "leadership": "Headed by the Paramount Chiefs (e.g., of Buea) and the Maale (Elephant Secret Society).",
                "traditional_meals": "Timambusa (pounded cocoyams mixed with young cocoyam leaves, palm oil, and fresh fish)."
            },
            "baleng": {
                "leadership": "Governed by a localized Fon, supported by secret societies and royal court notables.",
                "traditional_meals": "Kondre (highly spiced plantains and meat porridge cooked inside a single clay pot)."
            },
            "bali": {
                "leadership": "Headed by the Fon of Bali (Ganyonga), a centralized palace hierarchy of Chamba origin.",
                "traditional_meals": "Vake (pounded corn/maize fufu) paired with a deeply savory huckleberry vegetable soup."
            },
            "balondo": {
                "leadership": "Managed by Elder Councils and local village chiefs along the coastal creek networks.",
                "traditional_meals": "Fresh catch fish soup heavily seasoned with local spices, served with boiled green plantains."
            },
            "bamendjou": {
                "leadership": "Led by the Fon of Bamendjou, working with traditional kingmakers and elite title-holders.",
                "traditional_meals": "Pounded maize cooked into a dense paste and served with a rich groundnut and beef soup."
            },
            "bamenyam": {
                "leadership": "Governed by a traditional Fon, working with local lineage heads on the Grassfields edge.",
                "traditional_meals": "Corn fufu accompanied by a thick, spiced huckleberry vegetable and smoked meat stew."
            },
            "bamessing": {
                "leadership": "Led by the Fon of Bamessing, closely advised by the Kwifon and master craft elders.",
                "traditional_meals": "Pounded cocoyams served alongside a well-seasoned garden egg (eggplant) and fish soup."
            }
        }
    }

    # Apply comprehensive profiles
    for name, sections in new_data["comprehensive_profiles"].items():
        key = name.lower()
        if key in data:
            data[key]["sections"].update(sections)
            print(f"Updated full profile for {name}")

    # Apply Big Five patches
    for key, sections in new_data["big_five_patches"].items():
        if key in data:
            data[key]["sections"].update(sections)
            print(f"Patched Big Five: {key}")

    # Apply Standard group patches
    for key, sections in new_data["standard_group_patches"].items():
        if key in data:
            data[key]["sections"].update(sections)
            print(f"Patched Standard Group: {key}")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    update_tribes_data(r"c:\Users\manuel\Desktop\CULTIA\Robix\Robix\cultureAI\intelligent_tribes_data.json")
