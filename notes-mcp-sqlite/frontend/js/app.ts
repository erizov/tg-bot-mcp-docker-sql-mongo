// Main Application TypeScript File
interface DatabaseStatus {
    name: string;
    status: 'online' | 'offline' | 'warning' | 'unknown';
    notes: number;
    lastChecked: Date;
}

interface SearchResult {
    id: string;
    title: string;
    content: string;
    due_at?: string;
    created_at: string;
    database: string;
}

interface PerformanceMetric {
    database: string;
    insertTime: number;
    lookupTime: number;
    totalNotes: number;
}

interface HealthMetric {
    name: string;
    value: string | number;
    status: 'success' | 'warning' | 'error';
    trend?: 'up' | 'down' | 'stable';
}

interface ActivityItem {
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    title: string;
    description: string;
    timestamp: Date;
}

class NotesBotDashboard {
    private currentTab: string = 'dashboard';
    private monitoringInterval: number | null = null;
    private refreshRate: number = 5000;
    private performanceChart: Chart | null = null;
    private databases: DatabaseStatus[] = [];
    private apiBaseUrl: string = 'http://localhost:8001';

    constructor() {
        this.init();
    }

    private init(): void {
        this.setupEventListeners();
        this.loadDashboard();
        this.checkDatabaseStatuses();
    }

