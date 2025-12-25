// CHARTS.JS - FIXED VERSION
console.log('🚀 charts.js loading...');

class ChartManager {
    constructor() {
        this.charts = new Map();
        console.log('✅ ChartManager created');
    }

    initDemoCharts() {
        console.log('📊 Initializing demo charts');
        this.destroyAllCharts(); // Destroy existing charts first
        this.createDemoChart();
        this.createMiniCharts();
    }

    createDemoChart() {
        const ctx = document.getElementById('mainChart');
        if (!ctx) {
            console.log('❌ mainChart canvas not found');
            return;
        }

        // Destroy existing chart if it exists
        if (this.charts.has('mainChart')) {
            this.charts.get('mainChart').destroy();
        }

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Revenue',
                    data: [65, 59, 80, 81, 56, 55, 40, 70, 85, 92, 78, 88],
                    borderColor: 'rgb(147, 51, 234)',
                    backgroundColor: 'rgba(147, 51, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Customers',
                    data: [28, 48, 40, 19, 86, 27, 90, 45, 60, 75, 82, 68],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Monthly Performance'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        this.charts.set('mainChart', chart);
        console.log('✅ Demo chart created');
    }

    createMiniCharts() {
        // Mini Chart 1
        const ctx1 = document.getElementById('miniChart1');
        if (ctx1) {
            // Destroy existing chart if it exists
            if (this.charts.has('miniChart1')) {
                this.charts.get('miniChart1').destroy();
            }

            const chart1 = new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'Pending', 'Failed'],
                    datasets: [{
                        data: [65, 25, 10],
                        backgroundColor: [
                            'rgb(34, 197, 94)',
                            'rgb(249, 115, 22)',
                            'rgb(239, 68, 68)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });

            this.charts.set('miniChart1', chart1);
        }

        // Mini Chart 2
        const ctx2 = document.getElementById('miniChart2');
        if (ctx2) {
            // Destroy existing chart if it exists
            if (this.charts.has('miniChart2')) {
                this.charts.get('miniChart2').destroy();
            }

            const chart2 = new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [{
                        label: 'Growth',
                        data: [30, 45, 35, 60],
                        backgroundColor: 'rgb(139, 92, 246)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            this.charts.set('miniChart2', chart2);
        }

        console.log('✅ Mini charts created');
    }

    loadDemoData() {
        console.log('📈 Loading demo chart data...');
        this.initDemoCharts();
    }

    destroyAllCharts() {
        this.charts.forEach((chart, key) => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
                console.log(`🗑️ Destroyed chart: ${key}`);
            }
        });
        this.charts.clear();
    }

    // Method to safely update charts
    safeUpdateCharts() {
        this.destroyAllCharts();
        this.initDemoCharts();
    }
}

// GLOBAL INSTANCE
console.log('🌍 Creating global chartManager...');
window.chartManager = new ChartManager();

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for the DOM to be fully ready
    setTimeout(() => {
        window.chartManager.initDemoCharts();
        console.log('✅ Global chartManager created and charts initialized');
    }, 100);
});