/**
 * Dashboard Page JavaScript
 * Handles fetching statistics and rendering mini charts on the homepage
 */

class DashboardManager {
    constructor() {
        this.stats = null;
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadStatistics();
        this.updateStatCards();
        this.renderMiniCharts();
        
        // Refresh statistics every 2 minutes
        setInterval(() => {
            this.loadStatistics();
            this.updateStatCards();
            this.updateCharts();
        }, 2 * 60 * 1000);
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.success) {
                this.stats = data.stats;
            } else {
                console.error('Failed to load statistics:', data.error);
            }
        } catch (error) {
            console.error('Error fetching statistics:', error);
        }
    }

    updateStatCards() {
        if (!this.stats) return;

        // Update today's events
        const todayEventsEl = document.getElementById('todayEvents');
        if (todayEventsEl) {
            todayEventsEl.textContent = this.stats.today_events || 0;
        }

        // Update total events
        const totalEventsEl = document.getElementById('totalEvents');
        if (totalEventsEl) {
            totalEventsEl.textContent = this.stats.total_events || 0;
        }

        // Update this week events
        const thisWeekEl = document.getElementById('thisWeekEvents');
        if (thisWeekEl) {
            thisWeekEl.textContent = this.stats.this_week_events || 0;
        }

        // Update average confidence
        const avgConfEl = document.getElementById('avgConfidence');
        if (avgConfEl) {
            const avgConf = this.stats.average_confidence || 0;
            avgConfEl.textContent = `${avgConf.toFixed(1)}%`;
        }
    }

    renderMiniCharts() {
        if (!this.stats) return;

        this.renderEventsTimelineChart();
        this.renderEventTypeDistribution();
    }

    updateCharts() {
        // Destroy existing charts and re-render
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
        this.renderMiniCharts();
    }

    renderEventsTimelineChart() {
        const canvas = document.getElementById('eventsTimelineChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const eventsByDate = this.stats.events_by_date;

        if (!eventsByDate || Object.keys(eventsByDate).length === 0) {
            return;
        }

        // Sort dates and get last 7 days
        const sortedDates = Object.keys(eventsByDate).sort();
        const last7Dates = sortedDates.slice(-7);
        const counts = last7Dates.map(date => eventsByDate[date]);

        // Format dates for display (e.g., "Nov 7")
        const labels = last7Dates.map(date => {
            const d = new Date(date);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });

        this.charts.eventsTimeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Events',
                    data: counts,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5
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
                        text: 'Events Over Time (Last 7 Days)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        padding: {
                            top: 5,
                            bottom: 10
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
                            stepSize: 1,
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        ticks: {
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    renderEventTypeDistribution() {
        const canvas = document.getElementById('eventTypeChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const eventsByType = this.stats.events_by_type;

        if (!eventsByType || Object.keys(eventsByType).length === 0) {
            return;
        }

        // Get top 5 types
        const sortedTypes = Object.entries(eventsByType)
            .sort((a, b) => b[1].count - a[1].count)
            .slice(0, 5);

        const labels = sortedTypes.map(([type]) => type);
        const counts = sortedTypes.map(([, data]) => data.count);

        // Generate colors
        const colors = [
            'rgba(239, 68, 68, 0.7)',   // red
            'rgba(251, 146, 60, 0.7)',  // orange
            'rgba(59, 130, 246, 0.7)',  // blue
            'rgba(34, 197, 94, 0.7)',   // green
            'rgba(168, 85, 247, 0.7)'   // purple
        ];

        this.charts.eventType = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: colors.slice(0, labels.length),
                    borderColor: colors.slice(0, labels.length).map(c => c.replace('0.7', '1')),
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
                            padding: 8,
                            font: {
                                size: 10
                            },
                            boxWidth: 12,
                            boxHeight: 12
                        }
                    },
                    title: {
                        display: true,
                        text: 'Top Detected Objects',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        padding: {
                            top: 5,
                            bottom: 10
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return `${label}: ${value} events`;
                            }
                        }
                    }
                }
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new DashboardManager();
});
