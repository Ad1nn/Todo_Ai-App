/**
 * Notification context provider for global notification state.
 */

'use client';

import {
  createContext,
  useContext,
  useCallback,
  useState,
  useEffect,
  type ReactNode,
} from 'react';
import { useNotifications } from '@/hooks/useNotifications';
import { useToast } from '@/providers/ToastProvider';
import { useAuth } from '@/hooks/useAuth';
import type { Notification } from '@/lib/types';

interface NotificationContextValue {
  // Notification data
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: Error | null;

  // Notification actions
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  refresh: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextValue | null>(null);

interface NotificationProviderProps {
  children: ReactNode;
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  const { isAuthenticated } = useAuth();
  const toast = useToast();

  // Only use notifications when authenticated
  const {
    notifications,
    unreadCount,
    isLoading,
    error,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    refresh,
  } = useNotifications();

  const [previousUnreadCount, setPreviousUnreadCount] = useState(0);

  // Show toast when new notifications arrive (only when authenticated)
  useEffect(() => {
    if (!isAuthenticated) {
      setPreviousUnreadCount(0);
      return;
    }

    if (unreadCount > previousUnreadCount && previousUnreadCount > 0) {
      // New notification arrived
      const newCount = unreadCount - previousUnreadCount;
      toast.info(
        `${newCount} new notification${newCount > 1 ? 's' : ''}`,
        'Check your notifications'
      );
    }
    setPreviousUnreadCount(unreadCount);
  }, [unreadCount, previousUnreadCount, isAuthenticated, toast]);

  const handleMarkAsRead = useCallback(
    async (id: string) => {
      try {
        await markAsRead(id);
      } catch (err) {
        toast.error(
          'Failed to mark as read',
          err instanceof Error ? err.message : 'Unknown error'
        );
      }
    },
    [markAsRead, toast]
  );

  const handleMarkAllAsRead = useCallback(async () => {
    try {
      const count = await markAllAsRead();
      if (count > 0) {
        toast.success(
          'All caught up!',
          `Marked ${count} notification${count > 1 ? 's' : ''} as read`
        );
      }
    } catch (err) {
      toast.error(
        'Failed to mark all as read',
        err instanceof Error ? err.message : 'Unknown error'
      );
    }
  }, [markAllAsRead, toast]);

  const handleDeleteNotification = useCallback(
    async (id: string) => {
      try {
        await deleteNotification(id);
      } catch (err) {
        toast.error(
          'Failed to delete notification',
          err instanceof Error ? err.message : 'Unknown error'
        );
      }
    },
    [deleteNotification, toast]
  );

  const value: NotificationContextValue = {
    notifications: isAuthenticated ? notifications : [],
    unreadCount: isAuthenticated ? unreadCount : 0,
    isLoading,
    error: error as Error | null,
    markAsRead: handleMarkAsRead,
    markAllAsRead: handleMarkAllAsRead,
    deleteNotification: handleDeleteNotification,
    refresh,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotificationContext() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error(
      'useNotificationContext must be used within a NotificationProvider'
    );
  }
  return context;
}
