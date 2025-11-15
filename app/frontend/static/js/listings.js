// ============================================
// LISTINGS PAGE JAVASCRIPT (Jobs, Companies, Students)
// ============================================

// Mock Data for Listings
const mockJobs = [
    {
        id: 1,
        title: "Desarrollador Python Senior",
        company: "TechCorp",
        location: "Córdoba",
        modality: "remoto",
        sector: "tecnologia",
        level: "senior",
        salary: "$150,000 - $200,000",
        description: "Buscamos un desarrollador Python experimentado para liderar nuestro equipo de backend.",
        skills: ["Python", "FastAPI", "PostgreSQL", "Docker"],
        published: 2,
        match: 95
    },
    {
        id: 2,
        title: "Frontend Developer React",
        company: "WebSolutions",
        location: "Buenos Aires",
        modality: "hibrido",
        sector: "tecnologia",
        level: "semi-senior",
        salary: "$120,000 - $150,000",
        description: "Se necesita desarrollador frontend con experiencia en React y TypeScript.",
        skills: ["React", "JavaScript", "TypeScript", "CSS"],
        published: 5,
        match: 88
    },
    {
        id: 3,
        title: "Analista de Datos",
        company: "DataInsights",
        location: "Mendoza",
        modality: "presencial",
        sector: "finanzas",
        level: "junior",
        salary: "$90,000 - $110,000",
        description: "Analista de datos con conocimientos en Python y SQL para análisis empresarial.",
        skills: ["Python", "SQL", "Power BI", "Excel"],
        published: 12,
        match: 82
    },
    {
        id: 4,
        title: "Especialista en Marketing Digital",
        company: "CreativeAgency",
        location: "Córdoba",
        modality: "hibrido",
        sector: "marketing",
        level: "semi-senior",
        salary: "$100,000 - $130,000",
        description: "Especialista en estrategias digitales, SEO y gestión de redes sociales.",
        skills: ["SEO", "SEM", "Redes Sociales", "Analytics"],
        published: 3,
        match: 75
    },
    {
        id: 5,
        title: "Administrador de Sistemas",
        company: "SysAdmin Inc",
        location: "Buenos Aires",
        modality: "presencial",
        sector: "tecnologia",
        level: "senior",
        salary: "$130,000 - $170,000",
        description: "Buscamos administrador de sistemas con experiencia en cloud computing.",
        skills: ["AWS", "Linux", "Networking", "Security"],
        published: 1,
        match: 80
    },
    {
        id: 6,
        title: "Contador Senior",
        company: "FinancePartners",
        location: "Córdoba",
        modality: "presencial",
        sector: "finanzas",
        level: "senior",
        salary: "$140,000 - $180,000",
        description: "Contador con experiencia en impuestos y auditoría para empresa multinacional.",
        skills: ["Contabilidad", "Impuestos", "Auditoría"],
        published: 8,
        match: 70
    },
    {
        id: 7,
        title: "Especialista en RH",
        company: "TalentMasters",
        location: "Buenos Aires",
        modality: "remoto",
        sector: "rrhh",
        level: "semi-senior",
        salary: "$95,000 - $125,000",
        description: "Especialista en reclutamiento y selección de personal para empresa en crecimiento.",
        skills: ["Reclutamiento", "Entrevistas", "LinkedIn"],
        published: 4,
        match: 78
    },
    {
        id: 8,
        title: "QA Engineer",
        company: "QualityFirst",
        location: "Mendoza",
        modality: "remoto",
        sector: "tecnologia",
        level: "junior",
        salary: "$85,000 - $105,000",
        description: "Ingeniero de QA para testing automatizado en aplicaciones web.",
        skills: ["Selenium", "Testing", "Python", "JIRA"],
        published: 6,
        match: 72
    }
];

