/**
 * MoirAI - Profile Page JavaScript
 * Gestión del perfil de usuario y upload de CV
 */

let currentUser = null;
let uploadInProgress = false;

document.addEventListener('DOMContentLoaded', () => {
    initProfilePage();
});

/**
 * Inicializar página de perfil
 */
async function initProfilePage() {
    // Proteger ruta - todos los roles autenticados pueden acceder
    await protectedPageManager.initProtectedPage({
        redirectOnUnauth: '/login?redirect=/profile',
        loadingMessage: 'Cargando perfil...',
        onInit: async () => {
            await loadUserProfile();
            setupFormHandlers();
            setupCVUpload();
        }
    });
}

/**
 * Cargar datos del perfil del usuario
 */
async function loadUserProfile() {
    try {
        currentUser = await authManager.getCurrentUser();

        if (!currentUser) {
            throw new Error('No se pudo obtener datos del usuario');
        }

        // Llenar formulario con datos existentes
        const form = document.getElementById('profile-form');
        if (form) {
            form.querySelector('[name="first_name"]').value = currentUser.first_name || '';
            form.querySelector('[name="last_name"]').value = currentUser.last_name || '';
            form.querySelector('[name="email"]').value = currentUser.email || '';
            form.querySelector('[name="phone"]').value = currentUser.phone || '';
            form.querySelector('[name="bio"]').value = currentUser.bio || '';

            // Llenar campos específicos de estudiante
            if (authManager.isStudent()) {
                const studentForm = document.getElementById('student-fields');
                if (studentForm) {
                    studentForm.querySelector('[name="career"]').value = currentUser.career || '';
                    studentForm.querySelector('[name="year"]').value = currentUser.year || '';
                }
            }
        }

        // Mostrar CV cargado si existe
        if (currentUser.cv_file) {
            showCVStatus(true, currentUser.cv_file);
        }

        // Mostrar habilidades inferidas
        if (currentUser.inferred_skills) {
            displayInferredSkills(currentUser.inferred_skills);
        }

        return currentUser;

    } catch (error) {
        notificationManager.error('Error al cargar perfil');
        throw error;
    }
}

/**
 * Setup de manejadores de formulario
 */
function setupFormHandlers() {
    const form = document.getElementById('profile-form');
    if (!form) return;

    // Validación en tiempo real
    FormValidator.setupRealtimeValidation(form);

    // Manejador del submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validar formulario
        const validation = FormValidator.validateForm(form);
        if (!validation.valid) {
            notificationManager.error('Por favor completa todos los campos correctamente');
            return;
        }

        // Obtener datos
        const formData = FormValidator.getFormData(form);

        // Mostrar loading
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        notificationManager.loading('Actualizando perfil...');

        try {
            // Enviar datos al API
            const response = await apiClient.put(`/students/${currentUser.id}`, formData);

            // Actualizar datos locales
            currentUser = { ...currentUser, ...response };

            // Guardar en localStorage
            StorageManager.set('currentUser', currentUser);

            notificationManager.hideLoading();
            notificationManager.success('Perfil actualizado exitosamente');

            submitBtn.disabled = false;
            submitBtn.textContent = originalText;

        } catch (error) {
            notificationManager.hideLoading();
            notificationManager.error(error.message || 'Error al actualizar perfil');

            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

/**
 * Setup del upload de CV
 */
function setupCVUpload() {
    const uploadArea = document.getElementById('cv-upload-area');
    const fileInput = document.getElementById('cv-file-input');
    const uploadBtn = document.getElementById('cv-upload-btn');

    if (!uploadArea || !fileInput) return;

    // Click en área para abrir file picker
    uploadArea.addEventListener('click', () => fileInput.click());

    // Cambio en input de archivo
    fileInput.addEventListener('change', (e) => handleCVUpload(e.target.files[0]));

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleCVUpload(e.dataTransfer.files[0]);
    });
}

/**
 * Manejar upload de CV
 */
async function handleCVUpload(file) {
    if (!file) return;

    // Validar tipo de archivo
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
        notificationManager.error('Solo se permiten archivos PDF o DOCX');
        return;
    }

    // Validar tamaño (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
        notificationManager.error('El archivo no debe superar 5MB');
        return;
    }

    // Fix: Prevenir uploads duplicados
    if (uploadInProgress) {
        notificationManager.warning('Ya hay un upload en proceso');
        return;
    }

    uploadInProgress = true;
    notificationManager.loading(`Subiendo CV...`);

    try {
        // Crear FormData
        const formData = new FormData();
        formData.append('file', file);
        formData.append('student_id', currentUser.id);

        // Usar XMLHttpRequest para obtener progress
        const response = await uploadFileWithProgress(
            `/students/${currentUser.id}/upload-resume`,
            file,
            (percentComplete) => {
                notificationManager.loading(`Subiendo CV... ${Math.round(percentComplete)}%`);
            }
        );

        // Procesar respuesta
        currentUser.cv_file = response.file_path;
        currentUser.cv_uploaded = true;

        // Guardar en localStorage
        StorageManager.set('currentUser', currentUser);

        notificationManager.hideLoading();
        notificationManager.success('CV subido exitosamente');

        // Mostrar estado del CV
        showCVStatus(true, response.file_path);

        // Mostrar habilidades inferidas si están disponibles
        if (response.inferred_skills) {
            currentUser.inferred_skills = response.inferred_skills;
            displayInferredSkills(response.inferred_skills);
            notificationManager.success('¡Habilidades analizadas!');
        }

        uploadInProgress = false;

    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error(error.message || 'Error al subir CV');
        uploadInProgress = false;
    }
}

