'use client';

/**
 * Linear-inspired header with glass effect and subtle accents.
 */

import { Bars2Icon, SparklesIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { ProfileDropdown } from '@/components/profile/ProfileDropdown';
import { NotificationCenter } from '@/components/NotificationCenter';
import { useNotificationContext } from '@/providers/NotificationProvider';
import { useAuth } from '@/hooks/useAuth';
import type { ReactNode } from 'react';

export interface HeaderProps {
  showMobileMenuToggle?: boolean;
  onMobileMenuToggle?: () => void;
  actions?: ReactNode;
  className?: string;
}

export function Header({
  showMobileMenuToggle = true,
  onMobileMenuToggle,
  actions,
  className,
}: HeaderProps) {
  const { isAuthenticated } = useAuth();
  const {
    notifications,
    unreadCount,
    isLoading: notificationsLoading,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  } = useNotificationContext();

  return (
    <header
      className={cn(
        'sticky top-0 z-40 h-14',
        'flex items-center justify-between px-4 lg:px-6',
        'glass',
        'border-b border-gray-200/50 dark:border-gray-800/50',
        className
      )}
    >
      <div className="flex items-center gap-3">
        {/* Mobile menu toggle */}
        {showMobileMenuToggle && onMobileMenuToggle && (
          <button
            type="button"
            onClick={onMobileMenuToggle}
            className={cn(
              'inline-flex h-9 w-9 items-center justify-center rounded-lg',
              'text-gray-500 hover:text-indigo-500 hover:bg-indigo-500/10',
              'transition-all duration-200',
              'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500',
              'lg:hidden',
              'dark:text-gray-400 dark:hover:text-indigo-400'
            )}
            aria-label="Open menu"
          >
            <Bars2Icon className="h-5 w-5" aria-hidden="true" />
          </button>
        )}

        {/* Logo/Title with accent */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <SparklesIcon className="h-4 w-4 text-white" />
            </div>
          </div>
          <h1 className="text-base font-semibold text-gray-900 dark:text-white">
            Tasks
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-1">
        {/* Theme toggle */}
        <ThemeToggle size="sm" />

        {/* Notifications (only when authenticated) */}
        {isAuthenticated && (
          <NotificationCenter
            notifications={notifications}
            unreadCount={unreadCount}
            onMarkAsRead={markAsRead}
            onMarkAllAsRead={markAllAsRead}
            onDelete={deleteNotification}
            isLoading={notificationsLoading}
          />
        )}

        {/* Custom actions */}
        {actions}

        {/* Profile dropdown */}
        <ProfileDropdown />
      </div>
    </header>
  );
}
