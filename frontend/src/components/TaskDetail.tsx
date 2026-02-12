/**
 * Task detail view with audit history tab.
 */

'use client';

import { useState } from 'react';
import {
  CalendarIcon,
  ClockIcon,
  TagIcon,
  FlagIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import { AuditEntry } from '@/components/AuditEntry';
import { useTaskAudit } from '@/hooks/useAudit';
import type { Task } from '@/lib/types';
import {
  PRIORITY_CONFIG,
  RECURRENCE_CONFIG,
  formatDueDate,
  getDueDateStatus,
} from '@/lib/types';
import { cn } from '@/lib/utils';

interface TaskDetailProps {
  task: Task;
  onClose?: () => void;
}

type Tab = 'details' | 'history';

export function TaskDetail({ task, onClose }: TaskDetailProps) {
  const [activeTab, setActiveTab] = useState<Tab>('details');
  const { entries: auditEntries, isLoading: auditLoading } = useTaskAudit(task.id);

  const dueDateStatus = getDueDateStatus(task);

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        <button
          type="button"
          onClick={() => setActiveTab('details')}
          className={cn(
            'flex-1 py-3 text-sm font-medium text-center transition-colors',
            activeTab === 'details'
              ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
          )}
        >
          Details
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('history')}
          className={cn(
            'flex-1 py-3 text-sm font-medium text-center transition-colors',
            activeTab === 'history'
              ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
          )}
        >
          History
          {auditEntries.length > 0 && (
            <span className="ml-1.5 px-1.5 py-0.5 text-xs rounded-full bg-gray-200 dark:bg-gray-700">
              {auditEntries.length}
            </span>
          )}
        </button>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'details' ? (
          <div className="p-4 space-y-4">
            {/* Title and status */}
            <div>
              <div className="flex items-start gap-2">
                <span
                  className={cn(
                    'mt-1 w-4 h-4 rounded-full border-2 flex-shrink-0',
                    task.completed
                      ? 'bg-green-500 border-green-500'
                      : 'border-gray-300 dark:border-gray-600'
                  )}
                />
                <h3
                  className={cn(
                    'text-lg font-semibold',
                    task.completed
                      ? 'text-gray-400 dark:text-gray-500 line-through'
                      : 'text-gray-900 dark:text-white'
                  )}
                >
                  {task.title}
                </h3>
              </div>
            </div>

            {/* Description */}
            {task.description && (
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {task.description}
                </p>
              </div>
            )}

            {/* Meta info */}
            <div className="space-y-3">
              {/* Due date */}
              {task.due_date && (
                <div className="flex items-center gap-3">
                  <CalendarIcon className="h-4 w-4 text-gray-400" />
                  <span
                    className={cn(
                      'text-sm',
                      dueDateStatus === 'overdue' &&
                        'text-red-600 dark:text-red-400 font-medium',
                      dueDateStatus === 'today' &&
                        'text-amber-600 dark:text-amber-400 font-medium',
                      dueDateStatus !== 'overdue' &&
                        dueDateStatus !== 'today' &&
                        'text-gray-600 dark:text-gray-400'
                    )}
                  >
                    {formatDueDate(task.due_date)}
                  </span>
                </div>
              )}

              {/* Priority */}
              {task.priority && (
                <div className="flex items-center gap-3">
                  <FlagIcon className="h-4 w-4 text-gray-400" />
                  <span
                    className={cn(
                      'text-sm font-medium',
                      PRIORITY_CONFIG[task.priority].color
                    )}
                  >
                    {PRIORITY_CONFIG[task.priority].label}
                  </span>
                </div>
              )}

              {/* Category */}
              {task.category && (
                <div className="flex items-center gap-3">
                  <TagIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {task.category}
                  </span>
                </div>
              )}

              {/* Recurrence */}
              {task.recurrence_rule && task.recurrence_rule !== 'none' && (
                <div className="flex items-center gap-3">
                  <ArrowPathIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {RECURRENCE_CONFIG[task.recurrence_rule].icon}{' '}
                    {RECURRENCE_CONFIG[task.recurrence_rule].description}
                  </span>
                </div>
              )}

              {/* Timestamps */}
              <div className="pt-3 border-t border-gray-100 dark:border-gray-800">
                <div className="flex items-center gap-3 text-xs text-gray-400">
                  <ClockIcon className="h-3.5 w-3.5" />
                  <span>
                    Created {new Date(task.created_at).toLocaleDateString()}
                  </span>
                </div>
                {task.updated_at !== task.created_at && (
                  <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
                    <ClockIcon className="h-3.5 w-3.5" />
                    <span>
                      Updated {new Date(task.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div>
            {auditLoading ? (
              <div className="px-4 py-8 text-center">
                <div className="animate-spin h-6 w-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto" />
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Loading history...
                </p>
              </div>
            ) : auditEntries.length === 0 ? (
              <div className="px-4 py-8 text-center">
                <ClockIcon className="h-10 w-10 text-gray-300 dark:text-gray-600 mx-auto" />
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  No history yet
                </p>
              </div>
            ) : (
              <div>
                {auditEntries.map((entry) => (
                  <AuditEntry key={entry.id} entry={entry} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
