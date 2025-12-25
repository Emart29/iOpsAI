import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

export const NotFoundPage = () => {
    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
            <div className="text-center">
                <h1 className="text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">
                    404
                </h1>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mt-4">
                    Page Not Found
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mt-2 mb-8">
                    Oops! The page you're looking for doesn't exist or has been moved.
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
                    <Link
                        to="/dashboard"
                        className="inline-flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                    >
                        <Home className="w-5 h-5 mr-2" />
                        Go to Dashboard
                    </Link>
                    <Link
                        to="/"
                        className="inline-flex items-center px-6 py-3 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 mr-2" />
                        Back Home
                    </Link>
                </div>
            </div>
        </div>
    );
};
