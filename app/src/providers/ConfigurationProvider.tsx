import { createContext, useContext, useState, useEffect, useSyncExternalStore, type ReactNode } from 'react';
import { getContext } from '@microsoft/power-apps/app';
import { useQuery } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { listSettings, type AppSetting } from '../api/appSettings.api';
import { isDemoModeActive } from '../lib/demoMode';
import { isImpersonatingUser, subscribeToImpersonation } from '../lib/adminImpersonation';
import {
  PMO_TEAM_FLAG,
  TENANT_ID as COMPILE_TIME_TENANT_ID,
  SP_DOCUMENT_CATEGORIES,
  SETTING_DASHBOARD_DISPLAY_CONFIG,
  SETTING_INTAKE_TRIAGE_SIMILARITY_CONFIG,
  SETTING_NOTIFICATION_DISPLAY_CONFIG,
  SETTING_SP_DOCUMENT_CATEGORIES,
  SETTING_SP_LIBRARY_BASE_URL,
  SP_LIBRARY_BASE_URL,
  SETTING_PMO_TEAM_FIELD,
  SETTING_TENANT_ID,
  SETTING_INTAKE_ROUTING_CONFIG,
  SETTING_PRIORITIZATION_WEIGHTS,
  SETTING_PRIORITIZATION_BUDGET_TIERS,
  SETTING_MIRA_SIGNAL_THRESHOLDS,
  SETTING_FEATURE_TOGGLES,
} from '../lib/constants';
import { INTAKE_ROUTING_CONFIG, intakeEntriesToRoutingDomains, type RoutingDomain } from '../lib/intakeRoutingConfig';
export type { RoutingDomain };

export type AdminRole = 'none' | 'pmo_admin' | 'system_admin';

// ─── Phase 2 config interfaces (§4.6) ────────────────────────────────────────

export interface DashboardDisplayConfig {
  dueSoonDays: number;
  needsAttentionLimit: number;
  recentIntakeLimit: number;
  urgentDayThreshold: number;
  warningDayThreshold: number;
}

export interface IntakeTriageSimilarityConfig {
  lookbackDays: number;
  minScore: number;
  topN: number;
}

export interface NotificationDisplayConfig {
  pollIntervalMs: number;
  categoryLabels: Record<string, string>;
  categoryColors: Record<string, string>;
}

export interface PrioritizationWeights {
  strategicPriority: number;
  complexity: number;
  health: number;
  budget: number;
  progress: number;
}

export interface BudgetTier {
  minAmount: number;
  score: number;
}

export interface MiraSignalThresholds {
  riskCountWarn: number;
  riskCountCritical: number;
  riskScoreWarn: number;
  riskScoreCritical: number;
}

export interface FeatureToggles {
  [key: string]: boolean;
}

export interface RuntimeConfig {
  dashboardDisplay: DashboardDisplayConfig;
  intakeTriageSimilarity: IntakeTriageSimilarityConfig;
  notificationDisplay: NotificationDisplayConfig;
  spDocumentCategories: string[];
  spLibraryBaseUrl: string;
  pmoTeamField: string;
  tenantId: string;
  intakeRoutingConfig: RoutingDomain[];
  prioritizationWeights: PrioritizationWeights;
  prioritizationBudgetTiers: BudgetTier[];
  miraSignalThresholds: MiraSignalThresholds;
  featureToggles: FeatureToggles;
}

// ─── Compile-time defaults ────────────────────────────────────────────────────

export const DEFAULT_DASHBOARD_DISPLAY: DashboardDisplayConfig = {
  dueSoonDays: 30,
  needsAttentionLimit: 6,
  recentIntakeLimit: 7,
  urgentDayThreshold: 0,
  warningDayThreshold: 7,
};

export const DEFAULT_INTAKE_TRIAGE_SIMILARITY: IntakeTriageSimilarityConfig = {
  lookbackDays: 90,
  minScore: 0.1,
  topN: 3,
};

export const DEFAULT_NOTIFICATION_DISPLAY: NotificationDisplayConfig = {
  pollIntervalMs: 60000,
  categoryLabels: {},
  categoryColors: {},
};

