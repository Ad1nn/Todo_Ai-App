/**
 * Component API Contracts for UI/UX Enhancement
 * Feature: 004-ui-ux-enhancement
 * Date: 2026-01-30
 *
 * These interfaces define the public API for all UI components.
 * Implementation MUST conform to these contracts.
 */

import { ComponentPropsWithoutRef, ReactNode } from 'react';

// =============================================================================
// BUTTON
// =============================================================================

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ComponentPropsWithoutRef<'button'> {
  /** Visual style variant */
  variant?: ButtonVariant;
  /** Size of the button */
  size?: ButtonSize;
  /** Show loading spinner and disable interactions */
  isLoading?: boolean;
  /** Icon to display before children */
  leftIcon?: ReactNode;
  /** Icon to display after children */
  rightIcon?: ReactNode;
  /** Full width button */
  fullWidth?: boolean;
}

// =============================================================================
// INPUT
// =============================================================================

export type InputSize = 'sm' | 'md' | 'lg';
export type InputValidationState = 'default' | 'valid' | 'invalid';

export interface InputProps extends ComponentPropsWithoutRef<'input'> {
  /** Size of the input */
  size?: InputSize;
  /** Validation state for styling */
  validationState?: InputValidationState;
  /** Error message to display below input */
  errorMessage?: string;
  /** Helper text to display below input */
  helperText?: string;
  /** Label text (required for accessibility) */
  label?: string;
  /** Hide the label visually but keep for screen readers */
  hideLabel?: boolean;
  /** Icon to display at start of input */
  leftIcon?: ReactNode;
  /** Icon or button to display at end of input */
  rightElement?: ReactNode;
}

// =============================================================================
// MODAL
// =============================================================================

export interface ModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when modal should close */
  onClose: () => void;
  /** Modal title (required for accessibility) */
  title: string;
  /** Modal content */
  children: ReactNode;
  /** Size of the modal */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Whether clicking backdrop closes modal */
  closeOnBackdropClick?: boolean;
  /** Whether pressing Escape closes modal */
  closeOnEscape?: boolean;
  /** Custom footer content */
  footer?: ReactNode;
}

// =============================================================================
// TOAST
// =============================================================================

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  /** Unique identifier */
  id: string;
  /** Visual style variant */
  variant: ToastVariant;
  /** Toast title */
  title: string;
  /** Optional description */
  description?: string;
  /** Duration in ms before auto-dismiss (0 = no auto-dismiss) */
  duration?: number;
  /** Callback when toast is dismissed */
  onDismiss?: () => void;
}

// =============================================================================
// THEME TOGGLE
// =============================================================================

export interface ThemeToggleProps {
  /** Additional CSS classes */
  className?: string;
  /** Size of the toggle */
  size?: 'sm' | 'md' | 'lg';
}

// =============================================================================
// SPINNER / LOADING
// =============================================================================

export interface SpinnerProps {
  /** Size of the spinner */
  size?: 'sm' | 'md' | 'lg';
  /** Color (inherits from parent by default) */
  color?: string;
  /** Accessible label */
  label?: string;
}

// =============================================================================
// HEADER
// =============================================================================

export interface HeaderProps {
  /** Show mobile menu toggle */
  showMobileMenuToggle?: boolean;
  /** Callback when mobile menu toggle clicked */
  onMobileMenuToggle?: () => void;
  /** Custom actions to display in header */
  actions?: ReactNode;
}

// =============================================================================
// SIDEBAR / NAVIGATION
// =============================================================================

export interface NavItem {
  /** Display label */
  label: string;
  /** Navigation href */
  href: string;
  /** Icon component */
  icon?: ReactNode;
  /** Badge content */
  badge?: string | number;
  /** Whether item is active */
  active?: boolean;
}

export interface SidebarProps {
  /** Navigation items */
  items: NavItem[];
  /** Whether sidebar is collapsed */
  isCollapsed?: boolean;
  /** Callback when collapse state changes */
  onCollapse?: (collapsed: boolean) => void;
}

export interface MobileNavProps {
  /** Whether menu is open */
  isOpen: boolean;
  /** Callback when menu should close */
  onClose: () => void;
  /** Navigation items */
  items: NavItem[];
}

// =============================================================================
// CHAT CONTAINER (ChatKit wrapper)
// =============================================================================

export interface ChatContainerProps {
  /** User ID for chat session */
  userId: string;
  /** Conversation ID (optional, creates new if not provided) */
  conversationId?: string;
  /** Callback when conversation changes */
  onConversationChange?: (conversationId: string) => void;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// TOOL CALL DISPLAY
// =============================================================================

export interface ToolCall {
  /** Tool name */
  tool: string;
  /** Tool arguments */
  args: Record<string, unknown>;
  /** Tool result */
  result: unknown;
}

export interface ToolCallDisplayProps {
  /** Tool calls to display */
  toolCalls: ToolCall[];
  /** Whether expanded by default */
  defaultExpanded?: boolean;
}

// =============================================================================
// EMPTY STATE
// =============================================================================

export interface EmptyStateProps {
  /** Icon or illustration */
  icon?: ReactNode;
  /** Title text */
  title: string;
  /** Description text */
  description?: string;
  /** Call to action button */
  action?: ReactNode;
}

// =============================================================================
// CONFIRMATION DIALOG
// =============================================================================

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
