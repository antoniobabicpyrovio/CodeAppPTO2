const GRAPH_BASE = 'https://graph.microsoft.com/v1.0';
const SP_SITE_PATH = 'enoviogroup.sharepoint.com:/sites/Pyrovio:';

export const SP_SITE = 'https://enoviogroup.sharepoint.com/sites/Pyrovio';
export const SP_LISTS = {
  balances:    'CodeAppPTOBalances',
  requests:    'CodeAppPTORequests',
  supervisors: 'CodeAppPTOSupervisors',
} as const;

// ---------- Types ----------

export interface PtoBalance {
  id: string;
  EmployeeName: string;
  EmployeeId: string;
  SupervisorName?: string;
  AvailableHours: number;
  UsedHours: number;
  AccruedHours: number;
  CarryOverHours: number;
  AsOfDate: string;
}

export interface PtoRequest {
  id: string;
  EmployeeName?: string;
  EmployeeId?: string;
  StartDate: string;
  EndDate: string;
  Type: string;
  Notes?: string;
  Status: 'Pending' | 'Approved' | 'Denied';
  SubmittedOn?: string;
}

export interface PtoSupervisor {
  id: string;
  SupervisorName: string;
  SupervisorEmail: string;
  Department?: string;
}

export interface NewPtoRequest {
  startDate: string;
  endDate: string;
  type: string;
  notes?: string;
}

// ---------- Internal fetch helper ----------

async function spFetch(listName: string, path: string, options?: RequestInit): Promise<Response> {
  const url = `${GRAPH_BASE}/sites/${SP_SITE_PATH}/lists/${encodeURIComponent(listName)}${path}`;
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...options?.headers,
    },
    credentials: 'include',
  });
}

// ---------- API functions ----------

export async function getPtoBalance(employeeId: string): Promise<PtoBalance | null> {
  const filter = employeeId
    ? `&$filter=fields/EmployeeId eq '${employeeId}'`
    : '';
  const res = await spFetch(
    SP_LISTS.balances,
    `/items?$expand=fields${filter}&$top=1`,
  );
  if (!res.ok) throw new Error(`Failed to fetch PTO balance: ${res.status}`);
  const json = await res.json();
  const item = json.value?.[0];
  if (!item) return null;
  const f = item.fields;
  return {
    id: item.id,
    EmployeeName: f.EmployeeName ?? '',
    EmployeeId: f.EmployeeId ?? '',
    SupervisorName: f.SupervisorName,
    AvailableHours: Number(f.AvailableHours ?? 0),
    UsedHours: Number(f.UsedHours ?? 0),
    AccruedHours: Number(f.AccruedHours ?? 0),
    CarryOverHours: Number(f.CarryOverHours ?? 0),
    AsOfDate: f.AsOfDate ?? '',
  };
}

export async function listPtoRequests(employeeId: string): Promise<PtoRequest[]> {
  const filter = employeeId
    ? `&$filter=fields/EmployeeId eq '${employeeId}'`
    : '';
  const res = await spFetch(
    SP_LISTS.requests,
    `/items?$expand=fields${filter}&$orderby=fields/Created desc`,
  );
  if (!res.ok) throw new Error(`Failed to fetch PTO requests: ${res.status}`);
  const json = await res.json();
  return (json.value ?? []).map((item: { id: string; fields: Record<string, unknown> }) => {
    const f = item.fields;
    return {
      id: item.id,
      EmployeeName: f.EmployeeName as string | undefined,
      EmployeeId: f.EmployeeId as string | undefined,
      StartDate: (f.StartDate as string) ?? '',
      EndDate: (f.EndDate as string) ?? '',
      Type: (f.Type as string) ?? '',
      Notes: f.Notes as string | undefined,
      Status: ((f.Status as string) ?? 'Pending') as 'Pending' | 'Approved' | 'Denied',
      SubmittedOn: f.Created as string | undefined,
    } satisfies PtoRequest;
  });
}

export async function createPtoRequest(req: NewPtoRequest): Promise<PtoRequest> {
  const res = await spFetch(SP_LISTS.requests, '/items', {
    method: 'POST',
    body: JSON.stringify({
      fields: {
        StartDate: req.startDate,
        EndDate: req.endDate,
        Type: req.type,
        Notes: req.notes ?? '',
        Status: 'Pending',
      },
    }),
  });
  if (!res.ok) throw new Error(`Failed to create PTO request: ${res.status}`);
  const item = await res.json();
  const f = item.fields ?? {};
  return {
    id: item.id,
    StartDate: (f.StartDate as string) ?? req.startDate,
    EndDate: (f.EndDate as string) ?? req.endDate,
    Type: (f.Type as string) ?? req.type,
    Notes: f.Notes as string | undefined,
    Status: 'Pending',
    SubmittedOn: f.Created as string | undefined,
  };
}

export async function listSupervisors(): Promise<PtoSupervisor[]> {
  const res = await spFetch(
    SP_LISTS.supervisors,
    '/items?$expand=fields&$orderby=fields/SupervisorName asc',
  );
  if (!res.ok) throw new Error(`Failed to fetch supervisors: ${res.status}`);
  const json = await res.json();
  return (json.value ?? []).map((item: { id: string; fields: Record<string, unknown> }) => {
    const f = item.fields;
    return {
      id: item.id,
      SupervisorName: (f.SupervisorName as string) ?? '',
      SupervisorEmail: (f.SupervisorEmail as string) ?? '',
      Department: f.Department as string | undefined,
    } satisfies PtoSupervisor;
  });
}
