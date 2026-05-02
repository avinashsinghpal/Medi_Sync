import { useQuery } from '@tanstack/react-query';
import api from '../utils/api';

// Mock data fallback
const MOCK_PATIENT = {
  id: 'p-1',
  name: 'Sarah Jenkins',
  age: 42,
  blood_group: 'O+',
  priority: 'moderate',
  diagnoses: ['Hypertension', 'Type 2 Diabetes', 'Asthma'],
  medications: ['Lisinopril 10mg', 'Metformin 500mg', 'Albuterol Inhaler'],
  risk_flags: ['High Blood Pressure', 'Allergic to Penicillin']
};

export const usePatientSummary = (patientId) => {
  return useQuery({
    queryKey: ['patient', patientId],
    queryFn: async () => {
      try {
        const response = await api.get(`/patients/${patientId}/summary`);
        return response.data;
      } catch (error) {
        console.warn(`Failed to fetch patient ${patientId}, using mock data.`, error);
        // Fallback to mock data for Dev D testing
        return new Promise((resolve) => {
          setTimeout(() => resolve(MOCK_PATIENT), 500);
        });
      }
    },
    enabled: !!patientId,
  });
};
