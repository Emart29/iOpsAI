// js/app.js - Main Application Logic
console.log('🚀 app.js loading...');

class InsightStudioApp {
    constructor() {
        this.currentSession = null;
        this.init();
    }

    init() {
        console.log('🔧 Initializing app...');
        this.setupEventListeners();
        this.checkServerHealth();
        this.checkForSession();
        console.log('✅ App initialized');
    }

    async checkServerHealth() {
        try {
            const health = await window.api.healthCheck();
            console.log('✅ Server is healthy:', health);
        } catch (error) {
            console.warn('⚠️ Server health check failed:', error);
            this.showNotification('Warning: Could not connect to server. Please ensure backend is running on http://localhost:8000', 'warning');
        }
    }

    setupEventListeners() {
        // Demo buttons
        const demoButtons = document.querySelectorAll('[data-action="demo"]');
        demoButtons.forEach(btn => {
            btn.addEventListener('click', () => this.loadDemo());
        });

        // Dark mode toggle
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', () => this.toggleDarkMode());
        }

        console.log('✅ Event listeners setup');
    }

    toggleDarkMode() {
        document.documentElement.classList.toggle('dark');
        const isDark = document.documentElement.classList.contains('dark');
        const icon = document.getElementById('darkModeIcon');
        if (icon) {
            icon.textContent = isDark ? '☀️' : '🌙';
        }
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }

    async loadDemo() {
        try {
            this.showLoading('Loading demo data...');
            
            // Create demo CSV data
            const demoCSV = `Name,Age,Salary,Department,Experience,Performance
John Doe,35,75000,Engineering,8,4.5
Jane Smith,28,65000,Marketing,5,4.2
Bob Johnson,42,85000,Engineering,15,4.8
Alice Williams,31,70000,Sales,6,4.3
Charlie Brown,38,80000,Engineering,10,4.6
Diana Prince,29,68000,Marketing,4,4.1
Eve Adams,45,95000,Management,20,4.9
Frank Castle,33,72000,Sales,7,4.4
Grace Hopper,40,90000,Engineering,16,4.7
Henry Ford,36,78000,Operations,9,4.5`;

            // Create a File object from the CSV string
            const blob = new Blob([demoCSV], { type: 'text/csv' });
            const file = new File([blob], 'demo_employee_data.csv', { type: 'text/csv' });

            // Upload the demo file
            const response = await window.api.uploadDatasetEnhanced(file);
            
            this.hideLoading();
            
            if (response.success) {
                this.currentSession = response.session_id;
                localStorage.setItem('iops_session', response.session_id);
                this.showNotification('Demo data loaded successfully! 🎉', 'success');
                
                // Scroll to upload section to show results
                const dataProfile = document.getElementById('dataProfile');
                if (dataProfile) {
                    dataProfile.scrollIntoView({ behavior: 'smooth' });
                }
            }
            
        } catch (error) {
            this.hideLoading();
            this.showNotification('Failed to load demo: ' + error.message, 'error');
            console.error('Demo load error:', error);
        }
    }

    checkForSession() {
        const sessionId = localStorage.getItem('iops_session');
        if (sessionId) {
            this.currentSession = sessionId;
            window.api.sessionId = sessionId;
            console.log('✅ Restored session:', sessionId);
        }
    }

    showLoading(message = 'Loading...') {
        let loadingEl = document.getElementById('globalLoading');
        
        if (!loadingEl) {
            loadingEl = document.createElement('div');
            loadingEl.id = 'globalLoading';
            loadingEl.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
            document.body.appendChild(loadingEl);
        }
        
        loadingEl.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg p-6 flex items-center space-x-4 max-w-md">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                <span class="text-gray-800 dark:text-white">${message}</span>
            </div>
        `;
    }

    hideLoading() {
        const loadingEl = document.getElementById('globalLoading');
        if (loadingEl) {
            loadingEl.remove();
        }
    }

    showNotification(message, type = 'info') {
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500',
            warning: 'bg-yellow-500'
        };
        
        const notifEl = document.createElement('div');
        notifEl.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 max-w-md`;
        notifEl.style.animation = 'slideInRight 0.3s ease-out';
        notifEl.textContent = message;
        document.body.appendChild(notifEl);
        
        setTimeout(() => {
            notifEl.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notifEl.remove(), 300);
        }, 5000);
    }
}

// Global utility functions
function showLoading(message) {
    if (window.app) {
        window.app.showLoading(message);
    }
}

function hideLoading() {
    if (window.app) {
        window.app.hideLoading();
    }
}

function showNotification(message, type) {
    if (window.app) {
        window.app.showNotification(message, type);
    } else {
        alert(message);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, creating app...');
    window.app = new InsightStudioApp();
    
    // Initialize dark mode
    const theme = localStorage.getItem('theme');
    if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        const icon = document.getElementById('darkModeIcon');
        if (icon) icon.textContent = '☀️';
    }
    
    console.log('✅ App ready!');
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

console.log('✅ app.js loaded');