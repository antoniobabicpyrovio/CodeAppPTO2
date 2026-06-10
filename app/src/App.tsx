import { lazy, Suspense, type ReactNode } from 'react';
import { HashRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from './components/ui/tooltip';
import { AppShell } from './components/layout/AppShell';
import { ThemeProvider } from './lib/theme';
import { ToastProvider } from './components/common/ToastProvider';
import { ConfigurationProvider, useEffectiveAdminRole } from './providers/ConfigurationProvider';
import { Loader2, AlertTriangle } from 'lucide-react';
import { useEffect } from 'react';

// --- PTO Pages ---
const PtoRequestPage = lazy(() =>
  import('./pages/Pto/PtoRequestPage').then((m) => ({ default: m.PtoRequestPage }))
);
const PtoBalancePage = lazy(() =>
  import('./pages/Pto/PtoBalancePage').then((m) => ({ default: m.PtoBalancePage }))
);

// --- Administration ---
const PtoSupervisorsPage = lazy(() =>
  import('./pages/Admin/PtoSupervisorsPage').then((m) => ({ default: m.PtoSupervisorsPage }))
);
const AdminSettingsPage = lazy(() =>
  import('./pages/Admin/AdminSettingsPage').then((m) => ({ default: m.AdminSettingsPage }))
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
      <span className="ml-2 text-sm text-muted-foreground">Loading...</span>
    </div>
  );
}

function NotFoundPage() {
  const navigate = useNavigate();
  useEffect(() => {
    const t = setTimeout(() => navigate('/pto-request', { replace: true }), 4000);
    return () => clearTimeout(t);
  }, [navigate]);
  return (
    <div className="flex flex-col items-center justify-center py-24 space-y-4">
      <AlertTriangle className="h-10 w-10 text-muted-foreground" />
      <p className="text-2xl font-semibold text-foreground">Page not found</p>
      <p className="text-sm text-muted-foreground">Redirecting to PTO Request...</p>
      <button onClick={() => navigate(-1)} className="text-xs text-primary underline underline-offset-2">Go back</button>
    </div>
  );
}

function AdminRoute({ children }: { children: ReactNode }) {
  const role = useEffectiveAdminRole();
  if (role === 'none') return <Navigate to="/pto-request" replace />;
  return <>{children}</>;
}

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <ConfigurationProvider>
          <ToastProvider>
            <TooltipProvider>
              <HashRouter>
                <Suspense fallback={<LoadingFallback />}>
                  <Routes>
                    <Route path="/" element={<AppShell />}>
                      <Route index element={<Navigate to="/pto-request" replace />} />

                      {/* PTO */}
                      <Route path="pto-request" element={<PtoRequestPage />} />
                      <Route path="pto-balance" element={<PtoBalancePage />} />

                      {/* Administration */}
                      <Route path="admin/pto-supervisors" element={<AdminRoute><PtoSupervisorsPage /></AdminRoute>} />
                      <Route path="admin/settings" element={<AdminRoute><AdminSettingsPage /></AdminRoute>} />
                      <Route path="*" element={<NotFoundPage />} />
                    </Route>
                  </Routes>
                </Suspense>
              </HashRouter>
            </TooltipProvider>
          </ToastProvider>
        </ConfigurationProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
