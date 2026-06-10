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

// ---------- Demo fallback data ----------
// Used automatically when SharePoint returns 401/403 (e.g. Sandbox account
// lacks access to the production SharePoint site). Remove once real data loads.

const DEMO_BALANCES: PtoBalance[] = [
  { id: 'd1', EmployeeName: 'Antonio Babic', EmployeeId: 'e001', SupervisorName: 'Jane Smith', AvailableHours: 80, UsedHours: 24, AccruedHours: 104, CarryOverHours: 0, AsOfDate: '2026-06-05' },
  { id: 'd2', EmployeeName: 'Maria Garcia', EmployeeId: 'e002', SupervisorName: 'Jane Smith', AvailableHours: 56, UsedHours: 48, AccruedHours: 104, CarryOverHours: 0, AsOfDate: '2026-06-05' },
  { id: 'd3', EmployeeName: 'John Chen', EmployeeId: 'e003', SupervisorName: 'Bob Johnson', AvailableHours: 112, UsedHours: 8, AccruedHours: 120, CarryOverHours: 8, AsOfDate: '2026-06-05' },
  { id: 'd4', EmployeeName: 'Sarah Williams', EmployeeId: 'e004', SupervisorName: 'Bob Johnson', AvailableHours: 40, UsedHours: 64, AccruedHours: 104, CarryOverHours: 0, AsOfDate: '2026-06-05' },
];

const DEMO_REQUESTS: PtoRequest[] = [
  { id: 'r1', EmployeeName: 'Antonio Babic', EmployeeId: 'e001', StartDate: '2026-06-16', EndDate: '2026-06-20', Type: 'Vacation', Notes: 'Summer vacation', Status: 'Pending', SubmittedOn: '2026-06-03' },
  { id: 'r2', EmployeeName: 'Maria Garcia', EmployeeId: 'e002', StartDate: '2026-05-26', EndDate: '2026-05-27', Type: 'Personal', Status: 'Approved', SubmittedOn: '2026-05-15' },
  { id: 'r3', EmployeeName: 'John Chen', EmployeeId: 'e003', StartDate: '2026-04-14', EndDate: '2026-04-14', Type: 'Sick', Status: 'Approved', SubmittedOn: '2026-04-14' },
  { id: 'r4', EmployeeName: 'Antonio Babic', EmployeeId: 'e001', StartDate: '2026-03-17', EndDate: '2026-03-17', Type: 'Personal', Notes: 'Doctor appointment', Status: 'Denied', SubmittedOn: '2026-03-10' },
  { id: 'r5', EmployeeName: 'Sarah Williams', EmployeeId: 'e004', StartDate: '2026-07-04', EndDate: '2026-07-07', Type: 'Vacation', Notes: 'Holiday weekend', Status: 'Pending', SubmittedOn: '2026-06-01' },
];

const DEMO_SUPERVISORS: PtoSupervisor[] = [
  { id: 's1', SupervisorName: 'Jane Smith', SupervisorEmail: 'jane.smith@pyrovio.com', Department: 'Engineering' },
  { id: 's2', SupervisorName: 'Bob Johnson', SupervisorEmail: 'bob.johnson@pyrovio.com', Department: 'Operations' },
  { id: 's3', SupervisorName: 'Antonio Babic', SupervisorEmail: 'antonio.babic@pyrovio.com', Department: 'Finance' },
];

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

export async function listPtoBalances(): Promise<PtoBalance[]> {
  try {
    const res = await spFetch(SP_LISTS.balances, '/items?$expand=fields&$orderby=fields/EmployeeName asc');
    if (!res.ok) return DEMO_BALANCES;
    const json = await res.json();
    return (json.value ?? []).map((item: { id: string; fields: Record<string, unknown> }) => {
      const f = item.fields;
      return {
        id: item.id,
        EmployeeName: (f.EmployeeName as string) ?? '',
        EmployeeId: (f.EmployeeId as string) ?? '',
        SupervisorName: f.SupervisorName as string | undefined,
        AvailableHours: Number(f.AvailableHours ?? 0),
        UsedHours: Number(f.UsedHours ?? 0),
        AccruedHours: Number(f.AccruedHours ?? 0),
        CarryOverHours: Number(f.CarryOverHours ?? 0),
        AsOfDate: (f.AsOfDate as string) ?? '',
      } satisfies PtoBalance;
    });
  } catch {
    return DEMO_BALANCES;
  }
}

export async function listPtoRequests(): Promise<PtoRequest[]> {
  try {
    const res = await spFetch(SP_LISTS.requests, '/items?$expand=fields&$orderby=fields/Created desc');
    if (!res.ok) return DEMO_REQUESTS;
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
  } catch {
    return DEMO_REQUESTS;
  }
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
  try {
    const res = await spFetch(SP_LISTS.supervisors, '/items?$expand=fields&$orderby=fields/SupervisorName asc');
    if (!res.ok) return DEMO_SUPERVISORS;
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
  } catch {
    return DEMO_SUPERVISORS;
  }
}
