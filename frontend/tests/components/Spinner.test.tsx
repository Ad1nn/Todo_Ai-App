/**
 * Spinner component tests.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

import { Spinner, type SpinnerSize } from '@/components/ui/Spinner';

describe('Spinner', () => {
  describe('Sizes', () => {
    const sizes: SpinnerSize[] = ['sm', 'md', 'lg'];

    sizes.forEach((size) => {
      it(`renders ${size} size correctly`, () => {
        render(<Spinner size={size} />);
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });

    it('sm size has smaller dimensions', () => {
      render(<Spinner size="sm" />);
      const spinner = screen.getByRole('status');
      expect(spinner.className).toMatch(/w-4|h-4/);
    });

    it('md size has medium dimensions', () => {
      render(<Spinner size="md" />);
      const spinner = screen.getByRole('status');
      expect(spinner.className).toMatch(/w-6|h-6/);
    });

    it('lg size has larger dimensions', () => {
      render(<Spinner size="lg" />);
      const spinner = screen.getByRole('status');
      expect(spinner.className).toMatch(/w-8|h-8/);
    });
  });

  describe('Accessibility', () => {
    it('has role="status" for assistive technology', () => {
      render(<Spinner />);
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('has accessible label', () => {
      render(<Spinner label="Loading content" />);
      expect(screen.getByText('Loading content')).toBeInTheDocument();
    });

    it('uses default label when none provided', () => {
      render(<Spinner />);
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('label is visually hidden but accessible', () => {
      render(<Spinner label="Processing" />);
      const label = screen.getByText('Processing');
      expect(label.className).toMatch(/sr-only/);
    });
  });

  describe('Animation', () => {
    it('has spinning animation class', () => {
      render(<Spinner />);
      const spinner = screen.getByRole('status');
      // The SVG inside should have animation
      const svg = spinner.querySelector('svg');
      expect(svg?.className).toMatch(/animate-spin/);
    });
  });

  describe('Custom Styling', () => {
    it('accepts custom className', () => {
      render(<Spinner className="text-red-500" />);
      const spinner = screen.getByRole('status');
      expect(spinner.className).toContain('text-red-500');
    });

    it('accepts custom color prop', () => {
      render(<Spinner color="text-blue-600" />);
      const spinner = screen.getByRole('status');
      // Color should be applied
      expect(spinner.className).toContain('text-blue-600');
    });
  });

  describe('SVG Attributes', () => {
    it('has proper SVG attributes for animation', () => {
      render(<Spinner />);
      const svg = screen.getByRole('status').querySelector('svg');
      expect(svg).toHaveAttribute('viewBox');
    });
  });
});
