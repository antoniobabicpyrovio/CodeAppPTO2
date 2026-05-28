"""Seed detailed 5-stage intake workflows for Projects and Programs."""
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
    print("Usage: python seed-intake-workflows.py <client_secret>")
    sys.exit(1)

# ── Auth ──
token_data = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "client_secret": SECRET,
    "scope": f"{ORG_URL}/.default",
    "grant_type": "client_credentials",
}).encode()
token_req = urllib.request.Request(
    f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token",
    data=token_data, method="POST",
)
with urllib.request.urlopen(token_req) as resp:
    TOKEN = json.loads(resp.read())["access_token"]
print("Authenticated.\n")


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
# 5-STAGE PROJECT INTAKE WORKFLOW
# ══════════════════════════════════════════════════════════════════════════════
print("=== 5-Stage Project Intake Workflow ===\n")

# Conversion rules: map intake fields → project fields on conversion
conversion_rules = json.dumps([
    {"intakeField": "pmo_name",                "projectField": "msdyn_subject",                "transform": "direct"},
    {"intakeField": "pmo_description",         "projectField": "msdyn_description",            "transform": "direct"},
    {"intakeField": "pmo_requestedstartdate",  "projectField": "msdyn_scheduledstart",         "transform": "direct"},
    {"intakeField": "pmo_estimatedbudget",     "projectField": "proj_budget",                  "transform": "direct"},
    {"intakeField": "_pmo_targetteam_value",   "projectField": "pmo_PrimaryTeam@odata.bind",   "transform": "odata_bind"},
])

code, wf_resp = post("/pmo_gatesettemplates", {
    "pmo_name": "Standard Project Intake (5-Stage)",
    "pmo_description": "Guided 5-stage intake: Basics → Scope → Justification → Timeline & Budget → Review & Approval. Breaks the request into small, logical steps.",
    "pmo_workflowscope": 893460200,       # IntakeWorkflow
    "pmo_targetentitytype": 893460210,     # Project
    "pmo_isdefault": False,
    "pmo_conversionrulesjson": conversion_rules,
})
wf_id = wf_resp.get("pmo_gatesettemplateid", "FAILED") if isinstance(wf_resp, dict) else "FAILED"
print(f"  Workflow created: HTTP {code} [{wf_id}]")

if code not in (200, 201, 204) or not isinstance(wf_resp, dict):
    print(f"  ERROR: {wf_resp}")
    sys.exit(1)

# ── Stage 1: Request Basics ──
# Capture identity: what is this request, what type, how urgent
stages = [
    {
        "pmo_stagelabel": "Request Basics",
        "pmo_name": "Request Basics",
        "pmo_gatetype": 893460090,   # Initiation
        "pmo_gateorder": 0,
        "pmo_requiredfieldsjson": json.dumps(["pmo_name", "pmo_requesttype", "pmo_priority"]),
        "pmo_requiredartifacttypesjson": json.dumps([]),
        "pmo_requiresapproval": False,
        "pmo_approvergroupid": "",
    },
    # ── Stage 2: Scope & Context ──
    # What is this about and who does it affect
    {
        "pmo_stagelabel": "Scope & Context",
        "pmo_name": "Scope & Context",
        "pmo_gatetype": 893460090,
        "pmo_gateorder": 1,
        "pmo_requiredfieldsjson": json.dumps(["pmo_description", "pmo_lineofbusiness"]),
        "pmo_requiredartifacttypesjson": json.dumps([]),
        "pmo_requiresapproval": False,
        "pmo_approvergroupid": "",
    },
    # ── Stage 3: Business Justification ──
    # Why should we do this — business case required
    {
        "pmo_stagelabel": "Business Justification",
        "pmo_name": "Business Justification",
        "pmo_gatetype": 893460091,   # Planning
        "pmo_gateorder": 2,
        "pmo_requiredfieldsjson": json.dumps(["pmo_businessjustification"]),
        "pmo_requiredartifacttypesjson": json.dumps([893460110]),  # Business Case
        "pmo_requiresapproval": False,
        "pmo_approvergroupid": "",
    },
    # ── Stage 4: Timeline & Budget ──
    # When and how much
    {
        "pmo_stagelabel": "Timeline & Budget",
        "pmo_name": "Timeline & Budget",
        "pmo_gatetype": 893460091,
        "pmo_gateorder": 3,
        "pmo_requiredfieldsjson": json.dumps([
            "pmo_requestedstartdate",
            "pmo_targetcompletiondate",
            "pmo_estimatedbudget",
        ]),
        "pmo_requiredartifacttypesjson": json.dumps([]),
        "pmo_requiresapproval": False,
        "pmo_approvergroupid": "",
    },
    # ── Stage 5: Review & Submit ──
    # Final review before PMO approval — charter artifact required
    {
        "pmo_stagelabel": "Review & Submit for Approval",
        "pmo_name": "Review & Submit for Approval",
        "pmo_gatetype": 893460092,   # Execution
        "pmo_gateorder": 4,
        "pmo_requiredfieldsjson": json.dumps([]),
        "pmo_requiredartifacttypesjson": json.dumps([893460111]),  # Project Charter
        "pmo_requiresapproval": True,
        "pmo_approvergroupid": "00000000-0000-0000-0000-000000000000",  # Placeholder AAD group
    },
]

