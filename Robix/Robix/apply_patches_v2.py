
import json
import os

def update_tribes_data_v2(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    patches = {
        "bamesso": { 
             "leadership": "Headed by a localized Fon who maintains a traditional court and lineage advisors.", 
             "traditional_meals": "Koki corn cooked with palm oil and wrapped securely in native banana leaves." 
         }, 
         "bamukumbit": { 
             "leadership": "Governed by the Fon of Bamukumbit, ruling with hereditary palace ministers.", 
             "traditional_meals": "Maize fufu served with a highly aromatic, dark green vegetable stew containing bushmeat." 
         }, 
         "bamumka": { 
             "leadership": "Led by the Fon of Bamumka, coordinating directly with the village regulatory councils.", 
             "traditional_meals": "Achou (pounded taro served alongside the classic yellow limestone-and-palm-oil soup)." 
         }, 
         "bamungo": { 
             "leadership": "Guided by Lineage Heads and traditional village chiefs in the Northwest high plateau.", 
             "traditional_meals": "Cornchaff (a slow-simmered mixture of whole corn kernels, beans, and palm oil)." 
         }, 
         "bamunka": { 
             "leadership": "Governed by the Fon of Bamunka, working in tandem with the Kwifon secret society.", 
             "traditional_meals": "Achou (smooth taro paste served with a rich, yellow spiced limestone soup)." 
         }, 
         "bana": { 
             "leadership": "Headed by the Fon (Fo'o) of Bana, supported by a closed council of noble title holders.", 
             "traditional_meals": "Kondre (peeled green plantains slow-stewed with goat meat, onions, and local spices)." 
         }, 
         "bandjoun": { 
             "leadership": "Governed by the powerful Fon (Fo'o) of Bandjoun, ruling a major, centralized chiefdom.", 
             "traditional_meals": "Koki corn paired with Kondre plantains during major royal and cultural festivals." 
         }, 
         "bangangte": { 
             "leadership": "Led by the Fon (Fo'o) of Bangangt\u00e9, working with the Kamveu council of elders.", 
             "traditional_meals": "Pounded macabo (cocoyam) paired with a highly nutritious black soup made of wild seeds." 
         }, 
         "bassa": { 
             "leadership": "Historically decentralized; led by the Mbombog (highly respected ritual and political leaders).", 
             "traditional_meals": "Plum Soup (Sauce Nd\u00f4) served alongside fresh Banga (palm nut) rice or Miondo." 
         }, 
         "batanga": { 
             "leadership": "Governed by Coastal Chiefs and elder councils holding historic maritime authority.", 
             "traditional_meals": "Mba (pounded cassava paste cooked in leaves) served with fresh, hot sea-fish bouillon." 
         }, 
         "bayangam": { 
             "leadership": "Led by the Fon of Bayangam, supported by traditional palace administrative circles.", 
             "traditional_meals": "Kondre (a rich, savory plantain porridge cooked with beef, palm oil, and local basil)." 
         }, 
         "bedzan": { 
             "leadership": "Decentralized; led horizontally by Elder Pygmy Hunters based on deep forest knowledge.", 
             "traditional_meals": "Wild forest honey, roasted wild tubers, and smoked river fish cooked over open coals." 
         }, 
         "bororo": { 
             "leadership": "Led by the Ardo (a hereditary lineage and camp leader who manages cattle migrations).", 
             "traditional_meals": "Kosam (fresh or fermented cow's milk) consumed alongside a thick cornmeal paste." 
         }, 
         "bulu": { 
             "leadership": "Managed by Lineage Chiefs (Mbombog) and village elders within a decentralized structure.", 
             "traditional_meals": "Sangah (fresh maize, palm nut cream, and bitterleaf greens boiled into a thick stew)." 
         }, 
         "esu": { 
             "leadership": "Headed by the Fon of Esu, ruling alongside traditional kingmakers in Menchum division.", 
             "traditional_meals": "Corn fufu served with a rich, slippery okra soup containing smoked river fish." 
         }, 
         "eton": { 
             "leadership": "Governed by Lineage Heads and family elders; lacked centralized monarchs pre-colonially.", 
             "traditional_meals": "Sangah (maize and cassava leaves stewed slowly in freshly extracted palm nut juice)." 
         }, 
         "ewondo": { 
             "leadership": "Led by Lineage Elders; modern structure features paramount chiefs recognized by the state.", 
             "traditional_meals": "Kpem (finely pounded cassava leaves cooked into a creamy paste with palm nut pulp)." 
         }, 
         "fang": { 
             "leadership": "Led horizontally by the Mbomo Mvok (lineage or clan heads) based on generational wisdom.", 
             "traditional_meals": "Kpem cooked with palm oil, served alongside boiled sweet cassava roots or plantains." 
         }, 
         "giziga": { 
             "leadership": "Headed by a traditional ruler known as the Bi-Gisiga (Prince/Chief) in the Far North.", 
             "traditional_meals": "Thick sorghum fufu paired with a highly seasoned okra or dried baobab leaf soup." 
         }, 
         "grassfields": { 
             "leadership": "Umbrella term; uniformly led by a Fon working with a Kwifon/Mfam regulatory society.", 
             "traditional_meals": "Achou or Corn Fufu served with savory huckleberry or bitterleaf vegetable soups." 
         }, 
         "hausa": { 
             "leadership": "Led by the Sarki (Chief/King), who coordinates trade, religious, and community affairs.", 
             "traditional_meals": "Tuwo Shinkafa (a thick, gelatinous rice flour fufu) served with Miyan Kuka (baobab soup)." 
         }, 
         "isubu": { 
             "leadership": "Headed historically by Coastal Kings and Chiefs (e.g., King William of Bimbia).", 
             "traditional_meals": "Boiled sweet potatoes paired with a rich, highly spiced fresh sea-fish broth." 
         }, 
         "kanuri": { 
             "leadership": "Governed by a highly centralized traditional ruler known as the Mai or local law elders.", 
             "traditional_meals": "Bisku (a dense millet or sorghum porridge) served with a rich, spiced meat broth." 
         }, 
         "kapsiki": { 
             "leadership": "Led by the Melu (Village Chief), who functions as a political leader and ritual mediator.", 
             "traditional_meals": "Millet fufu dipped into a savory soup made of groundnut paste and local wild greens." 
         }, 
         "kom": { 
             "leadership": "Headed by the Fon of Kom, who rules from Laikom with the Kwifoyn society and the Anlu.", 
             "traditional_meals": "Corn fufu served with Njama-Njama (highly seasoned, saut\u00e9ed huckleberry leaves)." 
         }, 
         "kotoko": { 
             "leadership": "Governed by a centralized sultan or Mra (Sultan/King) ruling over fortified river towns.", 
             "traditional_meals": "Dried fish stew served with a smooth, heavy sorghum or rice paste porridge." 
         }, 
         "mafa": { 
             "leadership": "Led by the Bula (Lineage/Village Head) and traditional rainmakers in the Mandara mountains.", 
             "traditional_meals": "Sorghum fufu paired with a rich, dark soup made from dried baobab leaves and seeds." 
         }, 
         "maka": { 
             "leadership": "Historically decentralized; led via Lineage Elders and councils of wise family heads.", 
             "traditional_meals": "Pounded plantains or cassava served with a rich wild bush-mango seed (Ekwang) soup." 
         }, 
         "mass": { 
             "leadership": "Headed by the Tokwomna (traditional chief/land chief) who regulates cattle and crop lands.", 
             "traditional_meals": "Millet porridge served with fresh cow's milk or a savory river fish stew." 
         }, 
         "mbo": { 
             "leadership": "Led by Clan Chiefs and lineage councils within the southwestern forest zone.", 
             "traditional_meals": "Pounded cocoyams served with a highly aromatic, slow-cooked wild herb soup." 
         }, 
         "mbum": { 
             "leadership": "Governed by the Belaka (centralized traditional king or chief) in the Adamawa region.", 
             "traditional_meals": "Millet fufu paired with a rich, savory vegetable soup seasoned with groundnut paste." 
         }, 
         "menka": { 
             "leadership": "Headed by localized Village Fons and councils of elders within the Momo division.", 
             "traditional_meals": "Corn fufu served with a thick, slippery soup made of fresh wild mushrooms and okra." 
         }, 
         "moundang": { 
             "leadership": "Governed by a traditional centralized ruler known as the Gong (King) of L\u00e9r\u00e9.", 
             "traditional_meals": "Sorghum paste served with a highly seasoned soup made of groundnuts and wild greens." 
         }, 
         "north_bantu": { 
             "leadership": "Umbrella term; uniformly led by Lineage Elders and decentralized family head councils.", 
             "traditional_meals": "Pounded cassava served with a rich, green leaf soup cooked in fresh palm oil." 
         }, 
         "aghem": { 
             "leadership": "Led by the Fon of Wum (Aghem), assisted by a council of traditional palace kingmakers.", 
             "traditional_meals": "Corn fufu served with a highly seasoned dish of huckleberry leaves (Njama-Njama)." 
         }, 
         "oroko": { 
             "leadership": "Governed by a Council of Chiefs representing the 10 distinct Oroko clan sub-groups.", 
             "traditional_meals": "Ambandi (smoothly pounded plantains) served with a rich, dark Eru or bitterleaf soup." 
         }, 
         "sawa": { 
             "leadership": "Coastal umbrella group; led by Paramount Kings and Chiefs along the Atlantic coast.", 
             "traditional_meals": "Missole (roasted sweet plantains) paired with grilled or stewed fresh sea-fish." 
         }, 
         "tikar": { 
             "leadership": "Governed by the Fon or Ngou (King), who heads a highly centralized palace hierarchy.", 
             "traditional_meals": "Pounded maize fufu served with a deeply savory soup made of ground pumpkin seeds." 
         }, 
         "tupuri": { 
             "leadership": "Led by the Wang (Chief/Spiritual Leader), who holds immense spiritual and land authority.", 
             "traditional_meals": "Millet paste porridge consumed with a highly nutritious wild leaf and fish broth." 
         }, 
         "widikum": { 
             "leadership": "Led by Village Chiefs and lineage councils; historically lacked a single centralized king.", 
             "traditional_meals": "Achou (pounded taro served with a savory yellow limestone-and-palm-oil soup)." 
         } 
    }

    for key, sections in patches.items():
        if key not in data:
            # Create a new tribe entry if it doesn't exist
            data[key] = {
                "name": key.replace('_', ' ').title(),
                "aliases": [key.replace('_', ' ').title()],
                "sections": sections,
                "keywords": [key.replace('_', ' ').lower(), "traditional", "cultural", "cameroon"],
                "metadata": {
                    "tribe_key": key,
                    "confidence_score": 0.5,
                    "total_paragraphs": 2,
                    "total_words": 50
                }
            }
            print(f"Created new tribe: {key}")
        else:
            # Update existing tribe
            data[key]["sections"].update(sections)
            print(f"Updated tribe: {key}")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    update_tribes_data_v2(r"c:\Users\manuel\Desktop\CULTIA\Robix\Robix\cultureAI\intelligent_tribes_data.json")
