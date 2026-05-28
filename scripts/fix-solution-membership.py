"""Add the custom API and flow to the CFRProjectManagement solution."""
import urllib.request
import urllib.parse
import json
import sys

TENANT = "fabb61b8-3afe-4e75-b934-a47f782b8cd7"
CLIENT_ID = "cc57f611-be88-4856-9d60-6ee9da06a32b"
ORG_URL = "https://nexusrcm-dev.crm.dynamics.com"
BASE = f"{ORG_URL}/api/data/v9.2"
SECRET = sys.argv[1] if len(sys.argv) > 1 else None
if not SECRET:
    print("Usage: python fix-solution-membership.py <client_secret>")
    sys.exit(1)

token_data = urllib.parse.urlencode({
    "client_id": CLIENT_ID, "client_secret": SECRET,
    "scope": f"{ORG_URL}/.default", "grant_type": "client_credentials",
}).encode()
req = urllib.request.Request(
    f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token",
    data=token_data, method="POST",
)
with urllib.request.urlopen(req) as resp:
    TOKEN = json.loads(resp.read())["access_token"]
print("Authenticated.\n")


def get(path):
    url = BASE + path
    r = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
    })
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read())


def post(path, data):
    body = json.dumps(data).encode()
    r = urllib.request.Request(BASE + path, data=body, method="POST", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
    })
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# 1. Find the solution
print("=== Finding solution ===")
sols = get("/solutions?" + urllib.parse.urlencode({
    "$filter": "uniquename eq 'CFRProjectManagement'",
    "$select": "solutionid,uniquename,friendlyname",
}))
sol = sols["value"][0] if sols["value"] else None
if not sol:
    print("  ERROR: Solution 'CFRProjectManagement' not found!")
    sys.exit(1)
sol_id = sol["solutionid"]
sol_name = sol["uniquename"]
print(f"  Found: {sol['friendlyname']} [{sol_id}]")

# 2. Find the custom API
print("\n=== Finding custom API ===")
apis = get("/customapis?" + urllib.parse.urlencode({
    "$filter": "uniquename eq 'pmo_UploadDocumentToSharePoint'",
    "$select": "customapiid,uniquename",
}))
api = apis["value"][0] if apis["value"] else None
if not api:
    print("  ERROR: Custom API not found!")
    sys.exit(1)
api_id = api["customapiid"]
print(f"  Found: {api['uniquename']} [{api_id}]")

# 3. Find the flow
print("\n=== Finding flow ===")
flows = get("/workflows?" + urllib.parse.urlencode({
    "$filter": "category eq 5 and contains(name,'PMO: Upload Document')",
    "$select": "workflowid,name,statecode",
}))
flow = flows["value"][0] if flows["value"] else None
if flow:
    flow_id = flow["workflowid"]
    print(f"  Found: {flow['name']} [{flow_id}] statecode={flow['statecode']}")
else:
    flow_id = None
    print("  Flow not found (may need to be recreated)")

# 4. Add custom API to solution
# ComponentType 10068 = Custom API
print("\n=== Adding Custom API to solution ===")
code, resp = post("/AddSolutionComponent", {
    "ComponentId": api_id,
    "ComponentType": 10068,
    "SolutionUniqueName": sol_name,
    "AddRequiredComponents": True,
    "IncludedComponentSettingsValues": None,
})
print(f"  AddSolutionComponent (Custom API): HTTP {code}")
if code not in (200, 204):
    print(f"  {resp[:300]}")

# 5. Add flow to solution (if found)
# ComponentType 29 = Workflow
if flow_id:
    print("\n=== Adding Flow to solution ===")
    code2, resp2 = post("/AddSolutionComponent", {
        "ComponentId": flow_id,
        "ComponentType": 29,
        "SolutionUniqueName": sol_name,
        "AddRequiredComponents": True,
        "IncludedComponentSettingsValues": None,
    })
    print(f"  AddSolutionComponent (Flow): HTTP {code2}")
    if code2 not in (200, 204):
        print(f"  {resp2[:300]}")

print("\n=== Done ===")
print(f"  Both components should now appear in {sol_name} solution.\n")
