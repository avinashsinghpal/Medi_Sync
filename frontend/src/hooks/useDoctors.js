import { useQuery } from '@tanstack/react-query';
import api from '../utils/api';

export const useDoctors = () =>
  useQuery({
    queryKey: ['doctors'],
    queryFn: async () => {
      const response = await api.get('/doctors');
      return response.data?.doctors || [];
    },
  });
