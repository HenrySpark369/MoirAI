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
 * ✅ Cargar perfil del usuario desde BD (NO localStorage)
 * Usa GET /students/me (datos frescos)
 * Si falla, usa localStorage como fallback
 */
async function loadUserProfile() {
    try {
        console.log('📥 Cargando perfil del usuario desde BD...');
        
        // ✅ Obtener perfil COMPLETO de BD
        currentUser = await authManager.getCurrentUser();

        if (!currentUser) {
            throw new Error('No se pudo obtener datos del usuario');
        }

        console.log('✅ Perfil cargado exitosamente:', {
            id: currentUser.id,
            email: currentUser.email,
            cvUploaded: currentUser.cv_uploaded,
            skillsCount: currentUser.skills?.length || 0
        });

        // Llenar formulario con datos existentes (de BD)
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
                    studentForm.querySelector('[name="program"]').value = currentUser.program || '';
                }
            }
        }

        // ✅ Mostrar CV si BD indica que existe (NO localStorage)
        if (currentUser.cv_uploaded && currentUser.cv_filename) {
            console.log('📄 CV encontrado:', currentUser.cv_filename);
            showCVStatus(true, currentUser.cv_filename, currentUser.cv_upload_date);
        } else {
            console.log('⚪ Sin CV');
            showCVStatus(false);
        }

        // ✅ Mostrar habilidades de BD
        const allSkills = [];
        
        if (currentUser.skills && Array.isArray(currentUser.skills)) {
            allSkills.push(...currentUser.skills);
            console.log(`📚 ${currentUser.skills.length} habilidades técnicas`);
        }
        
        if (currentUser.soft_skills && Array.isArray(currentUser.soft_skills)) {
            allSkills.push(...currentUser.soft_skills);
            console.log(`💬 ${currentUser.soft_skills.length} habilidades blandas`);
        }
        
        if (allSkills.length > 0) {
            displayInferredSkills(allSkills);
        }

        return currentUser;

    } catch (error) {
        console.error('❌ Error cargando perfil:', error);
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
 * ✅ Manejar upload de CV
 * Sincroniza correctamente con BD y localStorage
 */
async function handleCVUpload(file) {
    if (!file) return;

    // Validar tipo de archivo
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.txt')) {
        notificationManager.error('Solo se permiten archivos PDF, DOCX o TXT');
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
        // Preparar metadatos JSON para el endpoint
        const metadata = {
            name: currentUser.name || `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim(),
            email: currentUser.email,
            program: currentUser.career || currentUser.program || ''
        };

        // Usar XMLHttpRequest para obtener progress con FormData
        const response = await uploadFileWithProgress(
            `/students/upload_resume`,
            file,
            metadata,
            (percentComplete) => {
                notificationManager.loading(`Subiendo CV... ${Math.round(percentComplete)}%`);
            }
        );

        // ✅ Procesar respuesta: ResumeAnalysisResponse contiene student y skills extraídas
        if (response.student) {
            // ✅ CAMBIO: Usar respuesta de BD, NO localStorage solo
            // Actualizar currentUser con datos de la respuesta (de BD)
            currentUser = { ...currentUser, ...response.student };
            
            // ✅ Guardar en localStorage como caché (robusto, sin dependencias)
            try {
                localStorage.setItem('currentUserProfile', JSON.stringify(currentUser));
                localStorage.setItem('currentUserProfile_timestamp', Date.now().toString());
                console.log('✅ CV profile cached:', {
                    fileName: response.student.cv_filename,
                    skillsCount: response.extracted_skills?.length || 0
                });
            } catch (storageError) {
                console.warn('⚠️ localStorage no disponible:', storageError);
            }

            notificationManager.hideLoading();
            notificationManager.success('CV subido y analizado exitosamente');

            // Mostrar estado del CV
            showCVStatus(true, response.student.cv_filename || response.student.name, response.student.cv_upload_date);

            // ✅ Mostrar habilidades extraídas
            if (response.extracted_skills || response.extracted_soft_skills) {
                const allSkills = [
                    ...(response.extracted_skills || []),
                    ...(response.extracted_soft_skills || [])
                ];
                displayInferredSkills(allSkills);
                notificationManager.success(`¡${allSkills.length} habilidades analizadas!`);
            }
        } else {
            throw new Error('Respuesta inesperada del servidor');
        }

        uploadInProgress = false;

    } catch (error) {
        notificationManager.hideLoading();
        notificationManager.error(error.message || 'Error al subir CV');
        uploadInProgress = false;
    }
}

/**
 * Upload de archivo con progress
 * 
 * Utiliza FormData para enviar:
 * - meta: JSON string con metadatos del estudiante
 * - file: archivo de CV
 */
function uploadFileWithProgress(url, file, metadata, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        // ✅ Usar localStorage directamente sin dependencias condicionales
        const apiKey = localStorage.getItem('api_key') || localStorage.getItem('authToken');

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
                    reject(new Error(error.detail || error.message || 'Upload failed'));
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

        // Preparar FormData con meta como JSON string y file
        const formData = new FormData();
        formData.append('meta', JSON.stringify(metadata));
        formData.append('file', file);

        xhr.open('POST', `${window.API_BASE_URL}${url}`, true);
        if (apiKey) {
            xhr.setRequestHeader('X-API-Key', apiKey);
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

    if (!container || !skills || skills.length === 0) {
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-brain"></i>
                    <p>Sube tu CV para que analicemos tus habilidades</p>
                </div>
            `;
        }
        return;
    }

    let html = '<div class="skills-grid">';

    skills.forEach((skill, index) => {
        // Mostrar solo el texto tal como viene
        const skillName = typeof skill === 'string' ? skill : (skill.name || 'Desconocida');

        html += `
            <div class="skill-item skill-badge">
                <span class="skill-name">${skillName}</span>
                <button class="skill-remove" onclick="removeSkill('${index}')" title="Remover">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

/**
 * Remover habilidad
 */
async function removeSkill(skillId) {
    try {
        // Si es índice numérico (string skills)
        if (!isNaN(skillId)) {
            const index = parseInt(skillId);
            if (currentUser.inferred_skills) {
                currentUser.inferred_skills = currentUser.inferred_skills.filter((_, i) => i !== index);
            }
        } else {
            // Si es ID de objeto
            if (currentUser.inferred_skills) {
                currentUser.inferred_skills = currentUser.inferred_skills.filter(s => 
                    typeof s === 'string' ? true : s.id !== skillId
                );
            }
        }
        
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
