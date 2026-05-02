import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../utils/api';

export function useProcessConsultation() {
  return useMutation({
    mutationFn: async ({ appointmentId, textInput, audioBlob }) => {
      // Create FormData to send text and audio properly
      const formData = new FormData();
      formData.append('appointment_id', appointmentId);
      if (textInput) {
        formData.append('text_input', textInput);
      }
      if (audioBlob) {
        formData.append('audio', audioBlob, 'recording.webm');
      }

      // If backend only accepts JSON for text-only, we might need a fallback or ensure backend accepts multipart/form-data.
      // But based on FastAPI, if it accepts `UploadFile`, multipart/form-data is required.
      const response = await api.post('/consultation/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
  });
}

export function useCompleteConsultation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ appointmentId, consultationId }) => {
      const response = await api.patch(`/appointments/${appointmentId}/complete`, {
        consultation_id: consultationId
      });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate relevant queries to update dashboard and queue
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
