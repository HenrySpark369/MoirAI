/**
 * MoirAI Landing Page - Main JavaScript
 * Handles interactions, modals, and smooth scrolling
 */

document.addEventListener('DOMContentLoaded', function () {
    initializeModals();
    initializeNavigation();
    initializeFormHandlers();
    initializePasswordToggles();
});

/**
 * Modal Management
 */
function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close-modal');

    // Close modal when clicking close button
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            this.closest('.modal').style.display = 'none';
        });
    });

    // Close modal when clicking outside content
    modals.forEach(modal => {
        modal.addEventListener('click', function (event) {
            if (event.target === this) {
                this.style.display = 'none';
            }
        });
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        }
    });

    // Initialize register tabs with role-specific fields
    const registerTabs = document.querySelectorAll('.register-tab');
    registerTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const role = this.getAttribute('data-tab');
            
            // Update active tab
            registerTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update hidden role field
            const roleInput = document.querySelector('input[name="role"]');
            if (roleInput) {
                roleInput.value = role;
            }
            
            // Show/hide conditional fields
            const studentProgram = document.getElementById('student-program');
            const companyIndustry = document.getElementById('company-industry');
            const companySize = document.getElementById('company-size');
            const companyLocation = document.getElementById('company-location');
            
            if (role === 'student') {
                if (studentProgram) studentProgram.style.display = 'block';
                if (companyIndustry) companyIndustry.style.display = 'none';
                if (companySize) companySize.style.display = 'none';
                if (companyLocation) companyLocation.style.display = 'none';
            } else if (role === 'company') {
                if (studentProgram) studentProgram.style.display = 'none';
                if (companyIndustry) companyIndustry.style.display = 'block';
                if (companySize) companySize.style.display = 'block';
                if (companyLocation) companyLocation.style.display = 'block';
            }
        });
    });
}

/**
 * Open login modal
 */
function scrollToLogin() {
    const loginModal = document.getElementById('login-modal');
    if (loginModal) {
        loginModal.style.display = 'flex';
    }
}

/**
 * Open register modal
 */
function scrollToRegister() {
    const registerModal = document.getElementById('register-modal');
    if (registerModal) {
        registerModal.style.display = 'flex';
    }
}

/**
 * Navigation Management
 */
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    // Smooth scroll for nav links
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                    // Close mobile menu if open
                    if (navMenu.style.display === 'flex') {
                        navMenu.style.display = 'none';
                    }
                }
            }
        });
    });

    // Hamburger menu toggle
    if (hamburger) {
        hamburger.addEventListener('click', function () {
            navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function (event) {
        if (navMenu && navMenu.style.display === 'flex') {
            if (!event.target.closest('.nav-container')) {
                navMenu.style.display = 'none';
            }
        }
    });
}

/**
 * Form Handlers
 */
function initializeFormHandlers() {
    const contactForm = document.querySelector('.contact-form');
    const registerForm = document.querySelector('.register-form');
    const loginForm = document.querySelector('.login-form');

    // Contact form submission
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactFormSubmit);
    }

    // Register form submission
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterFormSubmit);
    }

    // Login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginFormSubmit);
    }
}

/**
 * Handle contact form submission
 */
async function handleContactFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData);

    try {
        // Show loading state
        const submitButton = this.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Enviando...';
        submitButton.disabled = true;

        // Simulate API call (replace with actual endpoint)
        const response = await fetch('/api/v1/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).catch(() => {
            // If API endpoint doesn't exist, show success anyway for demo
            return { ok: true };
        });

        // Show success message
        showNotification('¡Mensaje enviado correctamente!', 'success');
        this.reset();

        // Restore button
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    } catch (error) {
        console.error('Error sending message:', error);
        showNotification('Error al enviar el mensaje. Por favor intenta de nuevo.', 'error');
        const submitButton = this.querySelector('button[type="submit"]');
        submitButton.disabled = false;
    }
}

/**
 * Handle register form submission
 */
