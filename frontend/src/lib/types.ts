/**
 * TypeScript type definitions for the Todo application.
 */

// User types
export interface User {
  id: string;
  email: string;
  display_name: string | null;
  created_at: string;
}

export interface UserUpdate {
  display_name?: string | null;
}

export interface UserStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

// Priority levels in sort order (urgent = highest priority)
export type Priority = 'low' | 'normal' | 'high' | 'urgent';

// Recurrence patterns for recurring tasks (Phase 5)
export type RecurrenceRule = 'none' | 'daily' | 'weekly' | 'monthly';

// Recurrence display configuration
export const RECURRENCE_CONFIG: Record<
  RecurrenceRule,
  {
    label: string;
    icon: string;
    description: string;
  }
> = {
  none: { label: 'No repeat', icon: '', description: 'One-time task' },
  daily: { label: 'Daily', icon: '🔄', description: 'Repeats every day' },
  weekly: { label: 'Weekly', icon: '📅', description: 'Repeats every week' },
  monthly: { label: 'Monthly', icon: '📆', description: 'Repeats every month' },
};

// Priority display configuration
export const PRIORITY_CONFIG: Record<
  Priority,
  {
    label: string;
    color: string;
    bgColor: string;
    sortOrder: number;
  }
> = {
  urgent: { label: 'Urgent', color: 'text-red-600', bgColor: 'bg-red-100', sortOrder: 0 },
  high: { label: 'High', color: 'text-orange-600', bgColor: 'bg-orange-100', sortOrder: 1 },
  normal: { label: 'Normal', color: 'text-blue-600', bgColor: 'bg-blue-100', sortOrder: 2 },
  low: { label: 'Low', color: 'text-gray-600', bgColor: 'bg-gray-100', sortOrder: 3 },
};

// Default category suggestions
export const DEFAULT_CATEGORIES = ['work', 'personal', 'shopping', 'health', 'finance'] as const;

// Task types
export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  due_date: string | null;
  priority: Priority | null;
  category: string | null;
  recurrence_rule: RecurrenceRule;
  parent_task_id: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  due_date?: string | null;
  priority?: Priority | null;
  category?: string | null;
  recurrence_rule?: RecurrenceRule;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  due_date?: string | null;
  priority?: Priority | null;
  category?: string | null;
  recurrence_rule?: RecurrenceRule;
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
  if (task.completed) return 'none';

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
export const DUE_DATE_STATUS_CONFIG: Record<
  DueDateStatus,
  {
    color: string;
    bgColor: string;
    icon?: string;
  }
> = {
  overdue: { color: 'text-red-600', bgColor: 'bg-red-50', icon: '⚠️' },
  today: { color: 'text-amber-600', bgColor: 'bg-amber-50', icon: '📅' },
  soon: { color: 'text-amber-500', bgColor: 'bg-amber-50' },
  future: { color: 'text-gray-600', bgColor: 'bg-gray-50' },
  none: { color: 'text-gray-400', bgColor: '' },
};

// Notification types (Phase 5)
export type NotificationType = 'reminder' | 'system' | 'action';

export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string | null;
  read: boolean;
  task_id: string | null;
  created_at: string;
  read_at: string | null;
}

export interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
}

// Notification styling
export const NOTIFICATION_TYPE_CONFIG: Record<
  NotificationType,
  {
    icon: string;
    color: string;
    bgColor: string;
  }
> = {
  reminder: { icon: '⏰', color: 'text-amber-600', bgColor: 'bg-amber-50' },
  system: { icon: 'ℹ️', color: 'text-blue-600', bgColor: 'bg-blue-50' },
  action: { icon: '✅', color: 'text-green-600', bgColor: 'bg-green-50' },
};

// Audit types (Phase 5)
export type AuditAction = 'create' | 'update' | 'complete' | 'delete';

// Task snapshot type for audit before/after values
export interface TaskAuditValue {
  title?: string;
  description?: string | null;
  completed?: boolean;
  due_date?: string | null;
  priority?: Priority | null;
  category?: string | null;
  recurrence_rule?: RecurrenceRule;
}

export interface AuditEntry {
  id: string;
  user_id: string;
  entity_type: string;
  entity_id: string;
  action: AuditAction;
  before_value: TaskAuditValue | null;
  after_value: TaskAuditValue | null;
  timestamp: string;
  extra_data: Record<string, unknown> | null;
}

// Auth types
export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// API response types
export interface ApiError {
  detail: string;
}

export interface ValidationError {
  detail: Array<{
    loc: Array<string | number>;
    msg: string;
    type: string;
  }>;
}
