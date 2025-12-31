import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-light-hover dark:bg-dark-hover hover:bg-light-border dark:hover:bg-dark-border transition-colors"
      aria-label="Toggle theme"
    >
      <span className="text-sm font-medium">
        {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
      </span>
      <div className="w-8 h-8 flex items-center justify-center">
        {theme === 'dark' ? (
          <Moon className="w-4 h-4" />
        ) : (
          <Sun className="w-4 h-4" />
        )}
      </div>
    </button>
  );
};

export default ThemeToggle;
