/**
 * ThemeToggle component tests.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { ThemeProvider } from '@/providers/ThemeProvider';

// Wrapper to provide theme context
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
);

describe('ThemeToggle', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('renders toggle button', () => {
      render(<ThemeToggle />, { wrapper });
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('has accessible label', () => {
      render(<ThemeToggle />, { wrapper });
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label');
    });
  });

  describe('Sizes', () => {
    it('renders small size', () => {
      render(<ThemeToggle size="sm" />, { wrapper });
      const button = screen.getByRole('button');
      expect(button.className).toMatch(/h-8|w-8/);
    });

    it('renders medium size', () => {
      render(<ThemeToggle size="md" />, { wrapper });
      const button = screen.getByRole('button');
      expect(button.className).toMatch(/h-10|w-10/);
    });

    it('renders large size', () => {
      render(<ThemeToggle size="lg" />, { wrapper });
      const button = screen.getByRole('button');
      expect(button.className).toMatch(/h-12|w-12/);
    });
  });

  describe('Menu Interaction', () => {
    it('opens menu on click', async () => {
      const user = userEvent.setup();
      render(<ThemeToggle />, { wrapper });

      const button = screen.getByRole('button');
      await user.click(button);

      // Menu items should be visible
      expect(screen.getByText('Light')).toBeInTheDocument();
      expect(screen.getByText('Dark')).toBeInTheDocument();
      expect(screen.getByText('System')).toBeInTheDocument();
    });

    it('opens menu with keyboard', async () => {
      const user = userEvent.setup();
      render(<ThemeToggle />, { wrapper });

      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard('{Enter}');

      expect(screen.getByText('Light')).toBeInTheDocument();
    });
  });

  describe('Theme Selection', () => {
    it('can select light theme', async () => {
      const user = userEvent.setup();
      render(<ThemeToggle />, { wrapper });

      const button = screen.getByRole('button');
      await user.click(button);
      await user.click(screen.getByText('Light'));

      expect(localStorage.getItem('theme')).toBe('light');
    });

    it('can select dark theme', async () => {
      const user = userEvent.setup();
      render(<ThemeToggle />, { wrapper });

      const button = screen.getByRole('button');
      await user.click(button);
      await user.click(screen.getByText('Dark'));

      expect(localStorage.getItem('theme')).toBe('dark');
    });

    it('can select system theme', async () => {
      const user = userEvent.setup();
      render(<ThemeToggle />, { wrapper });

      const button = screen.getByRole('button');
      await user.click(button);
      await user.click(screen.getByText('System'));

      expect(localStorage.getItem('theme')).toBe('system');
    });
  });

  describe('Accessibility', () => {
    it('has focus-visible styles', () => {
      render(<ThemeToggle />, { wrapper });
      const button = screen.getByRole('button');
      expect(button.className).toMatch(/focus-visible:ring/);
    });

    it('has dark mode styles', () => {
      render(<ThemeToggle />, { wrapper });
      const button = screen.getByRole('button');
      expect(button.className).toMatch(/dark:/);
    });
  });
});
