/**
 * MoirAI Admin Dashboard - JavaScript
 * Handles navigation, data management, and interactions
 * Integrates AdminAnalyticsPage module
 */

// Global analytics instance
let dashboardAnalytics = null;

document.addEventListener('DOMContentLoaded', function () {
    initializeNavigation();
    initializeCharts();
    initializeEventListeners();
    loadDashboardData();
});

/**
 * Initialize Navigation
 */
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            if (section) {
                switchSection(section);
            }
        });
    });
}

/**
 * Switch Content Section
 */
function switchSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    // Show selected section
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }

    // Mark nav item as active
    const navItem = document.querySelector(`[data-section="${sectionId}"]`);
    if (navItem) {
        navItem.classList.add('active');
    }

    // Load data if needed
    if (sectionId === 'analytics') {
        initializeAnalytics();
    }
}

/**
 * Initialize Analytics Module (Integrated Mode)
 * This is called when user switches to analytics section
 */
function initializeAnalytics() {
    if (!dashboardAnalytics) {
        // Create analytics instance in integrated mode
        dashboardAnalytics = new AdminAnalyticsPage('#analytics');
        dashboardAnalytics.initialize(true).catch(error => {
            console.error('Error initializing analytics in dashboard:', error);
            showNotification('Error al cargar analítica', 'error');
        });
    } else if (dashboardAnalytics.initialized) {
        // Reload analytics data
        dashboardAnalytics.loadAnalytics(true).catch(error => {
            console.error('Error reloading analytics:', error);
        });
    }
}

/**
 * Initialize Charts (using Canvas)
 */
function initializeCharts() {
    // Check if Chart.js is available, otherwise use simple data visualization

    // Registers Chart
    const registersCanvas = document.getElementById('registersChart');
    if (registersCanvas) {
        createSimpleChart(registersCanvas,
            ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            [45, 52, 38, 65, 72, 58, 41],
            'Registros por Día'
        );
    }

    // Users Distribution Chart
    const usersCanvas = document.getElementById('usersChart');
    if (usersCanvas) {
        createPieChart(usersCanvas,
            ['Estudiantes', 'Empresas', 'Admins'],
            [1247, 156, 8]
        );
    }

    // Trends Chart
    const trendsCanvas = document.getElementById('trendsChart');
    if (trendsCanvas) {
        createSimpleChart(trendsCanvas,
            ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
            [120, 145, 178, 210],
            'Tendencia de Registros'
        );
    }

    // Major Distribution Chart
    const majorCanvas = document.getElementById('majorChart');
    if (majorCanvas) {
        createPieChart(majorCanvas,
            ['Sistemas', 'Admin', 'Contab.'],
            [450, 280, 150]
        );
    }

    // Conversion Chart
    const conversionCanvas = document.getElementById('conversionChart');
    if (conversionCanvas) {
        createSimpleChart(conversionCanvas,
            ['Enero', 'Febrero', 'Marzo', 'Abril'],
            [2.5, 3.2, 4.1, 5.3],
            'Tasa de Conversión (%)'
        );
    }
}

/**
 * Create Simple Line Chart (without Chart.js)
 */
