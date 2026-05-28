/**
 * SharePoint list client for the three PTO lists on the Pyrovio site.
 *
 * Lists:
 *   CodeAppPTOBalances   – employee balance records
 *   CodeAppPTORequests   – PTO request submissions
 *   CodeAppPTOSupervisors – supervisor lookup
 *
 * Authentication goes through the Power Apps Code App host context: all fetch
 * calls pass through Dataverse as a proxy via instant Power Automate flows
 * registered as connection references (similar to the document-upload proxy
 * pattern used in the original CFR solution).
 *
 * Once Power Automate flows are wired in the Pyrovio Sandbox environment,
 * replace the stub implementations below with real dv.executeAction calls.
 */

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

// ---------- API functions ----------
// These call Dataverse custom APIs / Power Automate flows that proxy to SharePoint.
// TODO: replace stubs with real executeAction calls once flows are deployed.

export async function getPtoBalance(_employeeId: string): Promise<PtoBalance | null> {
  // Placeholder — will call a Dataverse custom API backed by a Power Automate flow
  // that reads the current user's row from CodeAppPTOBalances.
  return null;
}

export async function listPtoRequests(_employeeId: string): Promise<PtoRequest[]> {
  // Placeholder — will call a Dataverse custom API backed by a Power Automate flow
  // that queries CodeAppPTORequests filtered to the current user.
  return [];
}

export async function createPtoRequest(req: NewPtoRequest): Promise<PtoRequest> {
  // Placeholder — will call a Dataverse custom API backed by a Power Automate flow
  // that creates an item in CodeAppPTORequests.
  void req;
  throw new Error('createPtoRequest: Power Automate flow not yet connected. Deploy to Pyrovio Sandbox first.');
}

export async function listSupervisors(): Promise<PtoSupervisor[]> {
  // Placeholder — will call a Dataverse custom API backed by a Power Automate flow
  // that reads CodeAppPTOSupervisors.
  return [];
}
