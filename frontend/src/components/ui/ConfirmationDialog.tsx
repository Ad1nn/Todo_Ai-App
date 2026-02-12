/**
 * Confirmation Dialog component for destructive actions.
 * Built on Modal with focus trap and accessibility.
 * Per contracts/components.ts ConfirmationDialogProps
 */

'use client';

import { Fragment } from 'react';
import { Dialog, DialogPanel, DialogTitle, Transition, TransitionChild } from '@headlessui/react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import { Button, type ButtonVariant } from './Button';

export interface ConfirmationDialogProps {
  /** Whether dialog is open */
  isOpen: boolean;
  /** Callback when dialog should close */
  onClose: () => void;
  /** Dialog title */
  title: string;
  /** Dialog message */
  message: string;
  /** Confirm button label */
  confirmLabel?: string;
  /** Cancel button label */
  cancelLabel?: string;
  /** Confirm button variant (danger for destructive actions) */
  confirmVariant?: ButtonVariant;
  /** Callback when confirmed */
  onConfirm: () => void;
  /** Whether confirm action is loading */
  isLoading?: boolean;
}

export function ConfirmationDialog({
  isOpen,
  onClose,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'danger',
  onConfirm,
  isLoading = false,
}: ConfirmationDialogProps) {
  const handleConfirm = () => {
    onConfirm();
  };

  const isDanger = confirmVariant === 'danger';

  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        {/* Backdrop */}
        <TransitionChild
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div
            className="fixed inset-0 bg-black/50 dark:bg-black/70"
            aria-hidden="true"
          />
        </TransitionChild>

        {/* Dialog container */}
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <TransitionChild
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <DialogPanel
                className={cn(
                  'relative w-full max-w-md transform rounded-xl shadow-xl transition-all',
                  'bg-white dark:bg-gray-800',
                  'p-6'
                )}
              >
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div
                    className={cn(
                      'flex h-10 w-10 shrink-0 items-center justify-center rounded-full',
                      isDanger
                        ? 'bg-error-100 dark:bg-error-900/30'
                        : 'bg-warning-100 dark:bg-warning-900/30'
                    )}
                  >
                    <ExclamationTriangleIcon
                      className={cn(
                        'h-5 w-5',
                        isDanger
                          ? 'text-error-600 dark:text-error-400'
                          : 'text-warning-600 dark:text-warning-400'
                      )}
                      aria-hidden="true"
                    />
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <DialogTitle
                      as="h3"
                      className="text-lg font-semibold text-gray-900 dark:text-gray-100"
                    >
                      {title}
                    </DialogTitle>
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      {message}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                  <Button
                    variant="secondary"
                    onClick={onClose}
                    disabled={isLoading}
                  >
                    {cancelLabel}
                  </Button>
                  <Button
                    variant={confirmVariant}
                    onClick={handleConfirm}
                    isLoading={isLoading}
                  >
                    {confirmLabel}
                  </Button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
