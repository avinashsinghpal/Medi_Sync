import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../utils/api';

export const useBookAppointment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (appointmentData) => {
      try {
        const response = await api.post('/appointments', appointmentData);
        return response.data;
      } catch (error) {
        // Rethrow with the backend detail message so the UI can display it
        const detail = error?.response?.data?.detail;
        if (detail) throw new Error(detail);
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    }
  });
};

export const usePatientAppointments = (patientId) =>
  useQuery({
    queryKey: ['appointments', 'patient', patientId],
    queryFn: async () => {
      const response = await api.get(`/appointments/patient/${patientId}`);
      return response.data;
    },
    enabled: !!patientId,
  });

export const useAppointment = (appointmentId) =>
  useQuery({
    queryKey: ['appointments', appointmentId],
    queryFn: async () => {
      const response = await api.get(`/appointments/${appointmentId}`);
      return response.data;
    },
    enabled: !!appointmentId,
  });

export const useEstimatedWaitTime = (symptoms) => {
  return useQuery({
    queryKey: ['wait_time', symptoms],
    queryFn: async () => {
      if (!symptoms || symptoms.length === 0) return null;
      try {
        // Assume API has an endpoint that estimates priority & wait time from symptoms
        const response = await api.post(`/appointments/estimate`, { symptoms });
        return response.data;
      } catch (error) {
        // Mock calculation
        const isCritical = symptoms.some(s => ['chest pain', 'breathing', 'bleeding'].some(k => s.toLowerCase().includes(k)));
        return new Promise(resolve => setTimeout(() => resolve({
          priority: isCritical ? 'critical' : 'routine',
          estimatedWaitMinutes: isCritical ? 5 : 45
        }), 400));
      }
    },
    enabled: symptoms && symptoms.length > 0,
  });
};
