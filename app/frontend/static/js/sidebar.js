// ============================================
// MEGA MENU NAVIGATION FUNCTIONALITY
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    initMegaMenu();
    initScrollEffect();
});

function initMegaMenu() {
    // Get navbar and elements
    const navbar = document.querySelector('.navbar');
    const navMenu = document.querySelector('.nav-menu');
    const navCta = document.querySelector('.nav-cta');

    // Create mobile toggle button
    const mobileToggle = document.createElement('button');
    mobileToggle.className = 'sidebar-toggle';
    mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
    mobileToggle.id = 'mobileToggle';

    // Add mobile toggle button for mobile view
    if (window.innerWidth <= 768) {
        const navContainer = document.querySelector('.nav-container');
        navContainer.appendChild(mobileToggle);
    }

    // Mobile toggle click handler
    mobileToggle.addEventListener('click', function () {
        navbar.classList.toggle('show');
        mobileToggle.classList.toggle('active');
    });

    // Close menu when clicking a link (mobile only)
    const navLinks = navbar.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                navbar.classList.remove('show');
                mobileToggle.classList.remove('active');
            }
        });
    });

    // Close menu when clicking outside on mobile
    document.addEventListener('click', function (event) {
        if (window.innerWidth <= 768) {
            const isClickInsideNavbar = navbar.contains(event.target);
            const isClickOnToggle = mobileToggle.contains(event.target);

            if (!isClickInsideNavbar && !isClickOnToggle && navbar.classList.contains('show')) {
                navbar.classList.remove('show');
                mobileToggle.classList.remove('active');
            }
        }
    });

    // Handle window resize
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            navbar.classList.remove('show');
            mobileToggle.style.display = 'none';
            mobileToggle.classList.remove('active');
        } else {
            mobileToggle.style.display = 'flex';
        }
    });

    // Set active link based on current page
    setActiveLink();
}

function initScrollEffect() {
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;

    window.addEventListener('scroll', function () {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // For Mobile or negative scrolling
    });
}

function setActiveLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.classList.remove('active');

        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
}

// Smooth scroll for anchor links
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Export functions for use in other scripts
window.megaMenuUtils = {
    setActiveLink,
    smoothScroll
};
