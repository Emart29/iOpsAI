import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Settings, LogOut, Database, Bell, HelpCircle, ChevronDown } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from '../ui/ToastProvider';
import { ThemeToggle } from '../ui/ThemeToggle';

export const UserMenu = () => {
    const [isOpen, setIsOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = () => {
        logout();
        toast.success('Logged out successfully');
        navigate('/login');
    };

    if (!user) return null;

    // Get initials for avatar
    const getInitials = () => {
        if (user.full_name) {
            return user.full_name
                .split(' ')
                .map((n: string) => n[0])
                .join('')
                .toUpperCase()
                .substring(0, 2);
        }
        return user.username.substring(0, 2).toUpperCase();
    };

    return (
        <div className="relative" ref={menuRef}>
            {/* Trigger Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
                {/* Avatar */}
                <div className="relative">
                    {user.profile_picture_url ? (
                        <img
                            src={user.profile_picture_url}
                            alt={user.username}
                            className="w-10 h-10 rounded-full object-cover"
                        />
                    ) : (
                        <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 flex items-center justify-center text-white font-semibold">
                            {getInitials()}
                        </div>
                    )}
                    {!user.is_verified && (
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 border-2 border-white rounded-full" title="Email not verified"></div>
                    )}
                </div>

                {/* User Info */}
                <div className="hidden md:block text-left">
                    <p className="text-sm font-medium text-gray-900">{user.full_name || user.username}</p>
                    <p className="text-xs text-gray-500">{user.email}</p>
                </div>

                {/* Chevron */}
                <ChevronDown className={`w-4 h-4 text-gray-600 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50 animate-fade-in">
                    {/* User Info Section */}
                    <div className="px-4 py-3 border-b border-gray-200">
                        <p className="text-sm font-semibold text-gray-900">{user.full_name || user.username}</p>
                        <p className="text-xs text-gray-500 mt-1">{user.email}</p>
                        {!user.is_verified && (
                            <div className="mt-2 flex items-center space-x-1 text-xs text-yellow-600">
                                <Bell className="w-3 h-3" />
                                <span>Email not verified</span>
                            </div>
                        )}
                    </div>

                    {/* Menu Items */}
                    <div className="py-2">
                        <Link
                            to="/profile"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center space-x-3 px-4 py-2 hover:bg-gray-50 transition-colors"
                        >
                            <User className="w-4 h-4 text-gray-600" />
                            <span className="text-sm text-gray-700">My Profile</span>
                        </Link>

                        <Link
                            to="/datasets"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center space-x-3 px-4 py-2 hover:bg-gray-50 transition-colors"
                        >
                            <Database className="w-4 h-4 text-gray-600" />
                            <span className="text-sm text-gray-700">My Datasets</span>
                        </Link>

                        <Link
                            to="/settings"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center space-x-3 px-4 py-2 hover:bg-gray-50 transition-colors"
                        >
                            <Settings className="w-4 h-4 text-gray-600" />
                            <span className="text-sm text-gray-700">Settings</span>
                        </Link>

                        <Link
                            to="/help"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center space-x-3 px-4 py-2 hover:bg-gray-50 transition-colors"
                        >
                            <HelpCircle className="w-4 h-4 text-gray-600" />
                            <span className="text-sm text-gray-700">Help & Support</span>
                        </Link>

                        <div className="border-t border-gray-200 my-1"></div>

                        <div className="px-4 py-2 flex items-center justify-between">
                            <span className="text-sm text-gray-700 font-medium">Dark Mode</span>
                            <ThemeToggle />
                        </div>
                    </div>

                    {/* Logout */}
                    <div className="border-t border-gray-200 pt-2">
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center space-x-3 px-4 py-2 hover:bg-red-50 transition-colors text-left"
                        >
                            <LogOut className="w-4 h-4 text-red-600" />
                            <span className="text-sm text-red-600 font-medium">Logout</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
