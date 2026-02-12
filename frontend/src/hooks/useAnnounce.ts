/**
 * Hook for announcing messages to screen readers via ARIA live regions.
 * Uses the #announcer element from Layout component.
 */

import { useCallback } from 'react';

export type AnnouncePoliteness = 'polite' | 'assertive';

/**
 * Hook that returns a function to announce messages to screen readers.
 * Uses the ARIA live region in the Layout component.
 */
export function useAnnounce() {
  const announce = useCallback(
    (message: string, politeness: AnnouncePoliteness = 'polite') => {
      const announcer = document.getElementById('announcer');
      if (!announcer) {
        console.warn('Announcer element not found. Make sure Layout is rendered.');
        return;
      }

      // Set politeness level
      announcer.setAttribute('aria-live', politeness);

      // Clear and set message (needed to trigger announcement for same message)
      announcer.textContent = '';

      // Use requestAnimationFrame to ensure the clear is processed
      requestAnimationFrame(() => {
        announcer.textContent = message;
      });
    },
    []
  );

  return announce;
}
