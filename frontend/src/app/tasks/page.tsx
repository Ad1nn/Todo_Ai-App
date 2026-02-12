/**
 * Linear-inspired tasks page with visual accents.
 */

'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { PlusIcon, FunnelIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';

import { Button } from '@/components/ui/Button';
import { TaskForm } from '@/components/TaskForm';
import { TaskList } from '@/components/TaskList';
import { Layout } from '@/components/layout/Layout';
import { Spinner } from '@/components/ui/Spinner';
import { Modal } from '@/components/ui/Modal';
import { useAuth } from '@/hooks/useAuth';
import { useTasks } from '@/hooks/useTasks';
import type { TaskCreate, TaskFilters, Priority } from '@/lib/types';
import { cn } from '@/lib/utils';

const FILTER_STORAGE_KEY = 'taskFilters';

interface StoredFilters {
  category: string;
  priority: Priority | '';
  sortBy: 'created_at' | 'due_date' | 'priority';
  sortOrder: 'asc' | 'desc';
  showOverdueOnly: boolean;
}

function loadFiltersFromStorage(): Partial<StoredFilters> {
  if (typeof window === 'undefined') return {};
  try {
    const stored = sessionStorage.getItem(FILTER_STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}

function saveFiltersToStorage(filters: StoredFilters): void {
  if (typeof window === 'undefined') return;
  try {
    sessionStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(filters));
  } catch {
    // Ignore
  }
}

export default function TasksPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [filtersInitialized, setFiltersInitialized] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<Priority | ''>('');
  const [sortBy, setSortBy] = useState<'created_at' | 'due_date' | 'priority'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showOverdueOnly, setShowOverdueOnly] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    const stored = loadFiltersFromStorage();
    if (stored.category) setCategoryFilter(stored.category);
    if (stored.priority) setPriorityFilter(stored.priority);
    if (stored.sortBy) setSortBy(stored.sortBy);
    if (stored.sortOrder) setSortOrder(stored.sortOrder);
    if (stored.showOverdueOnly !== undefined) setShowOverdueOnly(stored.showOverdueOnly);
    setFiltersInitialized(true);
  }, []);

  useEffect(() => {
    if (!filtersInitialized) return;
    saveFiltersToStorage({
      category: categoryFilter,
      priority: priorityFilter,
      sortBy,
      sortOrder,
      showOverdueOnly,
    });
  }, [filtersInitialized, categoryFilter, priorityFilter, sortBy, sortOrder, showOverdueOnly]);

  const filters: TaskFilters = useMemo(() => {
    const f: TaskFilters = {};
    if (categoryFilter) f.category = categoryFilter;
    if (priorityFilter) f.priority = priorityFilter;
    if (showOverdueOnly) f.overdue = true;
    if (sortBy !== 'created_at') f.sort = sortBy;
    if (sortOrder !== 'desc') f.order = sortOrder;
    return f;
  }, [categoryFilter, priorityFilter, sortBy, sortOrder, showOverdueOnly]);

  const {
    tasks,
    categories,
    isLoading: tasksLoading,
    createTask,
    updateTask,
    toggleTask,
    deleteTask,
  } = useTasks(filters);

  const hasActiveFilters = categoryFilter || priorityFilter || showOverdueOnly || sortBy !== 'created_at';
  const activeFilterCount = [categoryFilter, priorityFilter, showOverdueOnly, sortBy !== 'created_at'].filter(Boolean).length;

  const clearFilters = () => {
    setCategoryFilter('');
    setPriorityFilter('');
    setSortBy('created_at');
    setSortOrder('desc');
    setShowOverdueOnly(false);
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(FILTER_STORAGE_KEY);
    }
  };

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading || !isAuthenticated) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white dark:bg-black">
        <Spinner size="lg" />
      </main>
    );
  }

  const handleCreateTask = async (data: TaskCreate) => {
    await createTask(data);
    setIsCreating(false);
  };

  const pendingCount = tasks.filter(t => !t.completed).length;
  const completedCount = tasks.filter(t => t.completed).length;

  return (
    <Layout>
      <div className="mx-auto max-w-2xl px-4 py-6">
        {/* Header with gradient accent */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              All Tasks
            </h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="badge-linear badge-blue">{pendingCount} pending</span>
              {completedCount > 0 && (
                <span className="badge-linear badge-green">{completedCount} done</span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {/* Filter button */}
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm',
                'transition-all duration-200',
                hasActiveFilters
                  ? 'bg-indigo-500 text-white shadow-sm shadow-indigo-500/25'
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              )}
            >
              <AdjustmentsHorizontalIcon className="h-4 w-4" />
              {hasActiveFilters && <span className="font-medium">{activeFilterCount}</span>}
            </button>

            {/* New task button */}
            <Button size="sm" onClick={() => setIsCreating(true)}>
              <PlusIcon className="h-4 w-4" />
              New Task
            </Button>
          </div>
        </div>

        {/* Filters bar with glass effect */}
        {showFilters && (
          <div className="mb-4 p-4 rounded-xl glass border border-gray-200/50 dark:border-gray-700/50 animate-in fade-in slide-in-from-top">
            <div className="flex flex-wrap items-center gap-3">
              {/* Category */}
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="input-linear max-w-[160px]"
              >
                <option value="">All categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>

              {/* Priority */}
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value as Priority | '')}
                className="input-linear max-w-[140px]"
              >
                <option value="">All priorities</option>
                <option value="urgent">🔴 Urgent</option>
                <option value="high">🟠 High</option>
                <option value="normal">🔵 Normal</option>
                <option value="low">⚪ Low</option>
              </select>

              {/* Sort */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'created_at' | 'due_date' | 'priority')}
                className="input-linear max-w-[150px]"
              >
                <option value="created_at">Sort: Created</option>
                <option value="due_date">Sort: Due date</option>
                <option value="priority">Sort: Priority</option>
              </select>

              {/* Overdue */}
              <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors">
                <input
                  type="checkbox"
                  checked={showOverdueOnly}
                  onChange={(e) => setShowOverdueOnly(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-indigo-500 focus:ring-indigo-500 dark:bg-gray-800"
                />
                Overdue only
              </label>

              {/* Clear */}
              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="text-sm text-gray-500 hover:text-indigo-500 dark:text-gray-400 dark:hover:text-indigo-400 transition-colors"
                >
                  Clear all
                </button>
              )}
            </div>
          </div>
        )}

        {/* Task list container with card styling */}
        <div className="card-linear overflow-hidden">
          <TaskList
            tasks={tasks}
            isLoading={tasksLoading}
            onToggle={toggleTask}
            onUpdate={updateTask}
            onDelete={deleteTask}
            categories={categories}
          />
        </div>
      </div>

      {/* Create task modal */}
      <Modal
        isOpen={isCreating}
        onClose={() => setIsCreating(false)}
        title="New Task"
      >
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setIsCreating(false)}
          categories={categories}
        />
      </Modal>
    </Layout>
  );
}
