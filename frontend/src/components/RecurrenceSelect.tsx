/**
 * Recurrence pattern selection component for recurring tasks.
 */

'use client';

import type { RecurrenceRule } from '@/lib/types';
import { RECURRENCE_CONFIG } from '@/lib/types';

interface RecurrenceSelectProps {
  value: RecurrenceRule;
  onChange: (value: RecurrenceRule) => void;
  disabled?: boolean;
  className?: string;
}

export function RecurrenceSelect({
  value,
  onChange,
  disabled = false,
  className = '',
}: RecurrenceSelectProps) {
  const options: RecurrenceRule[] = ['none', 'daily', 'weekly', 'monthly'];

  return (
    <div className={className}>
      <label
        htmlFor="recurrence_rule"
        className="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        Repeat
      </label>
      <select
        id="recurrence_rule"
        name="recurrence_rule"
        value={value}
        onChange={(e) => onChange(e.target.value as RecurrenceRule)}
        disabled={disabled}
        className="block w-full rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:border-primary-500 dark:focus-visible:ring-primary-400 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {options.map((option) => {
          const config = RECURRENCE_CONFIG[option];
          return (
            <option key={option} value={option}>
              {config.icon ? `${config.icon} ` : ''}{config.label}
            </option>
          );
        })}
      </select>
      {value !== 'none' && (
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {RECURRENCE_CONFIG[value].description}
        </p>
      )}
    </div>
  );
}