    private setupEventListeners(): void {
        // Tab navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target as HTMLElement;
                const tab = target.closest('.nav-btn')?.getAttribute('data-tab');
                if (tab) {
                    this.switchTab(tab);
                }
            });
        });

        // Search functionality
        const searchBtn = document.getElementById('search-btn');
        const searchInput = document.getElementById('search-query') as HTMLInputElement;
        
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.performSearch());
        }
        
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }

        // Report generation
        const generateReportBtn = document.getElementById('generate-report');
        if (generateReportBtn) {
            generateReportBtn.addEventListener('click', () => this.generateReport());
        }

        // Monitoring controls
        const startMonitoringBtn = document.getElementById('start-monitoring');
        const stopMonitoringBtn = document.getElementById('stop-monitoring');
        const refreshRateSelect = document.getElementById('refresh-rate') as HTMLSelectElement;

        if (startMonitoringBtn) {
            startMonitoringBtn.addEventListener('click', () => this.startMonitoring());
        }

        if (stopMonitoringBtn) {
            stopMonitoringBtn.addEventListener('click', () => this.stopMonitoring());
        }

        if (refreshRateSelect) {
            refreshRateSelect.addEventListener('change', (e) => {
                this.refreshRate = parseInt((e.target as HTMLSelectElement).value);
                if (this.monitoringInterval) {
                    this.stopMonitoring();
                    this.startMonitoring();
                }
            });
        }
    }

    private switchTab(tabName: string): void {
        // Update active tab button
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName)?.classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific content
        switch (tabName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'search':
                this.loadSearch();
                break;
            case 'reports':
                this.loadReports();
                break;
            case 'monitoring':
                this.loadMonitoring();
                break;
        }
    }

    private async loadDashboard(): Promise<void> {
        this.showLoading();
        try {
            await this.checkDatabaseStatuses();
            this.updateStatusCards();
            this.loadPerformanceChart();
        } catch (error) {
            this.showToast('Failed to load dashboard', 'error');
        } finally {
            this.hideLoading();
        }
    }

    private async checkDatabaseStatuses(): Promise<void> {
        const databases = ['sqlite', 'mongo', 'neo4j', 'postgresql', 'cassandra', 'progress'];
        
        for (const db of databases) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/health?db=${db}`);
                const data = await response.json();
                
                this.databases.push({
                    name: db,
                    status: data.status === 'healthy' ? 'online' : 'offline',
                    notes: data.notes || 0,
                    lastChecked: new Date()
                });
            } catch (error) {
                this.databases.push({
                    name: db,
                    status: 'offline',
                    notes: 0,
                    lastChecked: new Date()
                });
            }
        }
    }

    private updateStatusCards(): void {
        this.databases.forEach(db => {
            const card = document.getElementById(`${db.name}-status`);
            if (!card) return;

            const statusIndicator = card.querySelector('.status-indicator');
            const notesElement = card.querySelector('.stat-value');

            if (statusIndicator) {
                statusIndicator.setAttribute('data-status', db.status);
                const statusText = statusIndicator.querySelector('.status-text');
                if (statusText) {
                    statusText.textContent = this.getStatusText(db.status);
                }
            }

            if (notesElement) {
                notesElement.textContent = db.notes.toString();
            }
        });
    }

    private getStatusText(status: string): string {
        switch (status) {
            case 'online': return 'Online';
            case 'offline': return 'Offline';
            case 'warning': return 'Warning';
            default: return 'Unknown';
        }
    }

    private loadPerformanceChart(): void {
        const ctx = document.getElementById('performanceChart') as HTMLCanvasElement;
        if (!ctx) return;

        // Sample performance data
        const performanceData: PerformanceMetric[] = [
            { database: 'SQLite', insertTime: 0.001, lookupTime: 0.0005, totalNotes: 150 },
            { database: 'MongoDB', insertTime: 0.002, lookupTime: 0.001, totalNotes: 200 },
            { database: 'Neo4j', insertTime: 0.003, lookupTime: 0.002, totalNotes: 75 },
            { database: 'PostgreSQL', insertTime: 0.0015, lookupTime: 0.0008, totalNotes: 180 },
            { database: 'Cassandra', insertTime: 0.0025, lookupTime: 0.0015, totalNotes: 120 },
            { database: 'Progress', insertTime: 0.0005, lookupTime: 0.0003, totalNotes: 50 }
        ];

        this.performanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: performanceData.map(d => d.database),
                datasets: [
                    {
                        label: 'Insert Time (ms)',
                        data: performanceData.map(d => d.insertTime * 1000),
                        backgroundColor: 'rgba(37, 99, 235, 0.8)',
                        borderColor: 'rgba(37, 99, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Lookup Time (ms)',
                        data: performanceData.map(d => d.lookupTime * 1000),
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderColor: 'rgba(16, 185, 129, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Time (milliseconds)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Database Performance Comparison'
                    },
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    private async performSearch(): Promise<void> {
        const query = (document.getElementById('search-query') as HTMLInputElement).value.trim();
        const database = (document.getElementById('search-db') as HTMLSelectElement).value;
        
        if (!query) {
            this.showToast('Please enter a search term', 'warning');
            return;
        }

        this.showLoading();
        try {
            const response = await fetch(`${this.apiBaseUrl}/search?q=${encodeURIComponent(query)}&db=${database}`);
            const results: SearchResult[] = await response.json();
            
            this.displaySearchResults(results);
        } catch (error) {
            this.showToast('Search failed', 'error');
            this.displaySearchResults([]);
        } finally {
            this.hideLoading();
        }
    }

    private displaySearchResults(results: SearchResult[]): void {
        const container = document.getElementById('search-results');
        if (!container) return;

        if (results.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <p>No results found</p>
                </div>
            `;
            return;
        }

        container.innerHTML = results.map(result => `
            <div class="search-result-item">
                <div class="search-result-header">
                    <h3 class="search-result-title">${this.escapeHtml(result.title)}</h3>
                    <div class="search-result-meta">
                        <span>${result.database}</span>
                        <span>${new Date(result.created_at).toLocaleDateString()}</span>
                    </div>
                </div>
                <div class="search-result-content">${this.escapeHtml(result.content)}</div>
                ${result.due_at ? `<div class="search-result-meta">Due: ${new Date(result.due_at).toLocaleString()}</div>` : ''}
                <div class="search-result-actions">
                    <button class="btn btn-primary" onclick="dashboard.viewNote('${result.id}', '${result.database}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-secondary" onclick="dashboard.editNote('${result.id}', '${result.database}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
            </div>
        `).join('');
    }

    private async generateReport(): Promise<void> {
        this.showLoading();
        try {
            const response = await fetch(`${this.apiBaseUrl}/report`);
            const reportHtml = await response.text();
            
            document.getElementById('report-content')!.innerHTML = reportHtml;
            document.getElementById('export-report')!.disabled = false;
            
            this.showToast('Report generated successfully', 'success');
        } catch (error) {
            this.showToast('Failed to generate report', 'error');
        } finally {
            this.hideLoading();
        }
    }

    private startMonitoring(): Promise<void> {
        this.monitoringInterval = window.setInterval(() => {
            this.updateMonitoringData();
        }, this.refreshRate);

        document.getElementById('start-monitoring')!.disabled = true;
        document.getElementById('stop-monitoring')!.disabled = false;
        
        this.showToast('Monitoring started', 'success');
        return Promise.resolve();
    }

    private stopMonitoring(): void {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }

        document.getElementById('start-monitoring')!.disabled = false;
        document.getElementById('stop-monitoring')!.disabled = true;
        
        this.showToast('Monitoring stopped', 'info');
    }

    private async updateMonitoringData(): Promise<void> {
        try {
            await this.checkDatabaseStatuses();
            this.updateHealthMetrics();
            this.updatePerformanceMetrics();
            this.updateActivityLog();
        } catch (error) {
            console.error('Failed to update monitoring data:', error);
        }
    }

    private updateHealthMetrics(): void {
        const container = document.getElementById('health-metrics');
        if (!container) return;

        const metrics: HealthMetric[] = this.databases.map(db => ({
            name: db.name.toUpperCase(),
            value: db.status === 'online' ? 'Healthy' : 'Unhealthy',
            status: db.status === 'online' ? 'success' : 'error'
        }));

        container.innerHTML = metrics.map(metric => `
            <div class="health-metric">
                <span class="health-metric-label">${metric.name}</span>
                <span class="health-metric-value ${metric.status}">${metric.value}</span>
            </div>
        `).join('');
    }

    private updatePerformanceMetrics(): void {
        const container = document.getElementById('performance-metrics');
        if (!container) return;

        const metrics: HealthMetric[] = this.databases.map(db => ({
            name: `${db.name} Notes`,
            value: db.notes,
            status: db.notes > 100 ? 'success' : db.notes > 50 ? 'warning' : 'error',
            trend: 'stable'
        }));

        container.innerHTML = metrics.map(metric => `
            <div class="performance-metric">
                <span class="performance-metric-label">${metric.name}</span>
                <span class="performance-metric-value">
                    ${metric.value}
                    ${metric.trend ? `<span class="performance-metric-trend ${metric.trend}">→</span>` : ''}
                </span>
            </div>
        `).join('');
    }

    private updateActivityLog(): void {
        const container = document.getElementById('activity-log');
        if (!container) return;

        const activities: ActivityItem[] = [
            {
                id: '1',
                type: 'info',
                title: 'Database Status Check',
                description: 'All databases checked successfully',
                timestamp: new Date()
            },
            {
                id: '2',
                type: 'success',
                title: 'Performance Report Generated',
                description: 'Latest performance metrics updated',
                timestamp: new Date(Date.now() - 30000)
            }
        ];

        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${activity.type}">
                    <i class="fas fa-${this.getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <h4 class="activity-title">${activity.title}</h4>
                    <p class="activity-description">${activity.description}</p>
                </div>
                <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
            </div>
        `).join('');
    }

    private getActivityIcon(type: string): string {
        switch (type) {
            case 'info': return 'info-circle';
            case 'success': return 'check-circle';
            case 'warning': return 'exclamation-triangle';
            case 'error': return 'times-circle';
            default: return 'info-circle';
        }
    }

    private formatTime(date: Date): string {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        return date.toLocaleDateString();
    }

    private loadSearch(): void {
        // Initialize search tab
        console.log('Loading search tab');
    }

    private loadReports(): void {
        // Initialize reports tab
        console.log('Loading reports tab');
    }

    private loadMonitoring(): void {
        // Initialize monitoring tab
        console.log('Loading monitoring tab');
    }

    private showLoading(): void {
        document.getElementById('loading-overlay')?.classList.add('active');
    }

    private hideLoading(): void {
        document.getElementById('loading-overlay')?.classList.remove('active');
    }

    private showToast(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info'): void {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas fa-${this.getToastIcon(type)}"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
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

    private escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Public methods for button callbacks
    public viewNote(id: string, database: string): void {
        this.showToast(`Viewing note ${id} from ${database}`, 'info');
    }

    public editNote(id: string, database: string): void {
        this.showToast(`Editing note ${id} from ${database}`, 'info');
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    (window as any).dashboard = new NotesBotDashboard();
});
