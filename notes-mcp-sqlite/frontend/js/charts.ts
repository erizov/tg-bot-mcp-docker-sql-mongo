// Chart Utilities and Components
interface ChartConfig {
    type: 'line' | 'bar' | 'pie' | 'doughnut' | 'radar' | 'polarArea';
    data: any;
    options?: any;
    responsive?: boolean;
    maintainAspectRatio?: boolean;
}

interface PerformanceData {
    database: string;
    insertTime: number;
    lookupTime: number;
    totalNotes: number;
    memoryUsage?: number;
    cpuUsage?: number;
}

interface TimeSeriesData {
    timestamp: string;
    value: number;
    label?: string;
}

class ChartManager {
    private charts: Map<string, Chart> = new Map();
    private defaultColors: string[] = [
        '#3B82F6', // Blue
        '#10B981', // Green
        '#F59E0B', // Yellow
        '#EF4444', // Red
        '#8B5CF6', // Purple
        '#06B6D4', // Cyan
        '#84CC16', // Lime
        '#F97316', // Orange
    ];

    constructor() {
        this.setupChartDefaults();
    }

    private setupChartDefaults(): void {
        // Set Chart.js defaults
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            Chart.defaults.font.size = 12;
            Chart.defaults.color = '#64748b';
            Chart.defaults.plugins.legend.labels.usePointStyle = true;
            Chart.defaults.plugins.legend.labels.padding = 20;
        }
    }

    // Create a new chart
    public createChart(
        canvasId: string,
        config: ChartConfig
    ): Chart | null {
        const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!canvas) {
            console.error(`Canvas element with id '${canvasId}' not found`);
            return null;
        }

        // Destroy existing chart if it exists
        if (this.charts.has(canvasId)) {
            this.destroyChart(canvasId);
        }

        const chartConfig = {
            type: config.type,
            data: config.data,
            options: {
                responsive: config.responsive !== false,
                maintainAspectRatio: config.maintainAspectRatio !== false,
                plugins: {
                    legend: {
                        position: 'top' as const,
                    },
                    tooltip: {
                        mode: 'index' as const,
                        intersect: false,
                    },
                },
                scales: config.type !== 'pie' && config.type !== 'doughnut' ? {
                    x: {
                        display: true,
                        grid: {
                            display: false,
                        },
                    },
                    y: {
                        display: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                        },
                    },
                } : undefined,
                ...config.options,
            },
        };

        try {
            const chart = new Chart(canvas, chartConfig);
            this.charts.set(canvasId, chart);
            return chart;
        } catch (error) {
            console.error('Failed to create chart:', error);
            return null;
        }
    }

    // Destroy a chart
    public destroyChart(canvasId: string): void {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }

    // Update chart data
    public updateChart(canvasId: string, newData: any): void {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    // Performance Comparison Chart
    public createPerformanceChart(canvasId: string, data: PerformanceData[]): Chart | null {
        const chartData = {
            labels: data.map(d => d.database),
            datasets: [
                {
                    label: 'Insert Time (ms)',
                    data: data.map(d => d.insertTime * 1000),
                    backgroundColor: this.defaultColors[0] + '80',
                    borderColor: this.defaultColors[0],
                    borderWidth: 2,
                    yAxisID: 'y',
                },
                {
                    label: 'Lookup Time (ms)',
                    data: data.map(d => d.lookupTime * 1000),
                    backgroundColor: this.defaultColors[1] + '80',
                    borderColor: this.defaultColors[1],
                    borderWidth: 2,
                    yAxisID: 'y',
                },
                {
                    label: 'Total Notes',
                    data: data.map(d => d.totalNotes),
                    backgroundColor: this.defaultColors[2] + '80',
                    borderColor: this.defaultColors[2],
                    borderWidth: 2,
                    yAxisID: 'y1',
                },
            ],
        };

        const options = {
            scales: {
                y: {
                    type: 'linear' as const,
                    display: true,
                    position: 'left' as const,
                    title: {
                        display: true,
                        text: 'Time (ms)',
                    },
                },
                y1: {
                    type: 'linear' as const,
                    display: true,
                    position: 'right' as const,
                    title: {
                        display: true,
                        text: 'Notes Count',
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Database Performance Comparison',
                },
            },
        };

        return this.createChart(canvasId, {
            type: 'bar',
            data: chartData,
            options,
        });
    }

    // Time Series Chart
    public createTimeSeriesChart(
        canvasId: string,
        datasets: Array<{
            label: string;
            data: TimeSeriesData[];
            color?: string;
        }>
    ): Chart | null {
        const chartData = {
            labels: datasets[0]?.data.map(d => new Date(d.timestamp).toLocaleTimeString()) || [],
            datasets: datasets.map((dataset, index) => ({
                label: dataset.label,
                data: dataset.data.map(d => d.value),
                backgroundColor: (dataset.color || this.defaultColors[index]) + '20',
                borderColor: dataset.color || this.defaultColors[index],
                borderWidth: 2,
                fill: false,
                tension: 0.1,
            })),
        };

        const options = {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time',
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: 'Value',
                    },
                },
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Time Series Data',
                },
            },
        };

        return this.createChart(canvasId, {
            type: 'line',
            data: chartData,
            options,
        });
    }

    // Pie Chart for Database Distribution
    public createDistributionChart(canvasId: string, data: Array<{ label: string; value: number }>): Chart | null {
        const chartData = {
            labels: data.map(d => d.label),
            datasets: [{
                data: data.map(d => d.value),
                backgroundColor: this.defaultColors.slice(0, data.length),
                borderColor: this.defaultColors.slice(0, data.length),
                borderWidth: 2,
            }],
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'Database Distribution',
                },
                legend: {
                    position: 'bottom' as const,
                },
            },
        };

        return this.createChart(canvasId, {
            type: 'pie',
            data: chartData,
            options,
        });
    }

    // Memory Usage Chart
    public createMemoryChart(canvasId: string, data: Array<{ database: string; usage: number }>): Chart | null {
        const chartData = {
            labels: data.map(d => d.database),
            datasets: [{
                label: 'Memory Usage (MB)',
                data: data.map(d => d.usage),
                backgroundColor: this.defaultColors.map(color => color + '80'),
                borderColor: this.defaultColors,
                borderWidth: 2,
            }],
        };

        const options = {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Memory Usage (MB)',
                    },
                },
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Database Memory Usage',
                },
            },
        };

        return this.createChart(canvasId, {
            type: 'bar',
            data: chartData,
            options,
        });
    }

    // Response Time Chart
    public createResponseTimeChart(canvasId: string, data: Array<{ database: string; avgTime: number; maxTime: number; minTime: number }>): Chart | null {
        const chartData = {
            labels: data.map(d => d.database),
            datasets: [
                {
                    label: 'Average Response Time (ms)',
                    data: data.map(d => d.avgTime),
                    backgroundColor: this.defaultColors[0] + '80',
                    borderColor: this.defaultColors[0],
                    borderWidth: 2,
                },
                {
                    label: 'Max Response Time (ms)',
                    data: data.map(d => d.maxTime),
                    backgroundColor: this.defaultColors[1] + '80',
                    borderColor: this.defaultColors[1],
                    borderWidth: 2,
                },
                {
                    label: 'Min Response Time (ms)',
                    data: data.map(d => d.minTime),
                    backgroundColor: this.defaultColors[2] + '80',
                    borderColor: this.defaultColors[2],
                    borderWidth: 2,
                },
            ],
        };

        const options = {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Response Time (ms)',
                    },
                },
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Database Response Times',
                },
            },
        };

        return this.createChart(canvasId, {
            type: 'bar',
            data: chartData,
            options,
        });
    }

    // Real-time Chart for Monitoring
    public createRealTimeChart(canvasId: string, maxDataPoints: number = 50): Chart | null {
        const chartData = {
            labels: Array(maxDataPoints).fill(''),
            datasets: [{
                label: 'CPU Usage (%)',
                data: Array(maxDataPoints).fill(0),
                backgroundColor: this.defaultColors[0] + '20',
                borderColor: this.defaultColors[0],
                borderWidth: 2,
                fill: true,
                tension: 0.1,
            }, {
                label: 'Memory Usage (%)',
                data: Array(maxDataPoints).fill(0),
                backgroundColor: this.defaultColors[1] + '20',
                borderColor: this.defaultColors[1],
                borderWidth: 2,
                fill: true,
                tension: 0.1,
            }],
        };

        const options = {
            scales: {
                x: {
                    display: false,
                },
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Usage (%)',
                    },
                },
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Real-time System Metrics',
                },
                legend: {
                    position: 'top' as const,
                },
            },
            animation: {
                duration: 0,
            },
        };

        return this.createChart(canvasId, {
            type: 'line',
            data: chartData,
            options,
        });
    }

    // Update real-time chart data
    public updateRealTimeChart(canvasId: string, cpuUsage: number, memoryUsage: number): void {
        const chart = this.charts.get(canvasId);
        if (!chart) return;

        const now = new Date().toLocaleTimeString();
        
        // Shift data and add new point
        chart.data.labels?.shift();
        chart.data.labels?.push(now);
        
        chart.data.datasets[0].data.shift();
        chart.data.datasets[0].data.push(cpuUsage);
        
        chart.data.datasets[1].data.shift();
        chart.data.datasets[1].data.push(memoryUsage);
        
        chart.update('none');
    }

    // Export chart as image
    public exportChart(canvasId: string, filename: string = 'chart.png'): void {
        const chart = this.charts.get(canvasId);
        if (!chart) return;

        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = filename;
        link.href = url;
        link.click();
    }

    // Get chart data as JSON
    public getChartData(canvasId: string): any {
        const chart = this.charts.get(canvasId);
        return chart ? chart.data : null;
    }

    // Resize all charts
    public resizeAllCharts(): void {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    // Destroy all charts
    public destroyAllCharts(): void {
        this.charts.forEach((chart, canvasId) => {
            this.destroyChart(canvasId);
        });
    }

    // Utility method to generate random data for testing
    public generateRandomData(count: number, min: number = 0, max: number = 100): number[] {
        return Array.from({ length: count }, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }

    // Utility method to generate time series data
    public generateTimeSeriesData(count: number, interval: number = 1000): TimeSeriesData[] {
        const data: TimeSeriesData[] = [];
        const now = Date.now();
        
        for (let i = 0; i < count; i++) {
            data.push({
                timestamp: new Date(now - (count - i) * interval).toISOString(),
                value: Math.random() * 100,
            });
        }
        
        return data;
    }
}

// Create global instance
const chartManager = new ChartManager();

// Export for use in other modules
(window as any).chartManager = chartManager;

// Global chart utility functions
(window as any).createPerformanceChart = (canvasId: string, data: PerformanceData[]) => {
    return chartManager.createPerformanceChart(canvasId, data);
};

(window as any).createTimeSeriesChart = (canvasId: string, datasets: any[]) => {
    return chartManager.createTimeSeriesChart(canvasId, datasets);
};

(window as any).createDistributionChart = (canvasId: string, data: any[]) => {
    return chartManager.createDistributionChart(canvasId, data);
};

(window as any).createMemoryChart = (canvasId: string, data: any[]) => {
    return chartManager.createMemoryChart(canvasId, data);
};

(window as any).createResponseTimeChart = (canvasId: string, data: any[]) => {
    return chartManager.createResponseTimeChart(canvasId, data);
};

(window as any).createRealTimeChart = (canvasId: string, maxDataPoints?: number) => {
    return chartManager.createRealTimeChart(canvasId, maxDataPoints);
};

(window as any).updateRealTimeChart = (canvasId: string, cpuUsage: number, memoryUsage: number) => {
    chartManager.updateRealTimeChart(canvasId, cpuUsage, memoryUsage);
};

(window as any).exportChart = (canvasId: string, filename?: string) => {
    chartManager.exportChart(canvasId, filename);
};
