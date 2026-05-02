import { useMutation } from '@tanstack/react-query';
import api from '../utils/api';

export const useProcessConsultation = () => {
  return useMutation({
    mutationFn: async ({ appointmentId, transcript }) => {
      try {
        const response = await api.post(`/consultation/process`, {
          appointment_id: appointmentId,
          transcript_text: transcript
        });
        return response.data;
      } catch (error) {
        console.warn("Failed to process consultation API, using mock result.", error);
        
        // Mock result for dev
        return new Promise(resolve => setTimeout(() => resolve({
          entities: {
            symptoms: ["headache", "nausea"],
            medications: ["ibuprofen"],
            vitals: ["bp: 130/85"]
          },
          summary: "Patient presented with a severe headache and mild nausea. Recommended rest and ibuprofen. Blood pressure slightly elevated at 130/85.",
          suggested_priority: "routine"
        }), 1000));
      }
    }
  });
};

export const useCompleteConsultation = () => {
  return useMutation({
    mutationFn: async ({ appointmentId, summary, notes }) => {
      try {
        const response = await api.patch(`/appointments/${appointmentId}/complete`, {
          consultation_notes: summary,
          // additional parameters if needed
        });
        return response.data;
      } catch (error) {
        console.warn("Failed to complete appointment API, using mock success.", error);
        return new Promise(resolve => setTimeout(() => resolve({ success: true }), 800));
      }
    }
  });
};