function createSimpleChart(canvas, labels, data, title) {
    const ctx = canvas.getContext('2d');
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;

    // Set canvas size
    canvas.width = width;
    canvas.height = height;

    // Calculate padding
    const padding = 40;
    const chartWidth = width - (padding * 2);
    const chartHeight = height - (padding * 2);

    // Find max value
    const maxValue = Math.max(...data) * 1.1;

    // Draw background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);

    // Draw axes
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // Draw grid lines
    ctx.strokeStyle = '#f3f4f6';
    for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }

    // Draw line
    ctx.strokeStyle = '#730f33';
    ctx.lineWidth = 2;
    ctx.beginPath();

    data.forEach((value, index) => {
        const x = padding + (chartWidth / (data.length - 1)) * index;
        const y = height - padding - (value / maxValue) * chartHeight;

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();

    // Draw points
    ctx.fillStyle = '#730f33';
    data.forEach((value, index) => {
        const x = padding + (chartWidth / (data.length - 1)) * index;
        const y = height - padding - (value / maxValue) * chartHeight;

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    });

    // Draw labels
    ctx.fillStyle = '#6b7280';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';

    labels.forEach((label, index) => {
        const x = padding + (chartWidth / (labels.length - 1)) * index;
        ctx.fillText(label, x, height - padding + 20);
    });
}

/**
 * Create Pie Chart (without Chart.js)
 */
function createPieChart(canvas, labels, data) {
    const ctx = canvas.getContext('2d');
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;

    canvas.width = width;
    canvas.height = height;

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 20;

    const total = data.reduce((a, b) => a + b, 0);
    const colors = ['#730f33', '#235b4e', '#bc935b'];

    let currentAngle = -Math.PI / 2;

    data.forEach((value, index) => {
        const sliceAngle = (value / total) * Math.PI * 2;

        // Draw slice
        ctx.fillStyle = colors[index % colors.length];
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
        ctx.lineTo(centerX, centerY);
        ctx.fill();

        // Draw label
        const labelAngle = currentAngle + sliceAngle / 2;
        const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
        const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(labels[index], labelX, labelY);

        currentAngle += sliceAngle;
    });
}

/**
 * Initialize Event Listeners
 */
function initializeEventListeners() {
    // Add Student Button
    const addStudentBtn = document.getElementById('addStudentBtn');
    if (addStudentBtn) {
        addStudentBtn.addEventListener('click', function () {
            showModal('addStudentModal');
        });
    }

    // Add Company Button
    const addCompanyBtn = document.getElementById('addCompanyBtn');
    if (addCompanyBtn) {
        addCompanyBtn.addEventListener('click', function () {
            showModal('addCompanyModal');
        });
    }

    // Tab Buttons
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const tabId = this.getAttribute('data-tab');
            switchTab(tabId);
        });
    });

    // Sidebar Toggle
    const toggleBtn = document.getElementById('toggleSidebar');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function () {
            document.querySelector('.sidebar').classList.toggle('collapsed');
        });
    }

    // Action Buttons
    const actionBtns = document.querySelectorAll('.action-btn');
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const action = this.classList.contains('view') ? 'view' :
                this.classList.contains('edit') ? 'edit' : 'delete';

            if (action === 'delete') {
                if (confirm('¿Está seguro de que desea eliminar este elemento?')) {
                    showNotification('Elemento eliminado correctamente', 'success');
                }
            } else {
                showNotification(`Acción: ${action}`, 'info');
            }
        });
    });
}

/**
 * Switch Tab Content
 */
function switchTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Remove active from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    const tabElement = document.getElementById(`${tabId}-tab`);
    if (tabElement) {
        tabElement.classList.add('active');
    }

    // Mark button as active
    const tabBtn = document.querySelector(`[data-tab="${tabId}"]`);
    if (tabBtn) {
        tabBtn.classList.add('active');
    }
}

/**
 * Load Dashboard Data
 */
function loadDashboardData() {
    // Simulate loading data from API
    console.log('Loading dashboard data...');

    // In a real application, you would fetch data from API endpoints:
    // GET /api/v1/admin/dashboard/stats
    // GET /api/v1/admin/students
    // GET /api/v1/admin/companies
    // etc.
}

/**
 * Show Modal
 */
function showModal(modalId) {
    // This is a placeholder - create modal as needed
    showNotification('Funcionalidad de modal por implementar', 'info');
}

/**
 * Show Notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: '0.5rem',
        color: 'white',
        fontSize: '1rem',
        zIndex: '10000',
        animation: 'slideInRight 0.3s ease',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
    });

    // Set background color based on type
    const colors = {
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6'
    };
    notification.style.backgroundColor = colors[type] || colors['info'];

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

/**
 * Format Currency
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(value);
}

/**
 * Format Date
 */
function formatDate(dateString) {
    return new Intl.DateTimeFormat('es-MX', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(dateString));
}

/**
 * Add Animation Styles
 */
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
    `;
    document.head.appendChild(style);
}

addAnimationStyles();

/**
 * API Integration Example
 * Uncomment and modify to use real API endpoints
 */
/*
async function fetchDashboardStats() {
    try {
        const response = await fetch('/api/v1/admin/dashboard/stats', {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        const data = await response.json();
        updateDashboardCards(data);
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        showNotification('Error al cargar datos del dashboard', 'error');
    }
}

async function fetchStudents() {
    try {
        const response = await fetch('/api/v1/admin/students', {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        const data = await response.json();
        populateStudentsTable(data);
    } catch (error) {
        console.error('Error fetching students:', error);
        showNotification('Error al cargar estudiantes', 'error');
    }
}

function getAuthToken() {
    return localStorage.getItem('authToken');
}
*/
