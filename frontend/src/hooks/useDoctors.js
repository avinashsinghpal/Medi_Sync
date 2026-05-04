import { useQuery } from '@tanstack/react-query';
import api from '../utils/api';

export const useDoctors = () =>
  useQuery({
    queryKey: ['doctors'],
    queryFn: async () => {
      const response = await api.get('/doctors');
      return response.data?.doctors || [];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
