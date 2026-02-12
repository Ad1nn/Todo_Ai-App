'use client';

/**
 * Hook for responsive design breakpoint detection.
 * Matches Tailwind CSS breakpoints.
 */

import { useEffect, useState } from 'react';

const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

type BreakpointKey = keyof typeof breakpoints;

/**
 * Returns true if the viewport matches the given media query.
 * @param query - CSS media query string
 */
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handler = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}

/**
 * Returns true if the viewport is at least the given breakpoint width.
 * @param breakpoint - Tailwind breakpoint key
 */
export function useBreakpoint(breakpoint: BreakpointKey): boolean {
  return useMediaQuery(`(min-width: ${breakpoints[breakpoint]})`);
}

/**
 * Returns true if the viewport is below the given breakpoint width.
 * @param breakpoint - Tailwind breakpoint key
 */
export function useBelowBreakpoint(breakpoint: BreakpointKey): boolean {
  return useMediaQuery(`(max-width: ${breakpoints[breakpoint]})`);
}

/**
 * Convenience hook for mobile detection (below md breakpoint).
 */
export function useIsMobile(): boolean {
  return useBelowBreakpoint('md');
}

/**
 * Convenience hook for desktop detection (at or above lg breakpoint).
 */
export function useIsDesktop(): boolean {
  return useBreakpoint('lg');
}
