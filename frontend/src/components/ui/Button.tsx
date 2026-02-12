/**
 * Linear-inspired button component with subtle animations.
 */

import { type ButtonHTMLAttributes, forwardRef, type ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Spinner } from './Spinner';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: cn(
    'bg-indigo-500 text-white',
    'hover:bg-indigo-600',
    'shadow-sm shadow-indigo-500/25',
    'hover:shadow-md hover:shadow-indigo-500/30',
    'active:scale-[0.98]'
  ),
  secondary: cn(
    'bg-gray-100 text-gray-900',
    'hover:bg-gray-200',
    'dark:bg-gray-800 dark:text-white',
    'dark:hover:bg-gray-700',
    'active:scale-[0.98]'
  ),
  ghost: cn(
    'bg-transparent text-gray-600',
    'hover:bg-gray-100 hover:text-gray-900',
    'dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white'
  ),
  danger: cn(
    'bg-red-500 text-white',
    'hover:bg-red-600',
    'shadow-sm shadow-red-500/25',
    'active:scale-[0.98]'
  ),
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'h-8 min-w-8 px-3 text-sm gap-1.5 rounded-lg',
  md: 'h-10 min-w-10 px-4 text-sm gap-2 rounded-lg',
  lg: 'h-12 min-w-12 px-6 text-base gap-2.5 rounded-xl',
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center font-medium',
          'transition-all duration-150',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2',
          'dark:focus-visible:ring-offset-[#0d0d0f]',
          'disabled:pointer-events-none disabled:opacity-40',
          variantStyles[variant],
          sizeStyles[size],
          fullWidth && 'w-full',
          className
        )}
        disabled={disabled || isLoading}
        aria-disabled={disabled || isLoading}
        aria-busy={isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <Spinner size="sm" />
            <span className="ml-2">Loading...</span>
          </>
        ) : (
          <>
            {leftIcon && <span className="shrink-0">{leftIcon}</span>}
            {children}
            {rightIcon && <span className="shrink-0">{rightIcon}</span>}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
