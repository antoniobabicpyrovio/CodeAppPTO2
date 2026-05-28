"""Backfill / patch a single Dataverse record using the pac CLI's cached MSAL token.

No SPN secret required. Reads pac's DPAPI-encrypted token cache, finds the
access token for the target environment, and PATCHes the record.

Usage:
    # Make sure pac is currently auth'd to the target env (forces a fresh token):
    pac auth select --name "Nexus-PROD"      # or --index 1 for DEV
    pac org who                              # forces token refresh into cache

    python scripts/pac-patch-record.py <org_url> <entity_set> <record_id> <json_patch>

Example (backfill REQ-2026-1016 currentstagenumber 5 -> 4):
    python scripts/pac-patch-record.py \
        https://rcm.crm.dynamics.com \
        pmo_projectrequests \
        <record_guid> \
        '{"pmo_currentstagenumber": 4}'

Notes:
- Requires Windows (DPAPI). Run from the same user account that ran pac.
- pip install pywin32   (for win32crypt)
- The cache lives at %LOCALAPPDATA%\\Microsoft\\PowerAppsCLI\\tokencache_msalv3.dat
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

try:
    import win32crypt  # type: ignore
except ImportError:
    print("ERROR: pywin32 not installed. Run: pip install pywin32")
    sys.exit(1)


CACHE_PATH = os.path.join(
    os.environ["LOCALAPPDATA"],
    "Microsoft", "PowerAppsCLI", "tokencache_msalv3.dat",
)


def load_cache():
    with open(CACHE_PATH, "rb") as f:
        encrypted = f.read()
    _desc, plaintext = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)
    return json.loads(plaintext.decode("utf-8"))


def find_access_token(cache, org_url):
    """Find a non-expired access token whose target matches the org host."""
    host = urllib.parse.urlparse(org_url).hostname.lower()
    now = int(time.time())
    candidates = []
    for key, entry in (cache.get("AccessToken") or {}).items():
        target = (entry.get("target") or "").lower()
        if host not in target and host not in key.lower():
            continue
        expires_on = int(entry.get("expires_on", 0))
        if expires_on <= now + 30:
            continue
        candidates.append((expires_on, entry["secret"]))
    if not candidates:
        return None
    candidates.sort(reverse=True)  # latest-expiring first
    return candidates[0][1]


def patch_record(org_url, entity_set, record_id, patch_body, token):
    url = f"{org_url}/api/data/v9.2/{entity_set}({record_id})"
    data = json.dumps(patch_body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "If-Match": "*",            # update-only, never insert
            "Prefer": "return=representation",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read().decode("utf-8")


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    org_url, entity_set, record_id, patch_json = sys.argv[1:5]
    patch_body = json.loads(patch_json)

    cache = load_cache()
    token = find_access_token(cache, org_url)
    if not token:
        print(f"ERROR: no fresh access token for {org_url} in pac cache.")
        print("Run:  pac auth select --name <profile>  &&  pac org who")
        sys.exit(2)

    status, body = patch_record(org_url, entity_set, record_id, patch_body, token)
    print(f"HTTP {status}")
    if body:
        print(body[:2000])


if __name__ == "__main__":
    main()
