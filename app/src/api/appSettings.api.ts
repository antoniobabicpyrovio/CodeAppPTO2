export interface AppSetting {
  pmo_appsettingid: string;
  pmo_key: string;
  pmo_value: string | null;
  pmo_description: string | null;
}

export async function listSettings(): Promise<AppSetting[]> {
  return [];
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export async function upsertSetting(_key: string, _value: string, _existing?: AppSetting): Promise<void> {
  // Dataverse not available in this environment — settings are stored in localStorage
}
