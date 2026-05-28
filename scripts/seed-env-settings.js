#!/usr/bin/env node
// seed-env-settings.js — Seed environment-specific app settings into Dataverse.
//
// Usage:
//   node scripts/seed-env-settings.js \
//     --environment https://contoso.crm.dynamics.com \
//     --tenantId <azure-ad-tenant-guid> \
//     --pmoTeamField <field-logical-name>
//
// Authentication:
//   Pass a bearer token via --accessToken or the DATAVERSE_ACCESS_TOKEN env var.
//   Obtain one via: az account get-access-token --resource <environment-url> --query accessToken -o tsv
//
// Idempotent: safe to re-run. Updates existing records; creates if absent.

const args = (() => {
  const map = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) map[argv[i].slice(2)] = argv[i + 1] ?? true;
  }
  return map;
})();

function require_arg(name) {
  if (!args[name]) {
    console.error(`Error: --${name} is required.`);
    process.exit(1);
  }
  return args[name];
}

const environment = require_arg('environment').replace(/\/$/, '');
const tenantId    = require_arg('tenantId');
const pmoTeamField = require_arg('pmoTeamField');
const token = args.accessToken || process.env.DATAVERSE_ACCESS_TOKEN;

if (!token) {
  console.error(
    'Error: Authentication required.\n' +
    'Provide --accessToken <bearer-token> or set DATAVERSE_ACCESS_TOKEN.\n' +
    'Obtain a token: az account get-access-token --resource ' + environment + ' --query accessToken -o tsv'
  );
  process.exit(1);
}

const apiBase = `${environment}/api/data/v9.2`;
const headers = {
  Authorization: `Bearer ${token}`,
  'Content-Type': 'application/json',
  'OData-MaxVersion': '4.0',
  'OData-Version': '4.0',
  Accept: 'application/json',
};

async function findSetting(key) {
  const url = `${apiBase}/pmo_appsettings?$select=pmo_appsettingid,pmo_key,pmo_value&$filter=pmo_key eq '${key}' and statecode eq 0`;
  const res = await fetch(url, { headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`GET pmo_appsettings (${key}): ${res.status} ${body}`);
  }
  const body = await res.json();
  return body.value?.[0] ?? null;
}

async function upsertSetting(key, value) {
  const existing = await findSetting(key);
  if (existing) {
    if (existing.pmo_value === value) {
      console.log(`  Unchanged: ${key} = ${value}`);
      return;
    }
    const url = `${apiBase}/pmo_appsettings(${existing.pmo_appsettingid})`;
    const res = await fetch(url, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ pmo_value: value }),
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`PATCH pmo_appsettings (${key}): ${res.status} ${body}`);
    }
    console.log(`  Updated:   ${key} = ${value}`);
  } else {
    const url = `${apiBase}/pmo_appsettings`;
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({ pmo_key: key, pmo_value: value }),
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`POST pmo_appsettings (${key}): ${res.status} ${body}`);
    }
    console.log(`  Created:   ${key} = ${value}`);
  }
}

async function main() {
  console.log(`Seeding environment settings → ${environment}`);
  try {
    await upsertSetting('pmo.tenant_id', tenantId);
    await upsertSetting('pmo.pmo_team_field', pmoTeamField);
    console.log('Done.');
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();
