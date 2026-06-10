import { PageHeader } from '../../components/layout/PageHeader';
import { usePtoBalance } from '../../hooks/usePtoBalance';

export function PtoBalancePage() {
  const { data: balances = [], isLoading, error } = usePtoBalance();

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="PTO Balance"
        subtitle="Available and used time-off balances"
      />

      <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
        <div className="px-5 py-3 border-b bg-muted/30">
          <h2 className="text-sm font-semibold">All Balances</h2>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">Loading…</div>
        ) : error ? (
          <div className="flex items-center justify-center py-12 text-sm text-rose-500">Failed to load balances.</div>
        ) : balances.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-2">
            <p className="text-sm">No balance records found.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/20 text-xs text-muted-foreground">
                <th className="text-left px-5 py-2.5 font-medium">Employee</th>
                <th className="text-left px-5 py-2.5 font-medium">Supervisor</th>
                <th className="text-right px-5 py-2.5 font-medium">Available</th>
                <th className="text-right px-5 py-2.5 font-medium">Used</th>
                <th className="text-right px-5 py-2.5 font-medium">Accrued YTD</th>
                <th className="text-right px-5 py-2.5 font-medium">Carry-over</th>
                <th className="text-left px-5 py-2.5 font-medium">As Of</th>
              </tr>
            </thead>
            <tbody>
              {balances.map((b) => (
                <tr key={b.id} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                  <td className="px-5 py-3 font-medium">{b.EmployeeName || '—'}</td>
                  <td className="px-5 py-3 text-muted-foreground">{b.SupervisorName || '—'}</td>
                  <td className="px-5 py-3 text-right text-emerald-700 font-medium">{b.AvailableHours} hrs</td>
                  <td className="px-5 py-3 text-right text-amber-700">{b.UsedHours} hrs</td>
                  <td className="px-5 py-3 text-right text-sky-700">{b.AccruedHours} hrs</td>
                  <td className="px-5 py-3 text-right">{b.CarryOverHours} hrs</td>
                  <td className="px-5 py-3 text-muted-foreground">{b.AsOfDate || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
