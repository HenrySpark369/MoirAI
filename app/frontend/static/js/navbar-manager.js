/**
 * Navbar Manager - Gestor global de la barra de navegación
 * Se ejecuta en TODAS las páginas y adapta la navbar según:
 * - Si el usuario está autenticado o no
 * - El role del usuario (student/company/admin)
 * - La página actual
 */

class NavbarManager {
    constructor() {
        this.isAuthenticated = false;
        this.userRole = null;
        this.userName = null;
        this.currentPage = null;
    }

    /**
     * Inicializar navbar manager
     */
    async initialize() {
        console.log('🔄 Inicializando NavbarManager...');
        
        try {
            // Detectar si está autenticado
            this.isAuthenticated = !!localStorage.getItem('api_key');
            this.userRole = localStorage.getItem('user_role') || null;
            this.userName = localStorage.getItem('user_name') || localStorage.getItem('user_email') || 'Usuario';
            this.currentPage = this.getCurrentPage();

            console.log(`📌 NavbarManager State:`, {
                isAuthenticated: this.isAuthenticated,
                userRole: this.userRole,
                currentPage: this.currentPage
            });

            // Actualizar navbar según estado
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

    /**
     * Obtener página actual desde URL
     */
    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path === '') return 'home';
        if (path === '/dashboard') return 'dashboard';
        if (path === '/oportunidades') return 'oportunidades';
        if (path === '/profile') return 'profile';
        if (path === '/applications') return 'applications';
        if (path === '/buscar-candidatos') return 'buscar-candidatos';
        if (path === '/mis-vacantes') return 'mis-vacantes';
        if (path === '/login') return 'login';
        if (path === '/registro') return 'registro';
        return 'other';
    }

    /**
     * Configurar navbar para usuario autenticado
     */
    setupAuthenticatedNavbar() {
        console.log('🔐 Configurando navbar autenticada...');
        
        const navbar = document.querySelector('.navbar');
        if (!navbar) {
            console.warn('⚠️ Navbar no encontrada en el DOM');
            return;
        }

        const navList = navbar.querySelector('.nav-list');
        if (!navList) {
            console.warn('⚠️ nav-list no encontrada');
            return;
        }

        // Limpiar menú (mantener solo Dashboard)
        const items = navList.querySelectorAll('.nav-item');
        if (items.length > 1) {
            for (let i = items.length - 1; i > 0; i--) {
                items[i].remove();
            }
        }

        // Agregar items según role
        const menuItems = this.getMenuItemsByRole();
        menuItems.forEach(item => {
            const li = document.createElement('li');
            li.className = 'nav-item';
            
            // Marcar como activo si es la página actual
            const isActive = item.page === this.currentPage ? 'active' : '';
            
            li.innerHTML = `
                <a href="${item.href}" class="nav-link ${isActive}">
                    <i class="fas ${item.icon}"></i>
                    <span>${item.label}</span>
                </a>
            `;
            navList.appendChild(li);
        });

        // Actualizar botón CTA
        const navCta = navbar.querySelector('.nav-cta');
        if (navCta) {
            navCta.innerHTML = `
                <div class="user-info" style="display: flex; align-items: center; gap: 15px; margin-right: 20px;">
                    <span class="user-name" style="font-size: 14px; color: #333;">${this.userName}</span>
                    <button class="btn btn-secondary" onclick="navbar_logout()" style="cursor: pointer;">
                        <i class="fas fa-sign-out-alt"></i> Salir
                    </button>
                </div>
            `;
        }

        console.log('✅ Navbar autenticada configurada para role:', this.userRole);
    }

    /**
     * Configurar navbar para usuario no autenticado
     */
    setupPublicNavbar() {
        console.log('🌐 Configurando navbar pública...');
        
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        const navList = navbar.querySelector('.nav-list');
        if (navList) {
            // Limpiar menú
            const items = navList.querySelectorAll('.nav-item');
            items.forEach(item => item.remove());

            // Agregar items públicos
            const publicItems = [
                { href: '/', icon: 'fa-home', label: 'Inicio', page: 'home' },
                { href: '/oportunidades', icon: 'fa-briefcase', label: 'Oportunidades', page: 'oportunidades' },
            ];

            publicItems.forEach(item => {
                const li = document.createElement('li');
                li.className = 'nav-item';
                const isActive = item.page === this.currentPage ? 'active' : '';
                li.innerHTML = `
                    <a href="${item.href}" class="nav-link ${isActive}">
                        <i class="fas ${item.icon}"></i>
                        <span>${item.label}</span>
                    </a>
                `;
                navList.appendChild(li);
            });
        }

        // Actualizar botón CTA
        const navCta = navbar.querySelector('.nav-cta');
        if (navCta) {
            navCta.innerHTML = `
                <button class="btn btn-primary" onclick="window.location.href='/login'" style="cursor: pointer;">
                    <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
                </button>
            `;
        }

        console.log('✅ Navbar pública configurada');
    }

    /**
     * Obtener items del menú según el role
     */
    getMenuItemsByRole() {
        const menus = {
            'student': [
                { href: '/dashboard', icon: 'fa-home', label: 'Dashboard', page: 'dashboard' },
                { href: '/oportunidades', icon: 'fa-briefcase', label: 'Oportunidades', page: 'oportunidades' },
                { href: '/profile', icon: 'fa-user', label: 'Mi Perfil', page: 'profile' },
                { href: '/applications', icon: 'fa-file-alt', label: 'Mis Aplicaciones', page: 'applications' }
            ],
            'company': [
                { href: '/dashboard', icon: 'fa-home', label: 'Dashboard', page: 'dashboard' },
                { href: '/buscar-candidatos', icon: 'fa-search', label: 'Buscar Candidatos', page: 'buscar-candidatos' },
                { href: '/profile', icon: 'fa-building', label: 'Mi Empresa', page: 'profile' },
                { href: '/mis-vacantes', icon: 'fa-briefcase', label: 'Mis Vacantes', page: 'mis-vacantes' }
            ],
            'admin': [
                { href: '/dashboard', icon: 'fa-home', label: 'Dashboard', page: 'dashboard' },
                { href: '/admin/users', icon: 'fa-users', label: 'Usuarios', page: 'admin-users' },
                { href: '/admin/analytics', icon: 'fa-chart-line', label: 'Analítica', page: 'admin-analytics' },
                { href: '/admin/settings', icon: 'fa-cog', label: 'Configuración', page: 'admin-settings' }
            ]
        };

        return menus[this.userRole] || menus['student'];
    }

    /**
     * Redirigir si no está autenticado
     */
    requireAuth() {
        if (!this.isAuthenticated) {
            console.log('🔒 No autenticado, redirigiendo a /login...');
            window.location.href = `/login?redirect=${window.location.pathname}`;
            return false;
        }
        return true;
    }

    /**
     * Redirigir si está autenticado
     */
    requirePublic() {
        if (this.isAuthenticated) {
            console.log('✅ Ya autenticado, redirigiendo a /dashboard...');
            window.location.href = '/dashboard';
            return false;
        }
        return true;
    }

    /**
     * Redirigir si no es el rol correcto
     */
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
}

// Instancia global
const navbarManager = new NavbarManager();

// Función de logout global
function navbar_logout() {
    console.log('🔓 Logout desde navbar...');
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/login';
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        navbarManager.initialize();
    }, 50);
});

// También inicializar si está al final del body
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            navbarManager.initialize();
        }, 50);
    });
} else {
    // Si ya está cargado, inicializar inmediatamente
    setTimeout(() => {
        navbarManager.initialize();
    }, 50);
}
