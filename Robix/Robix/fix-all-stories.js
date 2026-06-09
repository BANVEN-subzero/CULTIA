
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

    // 1. Update story-container padding to prevent overlap with back button
    content = content.replace(
        /padding:\s*60px;/g,
        'padding: 80px 60px 60px;'
    );

    // 2. Make sure we have settingsManager script
    if (!content.includes('js/settingsManager.js')) {
        content = content.replace(
            '<!-- Bootstrap 5 JS -->',
            '<!-- Add Settings Manager -->\n    <script src="js/settingsManager.js"></script>\n    <!-- Bootstrap 5 JS -->'
        );
    }

    // 3. Update the script section to properly initialize everything
    const scriptStart = '<script>\n        document.addEventListener(\'DOMContentLoaded\', function() {\n            AOS.init({ duration: 800, once: true });';
    const scriptEnd = '        });\n    </script>';

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
            let congratsModal;
            
            // First, check if story is already completed on load
            async function checkStoryCompletion() {
                try {
                    const progressResponse = await fetch('/api/folklore/progress', { credentials: 'include' });
                    if (progressResponse.ok) {
                        const progressData = await progressResponse.json();
                        if (progressData.success && progressData.progress && progressData.progress['${storyId}'] && progressData.progress['${storyId}'].is_completed) {
                            // Already completed
                            if (claimSection) {
                                claimSection.innerHTML = \`
                                    <div class="p-4">
                                        <div class="d-flex align-items-center justify-content-center gap-3 mb-3">
                                            <div class="bg-success bg-opacity-10 p-3 rounded-3">
                                                <i class="fas fa-check-circle text-success" style="font-size: 2.5rem;"></i>
                                            </div>
                                            <div class="text-start">
                                                <h6 class="fw-bold mb-0" style="color: #2d5a27;">Story Completed!</h6>
                                                <p class="text-muted mb-0">+50 points earned</p>
                                            </div>
                                        </div>
                                    </div>
                                \`;
                                if (completeBtn) {
                                    completeBtn.disabled = true;
                                    completeBtn.innerHTML = '<i class="fas fa-check me-2"></i>Already Completed';
                                    completeBtn.className = 'btn btn-secondary btn-lg rounded-pill px-5';
                                }
                            }
                        }
                    }
                } catch (err) {
                    console.error('Error checking story completion:', err);
                }
            }
            
            // Initialize modal
            const modalElement = document.getElementById('congratsModal');
            if (modalElement && window.bootstrap) {
                congratsModal = new bootstrap.Modal(modalElement);
            }
            
            checkStoryCompletion();
            
            if (completeBtn) {
                completeBtn.addEventListener('click', async function() {
                    try {
                        const response = await fetch(\`/api/folklore/progress/\${'${storyId}'}/complete\`, {
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
                                if (claimSection) {
                                    claimSection.innerHTML = \`
                                        <div class="p-4">
                                            <div class="d-flex align-items-center justify-content-center gap-3 mb-3">
                                                <div class="bg-success bg-opacity-10 p-3 rounded-3">
                                                    <i class="fas fa-check-circle text-success" style="font-size: 2.5rem;"></i>
                                                </div>
                                                <div class="text-start">
                                                    <h6 class="fw-bold mb-0" style="color: #2d5a27;">Story Completed!</h6>
                                                    <p class="text-muted mb-0">+50 points earned</p>
                                                </div>
                                            </div>
                                        </div>
                                    \`;
                                    completeBtn.disabled = true;
                                    completeBtn.innerHTML = '<i class="fas fa-check me-2"></i>Already Completed';
                                    completeBtn.className = 'btn btn-secondary btn-lg rounded-pill px-5';
                                }
                                
                                // Show modal if available
                                if (congratsModal) {
                                    congratsModal.show();
                                }
                            } else if (!data.success) {
                                // Handle already completed gracefully
                                if (data.message && data.message.includes('already')) {
                                    if (claimSection) {
                                        claimSection.innerHTML = \`
                                            <div class="p-4">
                                                <div class="d-flex align-items-center justify-content-center gap-3 mb-3">
                                                    <div class="bg-success bg-opacity-10 p-3 rounded-3">
                                                        <i class="fas fa-check-circle text-success" style="font-size: 2.5rem;"></i>
                                                    </div>
                                                    <div class="text-start">
                                                        <h6 class="fw-bold mb-0" style="color: #2d5a27;">Story Completed!</h6>
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
                            }
                        }
                    } catch (error) {
                        console.error('Error completing story:', error);
                        alert('Error completing story. Please try again.');
                    }
                });
            }

            // Add continue button listener if modal exists
            const continueBtn = document.getElementById('continueBtn');
            if (continueBtn && congratsModal) {
                continueBtn.addEventListener('click', function() {
                    congratsModal.hide();
                });
            }
        });
    </script>`;

    // Find and replace the old script section
    const scriptRegex = /<script>[\s\S]*?<\/script>/;
    if (scriptRegex.test(content)) {
        content = content.replace(scriptRegex, newScript);
    } else {
        // If no script, add it before closing body
        content = content.replace('</body>', newScript + '\n</body>');
    }

    // 4. Add the claim section and beautiful modal if they don't exist
    if (!content.includes('id="claimSection"')) {
        // Find where to insert the claim section (before back button or end of content)
        const beforeBack = /(<div class="text-center py-4">[\s\S]*?Back to Stories[\s\S]*?<\/div>)/;
        const claimAndModal = `
        <!-- Complete Story & Claim Points Section -->
        <div class="mt-5 p-5 bg-light rounded-4 text-center" id="claimSection">
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

        $1`;
        content = content.replace(beforeBack, claimAndModal);
    }

    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✅ Updated: ${storyId}.html`);
});

console.log('\n🎉 All folklore story pages updated!');
