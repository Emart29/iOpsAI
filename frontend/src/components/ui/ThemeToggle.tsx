import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

export const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle theme"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
            {theme === 'light' ? (
                <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            ) : (
                <Sun className="w-5 h-5 text-yellow-500" />
            )}
        </button>
    );
};
