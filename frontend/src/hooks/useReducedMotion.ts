/**
 * Hook to check if the user prefers reduced motion.
 * Respects the prefers-reduced-motion media query.
 */

import { useState, useEffect } from 'react';

/**
 * Returns true if the user has requested reduced motion in their system settings.
 * Use this to disable or simplify animations for users with vestibular disorders.
 *
 * @example
 * const prefersReducedMotion = useReducedMotion();
 * return (
 *   <div className={prefersReducedMotion ? '' : 'animate-bounce'}>
 *     Content
 *   </div>
 * );
 */
export function useReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    // Check if we're in the browser
    if (typeof window === 'undefined') {
      return;
    }

    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    // Set initial value
    setPrefersReducedMotion(mediaQuery.matches);

    // Listen for changes
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    // Modern browsers support addEventListener
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  return prefersReducedMotion;
}
