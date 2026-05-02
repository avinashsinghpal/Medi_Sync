import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import SpeechRecorder from '../components/doctor/SpeechRecorder';

// Mock the hook entirely to control state
vi.mock('../hooks/useAudioRecorder', () => {
  return {
    useAudioRecorder: vi.fn()
  };
});

import { useAudioRecorder } from '../hooks/useAudioRecorder';

describe('SpeechRecorder', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('enters recording state when "Start Recording" is clicked', async () => {
    // Setup initial mock state
    let mockStatus = 'idle';
    let mockStartRecording = vi.fn(() => {
      mockStatus = 'recording';
    });

    useAudioRecorder.mockImplementation(() => ({
      status: mockStatus,
      recordingTime: 0,
      startRecording: mockStartRecording,
      stopRecording: vi.fn()
    }));

    const { rerender } = render(<SpeechRecorder onTranscript={vi.fn()} />);

    // Initially should see "Start Recording" button
    const startBtn = screen.getByText('Start Recording');
    expect(startBtn).toBeInTheDocument();

    // Click it
    fireEvent.click(startBtn);

    // Assert the start function was called
    expect(mockStartRecording).toHaveBeenCalled();

    // Re-mock to simulate the state change that would happen inside the real hook
    useAudioRecorder.mockImplementation(() => ({
      status: mockStatus, // now 'recording'
      recordingTime: 0,
      startRecording: mockStartRecording,
      stopRecording: vi.fn()
    }));

    rerender(<SpeechRecorder onTranscript={vi.fn()} />);

    // Now the Stop button should be visible
    expect(screen.getByText('Stop')).toBeInTheDocument();
    
    // And the start button should be gone
    expect(screen.queryByText('Start Recording')).not.toBeInTheDocument();
  });
});