const mockCompanies = [
    {
        id: 1,
        name: "TechCorp",
        sector: "Tecnología",
        size: "grande",
        logo: "T",
        description: "Empresa líder en soluciones tecnológicas con más de 20 años en el mercado.",
        jobs: 12,
        employees: 500,
        certified: true,
        topEmployer: true,
        location: "Córdoba"
    },
    {
        id: 2,
        name: "WebSolutions",
        sector: "Tecnología",
        size: "pyme",
        logo: "W",
        description: "Agencia de desarrollo web especializada en aplicaciones React y Node.js.",
        jobs: 5,
        employees: 45,
        certified: true,
        topEmployer: false,
        location: "Buenos Aires"
    },
    {
        id: 3,
        name: "DataInsights",
        sector: "Finanzas",
        size: "startup",
        logo: "D",
        description: "Startup innovadora en análisis de datos y business intelligence.",
        jobs: 8,
        employees: 25,
        certified: false,
        topEmployer: false,
        location: "Mendoza"
    },
    {
        id: 4,
        name: "CreativeAgency",
        sector: "Marketing",
        size: "pyme",
        logo: "C",
        description: "Agencia creativa especializada en marketing digital y branding.",
        jobs: 3,
        employees: 30,
        certified: true,
        topEmployer: false,
        location: "Córdoba"
    },
    {
        id: 5,
        name: "FinancePartners",
        sector: "Finanzas",
        size: "grande",
        logo: "F",
        description: "Consultora financiera con presencia internacional en 15 países.",
        jobs: 15,
        employees: 800,
        certified: true,
        topEmployer: true,
        location: "Buenos Aires"
    },
    {
        id: 6,
        name: "SysAdmin Inc",
        sector: "Tecnología",
        size: "pyme",
        logo: "S",
        description: "Proveedor de servicios de administración de sistemas y cloud computing.",
        jobs: 6,
        employees: 50,
        certified: true,
        topEmployer: false,
        location: "Buenos Aires"
    },
    {
        id: 7,
        name: "TalentMasters",
        sector: "Recursos Humanos",
        size: "pyme",
        logo: "T",
        description: "Empresa especializada en reclutamiento y gestión de talento.",
        jobs: 4,
        employees: 35,
        certified: false,
        topEmployer: false,
        location: "Buenos Aires"
    },
    {
        id: 8,
        name: "QualityFirst",
        sector: "Tecnología",
        size: "startup",
        logo: "Q",
        description: "Centro de excelencia en testing y aseguramiento de calidad de software.",
        jobs: 7,
        employees: 20,
        certified: false,
        topEmployer: false,
        location: "Mendoza"
    }
];

const mockStudents = [
    {
        id: 1,
        name: "Juan García",
        career: "Ingeniería en Sistemas",
        year: 4,
        availability: "inmediata",
        avatar: "JG",
        bio: "Apasionado por el desarrollo full-stack y la inteligencia artificial.",
        skills: ["Python", "React", "JavaScript", "SQL"],
        projects: 5
    },
    {
        id: 2,
        name: "María López",
        career: "Administración de Empresas",
        year: 3,
        availability: "proximas-semanas",
        avatar: "ML",
        bio: "Especialista en gestión de proyectos y liderazgo de equipos.",
        skills: ["Gestión", "Excel", "SAP"],
        projects: 3
    },
    {
        id: 3,
        name: "Carlos Rodríguez",
        career: "Ingeniería en Sistemas",
        year: 2,
        availability: "vacaciones",
        avatar: "CR",
        bio: "Desarrollador frontend con experiencia en aplicaciones modernas.",
        skills: ["React", "Vue.js", "CSS", "JavaScript"],
        projects: 4
    },
    {
        id: 4,
        name: "Ana Martínez",
        career: "Contabilidad",
        year: 4,
        availability: "inmediata",
        avatar: "AM",
        bio: "Contadora con experiencia en auditoría y finanzas corporativas.",
        skills: ["Contabilidad", "Impuestos", "Auditoría"],
        projects: 2
    },
    {
        id: 5,
        name: "Diego Fernández",
        career: "Ingeniería Eléctrica",
        year: 3,
        availability: "proximas-semanas",
        avatar: "DF",
        bio: "Ingeniero con especialización en energías renovables.",
        skills: ["AutoCAD", "MATLAB", "Simulación"],
        projects: 3
    },
    {
        id: 6,
        name: "Sofia González",
        career: "Ingeniería en Sistemas",
        year: 4,
        availability: "inmediata",
        avatar: "SG",
        bio: "Desarrolladora backend especializada en microservicios y API REST.",
        skills: ["Python", "FastAPI", "Docker", "PostgreSQL"],
        projects: 6
    },
    {
        id: 7,
        name: "Lucas Pérez",
        career: "Marketing",
        year: 2,
        availability: "vacaciones",
        avatar: "LP",
        bio: "Especialista en marketing digital y redes sociales.",
        skills: ["Social Media", "SEO", "Analytics"],
        projects: 2
    },
    {
        id: 8,
        name: "Valentina Torres",
        career: "Administración de Empresas",
        year: 1,
        availability: "proximas-semanas",
        avatar: "VT",
        bio: "Emprendedora con pasión por la innovación y emprendimiento.",
        skills: ["Excel", "Comunicación", "Liderazgo"],
        projects: 1
    }
];

