/**
 * Input component visual and functional tests.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect } from 'vitest';

import { Input, type InputSize, type InputValidationState } from '@/components/ui/Input';

describe('Input', () => {
  describe('Basic Rendering', () => {
    it('renders with label', () => {
      render(<Input label="Email" name="email" />);
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    });

    it('renders without label', () => {
      render(<Input name="email" placeholder="Enter email" />);
      expect(screen.getByPlaceholderText(/enter email/i)).toBeInTheDocument();
    });

    it('associates label with input correctly', () => {
      render(<Input label="Password" name="password" />);
      const input = screen.getByLabelText(/password/i);
      expect(input).toHaveAttribute('id', 'password');
    });
  });

  describe('Sizes', () => {
    const sizes: InputSize[] = ['sm', 'md', 'lg'];

    sizes.forEach((size) => {
      it(`renders ${size} size correctly`, () => {
        render(<Input label="Test" name="test" inputSize={size} />);
        expect(screen.getByLabelText(/test/i)).toBeInTheDocument();
      });
    });

    it('sm size has correct height class', () => {
      render(<Input label="Small" name="small" inputSize="sm" />);
      const input = screen.getByLabelText(/small/i);
      expect(input.className).toMatch(/h-9/);
    });

    it('md size has correct height class', () => {
      render(<Input label="Medium" name="medium" inputSize="md" />);
      const input = screen.getByLabelText(/medium/i);
      expect(input.className).toMatch(/h-11/);
    });

    it('lg size has correct height class', () => {
      render(<Input label="Large" name="large" inputSize="lg" />);
      const input = screen.getByLabelText(/large/i);
      expect(input.className).toMatch(/h-12/);
    });
  });

  describe('Validation States', () => {
    const states: InputValidationState[] = ['default', 'valid', 'invalid'];

    states.forEach((state) => {
      it(`renders ${state} state correctly`, () => {
        render(<Input label="Test" name="test" validationState={state} />);
        expect(screen.getByLabelText(/test/i)).toBeInTheDocument();
      });
    });

    it('valid state has success border color', () => {
      render(<Input label="Valid" name="valid" validationState="valid" />);
      const input = screen.getByLabelText(/valid/i);
      expect(input.className).toMatch(/border-success/);
    });

    it('invalid state has error border color', () => {
      render(<Input label="Invalid" name="invalid" validationState="invalid" />);
      const input = screen.getByLabelText(/invalid/i);
      expect(input.className).toMatch(/border-error/);
    });
  });

  describe('Error Message', () => {
    it('displays error message', () => {
      render(
        <Input label="Email" name="email" errorMessage="Invalid email address" />
      );
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });

    it('sets aria-invalid when error is present', () => {
      render(
        <Input label="Email" name="email" errorMessage="Invalid email" />
      );
      const input = screen.getByLabelText(/email/i);
      expect(input).toHaveAttribute('aria-invalid', 'true');
    });

    it('error message has role="alert"', () => {
      render(
        <Input label="Email" name="email" errorMessage="Error!" />
      );
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('input is described by error message', () => {
      render(
        <Input label="Email" name="email" errorMessage="Invalid" />
      );
      const input = screen.getByLabelText(/email/i);
      expect(input).toHaveAttribute('aria-describedby', 'email-error');
    });
  });

  describe('Helper Text', () => {
    it('displays helper text', () => {
      render(
        <Input label="Password" name="password" helperText="Must be 8+ characters" />
      );
      expect(screen.getByText(/must be 8\+ characters/i)).toBeInTheDocument();
    });

    it('hides helper text when error is shown', () => {
      render(
        <Input
          label="Password"
          name="password"
          helperText="Must be 8+ characters"
          errorMessage="Too short"
        />
      );
      expect(screen.queryByText(/must be 8\+ characters/i)).not.toBeInTheDocument();
      expect(screen.getByText(/too short/i)).toBeInTheDocument();
    });
  });

  describe('Icons', () => {
    it('renders left icon', () => {
      render(
        <Input
          label="Search"
          name="search"
          leftIcon={<span data-testid="search-icon">🔍</span>}
        />
      );
      expect(screen.getByTestId('search-icon')).toBeInTheDocument();
    });

    it('renders right element', () => {
      render(
        <Input
          label="Password"
          name="password"
          rightElement={<button data-testid="toggle-visibility">👁</button>}
        />
      );
      expect(screen.getByTestId('toggle-visibility')).toBeInTheDocument();
    });

    it('left icon has padding adjustment', () => {
      render(
        <Input
          label="Search"
          name="search"
          leftIcon={<span>🔍</span>}
        />
      );
      const input = screen.getByLabelText(/search/i);
      expect(input.className).toMatch(/pl-10/);
    });
  });

  describe('Hide Label', () => {
    it('label is visually hidden but accessible', () => {
      render(<Input label="Hidden Label" name="hidden" hideLabel />);
      const label = screen.getByText(/hidden label/i);
      expect(label.className).toMatch(/sr-only/);
    });
  });

  describe('Disabled State', () => {
    it('renders disabled state correctly', () => {
      render(<Input label="Disabled" name="disabled" disabled />);
      const input = screen.getByLabelText(/disabled/i);
      expect(input).toBeDisabled();
    });

    it('disabled input has appropriate styling', () => {
      render(<Input label="Disabled" name="disabled" disabled />);
      const input = screen.getByLabelText(/disabled/i);
      expect(input.className).toMatch(/disabled:cursor-not-allowed/);
    });
  });

  describe('Dark Mode', () => {
    it('has dark mode classes', () => {
      render(<Input label="Dark" name="dark" />);
      const input = screen.getByLabelText(/dark/i);
      expect(input.className).toMatch(/dark:/);
    });
  });

  describe('User Input', () => {
    it('accepts user input', async () => {
      const user = userEvent.setup();
      render(<Input label="Email" name="email" />);

      const input = screen.getByLabelText(/email/i);
      await user.type(input, 'test@example.com');

      expect(input).toHaveValue('test@example.com');
    });
  });
});
