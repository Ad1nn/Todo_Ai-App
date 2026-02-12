/**
 * Notification center dropdown with list of notifications.
 */

'use client';

import { Fragment, useState } from 'react';
import { Menu, Transition } from '@headlessui/react';
import {
  CheckIcon,
  TrashIcon,
  BellSlashIcon,
  Cog6ToothIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { NotificationSettings } from '@/components/NotificationSettings';
import { NotificationBell } from '@/components/NotificationBell';
import type { Notification } from '@/lib/types';
import { NOTIFICATION_TYPE_CONFIG } from '@/lib/types';
import { cn } from '@/lib/utils';

interface NotificationCenterProps {
  notifications: Notification[];
  unreadCount: number;
  onMarkAsRead: (id: string) => Promise<void>;
  onMarkAllAsRead: () => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onClearOld?: (daysOld: number) => Promise<void>;
  isLoading?: boolean;
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function NotificationCenter({
  notifications,
  unreadCount,
  onMarkAsRead,
  onMarkAllAsRead,
  onDelete,
  onClearOld,
  isLoading = false,
}: NotificationCenterProps) {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <Menu as="div" className="relative">
      {({ open }) => (
        <>
          <Menu.Button as={Fragment}>
            <div>
              <NotificationBell
                unreadCount={unreadCount}
                onClick={() => {}}
                isOpen={open}
              />
            </div>
          </Menu.Button>

          <Transition
            as={Fragment}
            enter="transition ease-out duration-200"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-150"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <Menu.Items className="absolute right-0 mt-2 w-80 sm:w-96 origin-top-right rounded-xl bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5 dark:ring-gray-700 focus:outline-none overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                  {showSettings ? 'Settings' : 'Notifications'}
                </h3>
                <div className="flex items-center gap-2">
                  {!showSettings && unreadCount > 0 && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        onMarkAllAsRead();
                      }}
                      className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium"
                    >
                      Mark all as read
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setShowSettings(!showSettings);
                    }}
                    className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                    title={showSettings ? 'Back to notifications' : 'Settings'}
                  >
                    {showSettings ? (
                      <XMarkIcon className="h-4 w-4" />
                    ) : (
                      <Cog6ToothIcon className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Settings View */}
              {showSettings ? (
                <NotificationSettings onClose={() => setShowSettings(false)} />
              ) : (
              <>
              {/* Notification List */}
              <div className="max-h-96 overflow-y-auto">
                {isLoading ? (
                  <div className="px-4 py-8 text-center">
                    <div className="animate-spin h-6 w-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto" />
                    <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                      Loading notifications...
                    </p>
                  </div>
                ) : notifications.length === 0 ? (
                  <div className="px-4 py-8 text-center">
                    <BellSlashIcon className="h-10 w-10 text-gray-300 dark:text-gray-600 mx-auto" />
                    <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                      No notifications yet
                    </p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100 dark:divide-gray-700">
                    {notifications.map((notification) => {
                      const config = NOTIFICATION_TYPE_CONFIG[notification.type];
                      return (
                        <Menu.Item key={notification.id}>
                          {({ active }) => (
                            <div
                              className={cn(
                                'px-4 py-3 flex gap-3',
                                active && 'bg-gray-50 dark:bg-gray-700/50',
                                !notification.read && 'bg-indigo-50/50 dark:bg-indigo-900/20'
                              )}
                            >
                              {/* Icon */}
                              <span
                                className={cn(
                                  'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm',
                                  config.bgColor
                                )}
                              >
                                {config.icon}
                              </span>

                              {/* Content */}
                              <div className="flex-1 min-w-0">
                                <p
                                  className={cn(
                                    'text-sm',
                                    notification.read
                                      ? 'text-gray-600 dark:text-gray-300'
                                      : 'text-gray-900 dark:text-white font-medium'
                                  )}
                                >
                                  {notification.title}
                                </p>
                                {notification.message && (
                                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">
                                    {notification.message}
                                  </p>
                                )}
                                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                                  {formatTimeAgo(notification.created_at)}
                                </p>
                              </div>

                              {/* Actions */}
                              <div className="flex-shrink-0 flex items-start gap-1">
                                {!notification.read && (
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      onMarkAsRead(notification.id);
                                    }}
                                    className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-400 hover:text-green-600 dark:hover:text-green-400 transition-colors"
                                    title="Mark as read"
                                  >
                                    <CheckIcon className="h-4 w-4" />
                                  </button>
                                )}
                                <button
                                  type="button"
                                  onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    onDelete(notification.id);
                                  }}
                                  className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                                  title="Delete"
                                >
                                  <TrashIcon className="h-4 w-4" />
                                </button>
                              </div>
                            </div>
                          )}
                        </Menu.Item>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Footer */}
              {notifications.length > 0 && (
                <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-between">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {notifications.length} notification{notifications.length !== 1 ? 's' : ''}
                  </p>
                  {onClearOld && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        onClearOld(30);
                      }}
                      className="text-xs text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                    >
                      Clear old
                    </button>
                  )}
                </div>
              )}
              </>
              )}
            </Menu.Items>
          </Transition>
        </>
      )}
    </Menu>
  );
}
