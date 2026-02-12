/**
 * Toast notification component with auto-dismiss.
 */

'use client';

import { useEffect, useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

export type ToastType = 'info' | 'success' | 'warning' | 'error';

export interface ToastData {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number; // in milliseconds, default 5000
  taskId?: string; // optional link to task
}

interface ToastProps {
  toast: ToastData;
  onDismiss: (id: string) => void;
}

const toastStyles: Record<ToastType, { bg: string; border: string; icon: string }> = {
  info: {
    bg: 'bg-blue-50 dark:bg-blue-900/30',
    border: 'border-blue-200 dark:border-blue-800',
    icon: 'ℹ️',
  },
  success: {
    bg: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-200 dark:border-green-800',
    icon: '✅',
  },
  warning: {
    bg: 'bg-amber-50 dark:bg-amber-900/30',
    border: 'border-amber-200 dark:border-amber-800',
    icon: '⚠️',
  },
  error: {
    bg: 'bg-red-50 dark:bg-red-900/30',
    border: 'border-red-200 dark:border-red-800',
    icon: '❌',
  },
};

export function Toast({ toast, onDismiss }: ToastProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  const duration = toast.duration ?? 5000;
  const styles = toastStyles[toast.type];

  useEffect(() => {
    // Animate in
    requestAnimationFrame(() => {
      setIsVisible(true);
    });

    // Auto-dismiss
    const dismissTimer = setTimeout(() => {
      handleDismiss();
    }, duration);

    return () => {
      clearTimeout(dismissTimer);
    };
  }, [duration]);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      onDismiss(toast.id);
    }, 200); // Match animation duration
  };

  return (
    <div
      role="alert"
      className={cn(
        'pointer-events-auto w-full max-w-sm rounded-lg border shadow-lg',
        'transform transition-all duration-200 ease-out',
        styles.bg,
        styles.border,
        isVisible && !isExiting
          ? 'translate-x-0 opacity-100'
          : 'translate-x-4 opacity-0'
      )}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <span className="text-lg flex-shrink-0">{styles.icon}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {toast.title}
            </p>
            {toast.message && (
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                {toast.message}
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={handleDismiss}
            className={cn(
              'flex-shrink-0 rounded-md p-1',
              'text-gray-400 hover:text-gray-600',
              'dark:text-gray-500 dark:hover:text-gray-300',
              'focus:outline-none focus:ring-2 focus:ring-indigo-500',
              'transition-colors duration-150'
            )}
            aria-label="Dismiss notification"
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
      {/* Progress bar */}
      <div className="h-1 w-full bg-gray-200/50 dark:bg-gray-700/50 rounded-b-lg overflow-hidden">
        <div
          className={cn(
            'h-full transition-all ease-linear',
            toast.type === 'error' && 'bg-red-500',
            toast.type === 'warning' && 'bg-amber-500',
            toast.type === 'success' && 'bg-green-500',
            toast.type === 'info' && 'bg-blue-500'
          )}
          style={{
            animation: `shrink ${duration}ms linear forwards`,
          }}
        />
      </div>
      <style jsx>{`
        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
      `}</style>
    </div>
  );
}
