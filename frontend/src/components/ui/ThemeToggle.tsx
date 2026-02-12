'use client';

/**
 * Linear-inspired theme toggle with smooth animations.
 */

import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

export type ThemeToggleSize = 'sm' | 'md' | 'lg';

export interface ThemeToggleProps {
  className?: string;
  size?: ThemeToggleSize;
}

const sizeStyles: Record<ThemeToggleSize, { button: string; icon: string }> = {
  sm: { button: 'h-8 w-8', icon: 'h-4 w-4' },
  md: { button: 'h-9 w-9', icon: 'h-4.5 w-4.5' },
  lg: { button: 'h-10 w-10', icon: 'h-5 w-5' },
};

export function ThemeToggle({ className, size = 'md' }: ThemeToggleProps) {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const styles = sizeStyles[size];

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={cn(
        'inline-flex items-center justify-center rounded-lg',
        'text-gray-500 dark:text-gray-400',
        'hover:bg-amber-500/10 dark:hover:bg-indigo-500/10',
        'hover:text-amber-600 dark:hover:text-indigo-400',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
        'transition-all duration-200',
        styles.button,
        className
      )}
      aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {resolvedTheme === 'dark' ? (
        <SunIcon className={cn(styles.icon, 'transition-transform duration-200 hover:rotate-45')} aria-hidden="true" />
      ) : (
        <MoonIcon className={cn(styles.icon, 'transition-transform duration-200 hover:-rotate-12')} aria-hidden="true" />
      )}
    </button>
  );
}
