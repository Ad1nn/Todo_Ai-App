/**
 * TypeScript Type Contracts: Task Enhancements
 * Feature: 005-task-enhancements
 * Date: 2026-02-04
 *
 * These types define the contract between frontend and backend API.
 * They should be copied to frontend/src/lib/types.ts during implementation.
 */

// Priority levels in sort order (urgent = highest priority)
export type Priority = 'low' | 'normal' | 'high' | 'urgent';

// Priority display configuration
export const PRIORITY_CONFIG: Record<Priority, {
  label: string;
  color: string;      // Tailwind text color class
  bgColor: string;    // Tailwind background color class
  sortOrder: number;  // For client-side sorting
}> = {
  urgent: { label: 'Urgent', color: 'text-red-600', bgColor: 'bg-red-100', sortOrder: 0 },
  high: { label: 'High', color: 'text-orange-600', bgColor: 'bg-orange-100', sortOrder: 1 },
  normal: { label: 'Normal', color: 'text-blue-600', bgColor: 'bg-blue-100', sortOrder: 2 },
  low: { label: 'Low', color: 'text-gray-600', bgColor: 'bg-gray-100', sortOrder: 3 },
};

// Default category suggestions
export const DEFAULT_CATEGORIES = ['work', 'personal', 'shopping', 'health', 'finance'] as const;

// Task entity (API response)
export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;   // ISO 8601 datetime
  updated_at: string;   // ISO 8601 datetime
  due_date: string | null;      // ISO 8601 datetime (NEW)
  priority: Priority | null;    // (NEW)
  category: string | null;      // (NEW)
}

// Task creation payload
export interface TaskCreate {
  title: string;
  description?: string | null;
  due_date?: string | null;     // ISO 8601 datetime (NEW)
  priority?: Priority | null;   // (NEW)
  category?: string | null;     // (NEW)
}

// Task update payload (all fields optional)
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  due_date?: string | null;     // ISO 8601 datetime (NEW)
  priority?: Priority | null;   // (NEW)
  category?: string | null;     // (NEW)
}

// API query filters for list endpoint
export interface TaskFilters {
  category?: string;
  priority?: Priority;
  completed?: boolean;
  overdue?: boolean;
  sort?: 'created_at' | 'due_date' | 'priority';
  order?: 'asc' | 'desc';
}

// Helper: Build query string from filters
export function buildTaskQueryString(filters: TaskFilters): string {
  const params = new URLSearchParams();

  if (filters.category) params.set('category', filters.category);
  if (filters.priority) params.set('priority', filters.priority);
  if (filters.completed !== undefined) params.set('completed', String(filters.completed));
  if (filters.overdue !== undefined) params.set('overdue', String(filters.overdue));
  if (filters.sort) params.set('sort', filters.sort);
  if (filters.order) params.set('order', filters.order);

  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}

// Helper: Check if task is overdue
export function isTaskOverdue(task: Task): boolean {
  if (!task.due_date || task.completed) return false;
  return new Date(task.due_date) < new Date();
}

// Helper: Check if task is due today
export function isTaskDueToday(task: Task): boolean {
  if (!task.due_date) return false;
  const dueDate = new Date(task.due_date);
  const today = new Date();
  return (
    dueDate.getFullYear() === today.getFullYear() &&
    dueDate.getMonth() === today.getMonth() &&
    dueDate.getDate() === today.getDate()
  );
}

// Helper: Format due date for display
export function formatDueDate(dueDate: string | null): string {
  if (!dueDate) return '';

  const date = new Date(dueDate);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return diffDays === -1 ? 'Yesterday' : `${Math.abs(diffDays)} days ago`;
  } else if (diffDays === 0) {
    return 'Today';
  } else if (diffDays === 1) {
    return 'Tomorrow';
  } else if (diffDays <= 7) {
    return `In ${diffDays} days`;
  } else {
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  }
}

// Helper: Get due date status for styling
export type DueDateStatus = 'overdue' | 'today' | 'soon' | 'future' | 'none';

export function getDueDateStatus(task: Task): DueDateStatus {
  if (!task.due_date) return 'none';
  if (task.completed) return 'none'; // Completed tasks don't show urgency

  const date = new Date(task.due_date);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return 'overdue';
  if (diffDays === 0) return 'today';
  if (diffDays <= 3) return 'soon';
  return 'future';
}

// Due date status styling
export const DUE_DATE_STATUS_CONFIG: Record<DueDateStatus, {
  color: string;
  bgColor: string;
  icon?: string;
}> = {
  overdue: { color: 'text-red-600', bgColor: 'bg-red-50', icon: '⚠️' },
  today: { color: 'text-amber-600', bgColor: 'bg-amber-50', icon: '📅' },
  soon: { color: 'text-amber-500', bgColor: 'bg-amber-50' },
  future: { color: 'text-gray-600', bgColor: 'bg-gray-50' },
  none: { color: 'text-gray-400', bgColor: '' },
};
