// API Utility Functions
interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}

interface DatabaseHealth {
    status: 'healthy' | 'unhealthy';
    notes: number;
    uptime?: number;
    lastCheck: string;
}

interface SearchParams {
    query: string;
    database: string;
    filters?: {
        title?: boolean;
        content?: boolean;
        reminders?: boolean;
    };
}

interface NoteData {
    id: string;
    title: string;
    content: string;
    due_at?: string;
    created_at: string;
    updated_at?: string;
}

class ApiClient {
    private baseUrl: string;
    private timeout: number;

    constructor(baseUrl: string = 'http://localhost:8001', timeout: number = 10000) {
        this.baseUrl = baseUrl;
        this.timeout = timeout;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<ApiResponse<T>> {
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
    async getDatabaseHealth(database: string): Promise<ApiResponse<DatabaseHealth>> {
        return this.request<DatabaseHealth>(`/health?db=${database}`);
    }

    async getAllDatabaseHealth(): Promise<ApiResponse<Record<string, DatabaseHealth>>> {
        return this.request<Record<string, DatabaseHealth>>('/health/all');
    }

    // Search Methods
    async searchNotes(params: SearchParams): Promise<ApiResponse<NoteData[]>> {
        const searchParams = new URLSearchParams({
            q: params.query,
            db: params.database,
        });

        if (params.filters) {
            if (params.filters.title) searchParams.append('title', 'true');
            if (params.filters.content) searchParams.append('content', 'true');
            if (params.filters.reminders) searchParams.append('reminders', 'true');
        }

        return this.request<NoteData[]>(`/search?${searchParams.toString()}`);
    }

    // Note Management Methods
    async getNote(id: string, database: string): Promise<ApiResponse<NoteData>> {
        return this.request<NoteData>(`/notes/${id}?db=${database}`);
    }

    async createNote(note: Omit<NoteData, 'id' | 'created_at'>, database: string): Promise<ApiResponse<NoteData>> {
        return this.request<NoteData>(`/notes?db=${database}`, {
            method: 'POST',
            body: JSON.stringify(note),
        });
    }

    async updateNote(id: string, updates: Partial<NoteData>, database: string): Promise<ApiResponse<NoteData>> {
        return this.request<NoteData>(`/notes/${id}?db=${database}`, {
            method: 'PUT',
            body: JSON.stringify(updates),
        });
    }

    async deleteNote(id: string, database: string): Promise<ApiResponse<void>> {
        return this.request<void>(`/notes/${id}?db=${database}`, {
            method: 'DELETE',
        });
    }

    // Statistics Methods
    async getDatabaseStats(database: string): Promise<ApiResponse<any>> {
        return this.request(`/stats?db=${database}`);
    }

    async getAllDatabaseStats(): Promise<ApiResponse<Record<string, any>>> {
        return this.request('/stats/all');
    }

    // Report Methods
    async generatePerformanceReport(): Promise<ApiResponse<string>> {
        return this.request<string>('/report');
    }

    async getPerformanceReport(): Promise<ApiResponse<any>> {
        return this.request('/report/data');
    }

    // Monitoring Methods
    async getSystemMetrics(): Promise<ApiResponse<any>> {
        return this.request('/metrics');
    }

    async getActivityLog(limit: number = 50): Promise<ApiResponse<any[]>> {
        return this.request(`/activity?limit=${limit}`);
    }

    // Database Management Methods
    async switchDatabase(database: string): Promise<ApiResponse<void>> {
        return this.request<void>('/switch-db', {
            method: 'POST',
            body: JSON.stringify({ database }),
        });
    }

    async getAvailableDatabases(): Promise<ApiResponse<string[]>> {
        return this.request<string[]>('/databases');
    }

    // Backup and Restore Methods
    async createBackup(database: string): Promise<ApiResponse<string>> {
        return this.request<string>(`/backup?db=${database}`, {
            method: 'POST',
        });
    }

    async restoreBackup(database: string, backupData: any): Promise<ApiResponse<void>> {
        return this.request<void>(`/restore?db=${database}`, {
            method: 'POST',
            body: JSON.stringify(backupData),
        });
    }

    // Utility Methods
    async ping(): Promise<ApiResponse<{ timestamp: string; version: string }>> {
        return this.request<{ timestamp: string; version: string }>('/ping');
    }

    async getVersion(): Promise<ApiResponse<{ version: string; build: string }>> {
        return this.request<{ version: string; build: string }>('/version');
    }

    // Error Handling Utilities
    handleApiError(error: ApiResponse<any>): string {
        if (error.error) {
            return error.error;
        }
        if (error.message) {
            return error.message;
        }
        return 'An unknown error occurred';
    }

    isApiError(response: ApiResponse<any>): boolean {
        return !response.success;
    }

    // Connection Testing
    async testConnection(): Promise<boolean> {
        try {
            const response = await this.ping();
            return response.success;
        } catch {
            return false;
        }
    }

    // Batch Operations
    async batchOperation<T>(
        operations: Array<() => Promise<ApiResponse<T>>>
    ): Promise<ApiResponse<T[]>> {
        try {
            const results = await Promise.allSettled(
                operations.map(op => op())
            );

            const successfulResults: T[] = [];
            const errors: string[] = [];

            results.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    if (result.value.success && result.value.data) {
                        successfulResults.push(result.value.data);
                    } else {
                        errors.push(`Operation ${index + 1}: ${result.value.error || 'Unknown error'}`);
                    }
                } else {
                    errors.push(`Operation ${index + 1}: ${result.reason}`);
                }
            });

            if (errors.length > 0) {
                return {
                    success: false,
                    error: `Batch operation completed with errors: ${errors.join(', ')}`,
                    data: successfulResults,
                };
            }

            return {
                success: true,
                data: successfulResults,
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }
}

// Create a singleton instance
const apiClient = new ApiClient();

// Export for use in other modules
(window as any).apiClient = apiClient;

// Utility functions for common operations
export const DatabaseAPI = {
    async getHealth(database: string): Promise<DatabaseHealth | null> {
        const response = await apiClient.getDatabaseHealth(database);
        return response.success ? response.data || null : null;
    },

    async getAllHealth(): Promise<Record<string, DatabaseHealth> | null> {
        const response = await apiClient.getAllDatabaseHealth();
        return response.success ? response.data || null : null;
    },

    async search(params: SearchParams): Promise<NoteData[]> {
        const response = await apiClient.searchNotes(params);
        return response.success ? response.data || [] : [];
    },

    async getStats(database: string): Promise<any> {
        const response = await apiClient.getDatabaseStats(database);
        return response.success ? response.data : null;
    },

    async generateReport(): Promise<string | null> {
        const response = await apiClient.generatePerformanceReport();
        return response.success ? response.data || null : null;
    },

    async testConnection(): Promise<boolean> {
        return await apiClient.testConnection();
    }
};

// Error handling decorator
export function withErrorHandling<T extends any[], R>(
    fn: (...args: T) => Promise<R>,
    errorMessage: string = 'Operation failed'
): (...args: T) => Promise<R | null> {
    return async (...args: T): Promise<R | null> => {
        try {
            return await fn(...args);
        } catch (error) {
            console.error(errorMessage, error);
            return null;
        }
    };
}

// Retry utility
export async function withRetry<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    delay: number = 1000
): Promise<T> {
    let lastError: Error;
    
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await operation();
        } catch (error) {
            lastError = error as Error;
            if (i < maxRetries - 1) {
                await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
            }
        }
    }
    
    throw lastError!;
}
