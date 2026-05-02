import { useQuery } from '@tanstack/react-query';
import api from '../utils/api';

const MOCK_STATS = {
  total: 24,
  critical: 3,
  completed: 8,
};

const MOCK_QUEUE = [
  { id: 'app-1', queuePosition: 1, patientId: 'p-1', patientName: 'John Doe', age: 65, priority: 'critical', scheduledTime: '09:00 AM', estimatedDuration: '30m', status: 'CONFIRMED' },
  { id: 'app-2', queuePosition: 2, patientId: 'p-2', patientName: 'Mary Smith', age: 28, priority: 'moderate', scheduledTime: '09:30 AM', estimatedDuration: '15m', status: 'CONFIRMED' },
  { id: 'app-3', queuePosition: 3, patientId: 'p-3', patientName: 'James Wilson', age: 45, priority: 'routine', scheduledTime: '10:00 AM', estimatedDuration: '15m', status: 'CONFIRMED' },
  { id: 'app-4', queuePosition: 4, patientId: 'p-4', patientName: 'Alice Brown', age: 52, priority: 'routine', scheduledTime: '10:15 AM', estimatedDuration: '20m', status: 'CONFIRMED' },
];

export const useDashboardStats = (doctorId, date) => {
  return useQuery({
    queryKey: ['dashboard', 'stats', doctorId, date],
    queryFn: async () => {
      try {
        const response = await api.get('/dashboard/stats', { params: { doctorId, date } });
        return response.data;
      } catch (error) {
        console.warn('Failed to fetch stats, using mock data.');
        return new Promise(resolve => setTimeout(() => resolve(MOCK_STATS), 400));
      }
    },
  });
};

export const usePriorityQueue = (doctorId, date) => {
  return useQuery({
    queryKey: ['dashboard', 'queue', doctorId, date],
    queryFn: async () => {
      try {
        const response = await api.get('/appointments/queue', { params: { doctorId, date } });
        return response.data;
      } catch (error) {
        console.warn('Failed to fetch queue, using mock data.');
        return new Promise(resolve => setTimeout(() => resolve(MOCK_QUEUE), 500));
      }
    },
    refetchInterval: 60000, // Real-time refresh every 60 seconds
  });
};
