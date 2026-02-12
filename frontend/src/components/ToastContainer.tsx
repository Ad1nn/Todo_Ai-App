/**
 * Toast container component for managing multiple toast notifications.
 */

'use client';

import { Toast, type ToastData } from '@/components/Toast';

interface ToastContainerProps {
  toasts: ToastData[];
  onDismiss: (id: string) => void;
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      aria-live="polite"
      aria-label="Notifications"
      className="pointer-events-none fixed inset-0 z-50 flex flex-col items-end justify-start p-4 sm:p-6"
    >
      <div className="flex flex-col gap-3 w-full max-w-sm">
        {toasts.map((toast) => (
          <Toast key={toast.id} toast={toast} onDismiss={onDismiss} />
        ))}
      </div>
    </div>
  );
}
