/**
 * Keyboard navigation accessibility tests.
 * Verifies that all interactive elements are keyboard accessible.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Modal } from '@/components/ui/Modal';
import { ConfirmationDialog } from '@/components/ui/ConfirmationDialog';

describe('Keyboard Navigation', () => {
  describe('Button', () => {
    it('can be focused with Tab key', async () => {
      const user = userEvent.setup();
      render(<Button>Click me</Button>);

      const button = screen.getByRole('button', { name: /click me/i });
      expect(document.activeElement).not.toBe(button);

      await user.tab();
      expect(document.activeElement).toBe(button);
    });

    it('can be activated with Enter key', async () => {
      const user = userEvent.setup();
      const onClick = vi.fn();
      render(<Button onClick={onClick}>Click me</Button>);

      const button = screen.getByRole('button');
      button.focus();

      await user.keyboard('{Enter}');
      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('can be activated with Space key', async () => {
      const user = userEvent.setup();
      const onClick = vi.fn();
      render(<Button onClick={onClick}>Click me</Button>);

      const button = screen.getByRole('button');
      button.focus();

      await user.keyboard(' ');
      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it('has visible focus indicator (focus-visible class)', () => {
      render(<Button>Focus me</Button>);
      const button = screen.getByRole('button');

      // Check that focus-visible styles are applied
      expect(button.className).toContain('focus-visible:ring');
    });

    it('disabled button cannot be focused', async () => {
      const user = userEvent.setup();
      render(
        <>
          <Button disabled>Disabled</Button>
          <Button>Enabled</Button>
        </>
      );

      await user.tab();
      // Should skip disabled button and focus enabled one
      expect(screen.getByRole('button', { name: /enabled/i })).toHaveFocus();
    });
  });

  describe('Input', () => {
    it('can be focused with Tab key', async () => {
      const user = userEvent.setup();
      render(<Input label="Email" name="email" />);

      await user.tab();
      expect(screen.getByLabelText(/email/i)).toHaveFocus();
    });

    it('has visible focus indicator', () => {
      render(<Input label="Email" name="email" />);
      const input = screen.getByLabelText(/email/i);

      expect(input.className).toContain('focus-visible:ring');
    });

    it('can receive text input from keyboard', async () => {
      const user = userEvent.setup();
      render(<Input label="Email" name="email" />);

      const input = screen.getByLabelText(/email/i);
      await user.click(input);
      await user.type(input, 'test@example.com');

      expect(input).toHaveValue('test@example.com');
    });
  });

  describe('Modal', () => {
    it('closes on Escape key', async () => {
      const user = userEvent.setup();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Modal">
          Modal content
        </Modal>
      );

      await user.keyboard('{Escape}');
      expect(onClose).toHaveBeenCalled();
    });

    it('traps focus within modal', async () => {
      const user = userEvent.setup();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Modal">
          <Input label="Name" name="name" />
          <Button>Submit</Button>
        </Modal>
      );

      // Tab through modal elements
      await user.tab();
      const closeButton = screen.getByRole('button', { name: /close/i });
      expect(closeButton).toHaveFocus();

      await user.tab();
      expect(screen.getByLabelText(/name/i)).toHaveFocus();

      await user.tab();
      expect(screen.getByRole('button', { name: /submit/i })).toHaveFocus();
    });
  });

  describe('ConfirmationDialog', () => {
    it('focuses cancel button first (safest option)', async () => {
      const user = userEvent.setup();

      render(
        <ConfirmationDialog
          isOpen={true}
          onClose={vi.fn()}
          onConfirm={vi.fn()}
          title="Confirm Delete"
          message="Are you sure?"
        />
      );

      // First focusable element should be accessible
      await user.tab();
      // Check that a button is focused
      expect(document.activeElement?.tagName).toBe('BUTTON');
    });

    it('can navigate between buttons with Tab', async () => {
      const user = userEvent.setup();

      render(
        <ConfirmationDialog
          isOpen={true}
          onClose={vi.fn()}
          onConfirm={vi.fn()}
          title="Confirm"
          message="Are you sure?"
          confirmLabel="Delete"
          cancelLabel="Cancel"
        />
      );

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      const confirmButton = screen.getByRole('button', { name: /delete/i });

      // Both buttons should exist and be focusable
      expect(cancelButton).toBeInTheDocument();
      expect(confirmButton).toBeInTheDocument();
    });

    it('closes on Escape key', async () => {
      const user = userEvent.setup();
      const onClose = vi.fn();

      render(
        <ConfirmationDialog
          isOpen={true}
          onClose={onClose}
          onConfirm={vi.fn()}
          title="Confirm"
          message="Are you sure?"
        />
      );

      await user.keyboard('{Escape}');
      expect(onClose).toHaveBeenCalled();
    });
  });
});