/**
 * Upload de archivo con progress (Fix: progress bar real)
 */
function uploadFileWithProgress(url, file, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const token = typeof storageManager !== 'undefined' 
            ? storageManager.get('moirai_token')
            : localStorage.getItem('moirai_token');

        // Setup xhr
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                onProgress(percentComplete);
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response);
                } catch (e) {
                    reject(new Error('Invalid response format'));
                }
            } else {
                try {
                    const error = JSON.parse(xhr.responseText);
                    reject(new Error(error.message || 'Upload failed'));
                } catch (e) {
                    reject(new Error(`Upload failed with status ${xhr.status}`));
                }
            }
        });

        xhr.addEventListener('error', () => {
            reject(new Error('Network error during upload'));
        });

        xhr.addEventListener('abort', () => {
            reject(new Error('Upload cancelled'));
        });

        // Preparar y enviar
        const formData = new FormData();
        formData.append('file', file);
        formData.append('student_id', currentUser.id);

        xhr.open('POST', `${window.API_BASE_URL}${url}`, true);
        if (token) {
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        }
        xhr.send(formData);
    });
}

/**
 * Mostrar estado del CV
 */
function showCVStatus(uploaded, fileName) {
    const statusElement = document.getElementById('cv-status');
    const downloadBtn = document.getElementById('cv-download-btn');
    const deleteBtn = document.getElementById('cv-delete-btn');

    if (!statusElement) return;

    if (uploaded) {
        statusElement.innerHTML = `
            <div class="cv-status-success">
                <i class="fas fa-check-circle"></i>
                <p>CV cargado: <strong>${fileName}</strong></p>
                <p class="upload-date">Última actualización: ${new Date().toLocaleDateString('es-ES')}</p>
            </div>
        `;

        if (downloadBtn) {
            downloadBtn.style.display = 'block';
            downloadBtn.href = `/api/v1/students/${currentUser.id}/download-resume`;
        }

        if (deleteBtn) {
            deleteBtn.style.display = 'block';
            deleteBtn.addEventListener('click', deleteCVFile);
        }
    } else {
        statusElement.innerHTML = `
            <div class="cv-status-empty">
                <i class="fas fa-file-pdf"></i>
                <p>No hay CV cargado</p>
            </div>
        `;

        if (downloadBtn) downloadBtn.style.display = 'none';
        if (deleteBtn) deleteBtn.style.display = 'none';
    }
}

/**
 * Eliminar archivo CV
 */
async function deleteCVFile() {
    if (!confirm('¿Estás seguro de que deseas eliminar tu CV?')) {
        return;
    }

    notificationManager.loading('Eliminando CV...');

    try {
        await apiClient.delete(`/students/${currentUser.id}/resume`);

        currentUser.cv_file = null;
        currentUser.cv_uploaded = false;

        StorageManager.set('currentUser', currentUser);

        notificationManager.hideLoading();
        notificationManager.success('CV eliminado');

        showCVStatus(false);

    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error('Error al eliminar CV');
    }
}

/**
 * Mostrar habilidades inferidas
 */
function displayInferredSkills(skills) {
    const container = document.getElementById('inferred-skills');

    if (!container || !skills) return;

    let html = '<div class="skills-grid">';

    skills.forEach(skill => {
        const skillType = skill.type || 'technical'; // 'technical' o 'soft'
        const badge = skillType === 'soft' ? 'skill-badge-soft' : 'skill-badge-tech';

        html += `
            <div class="skill-item ${badge}">
                <span class="skill-name">${skill.name}</span>
                <span class="skill-score">${Math.round(skill.score * 100)}%</span>
                <button class="skill-remove" onclick="removeSkill('${skill.id}')" title="Remover">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });

    html += '</div>';

    container.innerHTML = html;

    // Mostrar mensaje si no hay skills
    if (skills.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-brain"></i>
                <p>Sube tu CV para que analicemos tus habilidades</p>
            </div>
        `;
    }
}

/**
 * Remover habilidad
 */
async function removeSkill(skillId) {
    try {
        currentUser.inferred_skills = currentUser.inferred_skills.filter(s => s.id !== skillId);
        displayInferredSkills(currentUser.inferred_skills);
        notificationManager.success('Habilidad removida');
    } catch (error) {
        notificationManager.error('Error al remover habilidad');
    }
}

/**
 * Cambiar contraseña
 */
async function handlePasswordChange() {
    const currentPassword = prompt('Ingresa tu contraseña actual:');
    if (!currentPassword) return;

    const newPassword = prompt('Ingresa tu nueva contraseña:');
    if (!newPassword) return;

    const confirmPassword = prompt('Confirma tu nueva contraseña:');
    if (confirmPassword !== newPassword) {
        notificationManager.error('Las contraseñas no coinciden');
        return;
    }

    // Validar nueva contraseña
    const validation = FormValidator.validate('password', newPassword);
    if (!validation.valid) {
        notificationManager.error(validation.error);
        return;
    }

    notificationManager.loading('Cambiando contraseña...');

    try {
        await authManager.changePassword(currentPassword, newPassword);
        notificationManager.hideLoading();
        notificationManager.success('Contraseña cambiada exitosamente');
    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error(error.message || 'Error al cambiar contraseña');
    }
}

/**
 * Logout desde perfil
 */
async function logout() {
    try {
        await authManager.logout();
        notificationManager.success('Hasta luego');
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    } catch (error) {
        notificationManager.error('Error al cerrar sesión');
    }
}