// Pagination variables
let currentPage = 1;
const itemsPerPage = 6;
let allData = [];
let filteredData = [];

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    detectPage();
    attachFilterListeners();
    applyFilters();
});

// Detect which page we're on
function detectPage() {
    const path = window.location.pathname;
    if (path.includes('oportunidades')) {
        allData = [...mockJobs];
        renderJobs(allData);
    } else if (path.includes('empresas')) {
        allData = [...mockCompanies];
        renderCompanies(allData);
    } else if (path.includes('estudiantes')) {
        allData = [...mockStudents];
        renderStudents(allData);
    }
}

// Attach filter listeners
function attachFilterListeners() {
    document.querySelectorAll('.filter-select, .filter-checkbox-group input, #sortFilter').forEach(el => {
        el.addEventListener('change', applyFilters);
    });

    const searchInputs = document.querySelectorAll('[id^="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', applyFilters);
    });
}

// Apply filters
function applyFilters() {
    currentPage = 1;
    const path = window.location.pathname;

    if (path.includes('oportunidades')) {
        filteredData = filterJobs();
        renderJobs(filteredData);
    } else if (path.includes('empresas')) {
        filteredData = filterCompanies();
        renderCompanies(filteredData);
    } else if (path.includes('estudiantes')) {
        filteredData = filterStudents();
        renderStudents(filteredData);
    }
}

// Filter Jobs
function filterJobs() {
    let data = [...allData];

    // Search filter
    const searchValue = document.getElementById('searchJobs')?.value.toLowerCase() || '';
    if (searchValue) {
        data = data.filter(job =>
            job.title.toLowerCase().includes(searchValue) ||
            job.company.toLowerCase().includes(searchValue) ||
            job.skills.some(s => s.toLowerCase().includes(searchValue))
        );
    }

    // Location filter
    const location = document.getElementById('locationFilter')?.value || '';
    if (location) {
        data = data.filter(job => job.location.toLowerCase() === location);
    }

    // Modality filter
    const modalities = Array.from(document.querySelectorAll('.modality-filter:checked')).map(el => el.value);
    if (modalities.length > 0) {
        data = data.filter(job => modalities.includes(job.modality));
    }

    // Sector filter
    const sector = document.getElementById('sectorFilter')?.value || '';
    if (sector) {
        data = data.filter(job => job.sector === sector);
    }

    // Level filter
    const levels = Array.from(document.querySelectorAll('.level-filter:checked')).map(el => el.value);
    if (levels.length > 0) {
        data = data.filter(job => levels.includes(job.level));
    }

    // Skills filter
    const skills = Array.from(document.querySelectorAll('.skill-filter:checked')).map(el => el.value);
    if (skills.length > 0) {
        data = data.filter(job =>
            skills.some(skill => job.skills.some(jobSkill => jobSkill.toLowerCase().includes(skill)))
        );
    }

    // Sort
    const sortBy = document.getElementById('sortFilter')?.value || 'recent';
    switch (sortBy) {
        case 'match':
            data.sort((a, b) => b.match - a.match);
            break;
        case 'salary-high':
            data.sort((a, b) => parseInt(b.salary) - parseInt(a.salary));
            break;
        case 'salary-low':
            data.sort((a, b) => parseInt(a.salary) - parseInt(b.salary));
            break;
        default:
            data.sort((a, b) => a.published - b.published);
    }

    return data;
}

