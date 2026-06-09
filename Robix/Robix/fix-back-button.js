
const fs = require('fs');
const path = require('path');

const stories = [
    'talking_python',
    'magic_mirror',
    'woman_tree',
    'bird_fon',
    'rainmaker_drum',
    'river_goddess',
    'crocodile_wouri',
    'forest_drummers',
    'woman_snake',
    'fire_sky',
    'wind_children',
    'lobe_river'
];

stories.forEach(storyId => {
    const filePath = path.join(__dirname, 'Frontends', 'bot', `${storyId}.html`);
    if (!fs.existsSync(filePath)) {
        console.warn(`File not found: ${filePath}`);
        return;
    }

    let content = fs.readFileSync(filePath, 'utf8');

    // Update CSS: add padding-top to story-container and adjust back-btn
    const oldCSS = `
        .story-container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 40px;
            padding: 60px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.05);
            position: relative;
            z-index: 10;
        }
`;
    const newCSS = `
        .story-container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 40px;
            padding: 80px 60px 60px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.05);
            position: relative;
            z-index: 10;
        }
`;

    content = content.replace(oldCSS, newCSS);

    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Fixed back button in: ${filePath}`);
});
