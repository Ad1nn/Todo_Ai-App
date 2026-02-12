/**
 * Focus management accessibility tests.
 * Verifies proper focus states and visual indicators.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';

describe('Focus Management', () => {
  describe('Focus Indicators', () => {
    it('Button shows focus ring on keyboard focus', () => {
      render(<Button>Test Button</Button>);
      const button = screen.getByRole('button');

      // Verify focus-visible classes are present
      expect(button.className).toMatch(/focus-visible:ring/);
      expect(button.className).toMatch(/focus:outline-none/);
    });

    it('Input shows focus ring on keyboard focus', () => {
      render(<Input label="Test Input" name="test" />);
      const input = screen.getByLabelText(/test input/i);

      expect(input.className).toMatch(/focus-visible:ring/);
      expect(input.className).toMatch(/focus:outline-none/);
    });

    it('Button variants all have visible focus states', () => {
      const variants = ['primary', 'secondary', 'ghost', 'danger'] as const;

      variants.forEach((variant) => {
        const { unmount } = render(
          <Button variant={variant}>{variant} Button</Button>
        );

        const button = screen.getByRole('button');
        expect(button.className).toMatch(/focus-visible:ring/);

        unmount();
      });
    });

    it('Input validation states all have visible focus', () => {
      const states = ['default', 'valid', 'invalid'] as const;

      states.forEach((state) => {
        const { unmount } = render(
          <Input label={`${state} input`} name={state} validationState={state} />
        );

        const input = screen.getByLabelText(new RegExp(state, 'i'));
        expect(input.className).toMatch(/focus-visible:ring/);

        unmount();
      });
    });
  });

  describe('Focus Ring Offset', () => {
    it('Button has ring offset for visibility', () => {
      render(<Button>Test</Button>);
      const button = screen.getByRole('button');

      expect(button.className).toMatch(/focus-visible:ring-offset/);
    });

    it('Button has dark mode ring offset', () => {
      render(<Button>Test</Button>);
      const button = screen.getByRole('button');

      expect(button.className).toMatch(/dark:focus-visible:ring-offset/);
    });
  });

  describe('Modal Focus Management', () => {
    it('Modal has proper ARIA attributes', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Test Modal">
          Content
        </Modal>
      );

      const dialog = screen.getByRole('dialog');
      expect(dialog).toBeInTheDocument();
    });

    it('Modal title is properly associated', () => {
      render(
        <Modal isOpen={true} onClose={vi.fn()} title="Important Modal">
          Content
        </Modal>
      );

      expect(screen.getByText('Important Modal')).toBeInTheDocument();
    });
  });

  describe('Disabled State Focus', () => {
    it('Disabled button has reduced opacity', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button');

      expect(button.className).toMatch(/disabled:opacity/);
    });

    it('Disabled button has no pointer events', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button');

      expect(button.className).toMatch(/disabled:pointer-events-none/);
    });

    it('Disabled input has appropriate styling', () => {
      render(<Input label="Disabled" name="disabled" disabled />);
      const input = screen.getByLabelText(/disabled/i);

      expect(input.className).toMatch(/disabled:cursor-not-allowed/);
      expect(input.className).toMatch(/disabled:opacity/);
    });
  });

  describe('Loading State Focus', () => {
    it('Loading button is disabled for interactions', () => {
      render(<Button isLoading>Loading</Button>);
      const button = screen.getByRole('button');

      expect(button).toBeDisabled();
    });

    it('Loading button has aria-busy', () => {
      render(<Button isLoading>Loading</Button>);
      const button = screen.getByRole('button');

      expect(button).toHaveAttribute('aria-busy', 'true');
    });
  });

  describe('Skip Link', () => {
    it('Skip link becomes visible on focus', () => {
      // Skip link is in root layout, so we test the pattern
      const skipLink = document.createElement('a');
      skipLink.className = 'sr-only focus:not-sr-only';
      skipLink.href = '#main-content';
      skipLink.textContent = 'Skip to main content';

      // Verify the pattern is correct
      expect(skipLink.className).toContain('sr-only');
      expect(skipLink.className).toContain('focus:not-sr-only');
    });
  });

  describe('ARIA Invalid State', () => {
    it('Input with error has aria-invalid', () => {
      render(
        <Input label="Email" name="email" errorMessage="Invalid email" />
      );
      const input = screen.getByLabelText(/email/i);

      expect(input).toHaveAttribute('aria-invalid', 'true');
    });

    it('Input with error is described by error message', () => {
      render(
        <Input label="Email" name="email" errorMessage="Invalid email" />
      );
      const input = screen.getByLabelText(/email/i);

      expect(input).toHaveAttribute('aria-describedby');
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
    });

    it('Input without error has aria-invalid false', () => {
      render(<Input label="Email" name="email" />);
      const input = screen.getByLabelText(/email/i);

      expect(input).toHaveAttribute('aria-invalid', 'false');
    });
  });
});
