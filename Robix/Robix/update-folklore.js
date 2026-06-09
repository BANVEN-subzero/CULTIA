
const fs = require('fs');
const path = require('path');

const stories = [
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

const completionSection = `
                <!-- Complete Story & Claim Points Section -->
                <div class="mt-5 p-4 bg-light rounded-4 text-center" id="claimSection">
                    <h5 class="fw-bold mb-3"><i class="fas fa-coins text-warning me-2"></i> Ready to Claim Your Points?</h5>
                    <p class="text-muted mb-4">Mark this story as completed and earn <span id="storyPoints" class="fw-bold text-success">50</span> points!</p>
                    <button id="completeStoryBtn" class="btn btn-success btn-lg rounded-pill px-5">
                        <i class="fas fa-check-circle me-2"></i> Complete Story & Claim Points
                    </button>
                </div>
`;

const modal = `
    <!-- Congratulation Modal -->
    <div class="modal fade" id="congratsModal" tabindex="-1" aria-labelledby="congratsModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0" style="border-radius: 35px; overflow: hidden;">
                <div class="modal-body p-0">
                    <div class="container-fluid">
                        <div class="row g-0">
                            <div class="col-md-5" style="background: linear-gradient(135deg, #2d5a27 0%, #1a3a17 100%);">
                                <div class="h-100 d-flex flex-column align-items-center justify-content-center p-5 text-white">
                                    <div class="mb-4" data-aos="zoom-in">
                                        <i class="fas fa-trophy" style="font-size: 120px; color: #f39c12;"></i>
                                    </div>
                                    <div class="text-center">
                                        <h2 class="fw-bold mb-2">
                                        </h2>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-7 p-5">
                                <div class="d-flex justify-content-end mb-3">
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <h3 class="fw-bold mb-3" style="color: #2d5a27;">
                                    <i class="fas fa-star text-warning me-2"></i>Congratulations!
                                </h3>
                                <p class="text-muted mb-4">You've completed the story and earned your points!</p>
                                
                                <div class="d-flex align-items-center gap-3 p-4 bg-success bg-opacity-10 rounded-3 mb-4">
                                    <div class="bg-success bg-opacity-20 p-3 rounded-3">
                                        <i class="fas fa-coins text-success" style="font-size: 2rem;"></i>
                                    </div>
                                    <div>
                                        <div class="fw-bold" style="color: #2d5a27;">50 Points Earned</div>
                                        <div class="text-muted small">Keep exploring to earn more!</div>
                                    </div>
                                    <div class="ms-auto">
                                        <span class="fw-bold text-success" style="font-size: 2.5rem;">+50</span>
                                    </div>
                                </div>

                                <div class="d-grid gap-2">
                                    <button type="button" class="btn btn-success btn-lg rounded-pill" id="continueBtn">
                                        Continue Exploring <i class="fas fa-arrow-right ms-2"></i>
                                    </button>
                                    <a href="folkloreAndMyths.html" class="btn btn-outline-success btn-lg rounded-pill">
                                        <i class="fas fa-book me-2"></i> Read Another Story
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
`;

const script = (storyId) => `
    <!-- Gamification JS -->
    <script src="js/gamification.js"></script>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            AOS.init({ duration: 800, once: true });
            
            // Shared Components
            fetch('includes/sidebar.html').then(r => r.text()).then(data => {
                document.getElementById('sidebar-container').innerHTML = data;
            });
            fetch('includes/header.html').then(r => r.text()).then(data => {
                document.getElementById('header-container').innerHTML = data.replace('{{PAGE_TITLE}}', 'Story');
            });

            // Complete Story Button
            const completeBtn = document.getElementById('completeStoryBtn');
            const claimSection = document.getElementById('claimSection');
            const congratsModal = new bootstrap.Modal(document.getElementById('congratsModal'));
            
            completeBtn.addEventListener('click', async function() {
                const storyId = '${storyId}';
                
                try {
                    const response = await fetch(\`/api/folklore/progress/\${storyId}/complete\`, {
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
                            
                            // Show modal
                            congratsModal.show();
                            
                            AOS.refresh();
                        } else if (!data.success) {
                            alert(data.error || 'Something went wrong');
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
    </script>
`;

stories.forEach(storyId => {
    const filePath = path.join(__dirname, 'Frontends', 'bot', `${storyId}.html`);
    if (!fs.existsSync(filePath)) {
        console.warn(`File not found: ${filePath}`);
        return;
    }

    let content = fs.readFileSync(filePath, 'utf8');

    // Find the cultural-note div
    const culturalNoteEnd = '</div>\n            </div>\n        </div>\n    </div>';
    if (!content.includes(culturalNoteEnd)) {
        console.warn(`Could not find cultural note in ${filePath}`);
        return;
    }

    // Add completion section after cultural note
    content = content.replace(culturalNoteEnd, culturalNoteEnd.replace('</div>\n            </div>', completionSection + '\n            </div>'));

    // Add modal before bootstrap js
    const bootstrapJsTag = '<!-- Bootstrap 5 JS -->';
    if (!content.includes(bootstrapJsTag)) {
        console.warn(`Could not find Bootstrap JS in ${filePath}`);
        return;
    }

    content = content.replace(bootstrapJsTag, modal + '\n\n' + bootstrapJsTag);

    // Replace existing script with updated one
    const oldScriptStart = '<!-- AOS Animations JS -->\n    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>\n\n    <script>';
    const oldScriptEnd = '    </script>';
    if (content.includes(oldScriptStart)) {
        const newScript = `<!-- AOS Animations JS -->\n    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>` + script(storyId);
        const oldScriptMatch = content.match(new RegExp(oldScriptStart.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[\\s\\S]*?' + oldScriptEnd.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
        if (oldScriptMatch) {
            content = content.replace(oldScriptMatch[0], newScript);
        }
    }

    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Updated: ${filePath}`);
});
