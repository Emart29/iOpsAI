import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './components/ui/ToastProvider';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { DashboardPage } from './pages/DashboardPage';
import { NotFoundPage } from './pages/NotFoundPage';

function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <ToastProvider />
                <Router>
                    <Routes>
                        {/* Public Routes */}
                        <Route path="/" element={<LandingPage />} />
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                        <Route path="/forgot-password" element={<ForgotPasswordPage />} />

                        {/* Dashboard - Now accessible without login */}
                        <Route path="/dashboard" element={<DashboardPage />} />

                        {/* 404 Route */}
                        <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                </Router>
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;
