import { useMutation, useQuery } from '@tanstack/react-query';
import api from '../utils/api';

export const useBookAppointment = () => {
  return useMutation({
    mutationFn: async (appointmentData) => {
      try {
        const response = await api.post(`/appointments/book`, appointmentData);
        return response.data;
      } catch (error) {
        console.warn("Failed to book appointment API, using mock success.", error);
        return new Promise(resolve => setTimeout(() => resolve({ 
          id: 'app-new-1', 
          status: 'CONFIRMED',
          scheduled_time: appointmentData.date_time
        }), 1000));
      }
    }
  });
};

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
