/**
 * Linear-inspired modal with glass effect and smooth animations.
 */

'use client';

import { Fragment, type ReactNode } from 'react';
import { Dialog, DialogPanel, DialogTitle, Transition, TransitionChild } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: ModalSize;
  closeOnBackdropClick?: boolean;
  closeOnEscape?: boolean;
  footer?: ReactNode;
}

const sizeStyles: Record<ModalSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
};

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  closeOnBackdropClick = true,
  closeOnEscape = true,
  footer,
}: ModalProps) {
  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog
        as="div"
        className="relative z-50"
        onClose={closeOnBackdropClick ? onClose : () => {}}
        static={!closeOnEscape}
      >
        {/* Backdrop with blur */}
        <TransitionChild
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-md dark:bg-black/70"
            aria-hidden="true"
          />
        </TransitionChild>

        {/* Modal container */}
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <TransitionChild
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95 translate-y-4"
              enterTo="opacity-100 scale-100 translate-y-0"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100 translate-y-0"
              leaveTo="opacity-0 scale-95 translate-y-4"
            >
              <DialogPanel
                className={cn(
                  'relative w-full transform rounded-xl',
                  'bg-white/95 dark:bg-[#17171c]/95',
                  'backdrop-blur-xl',
                  'border border-gray-200/50 dark:border-gray-800/50',
                  'shadow-2xl shadow-black/10 dark:shadow-black/30',
                  'transition-all',
                  sizeStyles[size]
                )}
              >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4">
                  <DialogTitle
                    as="h2"
                    className="text-base font-semibold text-gray-900 dark:text-white"
                  >
                    {title}
                  </DialogTitle>
                  <button
                    type="button"
                    onClick={onClose}
                    className={cn(
                      'rounded-lg p-1.5 -mr-1.5',
                      'text-gray-400 hover:text-gray-600 hover:bg-gray-100',
                      'dark:text-gray-500 dark:hover:text-gray-300 dark:hover:bg-gray-800',
                      'transition-all duration-150',
                      'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500'
                    )}
                    aria-label="Close"
                  >
                    <XMarkIcon className="h-5 w-5" aria-hidden="true" />
                  </button>
                </div>

                {/* Divider with gradient */}
                <div className="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent dark:via-gray-700" />

                {/* Content */}
                <div className="px-6 py-4">{children}</div>

                {/* Footer */}
                {footer && (
                  <>
                    <div className="h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent dark:via-gray-700" />
                    <div className="px-6 py-4">{footer}</div>
                  </>
                )}
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
