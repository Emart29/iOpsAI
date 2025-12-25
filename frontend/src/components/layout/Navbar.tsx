import { useState, useEffect } from 'react';
import { Brain, Menu, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';

export const Navbar = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled ? 'bg-white/80 backdrop-blur-md shadow-sm' : 'bg-transparent'}`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center">
                        <Link to="/" className="flex items-center space-x-2">
                            <div className="bg-purple-600 p-1.5 rounded-lg">
                                <Brain className="h-6 w-6 text-white" />
                            </div>
                            <span className="text-xl font-bold text-gray-900">iOps</span>
                        </Link>
                        {/* Dark mode toggle */}
                        <ThemeToggle />
                    </div>

                    <div className="hidden md:flex items-center space-x-8">
                        <a href="#features" className="text-gray-600 hover:text-purple-600 transition-colors">Features</a>
                        <a href="#how-it-works" className="text-gray-600 hover:text-purple-600 transition-colors">How It Works</a>
                        <a href="#contact" className="text-gray-600 hover:text-purple-600 transition-colors">Contact</a>
                        <Link to="/dashboard" className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors font-medium">
                            Launch App
                        </Link>
                    </div>

                    <div className="md:hidden">
                        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-gray-600">
                            {isMobileMenuOpen ? <X /> : <Menu />}
                        </button>
                    </div>
                </div>
            </div>

            {isMobileMenuOpen && (
                <div className="md:hidden bg-white border-t">
                    <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
                        <a href="#features" className="block px-3 py-2 text-gray-600 hover:text-purple-600">Features</a>
                        <a href="#how-it-works" className="block px-3 py-2 text-gray-600 hover:text-purple-600">How It Works</a>
                        <a href="#contact" className="block px-3 py-2 text-gray-600 hover:text-purple-600">Contact</a>
                        <Link to="/dashboard" className="block px-3 py-2 text-purple-600 font-medium">Launch App</Link>
                    </div>
                </div>
            )}
        </nav>
    );
};