export const DEFAULT_INTAKE_ROUTING_CONFIG: RoutingDomain[] = intakeEntriesToRoutingDomains(INTAKE_ROUTING_CONFIG);

export const DEFAULT_PRIORITIZATION_WEIGHTS: PrioritizationWeights = {
  strategicPriority: 35,
  complexity: 20,
  health: 15,
  budget: 15,
  progress: 15,
};

export const DEFAULT_PRIORITIZATION_BUDGET_TIERS: BudgetTier[] = [
  { minAmount: 500000, score: 100 },
  { minAmount: 100000, score: 70 },
  { minAmount: 25000, score: 40 },
];

export const DEFAULT_MIRA_SIGNAL_THRESHOLDS: MiraSignalThresholds = {
  riskCountWarn: 2,
  riskCountCritical: 4,
  riskScoreWarn: 6,
  riskScoreCritical: 10,
};

export const DEFAULT_FEATURE_TOGGLES: FeatureToggles = {
  'nav.ptoRequest': true,
  'nav.ptoBalance': true,
  'header.themeToggle': true,
  'header.shortcuts': true,
};

const TOGGLE_STORAGE_KEY = 'pto_feature_toggles';
const toggleSubscribers = new Set<() => void>();

// Cache so useSyncExternalStore gets the same reference when the store hasn't changed.
let _cachedRaw: string | null = null;
let _cachedToggles: FeatureToggles = DEFAULT_FEATURE_TOGGLES;

function getStoredToggles(): FeatureToggles {
  try {
    const raw = localStorage.getItem(TOGGLE_STORAGE_KEY);
    if (raw === _cachedRaw) return _cachedToggles;
    _cachedRaw = raw;
    _cachedToggles = raw
      ? { ...DEFAULT_FEATURE_TOGGLES, ...JSON.parse(raw) }
      : DEFAULT_FEATURE_TOGGLES;
    return _cachedToggles;
  } catch {
    return DEFAULT_FEATURE_TOGGLES;
  }
}

function subscribeToLocalToggles(fn: () => void): () => void {
  toggleSubscribers.add(fn);
  return () => { toggleSubscribers.delete(fn); };
}

export function saveFeatureToggles(toggles: FeatureToggles): void {
  localStorage.setItem(TOGGLE_STORAGE_KEY, JSON.stringify(toggles));
  toggleSubscribers.forEach((fn) => fn());
}

// ─── Parsing ──────────────────────────────────────────────────────────────────

function parseJson<T>(value: string | undefined, key: string, fallback: T): { value: T; malformed: boolean } {
  if (!value) return { value: fallback, malformed: false };
  try {
    return { value: JSON.parse(value) as T, malformed: false };
  } catch (e) {
    console.warn(`[ConfigurationProvider] Failed to parse setting "${key}":`, e);
    return { value: fallback, malformed: true };
  }
}

