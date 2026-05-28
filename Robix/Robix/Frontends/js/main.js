// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Theme is now managed by themeManager.js
    
    // Mobile Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
        
        // Close mobile menu when clicking on a link
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }
    
    // Back button functionality
    const backButtons = document.querySelectorAll('.back-button');
    backButtons.forEach(button => {
        // If the button doesn't have an explicit href, use history.back()
        if (!button.hasAttribute('href')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                window.history.back();
            });
        }
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Header scroll effect
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }
    
    // Parallax effect for hero section
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.pageYOffset;
            heroSection.style.backgroundPositionY = `${scrollPosition * 0.5}px`;
        });
    }
    
    // Fade in animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.card, .hero-content, .section h2');
    animateElements.forEach(el => {
        observer.observe(el);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#dc3545';
                } else {
                    input.style.borderColor = '#7EBD3A';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // Contact form submission (placeholder)
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
        });
    }
    
    // Login form submission is handled in individual page scripts
    
    // Blog category filtering
    const categoryButtons = document.querySelectorAll('.category-btn');
    const blogPosts = document.querySelectorAll('.blog-post');
    
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.dataset.category;
            
            // Update active button
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter posts
            blogPosts.forEach(post => {
                if (category === 'all' || post.dataset.category === category) {
                    post.style.display = 'block';
                } else {
                    post.style.display = 'none';
                }
            });
        });
    });
    
    // Tab functionality for features and explore pages
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Update active button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Show target content
            tabContents.forEach(content => {
                if (content.id === targetTab) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
        });
    });
    
    // Initialize first tab as active
    if (tabButtons.length > 0) {
        tabButtons[0].classList.add('active');
        if (tabContents.length > 0) {
            tabContents[0].classList.add('active');
        }
    }

    // Authentication UI State Management
    function updateAuthUI() {
        const userId = localStorage.getItem('user_id') || sessionStorage.getItem('user_id');
        const navMenu = document.querySelector('.nav-menu');
        
        if (userId && navMenu) {
            // User is logged in
            const loginLink = navMenu.querySelector('a[href="login.html"]');
            const registerLink = navMenu.querySelector('a[href="register.html"]');
            
            if (loginLink) {
                const loginLi = loginLink.parentElement;
                loginLi.innerHTML = `<a href="bot/dashboard.html" class="nav-link btn btn-primary"> <i class="fa-solid fa-gauge"></i> Dashboard</a>`;
            }
            
            if (registerLink) {
                const registerLi = registerLink.parentElement;
                registerLi.innerHTML = `<a href="#" id="landingLogoutBtn" class="nav-link btn btn-outline"> <i class="fa-solid fa-right-from-bracket"></i> Logout</a>`;
                
                // Add logout event listener
                const logoutBtn = document.getElementById('landingLogoutBtn');
                if (logoutBtn) {
                    logoutBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        showLogoutModal();
                    });
                }
            }
        }
    }

    /**
     * Show custom logout confirmation modal
     */
    function showLogoutModal() {
        // Create modal if it doesn't exist
        let modal = document.getElementById('logoutModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'logoutModal';
            modal.className = 'custom-modal-overlay';
            modal.innerHTML = `
                <div class="custom-modal-card">
                    <div class="custom-modal-icon">
                        <i class="fas fa-sign-out-alt"></i>
                    </div>
                    <h2>Confirm Logout</h2>
                    <p>Are you sure you want to log out? Your current session will be ended.</p>
                    <div class="custom-modal-actions">
                        <button class="modal-btn modal-btn-cancel" id="cancelLogout">Cancel</button>
                        <button class="modal-btn modal-btn-confirm" id="confirmLogout">Logout</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            // Add event listeners
            document.getElementById('cancelLogout').addEventListener('click', hideLogoutModal);
            document.getElementById('confirmLogout').addEventListener('click', performLogout);
            
            modal.addEventListener('click', function(e) {
                if (e.target === modal) hideLogoutModal();
            });
        }
        setTimeout(() => modal.classList.add('active'), 10);
    }

    function hideLogoutModal() {
        const modal = document.getElementById('logoutModal');
        if (modal) modal.classList.remove('active');
    }

    async function performLogout() {
        const confirmBtn = document.getElementById('confirmLogout');
        confirmBtn.textContent = 'Logging out...';
        confirmBtn.disabled = true;

        try {
            const response = await fetch('/api/logout', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                localStorage.removeItem('user_id');
                localStorage.removeItem('first_name');
                sessionStorage.clear();
                window.location.reload();
            }
        } catch (err) {
            console.error('Logout failed:', err);
            localStorage.removeItem('user_id');
            localStorage.removeItem('first_name');
            sessionStorage.clear();
            window.location.reload();
        }
    }

    updateAuthUI();
});

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: var(--primary-green);
        color: white;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Theme is now managed by themeManager.js - no duplicate theme handling here