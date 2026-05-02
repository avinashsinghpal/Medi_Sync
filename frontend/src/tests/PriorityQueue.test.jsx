import { render, screen, within } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import PriorityQueue from '../components/doctor/PriorityQueue';
import { BrowserRouter } from 'react-router-dom';

vi.mock('../hooks/useDashboard', () => ({
  usePriorityQueue: vi.fn()
}));

import { usePriorityQueue } from '../hooks/useDashboard';

describe('PriorityQueue', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  const renderWithRouter = (ui) => {
    return render(<BrowserRouter>{ui}</BrowserRouter>);
  };

  it('displays CRITICAL items first and highlights them with red background', () => {
    // Mock queue data where a routine item is first and critical is last in the raw array
    const mockQueue = [
      { id: 'app-1', patientName: 'Routine Patient', age: 30, priority: 'routine', scheduledTime: '10:00 AM' },
      { id: 'app-2', patientName: 'Critical Patient', age: 70, priority: 'critical', scheduledTime: '09:00 AM' }
    ];

    usePriorityQueue.mockReturnValue({
      data: mockQueue,
      isLoading: false,
      isError: false
    });

    renderWithRouter(<PriorityQueue doctorId="d-1" date="2023-10-10" />);
    
    // Check if both patients are rendered
    expect(screen.getByText('Routine Patient')).toBeInTheDocument();
    expect(screen.getByText('Critical Patient')).toBeInTheDocument();

    // Find the rows (tbody tr)
    const rows = screen.getAllByRole('row').slice(1); // skip header row
    expect(rows).toHaveLength(2);

    // The critical patient should be sorted to the top
    const firstRow = rows[0];
    const firstRowCells = within(firstRow).getAllByRole('cell');
    
    // Check name column
    expect(firstRowCells[1]).toHaveTextContent('Critical Patient');

    // Check styling on the row for red background
    // We used '#fef2f2' which is rgb(254, 242, 242)
    const styles = window.getComputedStyle(firstRow);
    expect(styles.backgroundColor).toBe('rgb(254, 242, 242)');
  });
});
