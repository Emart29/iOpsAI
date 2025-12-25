import { Toaster } from 'react-hot-toast';

export const ToastProvider = () => {
    return (
        <Toaster
            position="top-right"
            reverseOrder={false}
            gutter={8}
            toastOptions={{
                // Default options
                duration: 4000,
                style: {
                    background: '#fff',
                    color: '#363636',
                    padding: '16px',
                    borderRadius: '12px',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                },
                // Success
                success: {
                    duration: 3000,
                    iconTheme: {
                        primary: '#10b981',
                        secondary: '#fff',
                    },
                    style: {
                        background: '#f0fdf4',
                        border: '1px solid #86efac',
                    },
                },
                // Error
                error: {
                    duration: 5000,
                    iconTheme: {
                        primary: '#ef4444',
                        secondary: '#fff',
                    },
                    style: {
                        background: '#fef2f2',
                        border: '1px solid #fca5a5',
                    },
                },
                // Loading
                loading: {
                    iconTheme: {
                        primary: '#9333ea',
                        secondary: '#fff',
                    },
                },
            }}
        />
    );
};

// Helper functions for easy toast usage
export { toast } from 'react-hot-toast';
