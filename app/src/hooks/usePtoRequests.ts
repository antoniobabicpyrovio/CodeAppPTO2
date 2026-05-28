import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listPtoRequests, createPtoRequest, type NewPtoRequest } from '../lib/sharePointListClient';
import { useCurrentUserId } from './useCurrentUserId';

export function usePtoRequests() {
  const userId = useCurrentUserId();
  return useQuery({
    queryKey: ['pto-requests', userId],
    queryFn: () => listPtoRequests(userId ?? ''),
    enabled: userId !== undefined,
  });
}

export function useCreatePtoRequest() {
  const queryClient = useQueryClient();
  const userId = useCurrentUserId();
  return useMutation({
    mutationFn: (req: NewPtoRequest) => createPtoRequest(req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pto-requests', userId] });
    },
  });
}
