
const fs = require('fs');
const path = require('path');

const stories = [
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

const updateStoryFile = (storyId) => {
    const filePath = path.join(__dirname, 'Frontends', 'bot', `${storyId}.html`);
    if (!fs.existsSync(filePath)) {
        console.warn(`File not found: ${filePath}`);
        return;
    }
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Step 1: Add the claim section and modal
    const sectionToFind = `<div class="text-center py-4">
        <a href="folkloreAndMyths.html" class="btn btn-outline-success rounded-pill px-5 py-3">
            <i class="fas fa-arrow-left me-2"></i> Back to Stories
        </a>
    </div>`;
    
    const newSection = `        <div id="claimSection" class="bg-light rounded-4 p-5 mb-5 text-center">
            <div class="mb-3">
                <i class="fas fa-coins text-warning" style="font-size: 3rem;"></i>
            </div>
            <h4 class="fw-bold mb-2">Ready to Claim Your Points?</h4>
            <p class="text-muted mb-4">Mark this story as completed and earn <strong class="text-success">+50</strong> points!</p>
            <button id="completeStoryBtn" class="btn btn-success btn-lg rounded-pill px-5">
                <i class="fas fa-check-circle me-2"></i> Complete Story & Claim Points
            </button>
        </div>

        <!-- Beautiful Completion Modal -->
        <div class="modal fade" id="congratsModal" tabindex="-1" aria-labelledby="congratsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content rounded-4 border-0 shadow-lg overflow-hidden">
                    <div class="modal-header bg-gradient text-center" style="background: linear-gradient(135deg, #2d5a27 0%, #1a3a17 100%); border: none;">
                        <h5 class="modal-title text-white fw-bold" id="congratsModalLabel">🎉 Congratulations!</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body p-5 text-center">
                        <div class="mb-4">
                            <div class="mx-auto bg-success bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center" style="width: 100px; height: 100px;">
                                <i class="fas fa-trophy text-success" style="font-size: 3.5rem;"></i>
                            </div>
                        </div>
                        <h4 class="fw-bold mb-2">Story Completed!</h4>
                        <p class="text-muted mb-4">You've earned <strong class="text-success" style="font-size: 1.5rem;">+50 points</strong> for completing this story!</p>
                    </div>
                    <div class="modal-footer border-0 justify-content-center gap-3">
                        <button type="button" class="btn btn-secondary rounded-pill px-4" id="continueBtn">
                            Continue Exploring
                        </button>
                        <a href="folkloreAndMyths.html" class="btn btn-success rounded-pill px-4">
                            Read Another Story
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <div class="text-center py-4">
            <a href="folkloreAndMyths.html" class="btn btn-outline-success rounded-pill px-5 py-3">
                <i class="fas fa-arrow-left me-2"></i> Back to Stories
            </a>
        </div>`;
    
    content = content.replace(sectionToFind, newSection);
    
    // Step 2: Update the script section
    const scriptToFind = `    <script>
        document.addEventListener('DOMContentLoaded', function() {
            AOS.init({ duration: 800, once: true });
            
            // Load Header and Sidebar
            fetch('includes/sidebar.html').then(r => r.text()).then(data => {
                document.getElementById('sidebar-container').innerHTML = data;
            });
            fetch('includes/header.html').then(r => r.text()).then(data => {
                document.getElementById('header-container').innerHTML = data.replace('{{PAGE_TITLE}}', 'Story');
            });
        });
    </script>`;
    
    const newScript = `    <script>
        document.addEventListener('DOMContentLoaded', function() {
            AOS.init({ duration: 800, once: true });
            
            // Load Header and Sidebar
            fetch('includes/sidebar.html').then(r => r.text()).then(data => {
                document.getElementById('sidebar-container').innerHTML = data;
            });
            fetch('includes/header.html').then(r => r.text()).then(data => {
                document.getElementById('header-container').innerHTML = data.replace('{{PAGE_TITLE}}', 'Story');
                
                // Initialize Theme Toggle in Header
                if (window.settingsManager) {
                    window.settingsManager.initHeaderThemeToggle();
                }
            });

            // Complete Story Button
            const completeBtn = document.getElementById('completeStoryBtn');
            const claimSection = document.getElementById('claimSection');
            const congratsModal = new bootstrap.Modal(document.getElementById('congratsModal'));
            
            // First, check if story is already completed on load
            async function checkStoryCompletion() {
                try {
                    const storyIdParam = '${storyId}';
                    const progressResponse = await fetch('/api/folklore/progress', { credentials: 'include' });
                    if (progressResponse.ok) {
                        const progressData = await progressResponse.json();
                        if (progressData.success && progressData.progress && progressData.progress[storyIdParam] && progressData.progress[storyIdParam].is_completed) {
                            // Already completed
                            claimSection.innerHTML = \`
                                <div class="p-4">
                                    <div class="d-flex align-items-center justify-content-center gap-3 mb-3">
                                        <div class="bg-success bg-opacity-10 p-3 rounded-3">
                                            <i class="fas fa-check-circle text-success" style="font-size: 2.5rem;"></i>
                                        </div>
                                        <div class="text-start">
                                            <h5 class="fw-bold mb-0" style="color: #2d5a27;">Story Completed!</h5>
                                            <p class="text-muted mb-0">+50 points earned</p>
                                        </div>
                                    </div>
                                </div>
                            \`;
                            completeBtn.disabled = true;
                            completeBtn.innerHTML = '<i class="fas fa-check me-2"></i>Already Completed';
                            completeBtn.className = 'btn btn-secondary btn-lg rounded-pill px-5';
                        }
                    }
                } catch (err) {
                    console.error('Error checking story completion:', err);
                }
            }
            
            checkStoryCompletion();
            
            completeBtn.addEventListener('click', async function() {
                const storyIdParam = '${storyId}';
                
                try {
                    const response = await fetch(\`/api/folklore/progress/\${storyIdParam}/complete\`, {
                        method: 'POST',
                        credentials: 'include'
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success && data.points_awarded > 0) {
                            // Show notification via gamification system
                            if (window.gamification) {
                                window.gamification.points += data.points_awarded;
                                window.gamification.updateUI();
                                window.gamification.broadcastUpdate();
                            }
                            
                            // Update the section
                            claimSection.innerHTML = \`
                                <div class="p-4">
                                    <div class="d-flex align-items-center justify-content-center gap-3 mb-3">
                                        <div class="bg-success bg-opacity-10 p-3 rounded-3">
                                            <i class="fas fa-check-circle text-success" style="font-size: 2.5rem;"></i>
                                        </div>
                                        <div class="text-start">
                                            <h5 class="fw-bold mb-0" style="color: #2d5a27;">Story Completed!</h5>
                                            <p class="text-muted mb-0">+50 points earned</p>
                                        </div>
                                    </div>
                                </div>
                            \`;
                            
                            // Disable button
                            completeBtn.disabled = true;
                            completeBtn.innerHTML = '<i class="fas fa-check me-2"></i>Already Completed';
                            completeBtn.className = 'btn btn-secondary btn-lg rounded-pill px-5';
                            
                            // Show modal
                            congratsModal.show();
                            
                            AOS.refresh();
                        } else if (!data.success) {
                            // Handle already completed gracefully
                            if (data.message && data.message.includes('already')) {
                                claimSection.innerHTML = \`
                                    <div class="p-4">
                                        <div class="d-flex align-items-center justify-content-center gap-3 mb-3">
                                            <div class="bg-success bg-opacity-10 p-3 rounded-3">
                                                <i class="fas fa-check-circle text-success" style="font-size: 2.5rem;"></i>
                                            </div>
                                            <div class="text-start">
                                                <h5 class="fw-bold mb-0" style="color: #2d5a27;">Story Completed!</h5>
                                                <p class="text-muted mb-0">+50 points earned</p>
                                            </div>
                                        </div>
                                    </div>
                                \`;
                                completeBtn.disabled = true;
                                completeBtn.innerHTML = '<i class="fas fa-check me-2"></i>Already Completed';
                                completeBtn.className = 'btn btn-secondary btn-lg rounded-pill px-5';
                            } else {
                                alert(data.error || 'Something went wrong');
                            }
                        }
                    }
                } catch (error) {
                    console.error('Error completing story:', error);
                    alert('Error completing story. Please try again.');
                }
            });

            document.getElementById('continueBtn').addEventListener('click', function() {
                congratsModal.hide();
            });
        });
    </script>`;
    
    content = content.replace(scriptToFind, newScript);
    
    // Step 3: Update CSS to add padding-top to story-container
    const oldCSS = `        .story-container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 40px;
            padding: 60px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.05);
            position: relative;
            z-index: 10;
        }`;
    
    const newCSS = `        .story-container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 40px;
            padding: 80px 60px 60px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.05);
            position: relative;
            z-index: 10;
        }`;
    
    content = content.replace(oldCSS, newCSS);
    
    // Step 4: Ensure settingsManager.js is included
    if (!content.includes('js/settingsManager.js')) {
        const jsInclude = `    <!-- Add Settings Manager -->
    <script src="js/settingsManager.js"></script>`;
        content = content.replace('<!-- Bootstrap 5 JS -->', `${jsInclude}\n    <!-- Bootstrap 5 JS -->`);
    }
    
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✅ Updated: ${filePath}`);
};

stories.forEach(updateStoryFile);

console.log('\n🎉 All folklore stories updated successfully!');
