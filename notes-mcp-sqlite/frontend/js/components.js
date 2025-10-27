// UI Components and Utilities (JavaScript version)
class UIComponents {
    constructor() {
        this.toastContainer = null;
        this.modalContainer = null;
        this.init();
    }

    init() {
        this.createToastContainer();
        this.createModalContainer();
        this.setupGlobalStyles();
    }

    createToastContainer() {
        this.toastContainer = document.createElement('div');
        this.toastContainer.id = 'toast-container';
        this.toastContainer.className = 'toast-container';
        document.body.appendChild(this.toastContainer);
    }

    createModalContainer() {
        this.modalContainer = document.createElement('div');
        this.modalContainer.id = 'modal-container';
        this.modalContainer.className = 'modal-container';
        document.body.appendChild(this.modalContainer);
    }

    setupGlobalStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .modal-container {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: none;
                align-items: center;
                justify-content: center;
                z-index: 2000;
            }
            
            .modal-container.active {
                display: flex;
            }
            
            .modal {
                background: var(--surface-color);
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-lg);
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }
            
            .modal-header {
                padding: 1.5rem 1.5rem 1rem;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-title {
                font-size: 1.2rem;
                font-weight: 600;
                color: var(--text-primary);
                margin: 0;
            }
            
            .modal-close {
                background: none;
                border: none;
                font-size: 1.5rem;
                color: var(--text-secondary);
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .modal-body {
                padding: 1.5rem;
            }
            
            .modal-footer {
                padding: 1rem 1.5rem 1.5rem;
                border-top: 1px solid var(--border-color);
                display: flex;
                gap: 1rem;
                justify-content: flex-end;
            }
        `;
        document.head.appendChild(style);
    }

    // Toast Notification System
    showToast(message, options = { type: 'info' }) {
        if (!this.toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast ${options.type}`;
        
        const icon = this.getToastIcon(options.type);
        toast.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${this.escapeHtml(message)}</span>
        `;

        this.toastContainer.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
            toast.style.opacity = '1';
        }, 10);

        // Auto remove
        const duration = options.duration || 5000;
        setTimeout(() => {
            this.removeToast(toast);
        }, duration);
    }

    removeToast(toast) {
        toast.style.transform = 'translateX(100%)';
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    getToastIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'times-circle';
            case 'warning': return 'exclamation-triangle';
            case 'info': return 'info-circle';
            default: return 'info-circle';
        }
    }

    // Modal System
    showModal(options) {
        if (!this.modalContainer) return;

        const modal = document.createElement('div');
        modal.className = 'modal';
        
        const buttonsHtml = options.buttons?.map(btn => 
            `<button class="btn ${btn.class}" onclick="this.action()">${btn.text}</button>`
        ).join('') || '';

        modal.innerHTML = `
            <div class="modal-header">
                <h3 class="modal-title">${this.escapeHtml(options.title)}</h3>
                ${options.closable !== false ? '<button class="modal-close">&times;</button>' : ''}
            </div>
            <div class="modal-body">
                ${options.content}
            </div>
            ${buttonsHtml ? `<div class="modal-footer">${buttonsHtml}</div>` : ''}
        `;

        // Add event listeners
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideModal());
        }

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideModal();
            }
        });

        this.modalContainer.innerHTML = '';
        this.modalContainer.appendChild(modal);
        this.modalContainer.classList.add('active');

        // Store button actions
        if (options.buttons) {
            options.buttons.forEach((btn, index) => {
                const button = modal.querySelectorAll('.modal-footer .btn')[index];
                if (button) {
                    button.addEventListener('click', btn.action);
                }
            });
        }
    }

    hideModal() {
        if (this.modalContainer) {
            this.modalContainer.classList.remove('active');
        }
    }

    // Loading States
    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        if (!overlay) return;

        const spinner = overlay.querySelector('.loading-spinner p');
        if (spinner) {
            spinner.textContent = message;
        }

        overlay.classList.add('active');
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

    // Utility Methods
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(date) {
        const d = new Date(date);
        return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
    }

    formatBytes(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }

    // Animation Utilities
    fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.transition = `opacity ${duration}ms ease-in-out`;
        
        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    }

    fadeOut(element, duration = 300) {
        return new Promise((resolve) => {
            element.style.transition = `opacity ${duration}ms ease-in-out`;
            element.style.opacity = '0';
            
            setTimeout(() => {
                resolve();
            }, duration);
        });
    }

    // Validation Utilities
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    validateRequired(value) {
        return value !== null && value !== undefined && value !== '';
    }

    validateMinLength(value, minLength) {
        return value.length >= minLength;
    }

    validateMaxLength(value, maxLength) {
        return value.length <= maxLength;
    }
}

// Create global instance
const ui = new UIComponents();

// Export for use in other modules
window.ui = ui;

// Global utility functions
window.showToast = (message, type = 'info') => {
    ui.showToast(message, { type });
};

window.showModal = (options) => {
    ui.showModal(options);
};

window.hideModal = () => {
    ui.hideModal();
};

window.showLoading = (message) => {
    ui.showLoading(message);
};

window.hideLoading = () => {
    ui.hideLoading();
};
