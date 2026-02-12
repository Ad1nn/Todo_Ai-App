/**
 * Home page - ChatKit as primary interface.
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { Layout } from '@/components/layout/Layout';
import { Spinner } from '@/components/ui/Spinner';

export default function HomePage() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Loading state while checking auth
  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </main>
    );
  }

  // Redirect handled by useEffect
  if (!isAuthenticated) {
    return null;
  }

  return (
    <Layout>
      {/* Chat interface for AI task management */}
      <div className="h-[calc(100vh-4rem)] overflow-hidden">
        <ChatInterface className="h-full" />
      </div>
    </Layout>
  );
}
