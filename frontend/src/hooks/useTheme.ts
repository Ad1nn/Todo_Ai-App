'use client';

/**
 * Hook for accessing and managing theme state.
 * Re-exports useThemeContext for convenience.
 */

export { useThemeContext as useTheme } from '@/providers/ThemeProvider';
export type { Theme } from '@/providers/ThemeProvider';
