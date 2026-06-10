import { useQuery } from '@tanstack/react-query';
import { listPtoBalances } from '../lib/sharePointListClient';

export function usePtoBalance() {
  return useQuery({
    queryKey: ['pto-balances'],
    queryFn: listPtoBalances,
  });
}