for s in stages:
    s["pmo_GateSet@odata.bind"] = f"/pmo_gatesettemplates({wf_id})"
    sc, sr = post("/pmo_gatesetitems", s)
    req_fields = json.loads(s["pmo_requiredfieldsjson"])
    req_artifacts = json.loads(s["pmo_requiredartifacttypesjson"])
    approval = " [APPROVAL REQUIRED]" if s["pmo_requiresapproval"] else ""
    print(f"  Stage {s['pmo_gateorder']}: {s['pmo_stagelabel']} — "
          f"{len(req_fields)} fields, {len(req_artifacts)} artifacts{approval} — HTTP {sc}")


# ══════════════════════════════════════════════════════════════════════════════
# 5-STAGE PROGRAM INTAKE WORKFLOW
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 5-Stage Program Intake Workflow ===\n")

prog_conversion = json.dumps([
    {"intakeField": "pmo_name",                "projectField": "msdyn_subject",                "transform": "direct"},
    {"intakeField": "pmo_description",         "projectField": "msdyn_description",            "transform": "direct"},
    {"intakeField": "_pmo_targetteam_value",   "projectField": "pmo_PrimaryTeam@odata.bind",   "transform": "odata_bind"},
])

code2, wf2_resp = post("/pmo_gatesettemplates", {
    "pmo_name": "Standard Program Intake (5-Stage)",
    "pmo_description": "Guided 5-stage program intake: Identity → Strategic Fit → Governance Structure → Funding → Executive Approval.",
    "pmo_workflowscope": 893460200,
    "pmo_targetentitytype": 893460211,     # Program
    "pmo_isdefault": False,
    "pmo_conversionrulesjson": prog_conversion,
})
wf2_id = wf2_resp.get("pmo_gatesettemplateid", "FAILED") if isinstance(wf2_resp, dict) else "FAILED"
print(f"  Workflow created: HTTP {code2} [{wf2_id}]")

if code2 not in (200, 201, 204) or not isinstance(wf2_resp, dict):
    print(f"  ERROR: {wf2_resp}")
    sys.exit(1)

prog_stages = [
    {
        "pmo_stagelabel": "Program Identity",
        "pmo_name": "Program Identity",
        "pmo_gatetype": 893460090,
        "pmo_gateorder": 0,
        "pmo_requiredfieldsjson": json.dumps(["pmo_name", "pmo_requesttype", "pmo_priority"]),
        "pmo_requiredartifacttypesjson": json.dumps([]),
        "pmo_requiresapproval": False,
        "pmo_approvergroupid": "",
    },
    {
        "pmo_stagelabel": "Strategic Fit",
        "pmo_name": "Strategic Fit",
        "pmo_gatetype": 893460090,
        "pmo_gateorder": 1,
        "pmo_requiredfieldsjson": json.dumps(["pmo_description", "pmo_businessjustification", "pmo_lineofbusiness"]),
        "pmo_requiredartifacttypesjson": json.dumps([893460110]),  # Business Case
        "pmo_requiresapproval": False,
        "pmo_approvergroupid": "",
    },
    {
        "pmo_stagelabel": "Governance Structure",
        "pmo_name": "Governance Structure",
        "pmo_gatetype": 893460091,
        "pmo_gateorder": 2,
        "pmo_requiredfieldsjson": json.dumps([]),
        "pmo_requiredartifacttypesjson": json.dumps([893460111, 893460112]),  # Charter + RACI
        "pmo_requiresapproval": False,
        "pmo_approvergroupid": "",
    },
    {
        "pmo_stagelabel": "Funding & Timeline",
        "pmo_name": "Funding & Timeline",
        "pmo_gatetype": 893460091,
        "pmo_gateorder": 3,
        "pmo_requiredfieldsjson": json.dumps([
            "pmo_requestedstartdate",
            "pmo_targetcompletiondate",
            "pmo_estimatedbudget",
        ]),
        "pmo_requiredartifacttypesjson": json.dumps([893460116]),  # Budget
        "pmo_requiresapproval": False,
        "pmo_approvergroupid": "",
    },
    {
        "pmo_stagelabel": "Executive Approval",
        "pmo_name": "Executive Approval",
        "pmo_gatetype": 893460092,
        "pmo_gateorder": 4,
        "pmo_requiredfieldsjson": json.dumps([]),
        "pmo_requiredartifacttypesjson": json.dumps([893460115]),  # SOW
        "pmo_requiresapproval": True,
        "pmo_approvergroupid": "00000000-0000-0000-0000-000000000000",
    },
]

for s in prog_stages:
    s["pmo_GateSet@odata.bind"] = f"/pmo_gatesettemplates({wf2_id})"
    sc, sr = post("/pmo_gatesetitems", s)
    req_fields = json.loads(s["pmo_requiredfieldsjson"])
    req_artifacts = json.loads(s["pmo_requiredartifacttypesjson"])
    approval = " [APPROVAL REQUIRED]" if s["pmo_requiresapproval"] else ""
    print(f"  Stage {s['pmo_gateorder']}: {s['pmo_stagelabel']} — "
          f"{len(req_fields)} fields, {len(req_artifacts)} artifacts{approval} — HTTP {sc}")


# ══════════════════════════════════════════════════════════════════════════════
print("\n=== Summary ===")
print(f"  Project workflow: 5 stages — Basics → Scope → Justification → Timeline → Approval")
print(f"  Program workflow: 5 stages — Identity → Strategic Fit → Governance → Funding → Exec Approval")
print(f"  Field distribution: 3 → 2 → 1 → 3 → 0 required fields per stage (project)")
print(f"  Artifact distribution: 0 → 0 → 1 → 0 → 1 required artifacts per stage (project)")
print(f"  Approval gates: Stage 5 only (PMO/executive review)")
print(f"\n  Note: approver group ID is a placeholder (all zeros).")
print(f"  Update via Admin → Settings → Intake Workflows after seeding.\n")
