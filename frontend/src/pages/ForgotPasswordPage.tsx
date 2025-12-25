import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Brain, Mail, AlertCircle, CheckCircle2, ArrowLeft } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const ForgotPasswordPage = () => {
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await axios.post(`${API_URL}/api/auth/forgot-password`, { email });
            setSuccess(true);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to send reset email. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center p-4">
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                        <CheckCircle2 className="w-8 h-8 text-green-600" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Check Your Email</h2>
                    <p className="text-gray-600 mb-6">
                        If an account exists for <strong>{email}</strong>, you will receive a password reset link shortly.
                    </p>
                    <p className="text-sm text-gray-500 mb-6">
                        Please check your inbox and spam folder.
                    </p>
                    <Link
                        to="/login"
                        className="inline-flex items-center text-purple-600 hover:text-purple-700 font-medium"
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Login
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
            </div>

            <div className="relative w-full max-w-md">
                <div className="text-center mb-8">
                    <Link to="/" className="inline-flex items-center justify-center space-x-2 mb-4">
                        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-3 rounded-xl">
                            <Brain className="h-8 w-8 text-white" />
                        </div>
                    </Link>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Forgot Password?</h1>
                    <p className="text-gray-600">No worries, we'll send you reset instructions</p>
                </div>

                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-gray-200">
                    {error && (
                        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
                            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                            <p className="text-sm text-red-800">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                Email Address
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Mail className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent transition-all"
                                    placeholder="you@example.com"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center">
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                    Sending...
                                </span>
                            ) : (
                                'Send Reset Link'
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <Link
                            to="/login"
                            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back to Login
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};
