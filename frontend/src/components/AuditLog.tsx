/**
 * Audit log component with filtering and list display.
 */

'use client';

import { useState } from 'react';
import { ClockIcon, FunnelIcon } from '@heroicons/react/24/outline';
import { AuditEntry } from '@/components/AuditEntry';
import { useAudit } from '@/hooks/useAudit';
import type { AuditAction } from '@/lib/types';
import { cn } from '@/lib/utils';

interface AuditLogProps {
  className?: string;
}

export function AuditLog({ className }: AuditLogProps) {
  const [actionFilter, setActionFilter] = useState<AuditAction | ''>('');
  const [showFilters, setShowFilters] = useState(false);

  const { entries, isLoading, error } = useAudit({
    action: actionFilter || undefined,
    limit: 100,
  });

  return (
    <div className={cn('rounded-xl bg-white dark:bg-gray-900 shadow-sm', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <ClockIcon className="h-5 w-5 text-gray-400" />
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
            Activity Log
          </h3>
        </div>
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            'p-1.5 rounded-lg transition-colors',
            showFilters || actionFilter
              ? 'text-indigo-600 bg-indigo-100 dark:text-indigo-400 dark:bg-indigo-900/30'
              : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
          )}
          aria-label="Toggle filters"
        >
          <FunnelIcon className="h-4 w-4" />
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="px-4 py-2 border-b border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value as AuditAction | '')}
            className="text-sm rounded-lg border border-gray-200 dark:border-gray-700 px-2 py-1 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="">All actions</option>
            <option value="create">Created</option>
            <option value="update">Updated</option>
            <option value="complete">Completed</option>
            <option value="delete">Deleted</option>
          </select>
        </div>
      )}

      {/* Content */}
      <div className="max-h-96 overflow-y-auto">
        {isLoading ? (
          <div className="px-4 py-8 text-center">
            <div className="animate-spin h-6 w-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Loading activity...
            </p>
          </div>
        ) : error ? (
          <div className="px-4 py-8 text-center">
            <p className="text-sm text-red-500 dark:text-red-400">
              Failed to load activity log
            </p>
          </div>
        ) : entries.length === 0 ? (
          <div className="px-4 py-8 text-center">
            <ClockIcon className="h-10 w-10 text-gray-300 dark:text-gray-600 mx-auto" />
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              No activity yet
            </p>
          </div>
        ) : (
          <div>
            {entries.map((entry) => (
              <AuditEntry key={entry.id} entry={entry} showEntityInfo />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {entries.length > 0 && (
        <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
          <p className="text-xs text-center text-gray-500 dark:text-gray-400">
            Showing {entries.length} entries
          </p>
        </div>
      )}
    </div>
  );
}
