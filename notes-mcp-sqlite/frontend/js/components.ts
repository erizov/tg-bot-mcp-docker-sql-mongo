// UI Components and Utilities
interface ComponentConfig {
    id: string;
    template: string;
    data?: any;
    methods?: Record<string, Function>;
}

interface ToastOptions {
    type: 'success' | 'error' | 'warning' | 'info';
    duration?: number;
    position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

interface ModalOptions {
    title: string;
    content: string;
    buttons?: Array<{
        text: string;
        class: string;
        action: () => void;
    }>;
    closable?: boolean;
}

class UIComponents {
    private static instance: UIComponents;
    private toastContainer: HTMLElement | null = null;
    private modalContainer: HTMLElement | null = null;

    private constructor() {
        this.init();
    }

    public static getInstance(): UIComponents {
        if (!UIComponents.instance) {
            UIComponents.instance = new UIComponents();
        }
        return UIComponents.instance;
    }

    private init(): void {
        this.createToastContainer();
        this.createModalContainer();
        this.setupGlobalStyles();
    }

    private createToastContainer(): void {
        this.toastContainer = document.createElement('div');
        this.toastContainer.id = 'toast-container';
        this.toastContainer.className = 'toast-container';
        document.body.appendChild(this.toastContainer);
    }

    private createModalContainer(): void {
        this.modalContainer = document.createElement('div');
        this.modalContainer.id = 'modal-container';
        this.modalContainer.className = 'modal-container';
        document.body.appendChild(this.modalContainer);
    }

    private setupGlobalStyles(): void {
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
    public showToast(message: string, options: ToastOptions = { type: 'info' }): void {
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

    private removeToast(toast: HTMLElement): void {
        toast.style.transform = 'translateX(100%)';
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    private getToastIcon(type: string): string {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'times-circle';
            case 'warning': return 'exclamation-triangle';
            case 'info': return 'info-circle';
            default: return 'info-circle';
        }
    }

    // Modal System
    public showModal(options: ModalOptions): void {
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
                const button = modal.querySelectorAll('.modal-footer .btn')[index] as HTMLButtonElement;
                if (button) {
                    button.addEventListener('click', btn.action);
                }
            });
        }
    }

    public hideModal(): void {
        if (this.modalContainer) {
            this.modalContainer.classList.remove('active');
        }
    }

    // Loading States
    public showLoading(message: string = 'Loading...'): void {
        const overlay = document.getElementById('loading-overlay');
        if (!overlay) return;

        const spinner = overlay.querySelector('.loading-spinner p');
        if (spinner) {
            spinner.textContent = message;
        }

        overlay.classList.add('active');
    }

    public hideLoading(): void {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }

    // Form Utilities
    public createForm(config: {
        fields: Array<{
            name: string;
            label: string;
            type: string;
            required?: boolean;
            placeholder?: string;
            value?: string;
        }>;
        onSubmit: (data: any) => void;
        submitText?: string;
    }): string {
        const fieldsHtml = config.fields.map(field => `
            <div class="form-group">
                <label for="${field.name}">${field.label}${field.required ? ' *' : ''}</label>
                <input 
                    type="${field.type}" 
                    id="${field.name}" 
                    name="${field.name}" 
                    ${field.required ? 'required' : ''}
                    ${field.placeholder ? `placeholder="${field.placeholder}"` : ''}
                    ${field.value ? `value="${field.value}"` : ''}
                >
            </div>
        `).join('');

        return `
            <form class="form" onsubmit="event.preventDefault(); handleFormSubmit(this)">
                ${fieldsHtml}
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">
                        ${config.submitText || 'Submit'}
                    </button>
                </div>
            </form>
        `;
    }

