// API Utility Functions (JavaScript version)
class ApiClient {
    constructor(baseUrl = 'http://localhost:8001', timeout = 10000) {
        this.baseUrl = baseUrl;
        this.timeout = timeout;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const controller = new AbortController();
        
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return {
                success: true,
                data,
            };
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    return {
                        success: false,
                        error: 'Request timeout',
                    };
                }
                return {
                    success: false,
                    error: error.message,
                };
            }
            
            return {
                success: false,
                error: 'Unknown error occurred',
            };
        }
    }

    // Database Health Methods
    async getDatabaseHealth(database) {
        return this.request(`/health?db=${database}`);
    }

    async getAllDatabaseHealth() {
        return this.request('/health/all');
    }

    // Search Methods
    async searchNotes(params) {
        const searchParams = new URLSearchParams({
            q: params.query,
            db: params.database,
        });

        if (params.filters) {
            if (params.filters.title) searchParams.append('title', 'true');
            if (params.filters.content) searchParams.append('content', 'true');
            if (params.filters.reminders) searchParams.append('reminders', 'true');
        }

        return this.request(`/search?${searchParams.toString()}`);
    }

    // Note Management Methods
    async getNote(id, database) {
        return this.request(`/notes/${id}?db=${database}`);
    }

    async createNote(note, database) {
        return this.request(`/notes?db=${database}`, {
            method: 'POST',
            body: JSON.stringify(note),
        });
    }

    async updateNote(id, updates, database) {
        return this.request(`/notes/${id}?db=${database}`, {
            method: 'PUT',
            body: JSON.stringify(updates),
        });
    }

    async deleteNote(id, database) {
        return this.request(`/notes/${id}?db=${database}`, {
            method: 'DELETE',
        });
    }

    // Statistics Methods
    async getDatabaseStats(database) {
        return this.request(`/stats?db=${database}`);
    }

    async getAllDatabaseStats() {
        return this.request('/stats/all');
    }

    // Report Methods
    async generatePerformanceReport() {
        return this.request('/report');
    }

    async getPerformanceReport() {
        return this.request('/report/data');
    }

    // Monitoring Methods
    async getSystemMetrics() {
        return this.request('/metrics');
    }

    async getActivityLog(limit = 50) {
        return this.request(`/activity?limit=${limit}`);
    }

    // Database Management Methods
    async switchDatabase(database) {
        return this.request('/switch-db', {
            method: 'POST',
            body: JSON.stringify({ database }),
        });
    }

    async getAvailableDatabases() {
        return this.request('/databases');
    }

    // Utility Methods
    async ping() {
        return this.request('/ping');
    }

    async getVersion() {
        return this.request('/version');
    }

    // Error Handling Utilities
    handleApiError(error) {
        if (error.error) {
            return error.error;
        }
        if (error.message) {
            return error.message;
        }
        return 'An unknown error occurred';
    }

    isApiError(response) {
        return !response.success;
    }

    // Connection Testing
    async testConnection() {
        try {
            const response = await this.ping();
            return response.success;
        } catch {
            return false;
        }
    }
}

// Create a singleton instance
const apiClient = new ApiClient();

// Export for use in other modules
window.apiClient = apiClient;

// Utility functions for common operations
const DatabaseAPI = {
    async getHealth(database) {
        const response = await apiClient.getDatabaseHealth(database);
        return response.success ? response.data || null : null;
    },

    async getAllHealth() {
        const response = await apiClient.getAllDatabaseHealth();
        return response.success ? response.data || null : null;
    },

    async search(params) {
        const response = await apiClient.searchNotes(params);
        return response.success ? response.data || [] : [];
    },

    async getStats(database) {
        const response = await apiClient.getDatabaseStats(database);
        return response.success ? response.data : null;
    },

    async generateReport() {
        const response = await apiClient.generatePerformanceReport();
        return response.success ? response.data || null : null;
    },

    async testConnection() {
        return await apiClient.testConnection();
    }
};

// Export for global use
window.DatabaseAPI = DatabaseAPI;