function buildRuntimeConfig(settings: AppSetting[]): { config: RuntimeConfig; malformedKeys: Set<string> } {
  const map = Object.fromEntries(settings.map((s) => [s.pmo_key, s.pmo_value]));
  const malformedKeys = new Set<string>();

  function parse<T>(key: string, fallback: T): T {
    const result = parseJson<T>(map[key] ?? undefined, key, fallback);
    if (result.malformed) malformedKeys.add(key);
    return result.value;
  }

  const config: RuntimeConfig = {
    dashboardDisplay: parse(SETTING_DASHBOARD_DISPLAY_CONFIG, DEFAULT_DASHBOARD_DISPLAY),
    intakeTriageSimilarity: parse(SETTING_INTAKE_TRIAGE_SIMILARITY_CONFIG, DEFAULT_INTAKE_TRIAGE_SIMILARITY),
    notificationDisplay: parse(SETTING_NOTIFICATION_DISPLAY_CONFIG, DEFAULT_NOTIFICATION_DISPLAY),
    spDocumentCategories: parse(SETTING_SP_DOCUMENT_CATEGORIES, [...SP_DOCUMENT_CATEGORIES]),
    spLibraryBaseUrl: map[SETTING_SP_LIBRARY_BASE_URL] || SP_LIBRARY_BASE_URL,
    pmoTeamField: map[SETTING_PMO_TEAM_FIELD] || PMO_TEAM_FLAG,
    tenantId: map[SETTING_TENANT_ID] || COMPILE_TIME_TENANT_ID,
    intakeRoutingConfig: parse(SETTING_INTAKE_ROUTING_CONFIG, DEFAULT_INTAKE_ROUTING_CONFIG),
    prioritizationWeights: parse(SETTING_PRIORITIZATION_WEIGHTS, DEFAULT_PRIORITIZATION_WEIGHTS),
    prioritizationBudgetTiers: parse(SETTING_PRIORITIZATION_BUDGET_TIERS, DEFAULT_PRIORITIZATION_BUDGET_TIERS),
    miraSignalThresholds: parse(SETTING_MIRA_SIGNAL_THRESHOLDS, DEFAULT_MIRA_SIGNAL_THRESHOLDS),
    featureToggles: parse(SETTING_FEATURE_TOGGLES, DEFAULT_FEATURE_TOGGLES),
  };

  return { config, malformedKeys };
}

// ─── Role resolution ──────────────────────────────────────────────────────────

const HARDCODED_ADMINS = new Set([
  'antonio.babic@pyroviosandbox.onmicrosoft.com',
  'antonio.babic@pyrovio.com',
]);

async function resolveAdminRole(): Promise<AdminRole> {
  if (isDemoModeActive()) return 'system_admin';

  let email = '';

  // Primary: Power Apps SDK context (reliable inside Power Apps iframe)
  try {
    const ctx = await getContext();
    const user = (ctx as unknown as Record<string, unknown>).user as Record<string, unknown> | undefined;
    if (user) {
      email = ((user.email ?? user.upn ?? user.userPrincipalName ?? '') as string).toLowerCase();
    }
  } catch { /* not running inside Power Apps runtime */ }

  // Fallback: Microsoft Graph /me (works in dev/browser outside Power Apps)
  if (!email) {
    try {
      const meRes = await fetch(
        'https://graph.microsoft.com/v1.0/me?$select=mail,userPrincipalName',
        { credentials: 'include', headers: { Accept: 'application/json' } },
      );
      if (meRes.ok) {
        const me = await meRes.json();
        email = ((me.mail ?? me.userPrincipalName ?? '') as string).toLowerCase();
      }
    } catch { /* Graph unavailable */ }
  }

  if (!email) return 'none';

  // Hardcoded owners always have admin access regardless of list contents.
  if (HARDCODED_ADMINS.has(email)) return 'system_admin';

  // Everyone whose email appears in the PTO Supervisors list is a PTO admin.
  try {
    const filter = encodeURIComponent(`fields/SupervisorEmail eq '${email}'`);
    const spRes = await fetch(
      `https://graph.microsoft.com/v1.0/sites/enoviogroup.sharepoint.com:/sites/Pyrovio:/lists/CodeAppPTOSupervisors/items?$expand=fields&$filter=${filter}&$top=1`,
      { credentials: 'include', headers: { Accept: 'application/json' } },
    );
    if (spRes.ok) {
      const data = await spRes.json();
      if ((data.value?.length ?? 0) > 0) return 'pmo_admin';
    }
  } catch { /* supervisors list unavailable */ }

  return 'none';
}

// ─── Context ──────────────────────────────────────────────────────────────────

interface ConfigurationContextValue {
  settings: AppSetting[];
  userAdminRole: AdminRole;
  settingsFailed: boolean;
  config: RuntimeConfig;
  malformedKeys: Set<string>;
}

