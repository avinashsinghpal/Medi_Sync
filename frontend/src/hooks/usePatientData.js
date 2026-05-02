import { useQuery } from '@tanstack/react-query';
import api from '../utils/api';

export const usePatientSummary = (patientId) => {
  return useQuery({
    queryKey: ['patient', patientId],
    queryFn: async () => {
      const response = await api.get(`/patients/${patientId}/summary-card`);
      const data = response.data;
      return {
        id: data.patient_id,
        name: data.full_name,
        age: data.age,
        blood_group: data.blood_group,
        priority: data.priority_level,
        diagnoses: data.recent_diagnoses || [],
        medications: data.current_medications || [],
        risk_flags: data.risk_indicators || [],
      };
    },
    enabled: !!patientId,
  });
};

export const usePatientHistory = (patientId) => {
  return useQuery({
    queryKey: ['patientHistory', patientId],
    queryFn: async () => {
      const response = await api.get(`/patients/${patientId}/history`);
      return response.data.records || [];
    },
    enabled: !!patientId,
  });
};
