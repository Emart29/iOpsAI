import React, { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';

export const ThemeToggle: React.FC = () => {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
        // Check initial theme
        const savedTheme = localStorage.getItem('theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme === 'dark' || (!savedTheme && systemDark)) {
            setIsDark(true);
            document.documentElement.classList.add('dark');
        } else {
            setIsDark(false);
            document.documentElement.classList.remove('dark');
        }
    }, []);

    const toggleTheme = () => {
        if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            setIsDark(false);
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            setIsDark(true);
        }
    };

    return (
        <button
            onClick={toggleTheme}
            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
    );
};
