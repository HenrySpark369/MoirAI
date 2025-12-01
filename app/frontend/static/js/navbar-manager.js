/**
 * Navbar Manager - Gestor global de la barra de navegación
 * Se ejecuta en TODAS las páginas y adapta la navbar según:
 * - Si el usuario está autenticado o no
 * - El role del usuario (student/company/admin)
 * - La página actual
 *
 * Ahora usa la estructura de navbar raíz como base y la adapta para todos los roles
 */

class NavbarManager {
    constructor() {
        this.isAuthenticated = false;
        this.userRole = null;
        this.userName = null;
        this.currentPage = null;
        this.initialized = false;
        this.demoMode = false;
    }

    async initialize() {
        if (this.initialized) {
            console.log('ℹ️ NavbarManager ya inicializado');
            return;
        }
        this.initialized = true;

        console.log('🔄 Inicializando NavbarManager...');

        try {
            // Check for demo mode from URL parameter
            const urlParams = new URLSearchParams(window.location.search);
            this.demoMode = urlParams.get('demo') === 'true';
            this.demoRole = urlParams.get('role') || 'admin'; // admin, student, company

            // If no demo parameter and user is not authenticated, redirect to demo mode
            if (!this.demoMode && !this._isUserAuthenticated()) {
                console.log('🎭 Usuario anónimo detectado - redirigiendo a modo demo');
                const currentUrl = new URL(window.location);
                currentUrl.searchParams.set('demo', 'true');
                currentUrl.searchParams.set('role', 'student'); // Default to student demo
                window.location.href = currentUrl.toString();
                return;
            }

            if (this.demoMode) {
                console.log(`🎭 Demo mode detected - role: ${this.demoRole}`);
                this.isAuthenticated = true;
                this.userRole = this.demoRole;

                // ✅ Usar perfil demo real si está disponible
                let demoProfile = null;
                if (typeof storageManager !== 'undefined' && storageManager.isDemoMode()) {
                    demoProfile = storageManager.getDemoProfile();
                }

                // Set appropriate demo user info and API key
                if (this.demoRole === 'student') {
                    this.userName = demoProfile?.name || 'Demo Estudiante';
                    localStorage.setItem('api_key', 'demo-student-key');
                    localStorage.setItem('user_role', 'student');
                    localStorage.setItem('user_name', this.userName);
                } else if (this.demoRole === 'company') {
                    this.userName = demoProfile?.name || 'Demo Empresa';
                    localStorage.setItem('api_key', 'demo-company-key');
                    localStorage.setItem('user_role', 'company');
                    localStorage.setItem('user_name', this.userName);
                } else { // admin
                    this.userName = demoProfile?.name || 'Demo Admin';
                    localStorage.setItem('api_key', 'admin-key-123-change-me');
                    localStorage.setItem('user_role', 'admin');
                    localStorage.setItem('user_name', this.userName);
                }

                this.setupDemoNavbar();
                return;
            }

            if (typeof storageManager !== 'undefined') {
                this.isAuthenticated = storageManager.isAuthenticated();
                this.userRole = storageManager.getUserRole();
                this.userName = storageManager.getUserName() || storageManager.getUserEmail() || 'Usuario';
            } else {
                this.isAuthenticated = !!localStorage.getItem('api_key');
                this.userRole = localStorage.getItem('user_role') || null;
                this.userName = localStorage.getItem('user_name') || localStorage.getItem('user_email') || 'Usuario';
            }

            this.currentPage = this.getCurrentPage();

            console.log(`📌 NavbarManager State:`, {
                isAuthenticated: this.isAuthenticated,
                userRole: this.userRole,
                currentPage: this.currentPage,
                demoMode: this.demoMode
            });

            if (this.isAuthenticated) {
                this.setupAuthenticatedNavbar();
            } else {
                this.setupPublicNavbar();
            }

        } catch (error) {
            console.error('❌ Error en NavbarManager:', error);
            this.setupPublicNavbar();
        }
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path === '') return 'home';
        if (path === '/dashboard') return 'dashboard';
        if (path === '/oportunidades') return 'oportunidades';
        if (path === '/profile') return 'profile';
        if (path === '/applications') return 'applications';
        if (path === '/admin') return 'admin';
        return 'home';
    }

    _isUserAuthenticated() {
        // Check multiple authentication indicators
        if (typeof storageManager !== 'undefined' && storageManager) {
            return storageManager.isAuthenticated && storageManager.isAuthenticated();
        }

        // Fallback: check for API key in localStorage
        const apiKey = localStorage.getItem('api_key') ||
            localStorage.getItem('moirai_api_key') ||
            localStorage.getItem('moirai_token');

        return !!apiKey;
    }

    setupAuthenticatedNavbar() {
        console.log('🔐 Configurando navbar autenticada...');

        // Si estamos en modo demo, usar navbar demo
        if (this.demoMode) {
            this.setupDemoNavbar();
            return;
        }

        // Usar la estructura de navbar raíz como base
        const navbarContainer = document.getElementById('navbar-container') || document.querySelector('.navbar');
        if (!navbarContainer) {
            console.warn('⚠️ Navbar container no encontrada');
            return;
        }

        navbarContainer.innerHTML = '';

        // Generar items de navegación según el rol
        const navItems = this.getMenuItemsByRole(this.userRole);

        // Construir navbar usando estructura raíz
        navbarContainer.innerHTML = `
            <div class="nav-container">
                <div class="nav-logo">
                    <a href="/">
                        <i class="fas fa-brain"></i>
                        <span>MoirAI</span>
                    </a>
                </div>

                <div class="nav-menu">
                    <ul class="nav-list">
                        ${navItems}
                    </ul>
                </div>

                <div class="nav-cta">
                    <div class="user-info" style="display: flex; align-items: center; gap: 15px; margin-right: 20px;">
                        <span class="user-name" style="font-size: 14px; color: #333;">${this.userName}</span>
                        <button class="btn btn-secondary" onclick="logout()" style="cursor: pointer;">
                            <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                        </button>
                    </div>
                </div>
            </div>
        `;

        console.log('✅ Navbar autenticada configurada');
        this.setupMobileMenu();
    }

    setupDemoNavbar() {
        console.log(`🎭 Configurando navbar en modo demo (${this.demoRole})...`);

        const navbarContainer = document.getElementById('navbar-container') || document.querySelector('.navbar');
        if (!navbarContainer) {
            console.warn('⚠️ Navbar container no encontrada');
            return;
        }

        navbarContainer.innerHTML = '';

        // Generar items de navegación según el rol
        const navItems = this.getMenuItemsByRole(this.userRole);

        // Role switcher for demo mode
        const roleSwitcher = `
            <div class="demo-role-switcher" style="display: flex; gap: 10px; margin-right: 20px;">
                <button class="btn btn-sm ${this.demoRole === 'student' ? 'btn-primary' : 'btn-outline'}"
                        onclick="switchDemoRole('student')" style="font-size: 12px; padding: 4px 8px;">
                    👨‍🎓 Estudiante
                </button>
                <button class="btn btn-sm ${this.demoRole === 'company' ? 'btn-primary' : 'btn-outline'}"
                        onclick="switchDemoRole('company')" style="font-size: 12px; padding: 4px 8px;">
                    🏢 Empresa
                </button>
                <button class="btn btn-sm ${this.demoRole === 'admin' ? 'btn-primary' : 'btn-outline'}"
                        onclick="switchDemoRole('admin')" style="font-size: 12px; padding: 4px 8px;">
                    ⚙️ Admin
                </button>
            </div>
        `;

        // Construir navbar usando estructura raíz
        navbarContainer.innerHTML = `
            <div class="nav-container">
                <div class="nav-logo">
                    <a href="/dashboard?demo=true&role=${this.demoRole}">
                        <i class="fas fa-brain"></i>
                        <span>MoirAI</span>
                        <span class="demo-badge">DEMO</span>
                    </a>
                </div>

                <div class="nav-menu">
                    <ul class="nav-list">
                        ${navItems}
                    </ul>
                </div>

                <div class="nav-cta">
                    ${roleSwitcher}
                    <div class="user-info" style="display: flex; align-items: center; gap: 15px; margin-right: 20px;">
                        <span class="user-name" style="font-size: 14px; color: #333;">${this.userName}</span>
                        <button class="btn btn-secondary" onclick="window.location.href='/'" style="cursor: pointer;">
                            <i class="fas fa-home"></i> Salir Demo
                        </button>
                    </div>
                </div>
            </div>
        `;

        console.log('✅ Navbar demo configurada');
        this.setupMobileMenu();
    }

    setupPublicNavbar() {
        console.log('🌐 Configurando navbar pública...');

        const navbarContainer = document.getElementById('navbar-container') || document.querySelector('.navbar');
        if (!navbarContainer) {
            console.warn('⚠️ Navbar container no encontrada');
            return;
        }

        navbarContainer.innerHTML = '';

        // Usar la estructura de navbar raíz del index.html
        navbarContainer.innerHTML = `
            <div class="nav-container">
                <div class="nav-logo">
                    <a href="/">
                        <i class="fas fa-brain"></i>
                        <span>MoirAI</span>
                    </a>
                </div>

                <div class="nav-menu">
                    <ul class="nav-list">
                        <li class="nav-item">
                            <a href="/" class="nav-link ${this.currentPage === 'home' ? 'active' : ''}">
                                <i class="fas fa-home"></i>
                                <span>Inicio</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="/oportunidades" class="nav-link ${this.currentPage === 'oportunidades' ? 'active' : ''}">
                                <i class="fas fa-briefcase"></i>
                                <span>Oportunidades</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="/empresas" class="nav-link ${this.currentPage === 'empresas' ? 'active' : ''}">
                                <i class="fas fa-building"></i>
                                <span>Empresas</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="/estudiantes" class="nav-link ${this.currentPage === 'estudiantes' ? 'active' : ''}">
                                <i class="fas fa-user-graduate"></i>
                                <span>Estudiantes</span>
                            </a>
                        </li>
                        <li class="nav-item">
                            <a href="#contact" class="nav-link ${this.currentPage === 'contact' ? 'active' : ''}">
                                <i class="fas fa-envelope"></i>
                                <span>Contacto</span>
                            </a>
                        </li>
                        <li class="nav-item demo-link">
                            <a href="/dashboard?demo=true" class="nav-link demo-btn" data-tooltip="Ver Dashboard Demo">
                                <i class="fas fa-play-circle"></i>
                                <span>Demo</span>
                                <span class="demo-badge">GRATIS</span>
                            </a>
                        </li>
                    </ul>
                </div>

                <div class="nav-cta">
                    <a href="/dashboard?demo=true" class="btn btn-secondary demo-cta">
                        <i class="fas fa-eye"></i> Ver Demo
                    </a>
                    <button class="btn btn-secondary" onclick="scrollToLogin()">
                        <i class="fas fa-sign-in-alt"></i> Inicia Sesión
                    </button>
                    <button class="btn btn-primary" onclick="scrollToRegister()">
                        <i class="fas fa-plus"></i> Únete Ahora
                    </button>
                </div>
            </div>
        `;

        console.log('✅ Navbar pública configurada');
        this.setupMobileMenu();
    }

    getMenuItemsByRole() {
        const baseUrl = this.demoMode ? `?demo=true&role=${this.userRole}` : '';

        const menus = {
            'student': [
                { href: `/dashboard${baseUrl}`, icon: 'fa-home', label: 'Dashboard', page: 'dashboard' },
                { href: `/oportunidades${baseUrl}`, icon: 'fa-briefcase', label: 'Oportunidades', page: 'oportunidades' },
                { href: `/profile${baseUrl}`, icon: 'fa-user', label: 'Mi Perfil', page: 'profile' },
                { href: `/applications${baseUrl}`, icon: 'fa-file-alt', label: 'Mis Aplicaciones', page: 'applications' }
            ],
            'company': [
                { href: `/dashboard${baseUrl}`, icon: 'fa-home', label: 'Dashboard', page: 'dashboard' },
                { href: `/buscar-candidatos${baseUrl}`, icon: 'fa-search', label: 'Buscar Candidatos', page: 'buscar-candidatos' },
                { href: `/applications${baseUrl}`, icon: 'fa-file-alt', label: 'Aplicaciones', page: 'applications' },
                { href: `/profile${baseUrl}`, icon: 'fa-building', label: 'Mi Empresa', page: 'profile' }
            ],
            'admin': [
                { href: `/dashboard${baseUrl}`, icon: 'fa-home', label: 'Dashboard', page: 'dashboard' },
                { href: `/admin/users${baseUrl}`, icon: 'fa-users', label: 'Usuarios', page: 'admin-users' },
                { href: `/admin/analytics${baseUrl}`, icon: 'fa-chart-line', label: 'Analítica', page: 'admin-analytics' },
                { href: `/admin/settings${baseUrl}`, icon: 'fa-cog', label: 'Configuración', page: 'admin-settings' }
            ]
        };

        const menuItems = menus[this.userRole] || menus['student'];

        return menuItems.map(item => {
            const isActive = this.currentPage === item.page ? 'active' : '';
            return `
                <li class="nav-item">
                    <a href="${item.href}" class="nav-link ${isActive}">
                        <i class="fas ${item.icon}"></i>
                        <span>${item.label}</span>
                    </a>
                </li>
            `;
        }).join('');
    }

    requireAuth() {
        if (!this.isAuthenticated) {
            console.log('🔒 No autenticado, redirigiendo a /login...');
            window.location.href = `/login?redirect=${window.location.pathname}`;
            return false;
        }
        return true;
    }

    requirePublic() {
        if (this.isAuthenticated) {
            console.log('✅ Ya autenticado, redirigiendo a /dashboard...');
            window.location.href = '/dashboard';
            return false;
        }
        return true;
    }

    requireRole(allowedRoles) {
        if (!Array.isArray(allowedRoles)) {
            allowedRoles = [allowedRoles];
        }

        if (!allowedRoles.includes(this.userRole)) {
            console.log(`🚫 Rol no permitido. Required: ${allowedRoles}, Got: ${this.userRole}`);
            window.location.href = '/dashboard';
            return false;
        }
        return true;
    }
    setupMobileMenu() {
        const navbar = document.querySelector('.navbar');
        const navContainer = document.querySelector('.nav-container');

        if (!navbar || !navContainer) return;

        let mobileToggle = document.getElementById('mobileToggle');
        if (!mobileToggle) {
            mobileToggle = document.createElement('button');
            mobileToggle.className = 'sidebar-toggle';
            mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
            mobileToggle.id = 'mobileToggle';
            navContainer.appendChild(mobileToggle);
        }

        // Remove existing listeners to avoid duplicates if re-initialized
        const newToggle = mobileToggle.cloneNode(true);
        mobileToggle.parentNode.replaceChild(newToggle, mobileToggle);
        mobileToggle = newToggle;

        mobileToggle.addEventListener('click', () => {
            navbar.classList.toggle('show');
            mobileToggle.classList.toggle('active');
        });

        const navLinks = navbar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    navbar.classList.remove('show');
                    mobileToggle.classList.remove('active');
                }
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (event) => {
            if (window.innerWidth <= 768) {
                const isClickInsideNavbar = navbar.contains(event.target);
                const isClickOnToggle = mobileToggle.contains(event.target);

                if (!isClickInsideNavbar && !isClickOnToggle && navbar.classList.contains('show')) {
                    navbar.classList.remove('show');
                    mobileToggle.classList.remove('active');
                }
            }
        });

        // Reset on resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                navbar.classList.remove('show');
                if (mobileToggle) {
                    mobileToggle.style.display = 'none';
                    mobileToggle.classList.remove('active');
                }
            } else {
                if (mobileToggle) mobileToggle.style.display = 'flex';
            }
        });
    }
}

// Global function for demo role switching (called by HTML buttons)
window.switchDemoRole = function (role) {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('demo', 'true');
    currentUrl.searchParams.set('role', role);
    window.location.href = currentUrl.toString();
};

// ✅ CREAR INSTANCIA GLOBAL
const navbarManager = new NavbarManager();
console.log('✅ NavbarManager instance created:', navbarManager);

// Initialize immediately
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => navbarManager.initialize());
} else {
    navbarManager.initialize();
}
