import { Brain, Github, Twitter, Linkedin } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer = () => {
    return (
        <footer className="bg-gray-900 text-gray-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                    <div className="col-span-1 md:col-span-2">
                        <div className="flex items-center space-x-2 mb-4">
                            <div className="bg-purple-600 p-1.5 rounded-lg">
                                <Brain className="h-6 w-6 text-white" />
                            </div>
                            <span className="text-xl font-bold text-white">iOps</span>
                        </div>
                        <p className="text-gray-400 mb-4 max-w-md">
                            Your AI-powered data science copilot. Transform raw data into actionable insights with the power of artificial intelligence.
                        </p>
                        <div className="flex space-x-4">
                            <a href="#" className="text-gray-400 hover:text-purple-400 transition-colors">
                                <Github className="w-5 h-5" />
                            </a>
                            <a href="#" className="text-gray-400 hover:text-purple-400 transition-colors">
                                <Twitter className="w-5 h-5" />
                            </a>
                            <a href="#" className="text-gray-400 hover:text-purple-400 transition-colors">
                                <Linkedin className="w-5 h-5" />
                            </a>
                        </div>
                    </div>

                    <div>
                        <h3 className="text-white font-semibold mb-4">Product</h3>
                        <ul className="space-y-2">
                            <li><a href="#features" className="hover:text-purple-400 transition-colors">Features</a></li>
                            <li><a href="#how-it-works" className="hover:text-purple-400 transition-colors">How It Works</a></li>
                            <li><Link to="/dashboard" className="hover:text-purple-400 transition-colors">Dashboard</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="text-white font-semibold mb-4">Legal</h3>
                        <ul className="space-y-2">
                            <li><a href="#" className="hover:text-purple-400 transition-colors">Privacy Policy</a></li>
                            <li><a href="#" className="hover:text-purple-400 transition-colors">Terms of Service</a></li>
                            <li><a href="#contact" className="hover:text-purple-400 transition-colors">Contact</a></li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
                    <p>&copy; {new Date().getFullYear()} iOps. All rights reserved.</p>
                </div>
            </div>
        </footer>
    );
};
