/**
 * Linear-inspired input component with smooth focus states.
 */

import { type InputHTMLAttributes, forwardRef, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type InputSize = 'sm' | 'md' | 'lg';

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  inputSize?: InputSize;
  errorMessage?: string;
  helperText?: string;
  label?: string;
  hideLabel?: boolean;
  leftIcon?: ReactNode;
  rightElement?: ReactNode;
}

const sizeStyles: Record<InputSize, string> = {
  sm: 'h-8 px-3 text-sm rounded-lg',
  md: 'h-10 px-4 text-sm rounded-lg',
  lg: 'h-12 px-4 text-base rounded-xl',
};

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      inputSize = 'md',
      errorMessage,
      helperText,
      label,
      hideLabel = false,
      leftIcon,
      rightElement,
      id,
      disabled,
      ...props
    },
    ref
  ) => {
    const inputId = id || props.name;
    const hasError = !!errorMessage;
    const hasLeftIcon = !!leftIcon;
    const hasRightElement = !!rightElement;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className={cn(
              'block mb-2 text-sm font-medium',
              'text-gray-700 dark:text-gray-300',
              hideLabel && 'sr-only'
            )}
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <span
              className={cn(
                'absolute left-3 top-1/2 -translate-y-1/2',
                'text-gray-400 dark:text-gray-500',
                'pointer-events-none',
                'transition-colors duration-200'
              )}
              aria-hidden="true"
            >
              {leftIcon}
            </span>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'block w-full border bg-white',
              'text-gray-900 placeholder-gray-400',
              'transition-all duration-200',
              'focus:outline-none focus:ring-1',
              'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50',
              'dark:bg-[#17171c] dark:text-white dark:placeholder-gray-500',
              sizeStyles[inputSize],
              hasError
                ? 'border-red-500 focus:border-red-500 focus:ring-red-500/30'
                : 'border-gray-200 focus:border-indigo-500 focus:ring-indigo-500/30 dark:border-gray-700 dark:focus:border-indigo-500',
              hasLeftIcon && 'pl-10',
              hasRightElement && 'pr-10',
              className
            )}
            disabled={disabled}
            aria-invalid={hasError}
            aria-describedby={
              errorMessage
                ? `${inputId}-error`
                : helperText
                  ? `${inputId}-helper`
                  : undefined
            }
            {...props}
          />
          {rightElement && (
            <span
              className={cn(
                'absolute right-3 top-1/2 -translate-y-1/2',
                'text-gray-400 dark:text-gray-500'
              )}
            >
              {rightElement}
            </span>
          )}
        </div>
        {errorMessage && (
          <p
            id={`${inputId}-error`}
            className="mt-2 text-sm text-red-500 dark:text-red-400 flex items-center gap-1"
            role="alert"
          >
            <span className="inline-block w-1 h-1 rounded-full bg-red-500" />
            {errorMessage}
          </p>
        )}
        {helperText && !errorMessage && (
          <p
            id={`${inputId}-helper`}
            className="mt-2 text-sm text-gray-500 dark:text-gray-400"
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
