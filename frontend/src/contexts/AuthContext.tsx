import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Types
interface User {
    id: number;
    uuid: string;
    email: string;
    username: string;
    full_name: string | null;
    is_active: boolean;
    is_verified: boolean;
    profile_picture_url: string | null;
    created_at: string;
    last_login: string | null;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
    logout: () => void;
    refreshToken: () => Promise<void>;
    updateUser: (userData: Partial<User>) => void;
}

interface AuthProviderProps {
    children: ReactNode;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// API base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// AuthProvider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Check if user is authenticated on mount
    useEffect(() => {
        checkAuth();
    }, []);

    // Check authentication status
    const checkAuth = async () => {
        const accessToken = localStorage.getItem('access_token');

        if (!accessToken) {
            setIsLoading(false);
            return;
        }

        try {
            const response = await axios.get(`${API_URL}/api/auth/me`, {
                headers: {
                    Authorization: `Bearer ${accessToken}`
                }
            });
            setUser(response.data);
        } catch (error) {
            // Silently fail - clear invalid tokens and continue without auth
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setUser(null);
        } finally {
            setIsLoading(false);
        }
    };

    // Login function
    const login = async (email: string, password: string) => {
        try {
            const response = await axios.post(`${API_URL}/api/auth/login`, {
                email,
                password
            });

            const { access_token, refresh_token } = response.data;

            // Store tokens
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);

            // Get user data
            const userResponse = await axios.get(`${API_URL}/api/auth/me`, {
                headers: {
                    Authorization: `Bearer ${access_token}`
                }
            });

            setUser(userResponse.data);
        } catch (error: any) {
            throw new Error(error.response?.data?.detail || 'Login failed');
        }
    };

    // Register function
    const register = async (
        email: string,
        username: string,
        password: string,
        fullName?: string
    ) => {
        try {
            await axios.post(`${API_URL}/api/auth/register`, {
                email,
                username,
                password,
                full_name: fullName
            });
            // Note: User needs to verify email before logging in
        } catch (error: any) {
            throw new Error(error.response?.data?.detail || 'Registration failed');
        }
    };

    // Logout function
    const logout = () => {
        const refreshToken = localStorage.getItem('refresh_token');

        // Revoke refresh token on server
        if (refreshToken) {
            axios.post(`${API_URL}/api/auth/logout`, {
                refresh_token: refreshToken
            }).catch(() => {
                // Ignore errors, just clear local storage
            });
        }

        // Clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    };

    // Refresh token function
    const refreshToken = async () => {
        const refresh = localStorage.getItem('refresh_token');

        if (!refresh) {
            logout();
            return;
        }

        try {
            const response = await axios.post(`${API_URL}/api/auth/refresh`, {
                refresh_token: refresh
            });

            const { access_token, refresh_token } = response.data;

            // Update tokens
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);

            // Get user data
            const userResponse = await axios.get(`${API_URL}/api/auth/me`, {
                headers: {
                    Authorization: `Bearer ${access_token}`
                }
            });

            setUser(userResponse.data);
        } catch (error) {
            logout();
        }
    };

    // Update user data
    const updateUser = (userData: Partial<User>) => {
        if (user) {
            setUser({ ...user, ...userData });
        }
    };

    const value: AuthContextType = {
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshToken,
        updateUser
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
