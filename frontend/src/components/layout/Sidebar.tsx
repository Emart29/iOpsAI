import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    Home, Upload, FileText, Brain, BarChart3, MessageSquare,
    FileDown, Droplet, Code, Lightbulb, BookOpen, Menu, X, Activity, LogIn, LogOut, UserPlus
} from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
    activeSection: string;
    onSectionChange: (section: string) => void;
}

const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'upload', label: 'Upload Data', icon: Upload },
    { id: 'summary', label: 'Data Summary', icon: FileText },
    { id: 'profile', label: 'Deep Profile', icon: Activity },
    { id: 'insights', label: 'AI Insights', icon: Brain },
    { id: 'charts', label: 'Charts', icon: BarChart3 },
    { id: 'ml', label: 'AutoML', icon: Brain },
    { id: 'chat', label: 'Sight Chatbot', icon: MessageSquare },
    { id: 'report', label: 'EDA Report', icon: FileDown },
    { id: 'clean', label: 'Clean Data', icon: Droplet },
    { id: 'script', label: 'Python Script', icon: Code },
    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
    { id: 'experiments', label: 'Experiment Log', icon: BookOpen },
];

export const Sidebar = ({ activeSection, onSectionChange }: SidebarProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const { user, isAuthenticated, logout } = useAuth();

    return (
        <>
            {/* Mobile menu button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="md:hidden fixed top-4 left-4 z-50 bg-gray-900 text-white p-2 rounded-lg"
            >
                {isOpen ? <X /> : <Menu />}
            </button>

            {/* Sidebar */}
            <aside className={`
        fixed left-0 top-0 h-screen bg-gray-900 text-white w-64 transform transition-transform duration-300 z-40
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
                <div className="p-6 border-b border-gray-800 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <div className="bg-purple-600 p-2 rounded-lg">
                            <Brain className="h-6 w-6" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">iOps</h1>
                            <p className="text-xs text-gray-400">Insight Studio</p>
                        </div>
                    </div>
                    <ThemeToggle />
                </div>

                <nav className="p-4 overflow-y-auto h-[calc(100vh-100px)] flex flex-col">
                    <ul className="space-y-2 flex-1">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            return (
                                <li key={item.id}>
                                    <button
                                        onClick={() => {
                                            onSectionChange(item.id);
                                            setIsOpen(false);
                                        }}
                                        className={`
                      w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all
                      ${activeSection === item.id
                                                ? 'bg-purple-600 text-white'
                                                : 'text-gray-300 hover:bg-gray-800'
                                            }
                    `}
                                    >
                                        <Icon className="w-5 h-5" />
                                        <span className="text-sm font-medium">{item.label}</span>
                                    </button>
                                </li>
                            );
                        })}
                    </ul>

                    {/* Auth Section */}
                    <div className="mt-4 pt-4 border-t border-gray-800">
                        {isAuthenticated ? (
                            <div className="space-y-2">
                                <div className="px-4 py-2 bg-gray-800 rounded-lg">
                                    <p className="text-xs text-gray-400">Signed in as</p>
                                    <p className="text-sm font-medium text-white truncate">{user?.email}</p>
                                </div>
                                <button
                                    onClick={() => {
                                        logout();
                                        setIsOpen(false);
                                    }}
                                    className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 transition-all"
                                >
                                    <LogOut className="w-5 h-5" />
                                    <span className="text-sm font-medium">Logout</span>
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <Link
                                    to="/login"
                                    className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 transition-all"
                                    onClick={() => setIsOpen(false)}
                                >
                                    <LogIn className="w-5 h-5" />
                                    <span className="text-sm font-medium">Login</span>
                                </Link>
                                <Link
                                    to="/register"
                                    className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg bg-purple-600 hover:bg-purple-700 text-white transition-all"
                                    onClick={() => setIsOpen(false)}
                                >
                                    <UserPlus className="w-5 h-5" />
                                    <span className="text-sm font-medium">Sign Up</span>
                                </Link>
                            </div>
                        )}
                    </div>
                </nav>
            </aside>

            {/* Overlay for mobile */}
            {isOpen && (
                <div
                    onClick={() => setIsOpen(false)}
                    className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
                />
            )}
        </>
    );
};