// Filter Companies
function filterCompanies() {
    let data = [...allData];

    // Search filter
    const searchValue = document.getElementById('searchCompanies')?.value.toLowerCase() || '';
    if (searchValue) {
        data = data.filter(company =>
            company.name.toLowerCase().includes(searchValue) ||
            company.description.toLowerCase().includes(searchValue)
        );
    }

    // Sector filter
    const sector = document.getElementById('sectorFilter')?.value || '';
    if (sector) {
        data = data.filter(company => company.sector.toLowerCase() === sector);
    }

    // Size filter
    const sizes = Array.from(document.querySelectorAll('.size-filter:checked')).map(el => el.value);
    if (sizes.length > 0) {
        data = data.filter(company => sizes.includes(company.size));
    }

    // Location filter
    const location = document.getElementById('locationFilter')?.value || '';
    if (location) {
        data = data.filter(company => company.location.toLowerCase() === location);
    }

    // Accreditation filter
    const accreds = Array.from(document.querySelectorAll('.accred-filter:checked')).map(el => el.value);
    if (accreds.length > 0) {
        data = data.filter(company => {
            if (accreds.includes('verified') && !company.certified) return false;
            if (accreds.includes('iso') && !company.certified) return false;
            if (accreds.includes('top') && !company.topEmployer) return false;
            return true;
        });
    }

    // Jobs filter
    const hasJobs = document.querySelector('.jobs-filter:checked');
    if (hasJobs) {
        data = data.filter(company => company.jobs > 0);
    }

    return data;
}

// Filter Students
function filterStudents() {
    let data = [...allData];

    // Search filter
    const searchValue = document.getElementById('searchStudents')?.value.toLowerCase() || '';
    if (searchValue) {
        data = data.filter(student =>
            student.name.toLowerCase().includes(searchValue) ||
            student.career.toLowerCase().includes(searchValue) ||
            student.skills.some(s => s.toLowerCase().includes(searchValue))
        );
    }

    // Career filter
    const career = document.getElementById('careerFilter')?.value || '';
    if (career) {
        data = data.filter(student => student.career.toLowerCase().includes(career));
    }

    // Year filter
    const years = Array.from(document.querySelectorAll('.year-filter:checked')).map(el => parseInt(el.value));
    if (years.length > 0) {
        data = data.filter(student => years.includes(student.year));
    }

    // Availability filter
    const availabilities = Array.from(document.querySelectorAll('.availability-filter:checked')).map(el => el.value);
    if (availabilities.length > 0) {
        data = data.filter(student => availabilities.includes(student.availability));
    }

    // Skills filter
    const skills = Array.from(document.querySelectorAll('.skill-filter:checked')).map(el => el.value);
    if (skills.length > 0) {
        data = data.filter(student =>
            skills.some(skill => student.skills.some(studentSkill => studentSkill.toLowerCase().includes(skill)))
        );
    }

    // Experience filter
    const experience = document.getElementById('experienceFilter')?.value || '';
    if (experience) {
        data = data.filter(student => {
            if (experience === 'sin-experiencia' && student.projects > 0) return false;
            if (experience === '1-proyecto' && student.projects !== 1) return false;
            if (experience === '2-proyectos' && student.projects < 2) return false;
            return true;
        });
    }

    return data;
}

// Render Jobs
function renderJobs(jobs) {
    const container = document.getElementById('jobsContainer');
    const start = (currentPage - 1) * itemsPerPage;
    const paginatedJobs = jobs.slice(start, start + itemsPerPage);

    container.innerHTML = paginatedJobs.map(job => `
        <div class="job-card">
            <div class="job-header">
                <div>
                    <h3 class="job-title">${job.title}</h3>
                    <p class="job-company"><i class="fas fa-building"></i> ${job.company}</p>
                </div>
                <span class="job-match">${job.match}% Match</span>
            </div>
            
            <div class="job-meta">
                <div class="job-meta-item">
                    <i class="fas fa-map-marker-alt"></i> ${job.location}
                </div>
                <span class="job-modality ${job.modality}">
                    ${job.modality.charAt(0).toUpperCase() + job.modality.slice(1)}
                </span>
                <div class="job-meta-item">
                    <i class="fas fa-clock"></i> Publicado hace ${job.published}h
                </div>
            </div>
            
            <p class="job-description">${job.description}</p>
            
            <div class="job-skills">
                ${job.skills.map(skill => `<span class="skill-badge">${skill}</span>`).join('')}
            </div>
            
            <div class="job-footer">
                <span class="job-salary">${job.salary}</span>
                <button class="apply-btn" onclick="applyJob(${job.id})">
                    <i class="fas fa-paper-plane"></i> Postularse
                </button>
            </div>
        </div>
    `).join('');

    // Update count and pagination
    document.getElementById('jobCount').textContent = jobs.length;
    updatePagination(jobs.length);
}

