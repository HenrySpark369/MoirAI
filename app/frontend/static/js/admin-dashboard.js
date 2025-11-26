/**
 * MoirAI Admin Dashboard - Core Navigation & Tabs
 * Lightweight version: only handles tab/section switching and analytics integration
 * Charts, notifications, and utilities moved to separate modules
 */

let dashboardAnalytics = null;
let currentPage = 1, allUsers = [];

document.addEventListener('DOMContentLoaded', () => {
    // ✅ Verificar permisos de admin automáticamente al cargar
    checkAdminPermissions().then(() => {
        initializeNavigation();
        initializeEventListeners();
    });
});

/**
 * Navigate between sections using URL-based navigation
 * Updated for unified navbar - listens for URL changes and section clicks
 */
function initializeNavigation() {
    // Listen for clicks on navbar links that navigate to admin sections
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a[href*="/admin/"]');
        if (link) {
            e.preventDefault();
            const href = link.getAttribute('href');
            const section = getSectionFromUrl(href);
            if (section) {
                switchSection(section);
                // Update URL without page reload
                history.pushState(null, '', href);
            }
        }
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', () => {
        const section = getSectionFromUrl(window.location.pathname + window.location.search);
        if (section) {
            switchSection(section);
        }
    });

    // Initialize with current URL section
    const currentSection = getSectionFromUrl(window.location.pathname + window.location.search);
    if (currentSection) {
        switchSection(currentSection);
    }
}

/**
 * Extract section name from admin URL
 */
function getSectionFromUrl(url) {
    if (url.includes('/admin/users')) return 'students';
    if (url.includes('/admin/analytics')) return 'analytics';
    if (url.includes('/admin/settings')) return 'settings';
    if (url.includes('/admin/dashboard') || url === '/admin' || url === '/admin/') return 'dashboard';
    return null;
}

/**
 * Switch main section content and update navbar active state
 */
function switchSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));

    // Show target section
    const section = document.getElementById(sectionId);
    if (section) section.classList.add('active');

    // Update page title
    updatePageTitle(sectionId);

    // Load specific section content
    if (sectionId === 'analytics') {
        initializeAnalytics();
    } else if (sectionId === 'cv-monitor') {
        initializeCVMonitor();
    } else if (sectionId === 'companies') {
        initializeCompanies();
    } else if (sectionId === 'students') {
        initializeStudents();
    }

    console.log(`📱 Switched to section: ${sectionId}`);
}

/**
 * Update page title based on current section
 */
function updatePageTitle(sectionId) {
    const titles = {
        'dashboard': 'Dashboard - MoirAI Admin',
        'students': 'Gestión de Estudiantes - MoirAI Admin',
        'companies': 'Gestión de Empresas - MoirAI Admin',
        'api': 'API Endpoints - MoirAI Admin',
        'applications': 'Aplicaciones - MoirAI Admin',
        'cv-monitor': 'CV Monitor - MoirAI Admin',
        'analytics': 'Analítica - MoirAI Admin',
        'settings': 'Configuración - MoirAI Admin'
    };

    const title = titles[sectionId] || 'MoirAI - Admin Dashboard';
    document.title = title;
}

/**
 * Initialize analytics module on first load
 */
function initializeAnalytics() {
    if (!dashboardAnalytics) {
        dashboardAnalytics = new AdminAnalyticsPage('#analytics');
        dashboardAnalytics.initialize(true).catch(err => {
            console.error('📊 Analytics init error:', err);
            notificationManager?.show('Error al cargar analítica', 'error');
        });
    } else if (dashboardAnalytics.initialized) {
        dashboardAnalytics.loadAnalytics(true).catch(err => {
            console.error('📊 Analytics reload error:', err);
        });
    }
}

/**
 * Initialize CV Monitor module on first load
 */
function initializeCVMonitor() {
    // CV Monitor is initialized automatically by admin-cv-monitor.js
    // This function can be used for additional setup if needed
    console.log('🤖 CV Monitor section activated');
}

/**
 * Initialize Companies module on first load
 */
