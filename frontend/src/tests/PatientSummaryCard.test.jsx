import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import PatientSummaryCard from '../components/doctor/PatientSummaryCard';
import { BrowserRouter } from 'react-router-dom';

// Mock the hook
vi.mock('../hooks/usePatientData', () => ({
  usePatientSummary: vi.fn()
}));

import { usePatientSummary } from '../hooks/usePatientData';

describe('PatientSummaryCard', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  const renderWithRouter = (ui) => {
    return render(<BrowserRouter>{ui}</BrowserRouter>);
  };

  it('shows "Unknown" gracefully when blood_group is missing', () => {
    // Mock return value without blood_group
    usePatientSummary.mockReturnValue({
      data: {
        id: 'p-1',
        name: 'Jane Doe',
        age: 35,
        priority: 'routine',
        diagnoses: [],
        medications: [],
        risk_flags: []
      },
      isLoading: false,
      isError: false
    });

    renderWithRouter(<PatientSummaryCard patientId="p-1" />);
    
    // It should render "Unknown" inside the blood group span
    expect(screen.getByText('Unknown')).toBeInTheDocument();
  });

  it('shows actual blood group if present', () => {
    usePatientSummary.mockReturnValue({
      data: {
        id: 'p-2',
        name: 'John Doe',
        age: 40,
        blood_group: 'AB-',
        priority: 'routine'
      },
      isLoading: false,
      isError: false
    });

    renderWithRouter(<PatientSummaryCard patientId="p-2" />);
    expect(screen.getByText('AB-')).toBeInTheDocument();
  });
});
