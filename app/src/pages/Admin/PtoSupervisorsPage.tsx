import { Mail, Building2 } from 'lucide-react';
import { PageHeader } from '../../components/layout/PageHeader';
import { usePtoSupervisors } from '../../hooks/usePtoSupervisors';

export function PtoSupervisorsPage() {
  const { data: supervisors = [], isLoading, error } = usePtoSupervisors();

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="PTO Supervisors"
        subtitle="Supervisors authorized to approve PTO requests"
      />

      <div className="rounded-xl border bg-card shadow-sm overflow-hidden">
        <div className="px-5 py-3 border-b bg-muted/30">
          <h2 className="text-sm font-semibold">Supervisors</h2>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">
            Loading…
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-12 text-sm text-rose-500">
            Failed to load supervisors.
          </div>
        ) : supervisors.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground gap-2">
            <p className="text-sm">No supervisors found.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/20 text-xs text-muted-foreground">
                <th className="text-left px-5 py-2.5 font-medium">Name</th>
                <th className="text-left px-5 py-2.5 font-medium">Email</th>
                <th className="text-left px-5 py-2.5 font-medium">Department</th>
              </tr>
            </thead>
            <tbody>
              {supervisors.map((s) => (
                <tr key={s.id} className="border-b last:border-0 hover:bg-muted/20 transition-colors">
                  <td className="px-5 py-3 font-medium">{s.SupervisorName}</td>
                  <td className="px-5 py-3">
                    <a
                      href={`mailto:${s.SupervisorEmail}`}
                      className="inline-flex items-center gap-1.5 text-primary hover:underline"
                    >
                      <Mail className="h-3.5 w-3.5" />
                      {s.SupervisorEmail}
                    </a>
                  </td>
                  <td className="px-5 py-3 text-muted-foreground">
                    {s.Department ? (
                      <span className="inline-flex items-center gap-1.5">
                        <Building2 className="h-3.5 w-3.5" />
                        {s.Department}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
