import { Sparkles, Play } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Hero = () => {
    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-purple-50 via-white to-blue-50">
            {/* Animated background elements */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
                <div className="absolute top-40 left-40 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
            </div>

            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32 text-center">
                <div className="inline-flex items-center px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-8 animate-fade-in">
                    <Sparkles className="w-4 h-4 mr-2" />
                    AI-Powered Data Analysis
                </div>

                <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 animate-fade-in-up">
                    iOps: <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">Your Data Science Copilot</span>
                </h1>

                <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto animate-fade-in-up animation-delay-200">
                    Upload your data, chat with Sight AI, and get instant insights. Transform raw data into actionable intelligence in seconds.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in-up animation-delay-400">
                    <Link
                        to="/dashboard"
                        className="group relative px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 flex items-center"
                    >
                        Launch Insight Studio
                        <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                    </Link>

                    <button className="px-8 py-4 border-2 border-purple-600 text-purple-600 rounded-xl font-semibold text-lg hover:bg-purple-50 transition-all duration-200 flex items-center">
                        <Play className="w-5 h-5 mr-2" />
                        Watch Demo
                    </button>
                </div>

                {/* Stats */}
                <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
                    <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
                        <div className="text-4xl font-bold text-purple-600 mb-2">10x</div>
                        <div className="text-gray-600">Faster Analysis</div>
                    </div>
                    <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
                        <div className="text-4xl font-bold text-purple-600 mb-2">AI-Powered</div>
                        <div className="text-gray-600">Insights Generation</div>
                    </div>
                    <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
                        <div className="text-4xl font-bold text-purple-600 mb-2">100%</div>
                        <div className="text-gray-600">Automated EDA</div>
                    </div>
                </div>
            </div>
        </section>
    );
};
