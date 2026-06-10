import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listPtoRequests, createPtoRequest, type NewPtoRequest } from '../lib/sharePointListClient';

export function usePtoRequests() {
  return useQuery({
    queryKey: ['pto-requests'],
    queryFn: listPtoRequests,
  });
}

export function useCreatePtoRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (req: NewPtoRequest) => createPtoRequest(req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pto-requests'] });
    },
  });
}
