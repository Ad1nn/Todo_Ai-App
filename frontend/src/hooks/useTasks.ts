/**
 * Tasks hook for managing task state and operations.
 */

'use client';

import { useCallback, useMemo } from 'react';
import useSWR from 'swr';

import { api } from '@/lib/api';
import type { Task, TaskCreate, TaskUpdate, TaskFilters } from '@/lib/types';
import { buildTaskQueryString } from '@/lib/types';

const tasksFetcher = (url: string) => api.get<Task[]>(url);
const categoriesFetcher = () => api.get<string[]>('/api/v1/tasks/categories');

export function useTasks(filters: TaskFilters = {}) {
  // Build the API URL with filters
  const tasksUrl = useMemo(() => {
    const queryString = buildTaskQueryString(filters);
    return `/api/v1/tasks${queryString}`;
  }, [filters]);

  const { data: tasks, error, isLoading, mutate } = useSWR(tasksUrl, tasksFetcher);

  // Fetch user's categories for suggestions
  const { data: categories } = useSWR('categories', categoriesFetcher);

  const createTask = useCallback(
    async (data: TaskCreate): Promise<Task> => {
      const newTask = await api.post<Task>('/api/v1/tasks', data);
      await mutate();
      return newTask;
    },
    [mutate]
  );

  const updateTask = useCallback(
    async (taskId: string, data: TaskUpdate): Promise<Task> => {
      const updatedTask = await api.put<Task>(`/api/v1/tasks/${taskId}`, data);
      await mutate();
      return updatedTask;
    },
    [mutate]
  );

  const toggleTask = useCallback(
    async (taskId: string): Promise<Task> => {
      const updatedTask = await api.patch<Task>(`/api/v1/tasks/${taskId}/toggle`);
      await mutate();
      return updatedTask;
    },
    [mutate]
  );

  // Complete a task - handles recurring tasks by creating next occurrence
  const completeTask = useCallback(
    async (taskId: string): Promise<{ completed_task: Task; next_occurrence: Task | null }> => {
      const result = await api.post<{ completed_task: Task; next_occurrence: Task | null }>(
        `/api/v1/tasks/${taskId}/complete`
      );
      await mutate();
      return result;
    },
    [mutate]
  );

  const deleteTask = useCallback(
    async (taskId: string): Promise<void> => {
      await api.delete(`/api/v1/tasks/${taskId}`);
      await mutate();
    },
    [mutate]
  );

  return {
    tasks: tasks ?? [],
    categories: categories ?? [],
    isLoading,
    error,
    createTask,
    updateTask,
    toggleTask,
    completeTask,
    deleteTask,
    mutate,
  };
}
