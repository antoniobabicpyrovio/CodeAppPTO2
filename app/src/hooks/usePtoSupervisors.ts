import { useQuery } from '@tanstack/react-query';
import { listSupervisors } from '../lib/sharePointListClient';

export function usePtoSupervisors() {
  return useQuery({
    queryKey: ['pto-supervisors'],
    queryFn: listSupervisors,
    staleTime: 10 * 60 * 1000,
  });
}
