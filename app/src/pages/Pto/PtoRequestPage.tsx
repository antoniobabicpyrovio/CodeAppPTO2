import { useState } from 'react';
import { CalendarDays, Plus, Clock, CheckCircle, XCircle } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Button } from '../../components/ui/button';
import { usePtoRequests, useCreatePtoRequest } from '../../hooks/usePtoRequests';
import { toast } from '../../hooks/useToast';

type RequestStatus = 'Pending' | 'Approved' | 'Denied';

const STATUS_ICON: Record<RequestStatus, React.ReactNode> = {
  Pending: <Clock className="h-3.5 w-3.5 text-amber-500" />,
  Approved: <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />,
  Denied: <XCircle className="h-3.5 w-3.5 text-rose-500" />,
};

const STATUS_CLS: Record<RequestStatus, string> = {
  Pending: 'bg-amber-50 text-amber-700 border-amber-200',
  Approved: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Denied: 'bg-rose-50 text-rose-700 border-rose-200',
};

export function PtoRequestPage() {
  const { data: requests = [], isLoading, error } = usePtoRequests();
  const createRequest = useCreatePtoRequest();

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    startDate: '',
    endDate: '',
    type: 'Vacation',
    notes: '',
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.startDate || !form.endDate) {
      toast.error('Start date and end date are required.');
      return;
    }
    try {
      await createRequest.mutateAsync(form);
      toast.success('PTO request submitted successfully.');
      setShowForm(false);
      setForm({ startDate: '', endDate: '', type: 'Vacation', notes: '' });
    } catch {
      toast.error('Failed to submit PTO request. Please try again.');
    }
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="PTO Request"
        subtitle="Submit and track your time-off requests"
        icon={<CalendarDays className="h-5 w-5" />}
        actions={
          <Button onClick={() => setShowForm((v) => !v)} size="sm">
            <Plus className="h-4 w-4 mr-1.5" />
            New Request
          </Button>
        }
      />

      {/* New request form */}
      {showForm && (
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h2 className="text-sm font-semibold mb-4">Submit PTO Request</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Start Date</label>
              <input
                type="date"
                value={form.startDate}
                onChange={(e) => setForm({ ...form, startDate: e.target.value })}
                className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                required
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">End Date</label>
              <input
                type="date"
                value={form.endDate}
                onChange={(e) => setForm({ ...form, endDate: e.target.value })}
                className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                required
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Type</label>
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value })}
                className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              >
                <option>Vacation</option>
                <option>Sick</option>
                <option>Personal</option>
                <option>Bereavement</option>
                <option>Other</option>
              </select>
            </div>
            <div className="flex flex-col gap-1.5 sm:col-span-2">
              <label className="text-xs font-medium text-muted-foreground">Notes (optional)</label>
              <textarea
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                rows={3}
                className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
              />
            </div>
            <div className="sm:col-span-2 flex gap-2 justify-end">
              <Button type="button" variant="outline" size="sm" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button type="submit" size="sm" disabled={createRequest.isPending}>
                {createRequest.isPending ? 'Submitting…' : 'Submit Request'}
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Request list */}
      <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
        <div className="px-5 py-3 border-b bg-muted/30">
          <h2 className="text-sm font-semibold">My Requests</h2>
        </div>
        {isLoading ? (
          <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">Loading…</div>
        ) : error ? (
          <div className="flex items-center justify-center py-12 text-sm text-rose-500">Failed to load requests.</div>
        ) : requests.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-2">
            <CalendarDays className="h-8 w-8 opacity-30" />
            <p className="text-sm">No PTO requests yet.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/20 text-xs text-muted-foreground">
                <th className="text-left px-5 py-2.5 font-medium">Start</th>
                <th className="text-left px-5 py-2.5 font-medium">End</th>
                <th className="text-left px-5 py-2.5 font-medium">Type</th>
                <th className="text-left px-5 py-2.5 font-medium">Notes</th>
                <th className="text-left px-5 py-2.5 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((req) => {
                const status = (req.Status ?? 'Pending') as RequestStatus;
                return (
                  <tr key={req.id} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                    <td className="px-5 py-3">{req.StartDate}</td>
                    <td className="px-5 py-3">{req.EndDate}</td>
                    <td className="px-5 py-3">{req.Type}</td>
                    <td className="px-5 py-3 text-muted-foreground max-w-[240px] truncate">{req.Notes}</td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium border ${STATUS_CLS[status]}`}>
                        {STATUS_ICON[status]}
                        {status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
