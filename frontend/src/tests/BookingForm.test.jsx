import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import BookingForm from '../components/patient/BookingForm';
import { BrowserRouter } from 'react-router-dom';

vi.mock('../hooks/useAppointments', () => ({
  useBookAppointment: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  useEstimatedWaitTime: vi.fn(() => ({ data: null, isLoading: false }))
}));

describe('BookingForm', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  const renderWithRouter = (ui) => {
    return render(<BrowserRouter>{ui}</BrowserRouter>);
  };

  it('shows form validation error when advancing with empty symptoms', async () => {
    renderWithRouter(<BookingForm />);

    // Step 1: Reason
    const reasonInput = screen.getByRole('textbox');
    fireEvent.change(reasonInput, { target: { value: 'This is a valid reason that is long enough.' } });
    
    const nextBtn1 = screen.getByText('Next Step');
    fireEvent.click(nextBtn1);

    // Wait for Step 2 to render
    await waitFor(() => {
      expect(screen.getByText('Current Symptoms')).toBeInTheDocument();
    });

    // We are on Step 2. Try to advance without adding any symptoms.
    const nextBtn2 = screen.getByText('Next Step');
    fireEvent.click(nextBtn2);

    // Expect validation error to appear
    await waitFor(() => {
      expect(screen.getByText('Please add at least one symptom')).toBeInTheDocument();
    });
  });
});
