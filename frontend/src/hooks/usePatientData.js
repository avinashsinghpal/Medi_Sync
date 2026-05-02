import { useQuery, useMutation } from '@tanstack/react-query';
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

export const useAllPatients = (limit = 50, offset = 0) => {
  return useQuery({
    queryKey: ['patients', limit, offset],
    queryFn: async () => {
      const response = await api.get('/patients', { params: { limit, offset } });
      return response.data;
    },
  });
};

export const useSearchPatients = (query) => {
  return useQuery({
    queryKey: ['patientsSearch', query],
    queryFn: async () => {
      const response = await api.get('/patients/search', { params: { q: query } });
      return response.data.patients || [];
    },
    enabled: query?.length >= 2,
  });
};

export const useUpdatePatient = (patientId) => {
  return useMutation({
    mutationFn: async (data) => {
      const response = await api.patch(`/patients/${patientId}`, data);
      return response.data;
    },
  });
};
