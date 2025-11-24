/**
 * SaaS Demo Modal - Interceptor para Rate Limiting
 * Muestra un modal de suscripción cuando se excede el límite de la API (429)
 */

class SaaSDemoModal {
    constructor() {
        this.modalId = 'saas-demo-limit-modal';
        this.injectModal();
        this.setupListeners();
    }

    injectModal() {
        if (document.getElementById(this.modalId)) return;

        const modalHtml = `
            <div id="${this.modalId}" class="modal" style="display: none; z-index: 10000;">
                <div class="modal-content" style="max-width: 500px; text-align: center; border-radius: 15px; padding: 40px;">
                    <span class="close-modal" style="position: absolute; right: 20px; top: 15px; font-size: 24px; cursor: pointer;">&times;</span>
                    
                    <div style="margin-bottom: 20px;">
                        <i class="fas fa-rocket" style="font-size: 48px; color: #730f33;"></i>
                    </div>
                    
                    <h2 style="color: #333; margin-bottom: 15px;">¡Has alcanzado el límite!</h2>
                    
                    <p style="color: #666; margin-bottom: 25px; line-height: 1.6;">
                        Estás disfrutando de la versión gratuita de MoirAI. 
                        Para continuar realizando búsquedas ilimitadas y acceder a funciones premium, 
                        considera actualizar tu plan.
                    </p>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 25px; text-align: left;">
                        <h4 style="margin-bottom: 10px; color: #333;">Plan Premium incluye:</h4>
                        <ul style="list-style: none; padding: 0; margin: 0; color: #555;">
                            <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: #28a745; margin-right: 8px;"></i> Búsquedas ilimitadas</li>
                            <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: #28a745; margin-right: 8px;"></i> Prioridad en matching</li>
                            <li style="margin-bottom: 8px;"><i class="fas fa-check" style="color: #28a745; margin-right: 8px;"></i> Contacto directo</li>
                        </ul>
                    </div>
                    
                    <button class="btn btn-primary btn-lg" style="width: 100%; margin-bottom: 10px;" onclick="window.location.href='/#contact'">
                        Contactar Ventas
                    </button>
                    
                    <button class="btn btn-outline" style="width: 100%; border: none; color: #666;" onclick="document.getElementById('${this.modalId}').style.display='none'">
                        Quizás más tarde
                    </button>
                </div>
            </div>
        `;

        const div = document.createElement('div');
        div.innerHTML = modalHtml;
        document.body.appendChild(div.firstElementChild);
    }

    setupListeners() {
        // Escuchar evento de rate limit
        window.addEventListener('rate-limit-exceeded', (event) => {
            console.warn('Rate limit exceeded:', event.detail);
            this.show();
        });

        // Cerrar modal
        const modal = document.getElementById(this.modalId);
        if (modal) {
            const closeBtn = modal.querySelector('.close-modal');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.hide());
            }
            
            // Cerrar al hacer click fuera
            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hide();
                }
            });
        }
    }

    show() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.style.display = 'flex';
            // Asegurar que se vea sobre otros modales
            modal.style.zIndex = '10001'; 
        }
    }

    hide() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.saasDemoModal = new SaaSDemoModal();
});
