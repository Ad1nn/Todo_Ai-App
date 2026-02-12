# Data Model: UI/UX Enhancement

**Feature**: 004-ui-ux-enhancement
**Date**: 2026-01-30

## Overview

This feature is frontend-only; no database schema changes required. This document defines the TypeScript interfaces for design tokens and component props.

---

## Design Tokens

### Color Palette

```typescript
// styles/design-tokens.ts

export const colors = {
  // Primary (Blue)
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',  // Base
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },

  // Secondary (Gray)
  secondary: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',  // Base
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },

  // Semantic Colors
  success: {
    500: '#22c55e',
    600: '#16a34a',  // Base
    700: '#15803d',
  },
  warning: {
    400: '#facc15',
    500: '#eab308',  // Base
    600: '#ca8a04',
  },
  error: {
    500: '#ef4444',
    600: '#dc2626',  // Base
    700: '#b91c1c',
  },
} as const;

export type ColorScale = keyof typeof colors;
```

### Typography Scale

```typescript
export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],      // 12px
    sm: ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
    base: ['1rem', { lineHeight: '1.5rem' }],     // 16px
    lg: ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
    xl: ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
    '2xl': ['1.5rem', { lineHeight: '2rem' }],    // 24px
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }], // 36px
  },
  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
} as const;
```

### Spacing Scale

```typescript
export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
} as const;
```

### Breakpoints

```typescript
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;
```

---

## Theme State

```typescript
// types/theme.ts

export type Theme = 'light' | 'dark' | 'system';

export interface ThemeContextValue {
  theme: Theme;
  resolvedTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
}
```

---

## Component State Models

### Toast Notification

```typescript
// types/toast.ts

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  variant: ToastVariant;
  title: string;
  description?: string;
  duration?: number;  // ms, default 5000
  dismissible?: boolean;
}

export interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}
```

### Modal State

```typescript
// types/modal.ts

export interface ModalState {
  isOpen: boolean;
  content: React.ReactNode | null;
  title?: string;
  onClose?: () => void;
}
```

### Navigation State

```typescript
// types/navigation.ts

export interface NavItem {
  label: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  badge?: string | number;
}

export interface NavigationState {
  items: NavItem[];
  activeItem: string;
  isMobileMenuOpen: boolean;
}
```

---

## Validation Rules

### Form Input Validation States

```typescript
export type InputValidationState = 'default' | 'valid' | 'invalid' | 'loading';

export interface InputValidation {
  state: InputValidationState;
  message?: string;
}
```

### Button States

```typescript
export type ButtonState = 'default' | 'hover' | 'active' | 'focus' | 'disabled' | 'loading';
```

---

## Entity Relationships

```
ThemeProvider
    └── provides → ThemeContextValue

ToastProvider
    └── provides → ToastContextValue
    └── renders → Toast[]

Layout
    ├── contains → Header (ThemeToggle, MobileNav)
    ├── contains → Sidebar (NavItems)
    └── contains → MainContent (ChatKit | Pages)

ChatKit
    └── receives → control (from useChatKit)
    └── displays → Messages, ToolCalls, Input
```

---

## CSS Variable Mapping

```css
/* Tailwind config extension for CSS variables */
:root {
  /* Colors */
  --color-primary: theme('colors.primary.600');
  --color-background: theme('colors.white');
  --color-text-primary: theme('colors.secondary.900');
  --color-text-secondary: theme('colors.secondary.600');
  --color-border: theme('colors.secondary.200');

  /* ChatKit theming */
  --chatkit-primary: var(--color-primary);
  --chatkit-bg: var(--color-background);
  --chatkit-text: var(--color-text-primary);
}

.dark {
  --color-background: theme('colors.secondary.900');
  --color-text-primary: theme('colors.secondary.100');
  --color-text-secondary: theme('colors.secondary.400');
  --color-border: theme('colors.secondary.700');
}
```
