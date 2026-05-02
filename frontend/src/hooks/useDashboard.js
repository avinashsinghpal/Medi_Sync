import { useQuery } from '@tanstack/react-query';
import api from '../utils/api';

export const useDashboardStats = (doctorId, date) => {
  return useQuery({
    queryKey: ['dashboard', 'stats', doctorId, date],
    queryFn: async () => {
      const response = await api.get('/dashboard/overview', { params: { doctor_id: doctorId, d: date } });
      return {
        total: response.data.total_patients_today,
        critical: response.data.critical_count,
        completed: response.data.completed_consultations,
      };
    },
    enabled: !!doctorId,
  });
};

export const usePriorityQueue = (doctorId, date) => {
  return useQuery({
    queryKey: ['dashboard', 'queue', doctorId, date],
    queryFn: async () => {
      const response = await api.get(`/doctor/${doctorId}/queue`, { params: { d: date } });
      return (response.data.queue || []).map((item) => ({
        id: item.appointment_id,
        queuePosition: item.queue_position,
        patientId: item.patient_id,
        patientName: item.patient_name,
        age: item.age,
        priority: item.priority_level,
        scheduledTime: item.scheduled_at,
        estimatedDuration: `${item.estimated_duration_minutes}m`,
        status: item.status,
      }));
    },
    enabled: !!doctorId,
    refetchInterval: 60000,
  });
};
