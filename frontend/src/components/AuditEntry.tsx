/**
 * Single audit entry display component.
 */

'use client';

import { useState } from 'react';
import {
  PlusCircleIcon,
  PencilSquareIcon,
  CheckCircleIcon,
  TrashIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline';
import type { AuditEntry as AuditEntryType, AuditAction } from '@/lib/types';
import { cn } from '@/lib/utils';

interface AuditEntryProps {
  entry: AuditEntryType;
  showEntityInfo?: boolean;
}

const actionConfig: Record<
  AuditAction,
  { icon: React.ReactNode; label: string; color: string; bgColor: string }
> = {
  create: {
    icon: <PlusCircleIcon className="h-4 w-4" />,
    label: 'Created',
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
  },
  update: {
    icon: <PencilSquareIcon className="h-4 w-4" />,
    label: 'Updated',
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-100 dark:bg-blue-900/30',
  },
  complete: {
    icon: <CheckCircleIcon className="h-4 w-4" />,
    label: 'Completed',
    color: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-100 dark:bg-purple-900/30',
  },
  delete: {
    icon: <TrashIcon className="h-4 w-4" />,
    label: 'Deleted',
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-900/30',
  },
};

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

function formatFieldChange(
  field: string,
  before: unknown,
  after: unknown
): string {
  const formatValue = (v: unknown): string => {
    if (v === null || v === undefined) return 'none';
    if (typeof v === 'boolean') return v ? 'yes' : 'no';
    return String(v);
  };

  return `${field}: ${formatValue(before)} → ${formatValue(after)}`;
}

export function AuditEntry({ entry, showEntityInfo = false }: AuditEntryProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const config = actionConfig[entry.action];

  // Calculate what changed - use type assertion for dynamic access
  const changes: string[] = [];
  if (entry.before_value && entry.after_value) {
    const beforeRecord = entry.before_value as Record<string, unknown>;
    const afterRecord = entry.after_value as Record<string, unknown>;
    const allKeys = new Set([
      ...Object.keys(beforeRecord),
      ...Object.keys(afterRecord),
    ]);

    for (const key of allKeys) {
      if (key === 'id') continue; // Skip ID
      const before = beforeRecord[key];
      const after = afterRecord[key];
      if (JSON.stringify(before) !== JSON.stringify(after)) {
        changes.push(formatFieldChange(key, before, after));
      }
    }
  }

  const hasDetails =
    changes.length > 0 || entry.before_value || entry.after_value;

  return (
    <div
      className={cn(
        'px-4 py-3 border-b border-gray-100 dark:border-gray-800',
        'hover:bg-gray-50 dark:hover:bg-gray-800/50',
        'transition-colors duration-150'
      )}
    >
      <div className="flex items-start gap-3">
        {/* Action icon */}
        <div
          className={cn(
            'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
            config.bgColor,
            config.color
          )}
        >
          {config.icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={cn('text-sm font-medium', config.color)}>
              {config.label}
            </span>
            {showEntityInfo && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {entry.entity_type}
              </span>
            )}
          </div>

          {/* Summary of changes */}
          {entry.action === 'create' && entry.after_value?.title && (
            <p className="text-sm text-gray-700 dark:text-gray-300 mt-0.5">
              &ldquo;{entry.after_value.title}&rdquo;
            </p>
          )}
          {entry.action === 'delete' && entry.before_value?.title && (
            <p className="text-sm text-gray-700 dark:text-gray-300 mt-0.5">
              &ldquo;{entry.before_value.title}&rdquo;
            </p>
          )}
          {entry.action === 'update' && changes.length > 0 && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {changes.length} field{changes.length !== 1 ? 's' : ''} changed
            </p>
          )}

          {/* Timestamp */}
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            {formatTimestamp(entry.timestamp)}
          </p>
        </div>

        {/* Expand button */}
        {hasDetails && (
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            aria-label={isExpanded ? 'Collapse details' : 'Expand details'}
          >
            {isExpanded ? (
              <ChevronUpIcon className="h-4 w-4" />
            ) : (
              <ChevronDownIcon className="h-4 w-4" />
            )}
          </button>
        )}
      </div>

      {/* Expanded details */}
      {isExpanded && hasDetails && (
        <div className="mt-3 ml-11 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg text-xs font-mono">
          {changes.length > 0 ? (
            <ul className="space-y-1">
              {changes.map((change, idx) => (
                <li key={idx} className="text-gray-600 dark:text-gray-400">
                  {change}
                </li>
              ))}
            </ul>
          ) : (
            <pre className="text-gray-600 dark:text-gray-400 overflow-x-auto">
              {JSON.stringify(
                entry.after_value || entry.before_value,
                null,
                2
              )}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
