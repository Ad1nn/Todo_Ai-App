/**
 * Notification bell icon with unread count badge.
 */

'use client';

import { BellIcon } from '@heroicons/react/24/outline';
import { BellAlertIcon } from '@heroicons/react/24/solid';
import { cn } from '@/lib/utils';

interface NotificationBellProps {
  unreadCount: number;
  onClick: () => void;
  isOpen?: boolean;
}

export function NotificationBell({
  unreadCount,
  onClick,
  isOpen = false,
}: NotificationBellProps) {
  const hasUnread = unreadCount > 0;

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'relative p-2 rounded-lg transition-all duration-200',
        'hover:bg-gray-100 dark:hover:bg-gray-800',
        'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2',
        'dark:focus:ring-offset-gray-900',
        isOpen && 'bg-gray-100 dark:bg-gray-800'
      )}
      aria-label={`Notifications${hasUnread ? `, ${unreadCount} unread` : ''}`}
      aria-expanded={isOpen}
    >
      {hasUnread ? (
        <BellAlertIcon
          className={cn(
            'h-6 w-6 transition-colors',
            'text-indigo-600 dark:text-indigo-400',
            'animate-pulse'
          )}
        />
      ) : (
        <BellIcon className="h-6 w-6 text-gray-500 dark:text-gray-400" />
      )}

      {/* Unread count badge */}
      {hasUnread && (
        <span
          className={cn(
            'absolute -top-0.5 -right-0.5',
            'flex items-center justify-center',
            'min-w-[18px] h-[18px] px-1',
            'text-xs font-medium text-white',
            'bg-red-500 rounded-full',
            'ring-2 ring-white dark:ring-gray-900',
            'transform transition-transform duration-200',
            'animate-bounce-once'
          )}
        >
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}

      <style jsx>{`
        @keyframes bounce-once {
          0%,
          100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-25%);
          }
        }
        .animate-bounce-once {
          animation: bounce-once 0.5s ease-in-out;
        }
      `}</style>
    </button>
  );
}
