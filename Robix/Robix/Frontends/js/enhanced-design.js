/**
 * Enhanced Design JavaScript
 * Implements dynamic color schemes, animations, and interactive elements
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all enhanced design features
    initializeThemeToggle();
    initializeInteractiveMap();
    initializeScrollAnimations();
    initializeCardHoverEffects();

    // Apply any saved theme settings
    applySavedTheme();
});

// Theme toggle functionality - delegates to themeManager.js
function initializeThemeToggle() {
    // themeManager.js handles the toggle via initThemeToggle()
    // This function is kept for compatibility but does nothing extra
}

// Apply saved theme preference - delegated to themeManager.js
function applySavedTheme() {
    if (window.themeManager) {
        window.themeManager.applyTheme(window.themeManager.currentTheme);
    }
}

// Interactive map functionality
function initializeInteractiveMap() {
    const markers = document.querySelectorAll('.map-marker');
    const tooltip = document.getElementById('mapTooltip');

    if (!markers.length || !tooltip) return;

    // Tribe information for tooltips
    const tribeInfo = {
        'bamileke': {
            name: 'Bamileke',
            region: 'Western Highlands',
            description: 'Known for rich cultural heritage and traditional kingdoms'
        },
        'bamum': {
            name: 'Bamum',
            region: 'West-Central Cameroon',
            description: 'Ancient kingdom with rich written tradition'
        },
        'bassa': {
            name: 'Bassa',
            region: 'Littoral Region',
            description: 'Fishing traditions and rich oral literature'
        },
        'fulani': {
            name: 'Fulani',
            region: 'Northern Cameroon',
            description: 'Nomadic pastoralists with distinctive culture'
        },
        'duala': {
            name: 'Duala',
            region: 'Littoral Region',
            description: 'Coastal people with historical trade role'
        },
        'beti': {
            name: 'Beti',
            region: 'South Province',
            description: 'Agricultural traditions and historical kingdom'
        },
        'grassfields': {
            name: 'Grassfields Peoples',
            region: 'Northwest and West',
            description: 'Complex political systems and art forms'
        },
        'sawa': {
            name: 'Sawa',
            region: 'Coastal Regions',
            description: 'Maritime culture and fishing traditions'
        }
    };

    markers.forEach(marker => {
        const tribe = marker.dataset.tribe;
        const info = tribeInfo[tribe];

        if (!info) return;

        // Add hover events
        marker.addEventListener('mouseenter', function (e) {
            // Position tooltip near marker
            const rect = marker.getBoundingClientRect();
            const containerRect = marker.parentElement.getBoundingClientRect();

            tooltip.style.left = `${rect.left - containerRect.left + rect.width / 2}px`;
            tooltip.style.top = `${rect.top - containerRect.top - 10}px`;

            // Update tooltip content
            tooltip.innerHTML = `
                <h4>${info.name}</h4>
                <p><strong>Region:</strong> ${info.region}</p>
                <p>${info.description}</p>
            `;

            // Show tooltip
            tooltip.classList.add('active');
        });

        marker.addEventListener('mouseleave', function () {
            // Hide tooltip
            tooltip.classList.remove('active');
        });

        // Add click event to navigate to tribe page
        marker.addEventListener('click', function () {
            // In a real implementation, this would navigate to the tribe's page
            console.log(`Navigate to ${tribe} page`);
            // window.location.href = `tribe-details.html?tribe=${tribe}`;
        });
    });
}

// Scroll animations
function initializeScrollAnimations() {
    // Add intersection observer for scroll animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');

                // Add specific animations based on element type
                if (entry.target.classList.contains('card')) {
                    entry.target.classList.add('fade-in-up');
                } else if (entry.target.classList.contains('hero')) {
                    entry.target.classList.add('slide-in-left');
                } else {
                    entry.target.classList.add('fade-in-up');
                }
            }
        });
    }, observerOptions);

    // Observe elements that should animate on scroll
    const animateElements = document.querySelectorAll('.card, .hero, .section, .content-card');
    animateElements.forEach(el => observer.observe(el));
}

// Enhanced card hover effects
function initializeCardHoverEffects() {
    const cards = document.querySelectorAll('.card, .tribe-card, .content-card');

    cards.forEach(card => {
        // Add enhanced class for better styling
        card.classList.add('card-enhanced');

        // Add 3D tilt effect
        card.addEventListener('mousemove', function (e) {
            if (document.body.classList.contains('reduce-motion')) return;

            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateY = (x - centerX) / 25;
            const rotateX = (centerY - y) / 25;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
        });

        card.addEventListener('mouseleave', function () {
            card.style.transform = '';
        });
    });
}

// Dynamic color scheme based on selected tribe
function applyTribeColorScheme(tribeName) {
    // Remove any existing tribe theme classes
    document.body.className = document.body.className.replace(/theme-\w+/g, '');

    // Apply tribe-specific theme
    document.body.classList.add(`theme-${tribeName}`);

    // Save preference
    localStorage.setItem('tribeTheme', tribeName);

    console.log(`Applied color scheme for ${tribeName}`);
}

// Parallax effect for hero section
function initializeParallax() {
    const heroSection = document.querySelector('.hero');
    if (!heroSection) return;

    window.addEventListener('scroll', function () {
        if (document.body.classList.contains('reduce-motion')) return;

        const scrollPosition = window.pageYOffset;
        heroSection.style.backgroundPositionY = `${scrollPosition * 0.5}px`;
    });
}

// Export functions for use in other modules
window.EnhancedDesign = {
    applyTribeColorScheme: applyTribeColorScheme,
    initializeThemeToggle: initializeThemeToggle,
    initializeInteractiveMap: initializeInteractiveMap
};