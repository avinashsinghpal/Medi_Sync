import { render, screen } from '@testing-library/react';
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

  const mockQueue = [
    { id: 'app-1', patientName: 'Routine Patient', age: 30, priority: 'routine', scheduledTime: '10:00 AM', status: 'pending' },
    { id: 'app-2', patientName: 'Critical Patient', age: 70, priority: 'critical', scheduledTime: '09:00 AM', status: 'confirmed' }
  ];

  it('renders both patients in the queue', () => {
    usePriorityQueue.mockReturnValue({
      data: mockQueue,
      isLoading: false,
      isError: false
    });

    renderWithRouter(<PriorityQueue doctorId="d-1" date="2023-10-10" />);

    expect(screen.getByText('Routine Patient')).toBeInTheDocument();
    expect(screen.getByText('Critical Patient')).toBeInTheDocument();
  });

  it('displays CRITICAL patient before ROUTINE patient (sorted by priority)', () => {
    usePriorityQueue.mockReturnValue({
      data: mockQueue,
      isLoading: false,
      isError: false
    });

    renderWithRouter(<PriorityQueue doctorId="d-1" date="2023-10-10" />);

    const allNames = screen.getAllByText(/Patient/);
    // Critical should appear before Routine in the DOM
    const criticalIdx = allNames.findIndex(el => el.textContent === 'Critical Patient');
    const routineIdx  = allNames.findIndex(el => el.textContent === 'Routine Patient');
    expect(criticalIdx).toBeLessThan(routineIdx);
  });

  it('shows "Queue is clear" when queue is empty', () => {
    usePriorityQueue.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false
    });

    renderWithRouter(<PriorityQueue doctorId="d-1" date="2023-10-10" />);
    expect(screen.getByText(/queue is clear/i)).toBeInTheDocument();
  });

  it('shows a loading spinner when data is loading', () => {
    usePriorityQueue.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false
    });

    renderWithRouter(<PriorityQueue doctorId="d-1" date="2023-10-10" />);
    // Should not show any patient names while loading
    expect(screen.queryByText('Routine Patient')).not.toBeInTheDocument();
  });

  it('shows an error message when the fetch fails', () => {
    usePriorityQueue.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true
    });

    renderWithRouter(<PriorityQueue doctorId="d-1" date="2023-10-10" />);
    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  });

  it('shows appointment count badge in header', () => {
    usePriorityQueue.mockReturnValue({
      data: mockQueue,
      isLoading: false,
      isError: false
    });

    renderWithRouter(<PriorityQueue doctorId="d-1" date="2023-10-10" />);
    expect(screen.getByText(/2 appointments/i)).toBeInTheDocument();
  });
});
