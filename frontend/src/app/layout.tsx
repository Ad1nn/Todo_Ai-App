/**
 * Root layout with providers and global styles.
 */

import type { Metadata } from 'next';
import { Providers } from '@/providers/Providers';
import './globals.css';

// System font stack for Docker build compatibility (no external fetch required)
const fontClassName = 'font-sans';

export const metadata: Metadata = {
  title: 'Todo App',
  description: 'AI-powered task management with natural language',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={fontClassName}>
        <Providers>
          {/* Skip to main content link for keyboard users */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:z-[100] focus:top-4 focus:left-4 focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-lg focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            Skip to main content
          </a>
          <div className="min-h-screen flex flex-col">
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
