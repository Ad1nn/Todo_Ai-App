/**
 * Notification settings component for managing user preferences.
 */

'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/providers/AuthProvider';
import { cn } from '@/lib/utils';

interface NotificationPreferences {
  reminders_enabled: boolean;
  reminder_minutes_before: number;
  email_notifications: boolean;
  toast_notifications: boolean;
}

interface NotificationSettingsProps {
  onClose?: () => void;
}

const REMINDER_OPTIONS = [
  { value: 5, label: '5 minutes' },
  { value: 15, label: '15 minutes' },
  { value: 30, label: '30 minutes' },
  { value: 60, label: '1 hour' },
  { value: 120, label: '2 hours' },
  { value: 1440, label: '1 day' },
];

export function NotificationSettings({ onClose }: NotificationSettingsProps) {
  const { token } = useAuth();
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Fetch current preferences
  useEffect(() => {
    async function fetchPreferences() {
      if (!token) return;

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/me/preferences`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setPreferences(data);
        } else {
          setError('Failed to load preferences');
        }
      } catch {
        setError('Failed to load preferences');
      } finally {
        setIsLoading(false);
      }
    }

    fetchPreferences();
  }, [token]);

  const updatePreference = async (
    key: keyof NotificationPreferences,
    value: boolean | number
  ) => {
    if (!token || !preferences) return;

    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/me/preferences`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ [key]: value }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
        setSuccessMessage('Settings saved');
        setTimeout(() => setSuccessMessage(null), 2000);
      } else {
        setError('Failed to save settings');
      }
    } catch {
      setError('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="p-4 text-center text-gray-500 dark:text-gray-400">
        Loading settings...
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="p-4 text-center text-red-500">
        Failed to load settings
      </div>
    );
  }

  return (
    <div className="p-4 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Notification Settings
        </h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 rounded-lg">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="p-3 text-sm text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400 rounded-lg">
          {successMessage}
        </div>
      )}

      <div className="space-y-4">
        {/* Reminders Toggle */}
        <div className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-gray-900 dark:text-white">
              Task Reminders
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Get notified when tasks are due soon
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={preferences.reminders_enabled}
            onClick={() => updatePreference('reminders_enabled', !preferences.reminders_enabled)}
            disabled={isSaving}
            className={cn(
              'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
              preferences.reminders_enabled ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700',
              isSaving && 'opacity-50 cursor-not-allowed'
            )}
          >
            <span
              className={cn(
                'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                preferences.reminders_enabled ? 'translate-x-5' : 'translate-x-0'
              )}
            />
          </button>
        </div>

        {/* Reminder Timing */}
        {preferences.reminders_enabled && (
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900 dark:text-white">
              Remind me
            </label>
            <select
              value={preferences.reminder_minutes_before}
              onChange={(e) => updatePreference('reminder_minutes_before', parseInt(e.target.value))}
              disabled={isSaving}
              className="w-full px-3 py-2 text-sm border rounded-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
            >
              {REMINDER_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label} before due
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Toast Notifications Toggle */}
        <div className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-gray-900 dark:text-white">
              Toast Notifications
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Show pop-up notifications in the app
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={preferences.toast_notifications}
            onClick={() => updatePreference('toast_notifications', !preferences.toast_notifications)}
            disabled={isSaving}
            className={cn(
              'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
              preferences.toast_notifications ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700',
              isSaving && 'opacity-50 cursor-not-allowed'
            )}
          >
            <span
              className={cn(
                'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                preferences.toast_notifications ? 'translate-x-5' : 'translate-x-0'
              )}
            />
          </button>
        </div>

        {/* Email Notifications Toggle (Future) */}
        <div className="flex items-center justify-between opacity-50">
          <div>
            <label className="text-sm font-medium text-gray-900 dark:text-white">
              Email Notifications
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Coming soon
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={false}
            disabled
            className="relative inline-flex h-6 w-11 flex-shrink-0 cursor-not-allowed rounded-full border-2 border-transparent bg-gray-200 dark:bg-gray-700"
          >
            <span className="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 translate-x-0" />
          </button>
        </div>
      </div>
    </div>
  );
}
