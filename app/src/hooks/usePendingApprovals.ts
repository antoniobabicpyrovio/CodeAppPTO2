import { useQuery } from '@tanstack/react-query';
import { listProjectRequests } from '../api/projectRequests.api';
import { REQUEST_STATUS } from '../lib/constants';
import { useCurrentUserId } from './useCurrentUserId';

/**
 * Returns the count of intake requests awaiting approval action.
 * These are requests in Submitted or InTriage status — the statuses
 * that show the StageApprovalPanel on the IntakeDetailPage.
 */
export function usePendingApprovalCount(): number {
  const { data = [] } = useQuery({
    queryKey: ['pendingApprovals'],
    queryFn: () => listProjectRequests({
      $filter: `pmo_status eq ${REQUEST_STATUS.Submitted} or pmo_status eq ${REQUEST_STATUS.InTriage}`,
      $select: ['pmo_projectrequestid'],
    }),
    staleTime: 60_000,
    refetchInterval: 60_000,
  });
  return data.length;
}

/**
 * Per-user count of intake requests where the current user is the submitter
 * AND status is AwaitingClarification — i.e. "you have a request to clarify".
 * Combined with usePendingApprovalCount in the sidebar to drive the bubble.
 */
export function useMyActionRequiredCount(): number {
  const userId = useCurrentUserId();
  const { data = [] } = useQuery({
    queryKey: ['myActionRequired', userId ?? null],
    enabled: !!userId,
    queryFn: () => listProjectRequests({
      $filter: `pmo_status eq ${REQUEST_STATUS.AwaitingClarification} and (_createdby_value eq ${userId} or _pmo_requestedby_value eq ${userId})`,
      $select: ['pmo_projectrequestid'],
    }),
    staleTime: 60_000,
    refetchInterval: 60_000,
  });
  return data.length;
}
