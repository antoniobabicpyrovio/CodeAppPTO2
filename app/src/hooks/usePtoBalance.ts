import { useQuery } from '@tanstack/react-query';
import { getPtoBalance } from '../lib/sharePointListClient';
import { useCurrentUserId } from './useCurrentUserId';

export function usePtoBalance() {
  const userId = useCurrentUserId();
  return useQuery({
    queryKey: ['pto-balance', userId],
    queryFn: () => getPtoBalance(userId ?? ''),
    enabled: userId !== undefined,
  });
}
