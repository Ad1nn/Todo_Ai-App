/**
 * Notifications hook for managing notification state and operations.
 */

'use client';

import { useCallback } from 'react';
import useSWR from 'swr';

import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import type { Notification } from '@/lib/types';

interface UnreadCountResponse {
  unread_count: number;
}

interface MarkAllReadResponse {
  marked_as_read: number;
}

const notificationsFetcher = () => api.get<Notification[]>('/api/v1/notifications');
const unreadCountFetcher = () => api.get<UnreadCountResponse>('/api/v1/notifications/unread-count');

export function useNotifications() {
  const { isAuthenticated } = useAuth();

  const {
    data: notifications,
    error: notificationsError,
    isLoading: notificationsLoading,
    mutate: mutateNotifications,
  } = useSWR(
    isAuthenticated ? 'notifications' : null,
    notificationsFetcher,
    {
      refreshInterval: 30000, // Poll every 30 seconds
      revalidateOnFocus: true,
    }
  );

  const {
    data: unreadCountData,
    error: unreadCountError,
    mutate: mutateUnreadCount,
  } = useSWR(
    isAuthenticated ? 'notifications-unread-count' : null,
    unreadCountFetcher,
    {
      refreshInterval: 15000, // Poll every 15 seconds for unread count
      revalidateOnFocus: true,
    }
  );

  const markAsRead = useCallback(
    async (notificationId: string): Promise<Notification> => {
      const result = await api.post<Notification>(
        `/api/v1/notifications/${notificationId}/read`
      );
      await Promise.all([mutateNotifications(), mutateUnreadCount()]);
      return result;
    },
    [mutateNotifications, mutateUnreadCount]
  );

  const markAllAsRead = useCallback(async (): Promise<number> => {
    const result = await api.post<MarkAllReadResponse>(
      '/api/v1/notifications/mark-all-read'
    );
    await Promise.all([mutateNotifications(), mutateUnreadCount()]);
    return result.marked_as_read;
  }, [mutateNotifications, mutateUnreadCount]);

  const deleteNotification = useCallback(
    async (notificationId: string): Promise<void> => {
      await api.delete(`/api/v1/notifications/${notificationId}`);
      await Promise.all([mutateNotifications(), mutateUnreadCount()]);
    },
    [mutateNotifications, mutateUnreadCount]
  );

  const clearOldNotifications = useCallback(
    async (daysOld: number = 30): Promise<number> => {
      const result = await api.delete<{ deleted: number }>(
        `/api/v1/notifications/clear?days_old=${daysOld}`
      );
      await mutateNotifications();
      return result.deleted;
    },
    [mutateNotifications]
  );

  return {
    notifications: notifications ?? [],
    unreadCount: unreadCountData?.unread_count ?? 0,
    isLoading: notificationsLoading,
    error: notificationsError || unreadCountError,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearOldNotifications,
    refresh: async () => {
      await Promise.all([mutateNotifications(), mutateUnreadCount()]);
    },
  };
}
