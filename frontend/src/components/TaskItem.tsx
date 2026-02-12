/**
 * Linear-inspired task item with priority indicators and animations.
 */

'use client';

import { useState } from 'react';
import { CheckIcon, PencilIcon, TrashIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { TaskForm } from '@/components/TaskForm';
import type { Task, TaskUpdate } from '@/lib/types';
import {
  PRIORITY_CONFIG,
  RECURRENCE_CONFIG,
  formatDueDate,
  getDueDateStatus,
} from '@/lib/types';
import { cn } from '@/lib/utils';

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: string) => Promise<unknown>;
  onUpdate: (taskId: string, data: TaskUpdate) => Promise<unknown>;
  onDelete: (taskId: string) => Promise<unknown>;
  categories?: string[];
}

export function TaskItem({
  task,
  onToggle,
  onUpdate,
  onDelete,
  categories = [],
}: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleToggle = async () => {
    setIsLoading(true);
    try {
      await onToggle(task.id);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async (data: TaskUpdate) => {
    setIsLoading(true);
    try {
      await onUpdate(task.id, data);
      setIsEditing(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsLoading(false);
      setIsDeleting(false);
    }
  };

  const dueDateStatus = getDueDateStatus(task);
  const isOverdue = dueDateStatus === 'overdue';
  const isDueToday = dueDateStatus === 'today';

  return (
    <>
      <div
        className={cn(
          'group flex items-start gap-3 px-4 py-3',
          'border-b border-gray-100 dark:border-gray-800/50',
          'hover:bg-gray-50 dark:hover:bg-gray-800/30',
          'transition-all duration-200'
        )}
      >
        {/* Checkbox with animation */}
        <button
          type="button"
          onClick={handleToggle}
          disabled={isLoading}
          className={cn(
            'mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2',
            'transition-all duration-200',
            task.completed
              ? 'border-indigo-500 bg-indigo-500 shadow-sm shadow-indigo-500/30'
              : 'border-gray-300 hover:border-indigo-400 hover:shadow-sm hover:shadow-indigo-500/20 dark:border-gray-600 dark:hover:border-indigo-500'
          )}
          aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
        >
          {task.completed && (
            <CheckIcon className="h-3 w-3 text-white" strokeWidth={3} />
          )}
        </button>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={cn(
                'text-sm font-medium transition-colors duration-200',
                task.completed
                  ? 'text-gray-400 dark:text-gray-500 line-through'
                  : 'text-gray-900 dark:text-white'
              )}
            >
              {task.title}
            </span>

            {/* Priority indicator with glow effect */}
            {task.priority && task.priority !== 'normal' && !task.completed && (
              <span
                className={cn(
                  'priority-dot',
                  task.priority === 'urgent' && 'priority-urgent',
                  task.priority === 'high' && 'priority-high',
                  task.priority === 'low' && 'priority-low'
                )}
                title={PRIORITY_CONFIG[task.priority].label}
              />
            )}

            {/* Priority badge for urgent */}
            {task.priority === 'urgent' && !task.completed && (
              <span className="badge-linear badge-red">Urgent</span>
            )}

            {/* Recurrence badge */}
            {task.recurrence_rule && task.recurrence_rule !== 'none' && (
              <span
                className="badge-linear badge-purple"
                title={RECURRENCE_CONFIG[task.recurrence_rule].description}
              >
                {RECURRENCE_CONFIG[task.recurrence_rule].icon}{' '}
                {RECURRENCE_CONFIG[task.recurrence_rule].label}
              </span>
            )}
          </div>

          {/* Meta info with icons */}
          <div className="flex items-center gap-3 mt-1">
            {task.category && (
              <span className="badge-linear badge-gray">
                {task.category}
              </span>
            )}
            {task.due_date && (
              <span
                className={cn(
                  'inline-flex items-center gap-1 text-xs',
                  task.completed
                    ? 'text-gray-400 dark:text-gray-500'
                    : isOverdue
                      ? 'text-red-500 dark:text-red-400'
                      : isDueToday
                        ? 'text-amber-500 dark:text-amber-400'
                        : 'text-gray-500 dark:text-gray-400'
                )}
              >
                <CalendarIcon className="h-3 w-3" />
                {formatDueDate(task.due_date)}
              </span>
            )}
          </div>

          {task.description && (
            <p
              className={cn(
                'mt-1.5 text-sm leading-relaxed',
                task.completed
                  ? 'text-gray-300 dark:text-gray-600'
                  : 'text-gray-500 dark:text-gray-400'
              )}
            >
              {task.description}
            </p>
          )}
        </div>

        {/* Actions with hover animation */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200 translate-x-2 group-hover:translate-x-0">
          <button
            type="button"
            onClick={() => setIsEditing(true)}
            disabled={isLoading}
            className={cn(
              'p-1.5 rounded-lg',
              'text-gray-400 hover:text-indigo-500 hover:bg-indigo-500/10',
              'dark:hover:text-indigo-400',
              'transition-all duration-150'
            )}
            aria-label="Edit task"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => setIsDeleting(true)}
            disabled={isLoading}
            className={cn(
              'p-1.5 rounded-lg',
              'text-gray-400 hover:text-red-500 hover:bg-red-500/10',
              'transition-all duration-150'
            )}
            aria-label="Delete task"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Edit Modal */}
      <Modal isOpen={isEditing} onClose={() => setIsEditing(false)} title="Edit Task">
        <TaskForm
          task={task}
          onSubmit={handleUpdate}
          onCancel={() => setIsEditing(false)}
          isLoading={isLoading}
          categories={categories}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleting}
        onClose={() => setIsDeleting(false)}
        title="Delete Task"
        size="sm"
        footer={
          <div className="flex gap-2 justify-end">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsDeleting(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button variant="danger" size="sm" onClick={handleDelete} isLoading={isLoading}>
              Delete
            </Button>
          </div>
        }
      >
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Are you sure you want to delete &quot;{task.title}&quot;?
        </p>
      </Modal>
    </>
  );
}