async function handleRegisterFormSubmit(e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Registrando...';
        submitButton.disabled = true;

        // Remover field de términos antes de enviar (no es del API)
        delete data.terms;

        // Validar que los campos requeridos estén presentes
        if (!data.name || !data.email || !data.password || !data.role) {
            throw new Error('Por favor completa todos los campos requeridos');
        }

        // Enviar registro
        const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        // Manejar respuestas no exitosas
        if (!response.ok) {
            let errorMessage = 'Error al registrarse';
            
            try {
                const errorData = await response.json();
                
                // Mapear errores HTTP a mensajes amigables
                if (response.status === 409) {
                    errorMessage = errorData.detail || 'Este email ya está registrado';
                } else if (response.status === 400) {
                    errorMessage = errorData.detail || 'Datos inválidos. Por favor verifica los campos';
                } else if (response.status === 422) {
                    errorMessage = errorData.detail || 'Validación fallida. Verifica los datos';
                } else {
                    errorMessage = errorData.detail || `Error ${response.status}: ${response.statusText}`;
                }
            } catch (parseError) {
                // Si no se puede parsear JSON, usar status text
                errorMessage = `Error ${response.status}: ${response.statusText}`;
            }
            
            throw new Error(errorMessage);
        }

        const responseData = await response.json();
        
        // Guardar API key en localStorage
        if (responseData.api_key) {
            localStorage.setItem('api_key', responseData.api_key);
            localStorage.setItem('user_id', responseData.user_id);
            localStorage.setItem('user_role', responseData.role);
        }

        showNotification('¡Registro exitoso! Redirigiendo...', 'success');
        form.reset();
        
        // Cerrar modal
        const modal = document.getElementById('register-modal');
        if (modal) modal.style.display = 'none';

        // Redirigir al dashboard después de 2 segundos
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 2000);

        submitButton.textContent = originalText;
        submitButton.disabled = false;
    } catch (error) {
        console.error('Error registering:', error);
        showNotification(error.message || 'Error en el registro. Por favor intenta de nuevo.', 'error');
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.textContent = originalText || 'Crear Cuenta Gratis';
        submitButton.disabled = false;
    }
}

/**
 * Handle login form submission
 */
async function handleLoginFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData);

    try {
        const submitButton = this.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Iniciando sesión...';
        submitButton.disabled = true;

        // Simulated login
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).catch(() => {
            return { ok: true };
        });

        showNotification('¡Sesión iniciada correctamente!', 'success');
        this.reset();
        document.getElementById('login-modal').style.display = 'none';

        // Redirect to dashboard after short delay
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);

        submitButton.textContent = originalText;
        submitButton.disabled = false;
    } catch (error) {
        console.error('Error logging in:', error);
        showNotification('Error al iniciar sesión. Verifica tus credenciales.', 'error');
        const submitButton = this.querySelector('button[type="submit"]');
        submitButton.disabled = false;
    }
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add styles if not already in CSS
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: '0.5rem',
        color: 'white',
        fontSize: '1rem',
        zIndex: '9999',
        animation: 'slideInRight 0.3s ease',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
    });

    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#10b981';
            break;
        case 'error':
            notification.style.backgroundColor = '#ef4444';
            break;
        case 'warning':
            notification.style.backgroundColor = '#f59e0b';
            break;
        default:
            notification.style.backgroundColor = '#3b82f6';
    }

    document.body.appendChild(notification);

    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

/**
 * Scroll to top button
 */
function createScrollToTopButton() {
    const button = document.createElement('button');
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.className = 'scroll-to-top';
    Object.assign(button.style, {
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        width: '50px',
        height: '50px',
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #730f33, #e2bb84)',
        color: 'white',
        border: 'none',
        cursor: 'pointer',
        display: 'none',
        zIndex: '999',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
    });

    button.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            button.style.display = 'flex';
            button.style.alignItems = 'center';
            button.style.justifyContent = 'center';
        } else {
            button.style.display = 'none';
        }
    });

    document.body.appendChild(button);
}

// Initialize scroll to top button
createScrollToTopButton();

/**
 * Add animation styles to page
 */
/**
 * Initialize password toggle functionality
 */
function initializePasswordToggles() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            const input = this.closest('.password-input-group').querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
}

function addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100px);
                opacity: 0;
            }
        }

        .scroll-to-top:hover {
            transform: translateY(-3px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15);
        }
    `;
    document.head.appendChild(style);
}

// Add animation styles
addAnimationStyles();

/**
 * Analytics tracking (placeholder for actual implementation)
 */
function trackEvent(eventName, eventData = {}) {
    console.log('Event tracked:', eventName, eventData);
    // Implement your analytics here (Google Analytics, Mixpanel, etc.)
}

/**
 * Track page interactions
 */
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('btn')) {
        const buttonText = e.target.textContent;
        trackEvent('button_click', { button_text: buttonText });
    }
});
