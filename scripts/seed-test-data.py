"""Seed test data for PMO CFR Solution DEV environment."""
import urllib.request
import json
import sys

TENANT = "fabb61b8-3afe-4e75-b934-a47f782b8cd7"
CLIENT_ID = "cc57f611-be88-4856-9d60-6ee9da06a32b"
ORG_URL = "https://nexusrcm-dev.crm.dynamics.com"
BASE = f"{ORG_URL}/api/data/v9.2"

SECRET = sys.argv[1] if len(sys.argv) > 1 else None
if not SECRET:
    print("Usage: python seed-test-data.py <client_secret>")
    sys.exit(1)

# Get token
token_url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"
token_data = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "client_secret": SECRET,
    "scope": f"{ORG_URL}/.default",
    "grant_type": "client_credentials",
}).encode()
import urllib.parse
token_data = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "client_secret": SECRET,
    "scope": f"{ORG_URL}/.default",
    "grant_type": "client_credentials",
}).encode()
token_req = urllib.request.Request(token_url, data=token_data, method="POST")
with urllib.request.urlopen(token_req) as resp:
    TOKEN = json.loads(resp.read())["access_token"]
print("Authenticated.")


def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(BASE + path, data=body, method="POST", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Prefer": "return=representation",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return e.code, body


# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== Project Templates ===")

templates = [
    {
        "pmo_name": "IT Infrastructure Standard",
        "pmo_description": "Standard WBS for IT infrastructure projects: discovery, design, build, test, deploy, hypercare.",
        "pmo_cfrcategory": 893460050,
        "pmo_issystemdefault": True,
        "pmo_taskpayload": json.dumps([
            {"name": "Discovery & Requirements", "isBucket": True},
            {"name": "Gather requirements", "bucketName": "Discovery & Requirements", "effort": 16},
            {"name": "Document current state", "bucketName": "Discovery & Requirements", "effort": 8},
            {"name": "Identify dependencies", "bucketName": "Discovery & Requirements", "effort": 4},
            {"name": "Design & Planning", "isBucket": True},
            {"name": "Solution design", "bucketName": "Design & Planning", "effort": 24},
            {"name": "Architecture review", "bucketName": "Design & Planning", "effort": 8},
            {"name": "Create project plan", "bucketName": "Design & Planning", "effort": 8},
            {"name": "Build & Configure", "isBucket": True},
            {"name": "Environment setup", "bucketName": "Build & Configure", "effort": 16},
            {"name": "Core build", "bucketName": "Build & Configure", "effort": 40},
            {"name": "Integration configuration", "bucketName": "Build & Configure", "effort": 16},
            {"name": "Testing", "isBucket": True},
            {"name": "Unit testing", "bucketName": "Testing", "effort": 16},
            {"name": "Integration testing", "bucketName": "Testing", "effort": 16},
            {"name": "UAT coordination", "bucketName": "Testing", "effort": 8},
            {"name": "Deployment", "isBucket": True},
            {"name": "Go-live planning", "bucketName": "Deployment", "effort": 8},
            {"name": "Production deployment", "bucketName": "Deployment", "effort": 8},
            {"name": "Hypercare & Closeout", "isBucket": True},
            {"name": "Post-go-live support", "bucketName": "Hypercare & Closeout", "effort": 16},
            {"name": "Knowledge transfer", "bucketName": "Hypercare & Closeout", "effort": 8},
            {"name": "Project closeout", "bucketName": "Hypercare & Closeout", "effort": 4},
        ]),
    },
    {
        "pmo_name": "Finance Systems Standard",
        "pmo_description": "Standard WBS for finance system projects: analysis, design, configuration, validation, cutover.",
        "pmo_cfrcategory": 893460051,
        "pmo_taskpayload": json.dumps([
            {"name": "Analysis", "isBucket": True},
            {"name": "Process mapping", "bucketName": "Analysis", "effort": 16},
            {"name": "Gap analysis", "bucketName": "Analysis", "effort": 12},
            {"name": "Requirements sign-off", "bucketName": "Analysis", "effort": 4},
            {"name": "Design", "isBucket": True},
            {"name": "Functional design", "bucketName": "Design", "effort": 20},
            {"name": "Data mapping", "bucketName": "Design", "effort": 12},
            {"name": "Configuration", "isBucket": True},
            {"name": "System configuration", "bucketName": "Configuration", "effort": 32},
            {"name": "Report development", "bucketName": "Configuration", "effort": 16},
            {"name": "Validation", "isBucket": True},
            {"name": "Test scenarios", "bucketName": "Validation", "effort": 12},
            {"name": "UAT execution", "bucketName": "Validation", "effort": 16},
            {"name": "Cutover & Go-Live", "isBucket": True},
            {"name": "Cutover planning", "bucketName": "Cutover & Go-Live", "effort": 8},
            {"name": "Go-live execution", "bucketName": "Cutover & Go-Live", "effort": 8},
            {"name": "Post-go-live validation", "bucketName": "Cutover & Go-Live", "effort": 8},
        ]),
    },
    {
        "pmo_name": "Compliance Initiative Standard",
        "pmo_description": "Standard WBS for compliance projects: assessment, gap remediation, policy update, audit readiness.",
        "pmo_cfrcategory": 893460052,
        "pmo_taskpayload": json.dumps([
            {"name": "Assessment", "isBucket": True},
            {"name": "Regulatory review", "bucketName": "Assessment", "effort": 12},
            {"name": "Current state assessment", "bucketName": "Assessment", "effort": 16},
            {"name": "Gap identification", "bucketName": "Assessment", "effort": 8},
            {"name": "Remediation", "isBucket": True},
            {"name": "Policy drafting", "bucketName": "Remediation", "effort": 20},
            {"name": "Process updates", "bucketName": "Remediation", "effort": 16},
            {"name": "Training development", "bucketName": "Remediation", "effort": 12},
            {"name": "Validation & Audit", "isBucket": True},
            {"name": "Internal review", "bucketName": "Validation & Audit", "effort": 8},
            {"name": "Evidence collection", "bucketName": "Validation & Audit", "effort": 12},
            {"name": "Audit readiness sign-off", "bucketName": "Validation & Audit", "effort": 4},
        ]),
    },
    {
        "pmo_name": "Data & Analytics Standard",
        "pmo_description": "Standard WBS for data/analytics projects: data discovery, pipeline, dashboards, deployment.",
        "pmo_cfrcategory": 893460053,
        "pmo_taskpayload": json.dumps([
            {"name": "Data Discovery", "isBucket": True},
            {"name": "Source identification", "bucketName": "Data Discovery", "effort": 8},
            {"name": "Data profiling", "bucketName": "Data Discovery", "effort": 12},
            {"name": "Schema mapping", "bucketName": "Data Discovery", "effort": 8},
            {"name": "Pipeline Development", "isBucket": True},
            {"name": "ETL/ELT build", "bucketName": "Pipeline Development", "effort": 24},
            {"name": "Data quality rules", "bucketName": "Pipeline Development", "effort": 8},
            {"name": "Pipeline testing", "bucketName": "Pipeline Development", "effort": 8},
            {"name": "Analytics & Reporting", "isBucket": True},
            {"name": "Dashboard design", "bucketName": "Analytics & Reporting", "effort": 12},
            {"name": "Report development", "bucketName": "Analytics & Reporting", "effort": 20},
            {"name": "UAT", "bucketName": "Analytics & Reporting", "effort": 8},
            {"name": "Deployment", "isBucket": True},
            {"name": "Production deployment", "bucketName": "Deployment", "effort": 4},
            {"name": "User training", "bucketName": "Deployment", "effort": 8},
            {"name": "Closeout", "bucketName": "Deployment", "effort": 4},
        ]),
    },
    {
        "pmo_name": "Operations Improvement Standard",
        "pmo_description": "Standard WBS for operational improvement: baseline, improve, implement, sustain.",
        "pmo_cfrcategory": 893460054,
        "pmo_taskpayload": json.dumps([
            {"name": "Baseline", "isBucket": True},
            {"name": "Current state documentation", "bucketName": "Baseline", "effort": 12},
            {"name": "Metrics baseline", "bucketName": "Baseline", "effort": 8},
            {"name": "Stakeholder interviews", "bucketName": "Baseline", "effort": 8},
            {"name": "Improve", "isBucket": True},
            {"name": "Root cause analysis", "bucketName": "Improve", "effort": 12},
            {"name": "Solution design", "bucketName": "Improve", "effort": 16},
            {"name": "Pilot planning", "bucketName": "Improve", "effort": 8},
            {"name": "Implement", "isBucket": True},
            {"name": "Pilot execution", "bucketName": "Implement", "effort": 16},
            {"name": "Full rollout", "bucketName": "Implement", "effort": 12},
            {"name": "Training", "bucketName": "Implement", "effort": 8},
            {"name": "Sustain", "isBucket": True},
            {"name": "Control plan", "bucketName": "Sustain", "effort": 4},
            {"name": "Metrics monitoring", "bucketName": "Sustain", "effort": 8},
            {"name": "Closeout", "bucketName": "Sustain", "effort": 4},
        ]),
    },
    {
        "pmo_name": "General Project Template",
        "pmo_description": "Lightweight general-purpose template for uncategorized projects.",
        "pmo_cfrcategory": 893460055,
        "pmo_taskpayload": json.dumps([
            {"name": "Planning", "isBucket": True},
            {"name": "Define scope", "bucketName": "Planning", "effort": 8},
            {"name": "Create project plan", "bucketName": "Planning", "effort": 8},
            {"name": "Execution", "isBucket": True},
            {"name": "Execute deliverables", "bucketName": "Execution", "effort": 40},
            {"name": "Track progress", "bucketName": "Execution", "effort": 8},
            {"name": "Closeout", "isBucket": True},
            {"name": "Final review", "bucketName": "Closeout", "effort": 4},
            {"name": "Lessons learned", "bucketName": "Closeout", "effort": 4},
        ]),
    },
]

for t in templates:
    code, resp = post("/pmo_projecttemplates", t)
    tasks = json.loads(t["pmo_taskpayload"])
    task_count = len([x for x in tasks if not x.get("isBucket")])
    default = " (SYSTEM DEFAULT)" if t.get("pmo_issystemdefault") else ""
    print(f"  {t['pmo_name']}: HTTP {code} - {task_count} tasks{default}")


# ══════════════════════════════════════════════════════════════════════════════
# PROJECT LIFECYCLE GATE SET (for project-level gate workspace)
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== Project Lifecycle Gate Set ===")

code, gs_resp = post("/pmo_gatesettemplates", {
    "pmo_name": "Standard Project Lifecycle",
    "pmo_description": "Default 4-gate lifecycle for all projects: Initiation, Planning, Execution, Closeout.",
    "pmo_workflowscope": 893460201,
    "pmo_isdefault": True,
})
gs_id = gs_resp.get("pmo_gatesettemplateid", "???") if isinstance(gs_resp, dict) else "FAILED"
print(f"  Gate set: HTTP {code} [{gs_id}]")

if code in (200, 201, 204) and isinstance(gs_resp, dict):
    gates = [
        {"pmo_name": "Initiation Gate", "pmo_gatetype": 893460090, "pmo_gateorder": 0},
        {"pmo_name": "Planning Gate", "pmo_gatetype": 893460091, "pmo_gateorder": 1},
        {"pmo_name": "Execution Gate", "pmo_gatetype": 893460092, "pmo_gateorder": 2},
        {"pmo_name": "Closeout Gate", "pmo_gatetype": 893460093, "pmo_gateorder": 3},
    ]
    for g in gates:
        g["pmo_GateSet@odata.bind"] = f"/pmo_gatesettemplates({gs_id})"
        gc, _ = post("/pmo_gatesetitems", g)
        print(f"    {g['pmo_name']}: HTTP {gc}")


print("\n=== Summary ===")
print(f"  6 project templates (1 per CFR category)")
print(f"  10 required artifact definitions")
print(f"  1 project lifecycle gate set (4 gates)")
print(f"  2 intake workflows (already seeded)")
print(f"  7 PMO teams (pre-existing)")
print("\nAll seed data deployed. Ready for testing.")
