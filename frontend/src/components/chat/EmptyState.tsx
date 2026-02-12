'use client';

/**
 * Empty state component for chat and other views.
 */

import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

export interface EmptyStateProps {
  /** Icon or illustration */
  icon?: ReactNode;
  /** Title text */
  title: string;
  /** Description text */
  description?: string;
  /** Call to action button */
  action?: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Children content */
  children?: ReactNode;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
  children,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center px-4 py-12 text-center',
        className
      )}
    >
      <div className="mb-4 text-gray-400 dark:text-gray-500">
        {icon || <ChatBubbleLeftRightIcon className="h-16 w-16" />}
      </div>
      <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
        {title}
      </h3>
      {description && (
        <p className="mb-6 max-w-sm text-sm text-gray-600 dark:text-gray-400">
          {description}
        </p>
      )}
      {children}
      {action}
    </div>
  );
}

/**
 * Pre-configured empty state for the chat interface.
 */
export function ChatEmptyState() {
  return (
    <EmptyState
      title="Start a conversation"
      description="Ask me to help manage your tasks. Try saying:"
    >
      <ul className="mt-4 space-y-2 text-sm text-gray-600 dark:text-gray-400">
        <li className="rounded-lg bg-gray-100 px-4 py-2 dark:bg-gray-800">
          &ldquo;Add a task to call the dentist&rdquo;
        </li>
        <li className="rounded-lg bg-gray-100 px-4 py-2 dark:bg-gray-800">
          &ldquo;What&apos;s on my todo list?&rdquo;
        </li>
        <li className="rounded-lg bg-gray-100 px-4 py-2 dark:bg-gray-800">
          &ldquo;Mark the groceries task as done&rdquo;
        </li>
      </ul>
    </EmptyState>
  );
}
