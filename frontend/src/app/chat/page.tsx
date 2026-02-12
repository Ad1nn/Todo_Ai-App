'use client';

/**
 * Chat page - redirects to home where ChatKit is the primary interface.
 * Kept for backwards compatibility.
 */

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
  const router = useRouter();

  useEffect(() => {
    // ChatKit is now the primary interface on the home page
    router.replace('/');
  }, [router]);

  return (
    <div className="flex h-screen items-center justify-center">
      <p className="text-gray-500 dark:text-gray-400">Redirecting...</p>
    </div>
  );
}
