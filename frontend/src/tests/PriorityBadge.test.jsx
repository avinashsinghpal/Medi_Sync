import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import PriorityBadge from '../components/shared/PriorityBadge';

describe('PriorityBadge', () => {
  it('renders critical priority with red badge and 🔴 icon', () => {
    render(<PriorityBadge priority="critical" />);
    
    // Check if the component renders the label
    expect(screen.getByText('Critical')).toBeInTheDocument();
    
    // Check if the icon is present
    expect(screen.getByText('🔴')).toBeInTheDocument();
  });
  
  it('renders routine priority correctly', () => {
    render(<PriorityBadge priority="routine" />);
    expect(screen.getByText('Routine')).toBeInTheDocument();
    expect(screen.getByText('🟢')).toBeInTheDocument();
  });
});
