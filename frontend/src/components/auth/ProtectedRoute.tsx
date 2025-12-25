import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
    children: React.ReactNode;
    requireVerified?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    requireVerified = false
}) => {
    const { isAuthenticated, isLoading, user } = useAuth();
    const location = useLocation();

    if (isLoading) {
        // Show loading spinner while checking auth
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                    <p className="mt-4 text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        // Redirect to login, but save the attempted location
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (requireVerified && user && !user.is_verified) {
        // Redirect to verification notice if email not verified
        return <Navigate to="/verify-email-notice" replace />;
    }

    return <>{children}</>;
};
