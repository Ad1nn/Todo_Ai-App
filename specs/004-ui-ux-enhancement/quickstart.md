# Quickstart: UI/UX Enhancement Development

**Feature**: 004-ui-ux-enhancement
**Date**: 2026-01-30

## Prerequisites

- Node.js 20+
- npm or pnpm
- Running backend (for ChatKit session endpoints)

## Setup

### 1. Install New Dependencies

```bash
cd frontend

# ChatKit React bindings
npm install @openai/chatkit-react

# Accessible component primitives
npm install @headlessui/react

# Icons
npm install @heroicons/react

# Animation (optional, for reduced-motion-safe transitions)
npm install framer-motion
```

### 2. Add ChatKit CDN Script

Update `frontend/src/app/layout.tsx`:

```tsx
import Script from 'next/script';

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="beforeInteractive"
        />
      </head>
      <body>
        {/* ... */}
      </body>
    </html>
  );
}
```

### 3. Configure Tailwind Design Tokens

Update `frontend/tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
```

### 4. Add CSS Variables

Update `frontend/src/app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --color-background: 255 255 255;
    --color-foreground: 17 24 39;
    --color-primary: 37 99 235;
  }

  .dark {
    --color-background: 17 24 39;
    --color-foreground: 243 244 246;
  }

  /* ChatKit theming */
  openai-chatkit {
    --chatkit-primary-color: rgb(var(--color-primary));
    --chatkit-background: rgb(var(--color-background));
    --chatkit-text-color: rgb(var(--color-foreground));
  }
}

/* Focus visible for accessibility */
@layer utilities {
  .focus-ring {
    @apply focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2;
  }
}
```

### 5. Create Theme Provider

Create `frontend/src/providers/ThemeProvider.tsx`:

```tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system');

  useEffect(() => {
    const stored = localStorage.getItem('theme') as Theme | null;
    if (stored) setTheme(stored);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = theme === 'dark' || (theme === 'system' && systemDark);

    root.classList.toggle('dark', isDark);
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

## Development Workflow

### Running the App

```bash
# Terminal 1: Backend
cd backend
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Testing

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run accessibility tests only
npm test -- --testPathPattern=a11y
```

### Linting & Formatting

```bash
# Lint
npm run lint

# Format
npm run format

# Type check
npm run typecheck
```

## Component Development Pattern

### 1. Write Test First

```typescript
// tests/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { axe } from 'jest-axe';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('renders with correct variant styles', () => {
    render(<Button variant="primary">Click me</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-primary-600');
  });

  it('has no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    expect(await axe(container)).toHaveNoViolations();
  });
});
```

### 2. Implement Component

```typescript
// components/ui/Button.tsx
import { forwardRef } from 'react';
import { ButtonProps } from '@/contracts/components';
import { cn } from '@/lib/utils';

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center font-medium focus-ring',
          // Variant styles
          variant === 'primary' && 'bg-primary-600 text-white hover:bg-primary-700',
          variant === 'secondary' && 'bg-secondary-100 text-secondary-900 hover:bg-secondary-200',
          // Size styles
          size === 'sm' && 'h-8 px-3 text-sm',
          size === 'md' && 'h-10 px-4 text-base',
          size === 'lg' && 'h-12 px-6 text-lg',
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
```

### 3. Verify Accessibility

- Tab through all interactive elements
- Test with screen reader
- Check color contrast with dev tools
- Verify focus indicators are visible

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/styles/design-tokens.ts` | Color, spacing, typography values |
| `src/components/ui/*` | Design system primitives |
| `src/components/layout/*` | Page layout components |
| `src/components/chat/*` | ChatKit integration |
| `src/providers/ThemeProvider.tsx` | Dark mode management |
| `src/hooks/useTheme.ts` | Theme hook |
| `src/hooks/useMediaQuery.ts` | Responsive breakpoint hook |
| `tailwind.config.ts` | Tailwind design token extension |
| `src/app/globals.css` | CSS variables + ChatKit theme |

## Environment Variables

No new environment variables required for frontend. Backend may need:

```env
# Already configured in Phase 3
OPENAI_API_KEY=sk-...
```

## ChatKit Domain Allowlist

ChatKit requires domain verification. Add your domain in OpenAI organization settings:
- Development: `localhost:3000`
- Production: Your production domain

## Troubleshooting

### ChatKit not rendering
1. Check CDN script is loaded (Network tab)
2. Verify domain is allowlisted
3. Check console for ChatKit errors

### Dark mode flash on load
1. Ensure `suppressHydrationWarning` on `<html>`
2. Add inline script to check theme before hydration

### Accessibility audit failures
1. Run `npm test -- --testPathPattern=a11y`
2. Check axe report for specific violations
3. Use browser a11y dev tools for inspection
