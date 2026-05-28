import { Wallet, TrendingDown, CheckCircle } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { usePtoBalance } from '../../hooks/usePtoBalance';

export function PtoBalancePage() {
  const { data: balance, isLoading, error } = usePtoBalance();

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="PTO Balance"
        subtitle="View your available and used time-off balances"
        icon={<Wallet className="h-5 w-5" />}
      />

      {isLoading ? (
        <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">Loading balance…</div>
      ) : error ? (
        <div className="flex items-center justify-center py-12 text-sm text-rose-500">Failed to load balance.</div>
      ) : !balance ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-2">
          <Wallet className="h-8 w-8 opacity-30" />
          <p className="text-sm">No balance information found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <BalanceCard
            label="Available"
            value={balance.AvailableHours ?? 0}
            icon={<CheckCircle className="h-5 w-5 text-emerald-500" />}
            colorClass="border-emerald-200 bg-emerald-50"
            textClass="text-emerald-700"
          />
          <BalanceCard
            label="Used"
            value={balance.UsedHours ?? 0}
            icon={<TrendingDown className="h-5 w-5 text-amber-500" />}
            colorClass="border-amber-200 bg-amber-50"
            textClass="text-amber-700"
          />
          <BalanceCard
            label="Accrued YTD"
            value={balance.AccruedHours ?? 0}
            icon={<Wallet className="h-5 w-5 text-sky-500" />}
            colorClass="border-sky-200 bg-sky-50"
            textClass="text-sky-700"
          />
        </div>
      )}

      {balance && (
        <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b bg-muted/30">
            <h2 className="text-sm font-semibold">Balance Details</h2>
          </div>
          <div className="px-5 py-4 grid grid-cols-2 gap-y-3 text-sm">
            <span className="text-muted-foreground">Employee</span>
            <span className="font-medium">{balance.EmployeeName ?? '—'}</span>
            <span className="text-muted-foreground">Employee ID</span>
            <span className="font-medium">{balance.EmployeeId ?? '—'}</span>
            <span className="text-muted-foreground">Supervisor</span>
            <span className="font-medium">{balance.SupervisorName ?? '—'}</span>
            <span className="text-muted-foreground">Carry-over Hours</span>
            <span className="font-medium">{balance.CarryOverHours ?? 0} hrs</span>
            <span className="text-muted-foreground">As of</span>
            <span className="font-medium">{balance.AsOfDate ?? '—'}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function BalanceCard({
  label, value, icon, colorClass, textClass,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  colorClass: string;
  textClass: string;
}) {
  return (
    <div className={`rounded-xl border p-5 flex items-center gap-4 ${colorClass}`}>
      <div className="shrink-0">{icon}</div>
      <div>
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
        <p className={`text-2xl font-bold ${textClass}`}>{value} <span className="text-sm font-normal">hrs</span></p>
      </div>
    </div>
  );
}
