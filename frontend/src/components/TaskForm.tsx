/**
 * Task form component for creating and editing tasks.
 */

'use client';

import { useState, type FormEvent } from 'react';

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { RecurrenceSelect } from '@/components/RecurrenceSelect';
import type { Task, Priority, RecurrenceRule } from '@/lib/types';
import { DEFAULT_CATEGORIES } from '@/lib/types';

interface TaskFormData {
  title: string;
  description: string | null;
  due_date?: string | null;
  priority?: Priority | null;
  category?: string | null;
  recurrence_rule?: RecurrenceRule;
}

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  categories?: string[];
}

export function TaskForm({
  task,
  onSubmit,
  onCancel,
  isLoading = false,
  categories = [],
}: TaskFormProps) {
  const [title, setTitle] = useState(task?.title ?? '');
  const [description, setDescription] = useState(task?.description ?? '');
  const [dueDate, setDueDate] = useState(
    task?.due_date ? task.due_date.slice(0, 16) : ''
  );
  const [priority, setPriority] = useState<Priority | ''>(task?.priority ?? '');
  const [category, setCategory] = useState(task?.category ?? '');
  const [recurrenceRule, setRecurrenceRule] = useState<RecurrenceRule>(
    task?.recurrence_rule ?? 'none'
  );
  const [error, setError] = useState<string | null>(null);

  const isEditing = !!task;

  // Combine default categories with user's custom categories
  const allCategories = Array.from(
    new Set([...DEFAULT_CATEGORIES, ...categories])
  ).sort();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (title.length > 200) {
      setError('Title must be 200 characters or less');
      return;
    }

    // Validate: recurring tasks need a due date
    if (recurrenceRule !== 'none' && !dueDate) {
      setError('Recurring tasks require a due date');
      return;
    }

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || null,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        priority: priority || null,
        category: category.trim() || null,
        recurrence_rule: recurrenceRule,
      });

      if (!isEditing) {
        setTitle('');
        setDescription('');
        setDueDate('');
        setPriority('');
        setCategory('');
        setRecurrenceRule('none');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save task');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Input
          label="Title"
          name="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          required
          maxLength={200}
        />
      </div>

      <div>
        <label
          htmlFor="description"
          className="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Description (optional)
        </label>
        <textarea
          id="description"
          name="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details..."
          maxLength={2000}
          rows={3}
          className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:border-primary-500 dark:focus-visible:ring-primary-400 transition-colors duration-200"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Due Date */}
        <div>
          <label
            htmlFor="due_date"
            className="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Due Date
          </label>
          <input
            type="datetime-local"
            id="due_date"
            name="due_date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:border-primary-500 dark:focus-visible:ring-primary-400 transition-colors duration-200"
          />
        </div>

        {/* Priority */}
        <div>
          <label
            htmlFor="priority"
            className="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Priority
          </label>
          <select
            id="priority"
            name="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority | '')}
            className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:border-primary-500 dark:focus-visible:ring-primary-400 transition-colors duration-200"
          >
            <option value="">No priority</option>
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        {/* Category */}
        <div>
          <label
            htmlFor="category"
            className="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Category
          </label>
          <input
            type="text"
            id="category"
            name="category"
            list="category-suggestions"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g., work, personal"
            maxLength={50}
            className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:border-primary-500 dark:focus-visible:ring-primary-400 transition-colors duration-200"
          />
          <datalist id="category-suggestions">
            {allCategories.map((cat) => (
              <option key={cat} value={cat} />
            ))}
          </datalist>
        </div>

        {/* Recurrence */}
        <RecurrenceSelect
          value={recurrenceRule}
          onChange={setRecurrenceRule}
        />
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-lg bg-error-50 dark:bg-error-900/30 p-3 text-sm text-error-600 dark:text-error-400"
        >
          {error}
        </div>
      )}

      <div className="flex gap-3">
        <Button type="submit" isLoading={isLoading}>
          {isEditing ? 'Save Changes' : 'Add Task'}
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