// Render Companies
function renderCompanies(companies) {
    const container = document.getElementById('companiesContainer');
    const start = (currentPage - 1) * itemsPerPage;
    const paginatedCompanies = companies.slice(start, start + itemsPerPage);

    container.innerHTML = paginatedCompanies.map(company => `
        <div class="company-card">
            <div class="company-header">
                <div class="company-logo">${company.logo}</div>
                <div class="company-info">
                    <h3>${company.name}</h3>
                    <p class="company-sector"><i class="fas fa-industry"></i> ${company.sector}</p>
                </div>
            </div>
            
            <div class="company-stats">
                <div class="company-stat">
                    <i class="fas fa-briefcase"></i> ${company.jobs} vacantes
                </div>
                <div class="company-stat">
                    <i class="fas fa-users"></i> ${company.employees} empleados
                </div>
            </div>
            
            <p class="company-description">${company.description}</p>
            
            <div class="company-badges">
                ${company.certified ? '<span class="company-badge verified"><i class="fas fa-check"></i> Verificada</span>' : ''}
                ${company.topEmployer ? '<span class="company-badge top"><i class="fas fa-star"></i> Top Empleadora</span>' : ''}
            </div>
            
            <div class="company-footer">
                <span class="company-jobs">${company.jobs} oportunidades</span>
                <button class="visit-btn" onclick="viewCompany(${company.id})">
                    <i class="fas fa-arrow-right"></i> Ver detalles
                </button>
            </div>
        </div>
    `).join('');

    document.getElementById('companyCount').textContent = companies.length;
    updatePagination(companies.length);
}

// Render Students
function renderStudents(students) {
    const container = document.getElementById('studentsContainer');
    const start = (currentPage - 1) * itemsPerPage;
    const paginatedStudents = students.slice(start, start + itemsPerPage);

    container.innerHTML = paginatedStudents.map(student => `
        <div class="student-card">
            <div class="student-header">
                <div class="student-avatar">${student.avatar}</div>
                <div class="student-info">
                    <h3>${student.name}</h3>
                    <p class="student-career"><i class="fas fa-graduation-cap"></i> ${student.career}</p>
                </div>
            </div>
            
            <p class="student-bio">${student.bio}</p>
            
            <div class="student-skills">
                ${student.skills.map(skill => `<span class="skill-badge">${skill}</span>`).join('')}
            </div>
            
            <div class="student-footer">
                <span class="student-year">Año <span>${student.year}°</span></span>
                <button class="view-profile-btn" onclick="viewProfile(${student.id})">
                    <i class="fas fa-user-circle"></i> Ver perfil
                </button>
            </div>
        </div>
    `).join('');

    document.getElementById('studentCount').textContent = students.length;
    updatePagination(students.length);
}

// Update Pagination
function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const paginationNumbers = document.getElementById('paginationNumbers');
    paginationNumbers.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement('button');
        button.textContent = i;
        button.className = `page-num ${i === currentPage ? 'active' : ''}`;
        button.onclick = () => {
            currentPage = i;
            applyFilters();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        };
        paginationNumbers.appendChild(button);
    }
}

// Pagination Functions
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        applyFilters();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function nextPage() {
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        applyFilters();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Clear Filters
function clearFilters() {
    document.querySelectorAll('.filter-select').forEach(el => el.value = '');
    document.querySelectorAll('input[type="checkbox"]').forEach(el => el.checked = false);
    document.querySelectorAll('[id^="search"]').forEach(el => el.value = '');
    document.getElementById('sortFilter').value = 'recent';
    applyFilters();
}

// View Mode Toggle
function setViewMode(mode) {
    const path = window.location.pathname;
    let container;

    if (path.includes('empresas')) {
        container = document.getElementById('companiesContainer');
    } else if (path.includes('estudiantes')) {
        container = document.getElementById('studentsContainer');
    }

    if (container) {
        container.classList.remove('grid-view', 'list-view');
        container.classList.add(mode + '-view');

        document.getElementById('gridViewBtn').classList.toggle('active', mode === 'grid');
        document.getElementById('listViewBtn').classList.toggle('active', mode === 'list');
    }
}

// Action Functions
function applyJob(jobId) {
    const job = allData.find(j => j.id === jobId);
    alert(`¡Postulación registrada para: ${job.title} en ${job.company}!`);
}

function viewCompany(companyId) {
    const company = allData.find(c => c.id === companyId);
    alert(`Visitando perfil de ${company.name}`);
}

function viewProfile(studentId) {
    const student = allData.find(s => s.id === studentId);
    alert(`Visitando perfil de ${student.name}`);
}
