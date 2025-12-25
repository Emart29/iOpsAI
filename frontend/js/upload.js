// js/upload.js - CORRECTED VERSION
console.log('🚀 upload.js loading...');

class FileUploadManager {
    constructor() {
        console.log('📁 FileUploadManager constructor called');
        
        this.uploadArea = null;
        this.fileInput = null;
        this.dataProfile = null;
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            setTimeout(() => this.init(), 100);
        }
    }

    init() {
        console.log('🔧 Initializing upload manager...');
        
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.dataProfile = document.getElementById('dataProfile');
        
        if (!this.uploadArea || !this.fileInput) {
            console.error('❌ Required elements not found');
            return;
        }

        this.setupFileInput();
        this.setupDragAndDrop();
        console.log('✅ Upload manager initialized');
    }

    setupFileInput() {
        const uploadButton = document.getElementById('uploadButton');
        if (uploadButton) {
            uploadButton.addEventListener('click', () => {
                this.fileInput.click();
            });
        }
        
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });
    }

    setupDragAndDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => {
                this.uploadArea.classList.add('border-purple-400', 'bg-purple-50', 'dark:bg-purple-900');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => {
                this.uploadArea.classList.remove('border-purple-400', 'bg-purple-50', 'dark:bg-purple-900');
            }, false);
        });

        this.uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        }, false);
    }

    handleFileSelect(e) {
        const files = e.target.files;
        this.handleFiles(files);
    }

    handleFiles(files) {
        if (!files || files.length === 0) return;
        
        if (files.length > 1) {
            showNotification('Please upload one file at a time', 'warning');
            return;
        }
        
        const file = files[0];
        this.uploadFile(file);
    }

    async uploadFile(file) {
        console.log('📤 Uploading:', file.name);
        
        // Validate file type
        const validExtensions = ['.csv', '.xlsx', '.xls'];
        const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
        
        if (!validExtensions.includes(fileExtension)) {
            showNotification(`Invalid file type. Please upload CSV or Excel files.`, 'error');
            return;
        }

        // Validate file size (100MB limit)
        if (file.size > 100 * 1024 * 1024) {
            showNotification('File size exceeds 100MB limit', 'error');
            return;
        }

        try {
            showLoading('Analyzing ' + file.name + '...');

            const response = await window.api.uploadDatasetEnhanced(file);
            
            hideLoading();
            showNotification('Analysis complete! ✅', 'success');

            this.showEnhancedDataProfile(response);

        } catch (error) {
            console.error('❌ Upload failed:', error);
            hideLoading();
            showNotification('Upload failed: ' + error.message, 'error');
        }
    }

    showEnhancedDataProfile(response) {
        if (!this.dataProfile) return;
        
        const analysis = response.analysis;
        const overview = analysis.overview;
        
        this.dataProfile.classList.remove('hidden');
        this.dataProfile.innerHTML = `
            <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
                <div class="flex justify-between items-start mb-6">
                    <h3 class="text-2xl font-bold text-gray-800 dark:text-white">Analysis Results</h3>
                    <span class="text-sm text-green-600 bg-green-100 px-3 py-1 rounded-full">Complete</span>
                </div>
                
                <!-- Stats Grid -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <div class="text-center p-4 bg-purple-50 dark:bg-purple-900 rounded-lg">
                        <div class="text-2xl font-bold text-purple-600">${overview.rows.toLocaleString()}</div>
                        <div class="text-sm text-gray-600 dark:text-gray-300">Rows</div>
                    </div>
                    <div class="text-center p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                        <div class="text-2xl font-bold text-blue-600">${overview.columns}</div>
                        <div class="text-sm text-gray-600 dark:text-gray-300">Columns</div>
                    </div>
                    <div class="text-center p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                        <div class="text-2xl font-bold text-green-600">${analysis.data_quality.score.toFixed(1)}</div>
                        <div class="text-sm text-gray-600 dark:text-gray-300">Quality</div>
                    </div>
                    <div class="text-center p-4 bg-orange-50 dark:bg-orange-900 rounded-lg">
                        <div class="text-2xl font-bold text-orange-600">${overview.total_missing}</div>
                        <div class="text-sm text-gray-600 dark:text-gray-300">Missing</div>
                    </div>
                </div>

                <!-- Columns Preview -->
                <div class="mb-8">
                    <h4 class="text-lg font-semibold mb-4">Columns (${overview.columns})</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${Object.entries(analysis.columns).slice(0, 6).map(([colName, colData]) => `
                            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                                <div class="font-medium text-gray-800 dark:text-white truncate mb-2">${colName}</div>
                                <div class="text-sm text-gray-600 dark:text-gray-400">
                                    <div>Type: ${colData.type}</div>
                                    <div>Missing: ${colData.missing} (${(colData.missing_percentage * 100).toFixed(1)}%)</div>
                                    <div>Unique: ${colData.unique}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    ${Object.entries(analysis.columns).length > 6 ? `
                    <div class="text-center mt-4 text-gray-500">
                        ... and ${Object.entries(analysis.columns).length - 6} more columns
                    </div>
                    ` : ''}
                </div>

                <!-- Action Buttons -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button onclick="window.aiChat?.toggleChat()" class="bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 transition-colors font-semibold">
                        🤖 Ask AI
                    </button>
                    <button onclick="loadCharts()" class="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold">
                        📊 View Charts
                    </button>
                    <button onclick="exportCode()" class="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold">
                        🐍 Export Code
                    </button>
                </div>
            </div>
        `;
    }
}

// Global helper functions
async function loadCharts() {
    try {
        showLoading('Loading charts...');
        const data = await window.api.getChartData('overview');
        hideLoading();
        showNotification('Chart data loaded! Check console for details.', 'success');
        console.log('Chart data:', data);
    } catch (error) {
        hideLoading();
        showNotification('Failed to load charts: ' + error.message, 'error');
    }
}

async function exportCode() {
    try {
        showLoading('Generating Python code...');
        await window.api.exportPythonCode();
        hideLoading();
        showNotification('Python code exported successfully! ✅', 'success');
    } catch (error) {
        hideLoading();
        showNotification('Export failed: ' + error.message, 'error');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.uploadManager = new FileUploadManager();
    console.log('✅ Upload manager ready');
});

console.log('✅ upload.js loaded');