function initializeCompanies() {
    console.log('🏢 Companies section activated');
    
    // Check if AdminCompaniesManager is available and initialize if needed
    if (window.AdminCompaniesManager && !window.adminCompaniesManager) {
        try {
            window.adminCompaniesManager = new window.AdminCompaniesManager();
            console.log('✅ AdminCompaniesManager initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing AdminCompaniesManager:', error);
        }
    } else if (window.adminCompaniesManager) {
        console.log('ℹ️ AdminCompaniesManager already initialized');
    } else {
        console.warn('⚠️ AdminCompaniesManager class not available');
    }
}

/**
 * Initialize event listeners for tabs and actions
 */
function initializeEventListeners() {
    // Tab buttons within sections
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.getAttribute('data-tab')));
    });

    // Action buttons (view/edit/delete)
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            handleActionButton(btn);
        });
    });

    // Add event listeners for section-specific buttons
    initializeSectionButtons();
}

/**
 * Initialize buttons specific to each section
 */
function initializeSectionButtons() {
    // Add Student button
    const addStudentBtn = document.getElementById('addStudentBtn');
    if (addStudentBtn) {
        addStudentBtn.addEventListener('click', () => {
            notificationManager?.show('Función de agregar estudiante próximamente', 'info');
        });
    }

    // Add Company button
    const addCompanyBtn = document.getElementById('addCompanyBtn');
    if (addCompanyBtn) {
        addCompanyBtn.addEventListener('click', () => {
            notificationManager?.show('Función de agregar empresa próximamente', 'info');
        });
    }

    // Generate Docs button
    const generateDocsBtn = document.getElementById('generateDocsBtn');
    if (generateDocsBtn) {
        generateDocsBtn.addEventListener('click', () => {
            notificationManager?.show('Generación de documentación próximamente', 'info');
        });
    }

    // Refresh buttons
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            notificationManager?.show('Refrescando datos...', 'info');
            // Trigger refresh for current section
            const activeSection = document.querySelector('.content-section.active');
            if (activeSection) {
                const sectionId = activeSection.id;
                if (sectionId === 'cv-monitor') {
                    initializeCVMonitor();
                }
            }
        });
    }

    const refreshAnalytics = document.getElementById('refreshAnalytics');
    if (refreshAnalytics) {
        refreshAnalytics.addEventListener('click', () => {
            if (dashboardAnalytics) {
                dashboardAnalytics.loadAnalytics(true).catch(err => {
                    console.error('Error refreshing analytics:', err);
                    notificationManager?.show('Error al refrescar analítica', 'error');
                });
            }
        });
    }
}

/**
 * Switch between tabs within a section
 */
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    const tabElement = document.getElementById(`${tabId}-tab`);
    if (tabElement) tabElement.classList.add('active');

    const tabBtn = document.querySelector(`[data-tab="${tabId}"]`);
    if (tabBtn) tabBtn.classList.add('active');
}

/**
 * Initialize Students module on first load
 */
function initializeStudents() {
    console.log('🎓 Students section activated');
    loadUsers();
    
    // Add event listeners for filters
    const searchInput = document.getElementById('search-input');
    const roleFilter = document.getElementById('role-filter');
    const statusFilter = document.getElementById('status-filter');
    
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (roleFilter) roleFilter.addEventListener('change', applyFilters);
    if (statusFilter) statusFilter.addEventListener('change', applyFilters);
}

/**
 * Load users data from API (replaces loadStudents)
 */