    // Data Table Component
    public createDataTable(config: {
        headers: string[];
        data: any[][];
        actions?: Array<{
            text: string;
            class: string;
            action: (row: any[]) => void;
        }>;
    }): string {
        const headersHtml = config.headers.map(header => 
            `<th>${header}</th>`
        ).join('');

        const rowsHtml = config.data.map((row, index) => {
            const cellsHtml = row.map(cell => 
                `<td>${this.escapeHtml(String(cell))}</td>`
            ).join('');

            const actionsHtml = config.actions?.map((action, actionIndex) => 
                `<button class="btn btn-sm ${action.class}" onclick="handleTableAction(${index}, ${actionIndex})">
                    ${action.text}
                </button>`
            ).join('') || '';

            return `
                <tr>
                    ${cellsHtml}
                    ${actionsHtml ? `<td class="actions">${actionsHtml}</td>` : ''}
                </tr>
            `;
        }).join('');

        return `
            <div class="data-table">
                <table class="table">
                    <thead>
                        <tr>${headersHtml}${config.actions ? '<th>Actions</th>' : ''}</tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            </div>
        `;
    }

    // Chart Component Wrapper
    public createChartContainer(id: string, title: string): string {
        return `
            <div class="chart-container">
                <h3>${title}</h3>
                <canvas id="${id}" width="400" height="200"></canvas>
            </div>
        `;
    }

    // Status Indicator Component
    public createStatusIndicator(status: 'online' | 'offline' | 'warning' | 'unknown'): string {
        const statusText = {
            online: 'Online',
            offline: 'Offline',
            warning: 'Warning',
            unknown: 'Unknown'
        };

        return `
            <div class="status-indicator" data-status="${status}">
                <span class="status-dot"></span>
                <span class="status-text">${statusText[status]}</span>
            </div>
        `;
    }

    // Progress Bar Component
    public createProgressBar(value: number, max: number = 100, label?: string): string {
        const percentage = Math.min((value / max) * 100, 100);
        const statusClass = percentage >= 80 ? 'success' : percentage >= 50 ? 'warning' : 'error';

        return `
            <div class="progress-container">
                ${label ? `<label class="progress-label">${label}</label>` : ''}
                <div class="progress-bar">
                    <div class="progress-fill ${statusClass}" style="width: ${percentage}%"></div>
                </div>
                <span class="progress-text">${value}/${max}</span>
            </div>
        `;
    }

    // Utility Methods
    private escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    public formatDate(date: Date | string): string {
        const d = new Date(date);
        return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
    }

    public formatBytes(bytes: number): string {
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    public formatDuration(ms: number): string {
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
    public fadeIn(element: HTMLElement, duration: number = 300): void {
        element.style.opacity = '0';
        element.style.transition = `opacity ${duration}ms ease-in-out`;
        
        setTimeout(() => {
            element.style.opacity = '1';
        }, 10);
    }

    public fadeOut(element: HTMLElement, duration: number = 300): Promise<void> {
        return new Promise((resolve) => {
            element.style.transition = `opacity ${duration}ms ease-in-out`;
            element.style.opacity = '0';
            
            setTimeout(() => {
                resolve();
            }, duration);
        });
    }

    // Validation Utilities
    public validateEmail(email: string): boolean {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    public validateRequired(value: any): boolean {
        return value !== null && value !== undefined && value !== '';
    }

    public validateMinLength(value: string, minLength: number): boolean {
        return value.length >= minLength;
    }

    public validateMaxLength(value: string, maxLength: number): boolean {
        return value.length <= maxLength;
    }
}

// Create global instance
const ui = UIComponents.getInstance();

// Export for use in other modules
(window as any).ui = ui;

// Global utility functions
(window as any).showToast = (message: string, type: ToastOptions['type'] = 'info') => {
    ui.showToast(message, { type });
};

(window as any).showModal = (options: ModalOptions) => {
    ui.showModal(options);
};

(window as any).hideModal = () => {
    ui.hideModal();
};

(window as any).showLoading = (message?: string) => {
    ui.showLoading(message);
};

(window as any).hideLoading = () => {
    ui.hideLoading();
};
