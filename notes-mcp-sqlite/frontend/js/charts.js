// Chart Utilities and Components (JavaScript version)
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultColors = [
            '#3B82F6', // Blue
            '#10B981', // Green
            '#F59E0B', // Yellow
            '#EF4444', // Red
            '#8B5CF6', // Purple
            '#06B6D4', // Cyan
            '#84CC16', // Lime
            '#F97316', // Orange
        ];
        this.setupChartDefaults();
    }

    setupChartDefaults() {
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
    createChart(canvasId, config) {
        const canvas = document.getElementById(canvasId);
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
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
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
    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }

    // Update chart data
    updateChart(canvasId, newData) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    // Performance Comparison Chart
    createPerformanceChart(canvasId, data) {
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
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Time (ms)',
                    },
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
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
    createTimeSeriesChart(canvasId, datasets) {
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
    createDistributionChart(canvasId, data) {
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
                    position: 'bottom',
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
    createMemoryChart(canvasId, data) {
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

    // Real-time Chart for Monitoring
    createRealTimeChart(canvasId, maxDataPoints = 50) {
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
                    position: 'top',
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
    updateRealTimeChart(canvasId, cpuUsage, memoryUsage) {
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
    exportChart(canvasId, filename = 'chart.png') {
        const chart = this.charts.get(canvasId);
        if (!chart) return;

        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = filename;
        link.href = url;
        link.click();
    }

    // Get chart data as JSON
    getChartData(canvasId) {
        const chart = this.charts.get(canvasId);
        return chart ? chart.data : null;
    }

    // Resize all charts
    resizeAllCharts() {
        this.charts.forEach(chart => {
            chart.resize();
        });
    }

    // Destroy all charts
    destroyAllCharts() {
        this.charts.forEach((chart, canvasId) => {
            this.destroyChart(canvasId);
        });
    }

    // Utility method to generate random data for testing
    generateRandomData(count, min = 0, max = 100) {
        return Array.from({ length: count }, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }

    // Utility method to generate time series data
    generateTimeSeriesData(count, interval = 1000) {
        const data = [];
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
window.chartManager = chartManager;

// Global chart utility functions
window.createPerformanceChart = (canvasId, data) => {
    return chartManager.createPerformanceChart(canvasId, data);
};

window.createTimeSeriesChart = (canvasId, datasets) => {
    return chartManager.createTimeSeriesChart(canvasId, datasets);
};

window.createDistributionChart = (canvasId, data) => {
    return chartManager.createDistributionChart(canvasId, data);
};

window.createMemoryChart = (canvasId, data) => {
    return chartManager.createMemoryChart(canvasId, data);
};

window.createRealTimeChart = (canvasId, maxDataPoints) => {
    return chartManager.createRealTimeChart(canvasId, maxDataPoints);
};

window.updateRealTimeChart = (canvasId, cpuUsage, memoryUsage) => {
    chartManager.updateRealTimeChart(canvasId, cpuUsage, memoryUsage);
};

window.exportChart = (canvasId, filename) => {
    chartManager.exportChart(canvasId, filename);
};
