/**
 * Statistics Page JavaScript
 * Handles fetching statistics data and rendering charts with Chart.js
 */

class StatisticsManager {
    constructor() {
        this.stats = null;
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadStatistics();
        
        if (this.stats && this.stats.total_events > 0) {
            // Hide loading, show content
            document.getElementById('loading-state').classList.add('hidden');
            document.getElementById('stats-content').classList.remove('hidden');
            
            this.renderAllCharts();
            this.updateStatCards();
        } else {
            // Hide loading, show empty state
            document.getElementById('loading-state').classList.add('hidden');
            document.getElementById('empty-state').classList.remove('hidden');
        }
        
        // Refresh statistics every 5 minutes
        setInterval(() => {
            this.loadStatistics();
            this.updateCharts();
            this.updateStatCards();
        }, 5 * 60 * 1000);
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.success) {
                this.stats = data.stats;
            } else {
                console.error('Failed to load statistics:', data.error);
                this.showError('Failed to load statistics');
            }
        } catch (error) {
            console.error('Error fetching statistics:', error);
            this.showError('Error connecting to server');
        }
    }

    renderAllCharts() {
        if (!this.stats) {
            this.showError('No statistics data available');
            return;
        }

        this.renderEventsByTypeChart();
        this.renderEventsOverTimeChart();
        this.renderConfidenceDistributionChart();
        this.renderHourlyPatternChart();
        this.renderEventTypeTable();
    }

    updateCharts() {
        // Destroy existing charts and re-render
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
        this.renderAllCharts();
    }

    renderEventsByTypeChart() {
        const canvas = document.getElementById('eventsByTypeChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const eventsByType = this.stats.events_by_type;

        if (!eventsByType || Object.keys(eventsByType).length === 0) {
            this.showChartMessage(ctx, 'No data available');
            return;
        }

        const labels = Object.keys(eventsByType);
        const counts = labels.map(type => eventsByType[type].count);
        const percentages = labels.map(type => eventsByType[type].percentage);

        // Generate colors for each type
        const colors = this.generateColors(labels.length);

        this.charts.eventsByType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Events by Type',
                    data: counts,
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace('0.7', '1')),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Events Distribution by Object Type',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const percentage = percentages[context.dataIndex];
                                return `${label}: ${value} events (${percentage.toFixed(1)}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderEventsOverTimeChart() {
        const canvas = document.getElementById('eventsOverTimeChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const eventsByDate = this.stats.events_by_date;

        if (!eventsByDate || Object.keys(eventsByDate).length === 0) {
            this.showChartMessage(ctx, 'No data available');
            return;
        }

        // Sort dates chronologically
        const sortedDates = Object.keys(eventsByDate).sort();
        const counts = sortedDates.map(date => eventsByDate[date]);

        this.charts.eventsOverTime = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedDates,
                datasets: [{
                    label: 'Events per Day',
                    data: counts,
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Events Over Time',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Events: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Number of Events'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }

    renderConfidenceDistributionChart() {
        const canvas = document.getElementById('confidenceChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const eventsByType = this.stats.events_by_type;

        if (!eventsByType || Object.keys(eventsByType).length === 0) {
            this.showChartMessage(ctx, 'No data available');
            return;
        }

        const labels = Object.keys(eventsByType);
        const avgConfidences = labels.map(type => eventsByType[type].avg_confidence);

        const colors = this.generateColors(labels.length);

        this.charts.confidence = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Confidence',
                    data: avgConfidences,
                    backgroundColor: colors,
                    borderColor: colors.map(c => c.replace('0.7', '1')),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Average Confidence by Object Type',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Avg Confidence: ${context.parsed.y.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Confidence (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Object Type'
                        }
                    }
                }
            }
        });
    }

    renderHourlyPatternChart() {
        const canvas = document.getElementById('hourlyPatternChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const peakTimes = this.stats.peak_times;

        if (!peakTimes || !peakTimes.hourly_distribution || Object.keys(peakTimes.hourly_distribution).length === 0) {
            this.showChartMessage(ctx, 'Insufficient data for hourly pattern');
            return;
        }

        // Create array for all 24 hours
        const hourlyData = Array(24).fill(0);
        Object.entries(peakTimes.hourly_distribution).forEach(([hour, count]) => {
            hourlyData[parseInt(hour)] = count;
        });

        const labels = Array.from({length: 24}, (_, i) => `${i}:00`);

        // Highlight peak hour
        const peakHour = peakTimes.peak_hour;
        const backgroundColors = hourlyData.map((_, index) => 
            index === peakHour ? 'rgba(239, 68, 68, 0.7)' : 'rgba(59, 130, 246, 0.7)'
        );
        const borderColors = hourlyData.map((_, index) => 
            index === peakHour ? 'rgb(239, 68, 68)' : 'rgb(59, 130, 246)'
        );

        this.charts.hourlyPattern = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Events per Hour',
                    data: hourlyData,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: backgroundColors,
                    pointBorderColor: borderColors,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: `Hourly Detection Pattern (Peak: ${peakHour}:00 with ${peakTimes.peak_count} events)`,
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            top: 10,
                            bottom: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const hour = context.dataIndex;
                                const count = context.parsed.y;
                                const isPeak = hour === peakHour;
                                return `${count} events${isPeak ? ' (Peak)' : ''}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Number of Events'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Hour of Day'
                        }
                    }
                }
            }
        });
    }

    renderEventTypeTable() {
        const tableBody = document.getElementById('eventTypeTableBody');
        if (!tableBody) return;

        const eventsByType = this.stats.events_by_type;

        if (!eventsByType || Object.keys(eventsByType).length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="px-6 py-4 text-center text-gray-500">No data available</td></tr>';
            return;
        }

        // Sort by count descending
        const sortedTypes = Object.entries(eventsByType)
            .sort((a, b) => b[1].count - a[1].count);

        tableBody.innerHTML = sortedTypes.map(([type, data]) => `
            <tr class="border-b border-gray-200 hover:bg-gray-50">
                <td class="px-6 py-4 font-medium text-gray-900">${this.escapeHtml(type)}</td>
                <td class="px-6 py-4 text-gray-700">${data.count}</td>
                <td class="px-6 py-4 text-gray-700">${data.percentage.toFixed(1)}%</td>
                <td class="px-6 py-4 text-gray-700">${data.avg_confidence.toFixed(1)}%</td>
            </tr>
        `).join('');
    }

    updateStatCards() {
        if (!this.stats) return;

        // Update total events
        const totalEventsEl = document.getElementById('totalEvents');
        if (totalEventsEl) {
            totalEventsEl.textContent = this.stats.total_events || 0;
        }

        // Update average confidence
        const avgConfidenceEl = document.getElementById('avgConfidence');
        if (avgConfidenceEl) {
            const avgConf = this.stats.average_confidence || 0;
            avgConfidenceEl.textContent = `${avgConf.toFixed(1)}%`;
        }

        // Update this week events
        const thisWeekEl = document.getElementById('thisWeekEvents');
        if (thisWeekEl) {
            thisWeekEl.textContent = this.stats.this_week_events || 0;
        }

        // Update top threat
        const topThreatEl = document.getElementById('topThreat');
        if (topThreatEl) {
            const topThreat = this.stats.top_threat;
            if (topThreat && topThreat.type) {
                topThreatEl.textContent = `${this.escapeHtml(topThreat.type)} (${topThreat.count})`;
            } else {
                topThreatEl.textContent = 'N/A';
            }
        }
    }

    generateColors(count) {
        const baseColors = [
            'rgba(59, 130, 246, 0.7)',   // blue
            'rgba(239, 68, 68, 0.7)',    // red
            'rgba(34, 197, 94, 0.7)',    // green
            'rgba(251, 146, 60, 0.7)',   // orange
            'rgba(168, 85, 247, 0.7)',   // purple
            'rgba(236, 72, 153, 0.7)',   // pink
            'rgba(14, 165, 233, 0.7)',   // sky
            'rgba(132, 204, 22, 0.7)',   // lime
            'rgba(234, 179, 8, 0.7)',    // yellow
            'rgba(99, 102, 241, 0.7)'    // indigo
        ];

        // Repeat colors if needed
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        return colors;
    }

    showChartMessage(ctx, message) {
        ctx.font = '16px sans-serif';
        ctx.fillStyle = '#6b7280';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(message, ctx.canvas.width / 2, ctx.canvas.height / 2);
    }

    showError(message) {
        // Create or update error toast
        const existingToast = document.getElementById('statsErrorToast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.id = 'statsErrorToast';
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle mr-2"></i>
                <span>${this.escapeHtml(message)}</span>
            </div>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new StatisticsManager();
});