const DEFAULT_RUNTIME_CONFIG: RuntimeConfig = {
  dashboardDisplay: DEFAULT_DASHBOARD_DISPLAY,
  intakeTriageSimilarity: DEFAULT_INTAKE_TRIAGE_SIMILARITY,
  notificationDisplay: DEFAULT_NOTIFICATION_DISPLAY,
  spDocumentCategories: [...SP_DOCUMENT_CATEGORIES],
  spLibraryBaseUrl: SP_LIBRARY_BASE_URL,
  pmoTeamField: PMO_TEAM_FLAG,
  tenantId: COMPILE_TIME_TENANT_ID,
  intakeRoutingConfig: DEFAULT_INTAKE_ROUTING_CONFIG,
  prioritizationWeights: DEFAULT_PRIORITIZATION_WEIGHTS,
  prioritizationBudgetTiers: DEFAULT_PRIORITIZATION_BUDGET_TIERS,
  miraSignalThresholds: DEFAULT_MIRA_SIGNAL_THRESHOLDS,
  featureToggles: DEFAULT_FEATURE_TOGGLES,
};

const ConfigurationContext = createContext<ConfigurationContextValue>({
  settings: [],
  userAdminRole: 'none',
  settingsFailed: false,
  config: DEFAULT_RUNTIME_CONFIG,
  malformedKeys: new Set(),
});

// ─── Provider ─────────────────────────────────────────────────────────────────

export function ConfigurationProvider({ children }: { children: ReactNode }) {
  const {
    data: settings = [],
    isLoading: settingsLoading,
    isError: settingsFailed,
  } = useQuery({
    queryKey: ['appSettings'],
    queryFn: listSettings,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const [userAdminRole, setUserAdminRole] = useState<AdminRole>('none');
  const [roleResolved, setRoleResolved] = useState(false);

  useEffect(() => {
    resolveAdminRole().then((role) => {
      setUserAdminRole(role);
      setRoleResolved(true);
    });
  }, []);

  if (settingsLoading || !roleResolved) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
        <span className="ml-2 text-sm text-muted-foreground">Loading...</span>
      </div>
    );
  }

  const { config, malformedKeys } = buildRuntimeConfig(settings);

  return (
    <ConfigurationContext.Provider value={{ settings, userAdminRole, settingsFailed, config, malformedKeys }}>
      {children}
    </ConfigurationContext.Provider>
  );
}

// ─── Hooks ────────────────────────────────────────────────────────────────────

export function useConfig(): ConfigurationContextValue {
  return useContext(ConfigurationContext);
}

export function useAdminRole(): AdminRole {
  return useContext(ConfigurationContext).userAdminRole;
}

/**
 * Admin role after applying the per-session "act as user" impersonation
 * toggle. When an admin flips the sidebar pill, this hook reports 'none' so
 * the rest of the app gates them as a regular user.
 *
 * Use this hook for all UI gating. Use useAdminRole() only when you need the
 * real underlying role (e.g. to decide whether to show the impersonation
 * toggle itself).
 */
export function useEffectiveAdminRole(): AdminRole {
  const realRole = useAdminRole();
  const impersonating = useSyncExternalStore(subscribeToImpersonation, isImpersonatingUser);
  if (impersonating && realRole !== 'none') return 'none';
  return realRole;
}

export function usePmoTeamField(): string {
  return useContext(ConfigurationContext).config.pmoTeamField;
}

export function useTenantId(): string {
  return useContext(ConfigurationContext).config.tenantId;
}

export function useIntakeRoutingConfig(): RoutingDomain[] {
  return useContext(ConfigurationContext).config.intakeRoutingConfig;
}

export function usePrioritizationWeights(): PrioritizationWeights {
  return useContext(ConfigurationContext).config.prioritizationWeights;
}

export function usePrioritizationBudgetTiers(): BudgetTier[] {
  return useContext(ConfigurationContext).config.prioritizationBudgetTiers;
}

export function useMiraSignalThresholds(): MiraSignalThresholds {
  return useContext(ConfigurationContext).config.miraSignalThresholds;
}

export function useFeatureToggles(): FeatureToggles {
  return useSyncExternalStore(subscribeToLocalToggles, getStoredToggles);
}

export function useFeatureToggle(key: string): boolean {
  const toggles = useFeatureToggles();
  return toggles[key] ?? true;
}
