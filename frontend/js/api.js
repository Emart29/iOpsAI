// js/api.js - PRODUCTION VERSION
console.log('🚀 api.js loading...');

class InsightStudioAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.sessionId = null;
        console.log('✅ API initialized with baseURL:', this.baseURL);
    }

    // Basic upload
    async uploadDataset(file) {
        console.log('📤 Uploading file:', file.name);
        
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.baseURL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Upload failed: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            console.log('✅ Upload successful! Session:', this.sessionId);
            return data;
            
        } catch (error) {
            console.error('❌ Upload failed:', error);
            throw error;
        }
    }

    // Enhanced upload with full analysis
    async uploadDatasetEnhanced(file) {
        console.log('📤 Enhanced upload:', file.name);
        
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.baseURL}/upload-enhanced`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Enhanced upload failed: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            console.log('✅ Enhanced upload successful! Session:', this.sessionId);
            return data;
            
        } catch (error) {
            console.error('❌ Enhanced upload failed:', error);
            throw error;
        }
    }

    // Ask AI question
    async askAIQuestion(question) {
        if (!this.sessionId) {
            throw new Error('No active session. Please upload a file first.');
        }

        try {
            const response = await fetch(`${this.baseURL}/ask?session_id=${this.sessionId}&question=${encodeURIComponent(question)}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`AI request failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('❌ AI question error:', error);
            throw error;
        }
    }

    // Get chart data
    async getChartData(chartType = 'overview') {
        if (!this.sessionId) {
            throw new Error('No active session. Please upload a file first.');
        }

        try {
            const response = await fetch(`${this.baseURL}/chart-data/${this.sessionId}?chart_type=${chartType}`);
            
            if (!response.ok) {
                throw new Error(`Chart data request failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('❌ Chart data error:', error);
            throw error;
        }
    }

    // Get AI suggestions
    async getAISuggestions() {
        if (!this.sessionId) {
            throw new Error('No active session. Please upload a file first.');
        }

        try {
            const response = await fetch(`${this.baseURL}/ai-suggestions/${this.sessionId}`);
            
            if (!response.ok) {
                throw new Error(`AI suggestions request failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('❌ AI suggestions error:', error);
            throw error;
        }
    }

    // Export Python code
    async exportPythonCode() {
        if (!this.sessionId) {
            throw new Error('No active session. Please upload a file first.');
        }

        try {
            const response = await fetch(`${this.baseURL}/export/${this.sessionId}`);
            
            if (!response.ok) {
                throw new Error(`Export failed: ${response.status}`);
            }

            const data = await response.json();
            
            // Create download
            const blob = new Blob([data.code], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            return data;
        } catch (error) {
            console.error('❌ Export error:', error);
            throw error;
        }
    }

    // Export clean data
    async exportCleanData(format = 'csv') {
        if (!this.sessionId) {
            throw new Error('No active session. Please upload a file first.');
        }

        try {
            const response = await fetch(`${this.baseURL}/export-clean/${this.sessionId}?format=${format}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Export failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('❌ Export clean data error:', error);
            throw error;
        }
    }

    // Get session info
    async getSession() {
        if (!this.sessionId) {
            throw new Error('No active session.');
        }

        try {
            const response = await fetch(`${this.baseURL}/session/${this.sessionId}`);
            
            if (!response.ok) {
                throw new Error(`Get session failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('❌ Get session error:', error);
            throw error;
        }
    }

    // List all sessions
    async listSessions(limit = 50) {
        try {
            const response = await fetch(`${this.baseURL}/sessions?limit=${limit}`);
            
            if (!response.ok) {
                throw new Error(`List sessions failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('❌ List sessions error:', error);
            throw error;
        }
    }

    // Delete session
    async deleteSession(sessionId = null) {
        const sid = sessionId || this.sessionId;
        
        if (!sid) {
            throw new Error('No session ID provided.');
        }

        try {
            const response = await fetch(`${this.baseURL}/session/${sid}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`Delete session failed: ${response.status}`);
            }

            if (sid === this.sessionId) {
                this.sessionId = null;
            }

            return await response.json();
        } catch (error) {
            console.error('❌ Delete session error:', error);
            throw error;
        }
    }

    // Health check
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            
            if (!response.ok) {
                throw new Error(`Health check failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('❌ Health check error:', error);
            throw error;
        }
    }
}

// Create global instance
window.api = new InsightStudioAPI();
console.log('✅ Global API instance created');