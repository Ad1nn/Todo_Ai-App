/**
 * Linear-inspired task list with smooth animations.
 */

'use client';

import { TaskItem } from '@/components/TaskItem';
import { Spinner } from '@/components/ui/Spinner';
import { CheckCircleIcon, InboxIcon } from '@heroicons/react/24/outline';
import type { Task, TaskUpdate } from '@/lib/types';
import { cn } from '@/lib/utils';

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
  onToggle: (taskId: string) => Promise<unknown>;
  onUpdate: (taskId: string, data: TaskUpdate) => Promise<unknown>;
  onDelete: (taskId: string) => Promise<unknown>;
  categories?: string[];
}

export function TaskList({
  tasks,
  isLoading = false,
  onToggle,
  onUpdate,
  onDelete,
  categories = [],
}: TaskListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="flex flex-col items-center gap-3">
          <Spinner size="md" />
          <span className="text-sm text-gray-400 dark:text-gray-500">Loading tasks...</span>
        </div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="py-16 text-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
            <InboxIcon className="h-6 w-6 text-gray-400 dark:text-gray-500" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">No tasks yet</p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Create a task to get started</p>
          </div>
        </div>
      </div>
    );
  }

  const incompleteTasks = tasks.filter((t) => !t.completed);
  const completeTasks = tasks.filter((t) => t.completed);

  return (
    <div className="animate-in fade-in slide-in-from-bottom">
      {/* Incomplete tasks */}
      {incompleteTasks.length > 0 && (
        <div>
          {incompleteTasks.map((task, index) => (
            <div
              key={task.id}
              style={{ animationDelay: `${index * 30}ms` }}
              className="animate-in fade-in"
            >
              <TaskItem
                task={task}
                onToggle={onToggle}
                onUpdate={onUpdate}
                onDelete={onDelete}
                categories={categories}
              />
            </div>
          ))}
        </div>
      )}

      {/* Completed tasks */}
      {completeTasks.length > 0 && (
        <div className={cn(incompleteTasks.length > 0 && 'mt-2')}>
          <div className="px-4 py-2.5 bg-gray-50/80 dark:bg-gray-900/50 border-y border-gray-100 dark:border-gray-800/50">
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-4 w-4 text-emerald-500" />
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Completed
              </span>
              <span className="badge-linear badge-green ml-auto">{completeTasks.length}</span>
            </div>
          </div>
          {completeTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={onToggle}
              onUpdate={onUpdate}
              onDelete={onDelete}
              categories={categories}
            />
          ))}
        </div>
      )}
    </div>
  );
}
