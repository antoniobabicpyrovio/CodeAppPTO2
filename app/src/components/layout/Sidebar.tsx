import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useSidebarState } from './AppShell';
import {
  CalendarDays,
  Wallet,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Settings,
  Users,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useEffectiveAdminRole } from '../../providers/ConfigurationProvider';

interface NavItem {
  path: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavSection {
  id: string;
  header: string;
  items: NavItem[];
  defaultOpen?: boolean;
}

const NAV_SECTIONS: NavSection[] = [
  {
    id: 'pto',
    header: 'PTO',
    defaultOpen: true,
    items: [
      { path: '/pto-request', label: 'PTO Request', icon: CalendarDays },
      { path: '/pto-balance', label: 'PTO Balance', icon: Wallet },
    ],
  },
  {
    id: 'admin',
    header: 'Administration',
    items: [
      { path: '/admin/pto-supervisors', label: 'PTO Supervisors', icon: Users },
      { path: '/admin/settings', label: 'Settings', icon: Settings },
    ],
  },
];

export function Sidebar() {
  const { collapsed, setCollapsed } = useSidebarState();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const effectiveAdminRole = useEffectiveAdminRole();
  const [envLabel] = useState<string | null>(null);

  const visibleSections = NAV_SECTIONS
    .filter((s) => s.id !== 'admin' || effectiveAdminRole !== 'none');

  const [openSections, setOpenSections] = useState<Set<string>>(() => {
    const initial = new Set<string>();
    NAV_SECTIONS.forEach((s) => { if (s.defaultOpen) initial.add(s.id); });
    return initial;
  });

  const allItems = visibleSections.flatMap((s) => s.items);
  const selectedPath = (() => {
    const exact = allItems.find((item) => item.path === pathname);
    if (exact) return exact.path;
    const prefix = [...allItems]
      .sort((a, b) => b.path.length - a.path.length)
      .find((item) => pathname.startsWith(item.path));
    return prefix?.path ?? '';
  })();

  function toggleSection(id: string) {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function renderNavItem(item: NavItem) {
    const isActive = selectedPath === item.path;
    const Icon = item.icon;
    return (
      <button
        key={item.path}
        onClick={() => navigate(item.path)}
        title={collapsed ? item.label : undefined}
        className={cn(
          'relative w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm transition-all duration-150',
          isActive
            ? 'bg-primary/15 text-primary font-medium'
            : 'text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent'
        )}
      >
        {isActive && (
          <motion.div
            layoutId="activeNav"
            className="absolute left-0 top-1 bottom-1 w-0.5 bg-primary rounded-r-full"
            transition={{ type: 'spring', stiffness: 400, damping: 32 }}
          />
        )}
        <div className="relative shrink-0">
          <Icon className={cn('h-4 w-4', isActive ? 'text-primary' : 'text-sidebar-foreground/50')} />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              transition={{ duration: 0.2 }}
              className="whitespace-nowrap overflow-hidden text-[13px] leading-none"
            >
              {item.label}
            </motion.span>
          )}
        </AnimatePresence>
      </button>
    );
  }

  return (
    <motion.aside
      className="fixed left-0 top-0 h-screen bg-sidebar border-r border-sidebar-border z-50 flex flex-col"
      animate={{ width: collapsed ? 72 : 260 }}
      transition={{ duration: 0.28, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      {/* Logo header */}
      <div className="h-14 flex items-center px-4 border-b border-sidebar-border shrink-0">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg btn-brand shrink-0 glow-primary-sm">
          <span className="text-white font-bold text-sm select-none">P</span>
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <span className="ml-3 font-bold text-foreground text-base whitespace-nowrap flex items-center gap-2">
                PTO Manager
                {envLabel && (
                  <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded border bg-amber-100 text-amber-700 border-amber-300">
                    {envLabel}
                  </span>
                )}
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Collapsible nav sections */}
      <nav className="flex-1 overflow-y-auto py-1 px-2">
        {visibleSections.map((section) => {
          const isOpen = openSections.has(section.id);
          return (
            <div key={section.id} className="mb-0.5">
              <AnimatePresence>
                {!collapsed && (
                  <motion.button
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    onClick={() => toggleSection(section.id)}
                    className="w-full flex items-center justify-between px-2.5 py-1.5 mt-1 text-[10px] font-semibold text-sidebar-foreground/35 uppercase tracking-widest hover:text-sidebar-foreground/60 transition-colors"
                  >
                    {section.header}
                    <ChevronDown
                      className={cn(
                        'h-3 w-3 transition-transform duration-200',
                        isOpen ? 'rotate-0' : '-rotate-90'
                      )}
                    />
                  </motion.button>
                )}
              </AnimatePresence>
              <AnimatePresence initial={false}>
                {(isOpen || collapsed) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.18, ease: 'easeInOut' }}
                    className="overflow-hidden"
                  >
                    {section.items.map(renderNavItem)}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t border-sidebar-border p-2 shrink-0">
        <button
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sidebar-foreground/40 hover:text-sidebar-foreground hover:bg-sidebar-accent transition-colors text-sm"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
                className="whitespace-nowrap text-[13px]"
              >
                Collapse
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  );
}
