import { useState } from 'react';
import { Save, ChevronDown, AlertTriangle } from 'lucide-react';
import { Button } from '../ui/button';
import {
  saveFeatureToggles,
  useFeatureToggles,
  type FeatureToggles,
} from '../../providers/ConfigurationProvider';
import { toast } from '../../hooks/useToast';
import { cn } from '../../lib/utils';

interface ToggleItem {
  key: string;
  label: string;
  /** Optional warning message shown when toggling OFF — requires the user to confirm. */
  disableWarning?: string;
}

/** A subsection within a group — items grouped by sub-heading. */
interface ToggleSubSection {
  heading: string;
  items: ToggleItem[];
}

interface ToggleGroup {
  id: string;
  label: string;
  description: string;
  /** Either a flat list of items, or sub-sections with their own headings. */
  items?: ToggleItem[];
  subSections?: ToggleSubSection[];
}

const TOGGLE_GROUPS: ToggleGroup[] = [
  {
    id: 'left-nav',
    label: 'Left Navigation',
    description: 'Items shown in the left sidebar',
    items: [
      { key: 'nav.ptoRequest', label: 'PTO Request' },
      { key: 'nav.ptoBalance', label: 'PTO Balance' },
    ],
  },
  {
    id: 'header',
    label: 'Header Toolbar',
    description: 'Top-right header buttons',
    items: [
      { key: 'header.themeToggle', label: 'Theme Toggle (Light/Dark)' },
      { key: 'header.shortcuts', label: 'Keyboard Shortcuts' },
    ],
  },
];

/** Flatten a group's items (whether subsection-based or flat). */
function getAllItems(group: ToggleGroup): ToggleItem[] {
  if (group.items) return group.items;
  if (group.subSections) return group.subSections.flatMap((s) => s.items);
  return [];
}

function ItemCheckbox({ item, toggles, onToggle, onRequestDisable }: {
  item: ToggleItem;
  toggles: FeatureToggles;
  onToggle: (key: string) => void;
  onRequestDisable: (item: ToggleItem) => void;
}) {
  function handleClick() {
    const currentlyOn = toggles[item.key] !== false;
    if (currentlyOn && item.disableWarning) {
      onRequestDisable(item);
      return;
    }
    onToggle(item.key);
  }
  return (
    <label className="flex items-center gap-2.5 py-1.5 cursor-pointer hover:bg-muted/20 rounded px-1 -mx-1 transition-colors">
      <input
        type="checkbox"
        checked={toggles[item.key] !== false}
        onChange={handleClick}
        className="h-3.5 w-3.5 rounded border-border accent-primary shrink-0"
      />
      <span className="text-sm text-foreground flex-1">{item.label}</span>
      {item.disableWarning && (
        <span title="Disabling this has side effects" className="text-amber-500 shrink-0">
          <AlertTriangle className="h-3 w-3" />
        </span>
      )}
    </label>
  );
}

function ToggleGroupPanel({ group, toggles, onToggle, onRequestDisable }: {
  group: ToggleGroup;
  toggles: FeatureToggles;
  onToggle: (key: string) => void;
  onRequestDisable: (item: ToggleItem) => void;
}) {
  const [open, setOpen] = useState(false);
  const allItems = getAllItems(group);
  const enabledCount = allItems.filter((i) => toggles[i.key] !== false).length;
  const allEnabled = enabledCount === allItems.length;

  function toggleAll() {
    const target = !allEnabled;
    allItems.forEach((i) => {
      const currentlyOn = toggles[i.key] !== false;
      if (currentlyOn === target) return;
      if (!target && i.disableWarning) {
        onRequestDisable(i);
      } else {
        onToggle(i.key);
      }
    });
  }

  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-muted/30 transition-colors"
      >
        <ChevronDown className={cn('h-4 w-4 text-muted-foreground transition-transform', !open && '-rotate-90')} />
        <div className="flex-1 text-left">
          <p className="text-sm font-medium text-foreground">{group.label}</p>
          <p className="text-xs text-muted-foreground">{group.description}</p>
        </div>
        <span className="text-xs text-muted-foreground shrink-0">{enabledCount}/{allItems.length} enabled</span>
      </button>

      {open && (
        <div className="border-t px-4 py-2 bg-muted/10">
          {allItems.length > 1 && (
            <label className="flex items-center gap-2.5 py-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={allEnabled}
                onChange={toggleAll}
                className="h-3.5 w-3.5 rounded border-border accent-primary shrink-0"
              />
              <span className="text-xs font-medium text-muted-foreground italic">Toggle all</span>
            </label>
          )}

          {/* Sub-section style */}
          {group.subSections && (
            <div className="space-y-3 mt-1">
              {group.subSections.map((sub) => (
                <div key={sub.heading} className="space-y-0.5">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/80 pt-1.5 pb-0.5">
                    {sub.heading}
                  </p>
                  {sub.items.map((item) => (
                    <ItemCheckbox
                      key={item.key}
                      item={item}
                      toggles={toggles}
                      onToggle={onToggle}
                      onRequestDisable={onRequestDisable}
                    />
                  ))}
                </div>
              ))}
            </div>
          )}

          {/* Flat list style */}
          {group.items && (
            <div className="space-y-0.5 mt-1">
              {group.items.map((item) => (
                <ItemCheckbox
                  key={item.key}
                  item={item}
                  toggles={toggles}
                  onToggle={onToggle}
                  onRequestDisable={onRequestDisable}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function FeatureToggleSection() {
  const saved = useFeatureToggles();
  const [toggles, setToggles] = useState<FeatureToggles>({ ...saved });
  const [saving, setSaving] = useState(false);

  const hasChanges = JSON.stringify(toggles) !== JSON.stringify(saved);

  function handleToggle(key: string) {
    setToggles((prev) => ({ ...prev, [key]: prev[key] !== false ? false : true }));
  }

  function handleSave() {
    setSaving(true);
    saveFeatureToggles(toggles);
    toast.success('Feature toggles saved.');
    setSaving(false);
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-base font-semibold text-foreground">Feature Toggles</h3>
        <p className="text-xs text-muted-foreground mt-0.5">Enable or disable features across the application. Changes take effect immediately.</p>
      </div>
      <div className="space-y-2">
        {TOGGLE_GROUPS.map((group) => (
          <ToggleGroupPanel
            key={group.id}
            group={group}
            toggles={toggles}
            onToggle={handleToggle}
            onRequestDisable={() => {}}
          />
        ))}
      </div>
      <div className="flex justify-end">
        <Button size="sm" onClick={handleSave} disabled={saving || !hasChanges}>
          <Save className="h-3.5 w-3.5 mr-1.5" />
          {saving ? 'Saving...' : 'Save'}
        </Button>
      </div>
    </div>
  );
}
