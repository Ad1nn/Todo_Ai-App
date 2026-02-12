/**
 * Toast component tests.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

import { Toast, type ToastVariant } from '@/components/ui/Toast';

describe('Toast', () => {
  const defaultProps = {
    id: 'test-toast',
    variant: 'info' as ToastVariant,
    title: 'Test Toast',
  };

  describe('Variants', () => {
    const variants: ToastVariant[] = ['success', 'error', 'warning', 'info'];

    variants.forEach((variant) => {
      it(`renders ${variant} variant correctly`, () => {
        render(<Toast {...defaultProps} variant={variant} />);
        expect(screen.getByText('Test Toast')).toBeInTheDocument();
      });
    });

    it('success variant has green styling', () => {
      render(<Toast {...defaultProps} variant="success" />);
      const toast = screen.getByRole('alert');
      expect(toast.className).toMatch(/success|green/);
    });

    it('error variant has red styling', () => {
      render(<Toast {...defaultProps} variant="error" />);
      const toast = screen.getByRole('alert');
      expect(toast.className).toMatch(/error|red/);
    });
  });

  describe('Content', () => {
    it('renders title', () => {
      render(<Toast {...defaultProps} title="Important Message" />);
      expect(screen.getByText('Important Message')).toBeInTheDocument();
    });

    it('renders description when provided', () => {
      render(
        <Toast
          {...defaultProps}
          title="Title"
          description="Detailed description here"
        />
      );
      expect(screen.getByText('Detailed description here')).toBeInTheDocument();
    });

    it('does not render description when not provided', () => {
      render(<Toast {...defaultProps} />);
      const description = screen.queryByText(/detailed/i);
      expect(description).not.toBeInTheDocument();
    });
  });

  describe('Dismissal', () => {
    it('calls onDismiss when dismiss button is clicked', async () => {
      const user = userEvent.setup();
      const onDismiss = vi.fn();

      render(<Toast {...defaultProps} onDismiss={onDismiss} />);

      const dismissButton = screen.getByRole('button', { name: /dismiss|close/i });
      await user.click(dismissButton);

      expect(onDismiss).toHaveBeenCalled();
    });

    it('dismiss button is keyboard accessible', async () => {
      const user = userEvent.setup();
      const onDismiss = vi.fn();

      render(<Toast {...defaultProps} onDismiss={onDismiss} />);

      const dismissButton = screen.getByRole('button', { name: /dismiss|close/i });
      dismissButton.focus();
      await user.keyboard('{Enter}');

      expect(onDismiss).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has role="alert" for screen readers', () => {
      render(<Toast {...defaultProps} />);
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('is announced to assistive technology', () => {
      render(<Toast {...defaultProps} title="Announcement" />);
      const toast = screen.getByRole('alert');
      expect(toast).toBeInTheDocument();
    });
  });

  describe('Icons', () => {
    const variants: ToastVariant[] = ['success', 'error', 'warning', 'info'];

    variants.forEach((variant) => {
      it(`${variant} variant displays appropriate icon`, () => {
        render(<Toast {...defaultProps} variant={variant} />);
        // Icon should be present (svg or icon element)
        const toast = screen.getByRole('alert');
        expect(toast.querySelector('svg')).toBeInTheDocument();
      });
    });
  });
});
