import { useMutation } from '@tanstack/react-query';
import api from '../utils/api';

export const useProcessConsultation = () => {
  return useMutation({
    mutationFn: async ({ appointmentId, transcript }) => {
      const formData = new FormData();
      formData.append('appointment_id', appointmentId);
      
      if (transcript) {
        formData.append('text_input', transcript);
      }
      
      const response = await api.post('/consultation/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return {
        summary: response.data.consultation_summary,
        entities: response.data.structured_output,
        consultationId: response.data.consultation_id,
      };
    },
  });
};

export const useCompleteConsultation = () => {
  return useMutation({
    mutationFn: async ({ appointmentId, summary, consultationId }) => {
      // The backend requires consultation_id. Since the UI only sends { appointmentId, summary }, 
      // we generate a fallback consultationId if it's not provided.
      const response = await api.patch(`/appointments/${appointmentId}/complete`, {
        consultation_id: consultationId || `consultation-${appointmentId}`,
      });
      return response.data;
    },
  });
};
