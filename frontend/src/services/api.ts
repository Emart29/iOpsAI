import axios from 'axios';
import type { Dataset, FullDataProfile, Insight, ChatMessage, ChartData, Experiment, UsageStats } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - Handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If error is 401 and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');

                if (!refreshToken) {
                    // No refresh token, redirect to login
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                    return Promise.reject(error);
                }

                // Try to refresh the token
                const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
                    refresh_token: refreshToken
                });

                const { access_token, refresh_token: newRefreshToken } = response.data;

                // Update tokens
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', newRefreshToken);

                // Retry the original request with new token
                if (originalRequest.headers) {
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                }
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh failed, redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export const datasetService = {
    upload: async (file: File): Promise<Dataset> => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/api/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    getProfile: async (sessionId: string): Promise<FullDataProfile> => {
        const response = await api.post('/eda/profile', null, {
            params: { session_id: sessionId }
        });
        return response.data;
    },

    getInsights: async (sessionId: string): Promise<Insight[]> => {
        const response = await api.post(`/api/insights/${sessionId}`);
        return response.data;
    },

    chat: async (sessionId: string, message: string, chatHistory: ChatMessage[]): Promise<string> => {
        const response = await api.post('/api/chat', {
            session_id: sessionId,
            message,
            chat_history: chatHistory,
        });
        return response.data.response;
    },

    getCharts: async (sessionId: string): Promise<ChartData> => {
        const response = await api.get(`/api/charts/${sessionId}`);
        return response.data;
    },

    generateReport: async (sessionId: string): Promise<{ download_url: string }> => {
        const response = await api.post(`/api/generate-report/${sessionId}`);
        return response.data;
    },

    cleanData: async (sessionId: string, cleaningSteps: string[]): Promise<{ download_url: string; summary: string }> => {
        const response = await api.post(`/api/clean-data/${sessionId}`, {
            cleaning_steps: cleaningSteps,
        });
        return response.data;
    },

    generateScript: async (sessionId: string): Promise<string> => {
        const response = await api.get(`/api/generate-script/${sessionId}`);
        return response.data.script;
    },

    getRecommendations: async (sessionId: string): Promise<Insight[]> => {
        const response = await api.post(`/api/recommendations/${sessionId}`);
        return response.data;
    },

    getExperiments: async (): Promise<Experiment[]> => {
        const response = await api.get('/api/experiments');
        return response.data;
    },

    deleteExperiment: async (sessionId: string): Promise<void> => {
        await api.delete(`/api/experiments/${sessionId}`);
    },
};

export const usageService = {
    getUsage: async (): Promise<UsageStats> => {
        const response = await api.get('/api/auth/usage');
        return response.data;
    },
};
