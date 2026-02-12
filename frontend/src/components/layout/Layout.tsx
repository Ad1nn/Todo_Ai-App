'use client';

/**
 * Minimal Apple-like application layout.
 */

import { useState, type ReactNode } from 'react';
import {
  ChatBubbleLeftRightIcon,
  Squares2X2Icon,
} from '@heroicons/react/24/outline';
import { Header } from './Header';
import { Sidebar, type NavItem } from './Sidebar';
import { MobileNav } from './MobileNav';
import { cn } from '@/lib/utils';

const navigationItems: NavItem[] = [
  {
    label: 'Chat',
    href: '/',
    icon: <ChatBubbleLeftRightIcon className="h-4 w-4" />,
  },
  {
    label: 'All Tasks',
    href: '/tasks',
    icon: <Squares2X2Icon className="h-4 w-4" />,
  },
];

interface LayoutProps {
  children: ReactNode;
  showSidebar?: boolean;
  headerActions?: ReactNode;
  className?: string;
}

export function Layout({
  children,
  showSidebar = true,
  headerActions,
  className,
}: LayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-white dark:bg-black">
      {/* Desktop Sidebar */}
      {showSidebar && <Sidebar items={navigationItems} />}

      {/* Mobile Navigation */}
      <MobileNav
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        items={navigationItems}
      />

      {/* Main content area */}
      <div className={cn(showSidebar && 'lg:pl-56')}>
        {/* Header */}
        <Header
          showMobileMenuToggle={showSidebar}
          onMobileMenuToggle={() => setMobileMenuOpen(true)}
          actions={headerActions}
        />

        {/* Page content */}
        <main
          id="main-content"
          className={cn('flex-1 bg-white dark:bg-black', className)}
          tabIndex={-1}
        >
          {children}
        </main>

        {/* ARIA live region */}
        <div
          id="announcer"
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className="sr-only"
        />
      </div>
    </div>
  );
}
