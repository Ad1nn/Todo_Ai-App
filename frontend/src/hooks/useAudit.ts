/**
 * Audit hook for fetching audit log entries.
 */

'use client';

import useSWR from 'swr';

import { api } from '@/lib/api';
import { useAuth } from '@/hooks/useAuth';
import type { AuditEntry, AuditAction } from '@/lib/types';

interface UseAuditOptions {
  entityType?: string;
  action?: AuditAction;
  limit?: number;
  offset?: number;
}

const buildAuditUrl = (options: UseAuditOptions): string => {
  const params = new URLSearchParams();
  if (options.entityType) params.set('entity_type', options.entityType);
  if (options.action) params.set('action', options.action);
  if (options.limit) params.set('limit', String(options.limit));
  if (options.offset) params.set('offset', String(options.offset));
  const queryString = params.toString();
  return `/api/v1/audit${queryString ? `?${queryString}` : ''}`;
};

const auditFetcher = (url: string) => api.get<AuditEntry[]>(url);
const taskAuditFetcher = (url: string) => api.get<AuditEntry[]>(url);

export function useAudit(options: UseAuditOptions = {}) {
  const { isAuthenticated } = useAuth();
  const url = buildAuditUrl(options);

  const {
    data: entries,
    error,
    isLoading,
    mutate,
  } = useSWR(
    isAuthenticated ? url : null,
    auditFetcher,
    {
      revalidateOnFocus: false,
    }
  );

  return {
    entries: entries ?? [],
    isLoading,
    error,
    refresh: mutate,
  };
}

export function useTaskAudit(taskId: string | null) {
  const { isAuthenticated } = useAuth();

  const {
    data: entries,
    error,
    isLoading,
    mutate,
  } = useSWR(
    isAuthenticated && taskId ? `/api/v1/audit/task/${taskId}` : null,
    taskAuditFetcher,
    {
      revalidateOnFocus: false,
    }
  );

  return {
    entries: entries ?? [],
    isLoading,
    error,
    refresh: mutate,
  };
}