async function loadUsers() {
    const usersSection = document.getElementById('students');
    const tableBody = document.getElementById('users-tbody');
    const loadingState = document.getElementById('loading-state');
    const tableContainer = document.getElementById('table-container');
    const emptyState = document.getElementById('empty-state');
    
    // Check if we're in demo mode
    const urlParams = new URLSearchParams(window.location.search);
    const isDemoMode = urlParams.get('demo') === 'true';
    
    try {
        // Show loading state
        if (loadingState) loadingState.style.display = 'block';
        if (tableContainer) tableContainer.style.display = 'none';
        if (emptyState) emptyState.style.display = 'none';
        
        if (isDemoMode) {
            // Use real CV simulator data instead of mock data for demo mode
            console.log('🎭 Modo demo - usando datos reales del simulador de CVs');
            const apiKey = getApiKey();
            if (!apiKey) {
                throw new Error('No API key available for demo mode');
            }
            
            // Fetch users from CV simulator instead of mock data
            const response = await fetch(`${window.API_BASE_URL}/admin/users-from-cv-simulator?limit=50`, {
                headers: {
                    'X-API-Key': apiKey,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            allUsers = data.items || [];
        } else {
            // Get API key
            const apiKey = getApiKey();
            if (!apiKey) {
                throw new Error('No API key available');
            }
            
            // Fetch users data
            const response = await fetch(`${window.API_BASE_URL}/admin/users`, {
                headers: {
                    'X-API-Key': apiKey,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            allUsers = data.items || data.users || [];
        }
        
        // Update stats
        updateUserStats(allUsers);
        
        // Hide loading state
        if (loadingState) loadingState.style.display = 'none';
        
        if (allUsers.length === 0) {
            if (emptyState) emptyState.style.display = 'block';
        } else {
            renderUsersTable(allUsers);
            if (tableContainer) tableContainer.style.display = 'block';
        }
        
        console.log(`✅ Loaded ${allUsers.length} users`);
        
    } catch (error) {
        console.error('❌ Error loading users:', error);
        if (loadingState) loadingState.style.display = 'none';
        showError('Error al cargar usuarios: ' + error.message);
        notificationManager?.show('Error al cargar usuarios', 'error');
    }
}

/**
 * Update user statistics
 */
function updateUserStats(users) {
    document.getElementById('total-users').textContent = users.length;
    document.getElementById('total-students').textContent = users.filter(u => u.role === 'student').length;
    document.getElementById('total-companies').textContent = users.filter(u => u.role === 'company').length;
    document.getElementById('active-users').textContent = users.filter(u => u.is_active).length;
}

/**
 * Apply filters to users list
 */
function applyFilters() {
    const search = document.getElementById('search-input').value.toLowerCase();
    const role = document.getElementById('role-filter').value;
    const status = document.getElementById('status-filter').value;

    let filtered = allUsers.filter(u => {
        const matchSearch = !search || (u.name && u.name.toLowerCase().includes(search)) || (u.email && u.email.toLowerCase().includes(search));
        const matchRole = !role || u.role === role;
        const matchStatus = !status || (status === 'active' ? u.is_active : !u.is_active);
        return matchSearch && matchRole && matchStatus;
    });

    currentPage = 1;
    renderUsersTable(filtered);
}

/**
 * Render users table with data
 */
function renderUsersTable(users) {
    const tbody = document.getElementById('users-tbody');
    const start = (currentPage - 1) * 20, end = start + 20;
    const pageUsers = users.slice(start, end);

    tbody.innerHTML = pageUsers.map(u => `
        <tr>
            <td><strong>${u.name || 'N/A'}</strong></td>
            <td><small>${u.email || ''}</small></td>
            <td><span class="badge ${u.role}">${u.role.toUpperCase()}</span></td>
            <td><span class="badge ${u.is_active ? 'active' : 'inactive'}">${u.is_active ? 'Activo' : 'Inactivo'}</span></td>
            <td><div class="actions">
                <button class="btn-sm btn-info" onclick="viewUser('${u.id}')"><i class="fas fa-eye"></i></button>
                <button class="btn-sm btn-danger" onclick="deleteUser('${u.id}', '${u.name}')"><i class="fas fa-trash"></i></button>
            </div></td>
        </tr>
    `).join('');

    const totalPages = Math.ceil(users.length / 20);
    renderPagination(totalPages);
}

/**
 * Render pagination controls
 */
function renderPagination(total) {
    const pag = document.getElementById('pagination');
    if (total <= 1) { 
        pag.style.display = 'none'; 
        return; 
    }
    
    let html = '';
    if (currentPage > 1) html += `<button onclick="goToPage(${currentPage - 1})">← Ant</button>`;
    
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(total, currentPage + 2); i++) {
        html += `<button onclick="goToPage(${i})" ${i === currentPage ? 'class="active"' : ''}>${i}</button>`;
    }
    
    if (currentPage < total) html += `<button onclick="goToPage(${currentPage + 1})">Sig →</button>`;
    
    pag.innerHTML = html;
    pag.style.display = 'flex';
}

/**
 * Go to specific page
 */
function goToPage(p) { 
    currentPage = p; 
    renderUsersTable(allUsers); 
    window.scrollTo(0, 0); 
}

/**
 * View user details
 */
function viewUser(id) { 
    const urlParams = new URLSearchParams(window.location.search);
    const isDemoMode = urlParams.get('demo') === 'true';
    
    if (isDemoMode) {
        notificationManager?.show('Vista de detalles de usuario próximamente (modo demo)', 'info');
    } else {
        window.location.href = `/admin/user-details?user_id=${id}`;
    }
}

/**
 * Delete user
 */
async function deleteUser(id, name) {
    const urlParams = new URLSearchParams(window.location.search);
    const isDemoMode = urlParams.get('demo') === 'true';
    
    if (isDemoMode) {
        // In demo mode, just remove from local array
        if (!confirm(`¿Eliminar a ${name}? (Modo Demo)`)) return;
        
        allUsers = allUsers.filter(u => u.id !== id);
        updateUserStats(allUsers);
        renderUsersTable(allUsers);
        notificationManager?.show('Usuario eliminado (modo demo)', 'success');
    } else {
        if (!confirm(`¿Eliminar a ${name}?`)) return;
        
        try {
            const response = await fetch(`${window.API_BASE_URL}/admin/users/${id}`, { 
                method: 'DELETE', 
                headers: { 'X-API-Key': getApiKey() } 
            });
            
            if (!response.ok) throw new Error();
            
            loadUsers();
            notificationManager?.show('Usuario eliminado exitosamente', 'success');
            
        } catch { 
            showError('Error al eliminar usuario');
            notificationManager?.show('Error al eliminar usuario', 'error');
        }
    }
}

/**
 * Export users to CSV
 */
function exportUsers() {
    const urlParams = new URLSearchParams(window.location.search);
    const isDemoMode = urlParams.get('demo') === 'true';
    
    try {
        const headers = ['Nombre', 'Email', 'Rol', 'Estado', 'Fecha'];
        const rows = allUsers.map(u => [
            u.name, 
            u.email, 
            u.role.toUpperCase(), 
            u.is_active ? 'Activo' : 'Inactivo', 
            u.created_at ? new Date(u.created_at).toLocaleDateString('es-MX') : 'N/A'
        ]);
        
        let csv = headers.join(',') + '\n';
        rows.forEach(r => { 
            csv += r.map(c => `"${c.toString().replace(/"/g, '""')}"`).join(',') + '\n'; 
        });
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `usuarios${isDemoMode ? '_demo' : ''}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        notificationManager?.show('Usuarios exportados exitosamente', 'success');
        
    } catch { 
        showError('Error al exportar usuarios');
        notificationManager?.show('Error al exportar usuarios', 'error');
    }
}

/**
 * Student action handlers (legacy - kept for compatibility)
 */
function viewStudent(studentId) {
    viewUser(studentId);
}

function editStudent(studentId) {
    // TODO: Implement edit student
    notificationManager?.show('Función de editar estudiante próximamente', 'info');
}

/**
 * Check if current user has admin permissions and auto-login if needed
 */
async function checkAdminPermissions() {
    console.log('🔐 Verificando permisos de admin...');

    // Check if we're in demo mode
    const urlParams = new URLSearchParams(window.location.search);
    const isDemoMode = urlParams.get('demo') === 'true';
    
    if (isDemoMode) {
        console.log('🎭 Modo demo detectado - usando credenciales demo');
        // Set demo admin credentials
        localStorage.setItem('api_key', 'admin-key-123-change-me');
        localStorage.setItem('user_role', 'admin');
        localStorage.setItem('user_name', 'Demo Admin');
        
        notificationManager?.show('Modo demo activado - Acceso de administrador concedido', 'success', 2000);
        return;
    }

    // Show initial loading indicator
    notificationManager?.loading('Verificando permisos de administrador...');

    const apiKey = getApiKey();
    if (!apiKey) {
        console.log('❌ No hay API key, intentando login automático...');
        notificationManager?.hideLoading();
        await attemptAdminAutoLogin();
        return;
    }

    try {
        // Test admin permissions by calling a protected admin endpoint
        const response = await fetch(`${window.API_BASE_URL}/admin/users?limit=1`, {
            headers: {
                'X-API-Key': apiKey,
                'Content-Type': 'application/json'
            }
        });

        notificationManager?.hideLoading();

        if (response.ok) {
            console.log('✅ Usuario tiene permisos de admin');
            notificationManager?.show('Acceso de administrador verificado', 'success', 2000);
            return;
        }

        if (response.status === 403) {
            console.log('🚫 Usuario no tiene permisos de admin, intentando login automático...');
            await attemptAdminAutoLogin();
            return;
        }

        throw new Error(`HTTP ${response.status}: ${response.statusText}`);

    } catch (error) {
        console.error('❌ Error verificando permisos:', error);
        notificationManager?.hideLoading();

        // For network errors, still try auto-login
        if (error.name === 'TypeError' || error.message.includes('fetch')) {
            console.log('🔄 Error de red, intentando login automático...');
            await attemptAdminAutoLogin();
        } else {
            // For other errors, show manual login
            notificationManager?.show(
                'Error verificando permisos. Iniciando sesión manualmente.',
                'warning'
            );
            showAdminLoginPrompt();
        }
    }
}


/**
 * Attempt automatic admin login with retry logic for rate limiting
 */
async function attemptAdminAutoLogin(retryCount = 0) {
    const maxRetries = 3;
    const baseDelay = 2000; // 2 seconds

    try {
        console.log(`🔄 Intentando login automático como admin... (intento ${retryCount + 1}/${maxRetries + 1})`);

        // Credenciales de admin por defecto (pueden ser configurables)
        const adminCredentials = {
            email: 'admin@moirai.com',
            password: 'admin123'
        };

        const response = await fetch(`${window.API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(adminCredentials)
        });

        if (!response.ok) {
            // Handle rate limiting specifically
            if (response.status === 429) {
                if (retryCount < maxRetries) {
                    const delay = baseDelay * Math.pow(2, retryCount); // Exponential backoff
                    console.log(`⏳ Rate limited, esperando ${delay}ms antes del siguiente intento...`);

                    // Show user feedback about retry
                    notificationManager?.show(
                        `Esperando para reintentar login automático... (${retryCount + 1}/${maxRetries})`,
                        'info',
                        2000
                    );

                    await new Promise(resolve => setTimeout(resolve, delay));
                    return attemptAdminAutoLogin(retryCount + 1);
                } else {
                    throw new Error('Rate limiting persistente - demasiados intentos');
                }
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.role === 'admin' && data.api_key) {
            // ✅ Login exitoso - guardar nueva API key
            localStorage.setItem('api_key', data.api_key);
            console.log('✅ Login automático exitoso como admin');

            // Mostrar notificación de éxito
            notificationManager?.show('Sesión de admin iniciada automáticamente', 'success');

            // Recargar la página para que navbar-manager detecte el cambio
            setTimeout(() => {
                window.location.reload();
            }, 1000);

        } else {
            throw new Error('Login no retornó credenciales de admin válidas');
        }

    } catch (error) {
        console.error('❌ Error en login automático:', error);

        // If we exhausted retries due to rate limiting, show manual login
        if (error.message.includes('Rate limiting persistente') || retryCount >= maxRetries) {
            // Mostrar mensaje de error al usuario
            notificationManager?.show(
                'Sistema ocupado. Por favor, inicia sesión manualmente.',
                'warning'
            );

            // Mostrar modal o mensaje para login manual
            showAdminLoginPrompt();
        } else {
            // For other errors, show manual login immediately
            notificationManager?.show(
                'No se pudo iniciar sesión automáticamente como admin. Por favor, inicia sesión manualmente.',
                'warning'
            );

            // Mostrar modal o mensaje para login manual
            showAdminLoginPrompt();
        }
    }
}

/**
 * Show prompt for manual admin login with rate limiting handling
 */
function showAdminLoginPrompt() {
    // Check if modal already exists
    if (document.querySelector('.admin-login-modal')) {
        console.log('ℹ️ Modal de login ya existe');
        return;
    }

    // Crear un modal simple para login de admin
    const modal = document.createElement('div');
    modal.className = 'admin-login-modal';
    modal.innerHTML = `
        <div class="modal-backdrop">
            <div class="modal-header">
                <h3>🔐 Acceso de Administrador Requerido</h3>
                <p>Esta página requiere permisos de administrador.</p>
            </div>
            <div class="modal-body">
                <div class="login-form">
                    <div class="form-group">
                        <label for="admin-email">Email:</label>
                        <input type="email" id="admin-email" value="admin@moirai.com" readonly>
                    </div>
                    <div class="form-group">
                        <label for="admin-password">Contraseña:</label>
                        <input type="password" id="admin-password" value="admin123" readonly>
                    </div>
                    <div id="login-status" class="login-status" style="display: none;"></div>
                    <button id="admin-login-btn" class="btn btn-primary">
                        <span class="btn-text">Iniciar Sesión como Admin</span>
                        <span class="btn-spinner" style="display: none;">⏳</span>
                    </button>
                </div>
            </div>
            <div class="modal-footer">
                <button id="modal-close-btn" class="btn btn-outline">Cancelar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    let isLoggingIn = false;
    let retryTimeout = null;

    // Function to handle login attempts
    const attemptLogin = async (retryCount = 0) => {
        if (isLoggingIn) return;

        const maxRetries = 2;
        const baseDelay = 3000; // 3 seconds for manual login

        isLoggingIn = true;
        const loginBtn = document.getElementById('admin-login-btn');
        const btnText = loginBtn.querySelector('.btn-text');
        const btnSpinner = loginBtn.querySelector('.btn-spinner');
        const statusDiv = document.getElementById('login-status');

        // Update UI
        loginBtn.disabled = true;
        btnText.style.display = 'none';
        btnSpinner.style.display = 'inline';
        statusDiv.style.display = 'block';
        statusDiv.textContent = retryCount > 0 ? `Reintentando... (${retryCount}/${maxRetries})` : 'Iniciando sesión...';
        statusDiv.className = 'login-status info';

        try {
            const email = document.getElementById('admin-email').value;
            const password = document.getElementById('admin-password').value;

            const response = await fetch(`${window.API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                // Handle rate limiting
                if (response.status === 429) {
                    if (retryCount < maxRetries) {
                        const delay = baseDelay * Math.pow(2, retryCount);
                        statusDiv.textContent = `Sistema ocupado. Reintentando en ${delay/1000}s...`;
                        statusDiv.className = 'login-status warning';

                        retryTimeout = setTimeout(() => {
                            attemptLogin(retryCount + 1);
                        }, delay);
                        return;
                    } else {
                        throw new Error('Demasiados intentos. El sistema está ocupado.');
                    }
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.role === 'admin' && data.api_key) {
                localStorage.setItem('api_key', data.api_key);
                statusDiv.textContent = '¡Sesión iniciada exitosamente!';
                statusDiv.className = 'login-status success';

                notificationManager?.show('Sesión de admin iniciada exitosamente', 'success');

                setTimeout(() => {
                    modal.remove();
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error('Credenciales inválidas');
            }

        } catch (error) {
            console.error('Error al iniciar sesión:', error);
            statusDiv.textContent = error.message;
            statusDiv.className = 'login-status error';

            // Reset button after error
            setTimeout(() => {
                loginBtn.disabled = false;
                btnText.style.display = 'inline';
                btnSpinner.style.display = 'none';
                isLoggingIn = false;
            }, 2000);

        }
    };

    // Event listeners
    document.getElementById('admin-login-btn').addEventListener('click', () => {
        if (retryTimeout) {
            clearTimeout(retryTimeout);
            retryTimeout = null;
        }
        attemptLogin();
    });

    document.getElementById('modal-close-btn').addEventListener('click', () => {
        if (retryTimeout) {
            clearTimeout(retryTimeout);
        }
        modal.remove();
    });

    // Auto-attempt login after modal is shown
    setTimeout(() => {
        if (!isLoggingIn) {
            attemptLogin();
        }
    }, 500);
}

/**
 * Get API key from localStorage
 */
function getApiKey() {
    return localStorage.getItem('api_key');
}

/**
 * Student action handlers (legacy - kept for compatibility)
 */
function viewStudent(studentId) {
    viewUser(studentId);
}

function editStudent(studentId) {
    // TODO: Implement edit student
    notificationManager?.show('Función de editar estudiante próximamente', 'info');
}

async function deleteStudent(studentId, studentName) {
    deleteUser(studentId, studentName);
}
