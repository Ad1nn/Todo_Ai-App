'use client';

/**
 * Display component for AI tool call results.
 * Shows task operations (add, complete, delete) in chat.
 */

import { useState } from 'react';
import {
  CheckCircleIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  PlusCircleIcon,
  TrashIcon,
  PencilSquareIcon,
  ListBulletIcon,
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

export interface ToolCall {
  /** Tool name */
  tool: string;
  /** Tool arguments */
  args: Record<string, unknown>;
  /** Tool result */
  result: unknown;
}

export interface ToolCallDisplayProps {
  /** Tool calls to display */
  toolCalls: ToolCall[];
  /** Whether expanded by default */
  defaultExpanded?: boolean;
  /** Additional CSS classes */
  className?: string;
}

const toolIcons: Record<string, typeof CheckCircleIcon> = {
  add_task: PlusCircleIcon,
  complete_task: CheckCircleIcon,
  delete_task: TrashIcon,
  update_task: PencilSquareIcon,
  list_tasks: ListBulletIcon,
};

const toolLabels: Record<string, string> = {
  add_task: 'Created task',
  complete_task: 'Completed task',
  delete_task: 'Deleted task',
  update_task: 'Updated task',
  list_tasks: 'Listed tasks',
};

// Type definitions for tool results
interface TaskResult {
  title?: string;
}

interface ListTasksResult {
  tasks?: unknown[];
}

function getToolSummary(toolCall: ToolCall): string {
  const { tool, args, result } = toolCall;

  switch (tool) {
    case 'add_task':
      return `Created: "${args.title || 'New task'}"`;
    case 'complete_task':
      return `Completed: "${(result as TaskResult)?.title || 'task'}"`;
    case 'delete_task':
      return `Deleted: "${(result as TaskResult)?.title || 'task'}"`;
    case 'update_task':
      return `Updated: "${(result as TaskResult)?.title || 'task'}"`;
    case 'list_tasks': {
      const tasks = (result as ListTasksResult)?.tasks || [];
      return `Found ${tasks.length} task${tasks.length !== 1 ? 's' : ''}`;
    }
    default:
      return toolLabels[tool] || tool;
  }
}

export function ToolCallDisplay({
  toolCalls,
  defaultExpanded = false,
  className,
}: ToolCallDisplayProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  if (toolCalls.length === 0) return null;

  return (
    <div
      className={cn(
        'mt-2 rounded-lg border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50',
        className
      )}
    >
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
        aria-expanded={expanded}
      >
        {expanded ? (
          <ChevronDownIcon className="h-4 w-4" />
        ) : (
          <ChevronRightIcon className="h-4 w-4" />
        )}
        <span className="font-medium">
          {toolCalls.length} action{toolCalls.length !== 1 ? 's' : ''} performed
        </span>
      </button>

      {expanded && (
        <div className="border-t border-gray-200 px-3 py-2 dark:border-gray-700">
          <ul className="space-y-2">
            {toolCalls.map((toolCall, index) => {
              const Icon = toolIcons[toolCall.tool] || CheckCircleIcon;
              const summary = getToolSummary(toolCall);

              return (
                <li
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300"
                >
                  <Icon
                    className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary-600 dark:text-primary-400"
                    aria-hidden="true"
                  />
                  <span>{summary}</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
