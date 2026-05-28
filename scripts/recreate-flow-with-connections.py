"""
Recreate the document upload flow with:
1. Correct BusinessEventsTrigger operation (per MS Learn connector ref)
2. Correct catalog/category uniquenames (per reverse-engineered working trigger)
3. Existing authenticated connection references (per MS Learn flow creation docs)

Sources:
- Trigger operation: https://learn.microsoft.com/en-us/connectors/commondataserviceforapps/#when-an-action-is-performed
- Connection references in clientdata: https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- Catalog assignment: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/catalog-catalogassignment
"""
import urllib.request
import urllib.parse
import json
import sys

TENANT = "fabb61b8-3afe-4e75-b934-a47f782b8cd7"
CLIENT_ID = "cc57f611-be88-4856-9d60-6ee9da06a32b"
ORG_URL = "https://nexusrcm-dev.crm.dynamics.com"
BASE = f"{ORG_URL}/api/data/v9.2"
SOLUTION = "CFRProjectManagement"
SP_SITE = "https://aetnao365.sharepoint.com/sites/Nexus-PMO"
SP_LIB = "AppDocuments"
OLD_FLOW_ID = "59567d3e-113f-f111-88b4-6045bdd9fbbe"

# Existing authenticated connection references (queried from environment)
SP_CONN_REF = "pmo_PMOAppSharePoint"
SP_CONN_ID = "e3718154a40e49588c1d86bec7444e0d"
DV_CONN_REF = "pmo_ProjectDataverse"
DV_CONN_ID = "shared-commondataser-b20762f9-bfbd-4130-989c-d9c69250ba63"

SECRET = sys.argv[1] if len(sys.argv) > 1 else None
if not SECRET:
    print("Usage: python recreate-flow-with-connections.py <client_secret>")
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

# Delete old flow
print("=== Deleting old flow ===")
r = urllib.request.Request(BASE + f"/workflows({OLD_FLOW_ID})", method="DELETE", headers={
    "Authorization": f"Bearer {TOKEN}", "OData-MaxVersion": "4.0", "OData-Version": "4.0",
})
try:
    with urllib.request.urlopen(r) as resp:
        print(f"  HTTP {resp.status}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code} (may already be deleted)")

# Build flow with existing connection references
# Per MS Learn: connection.name = connectionId, connectionReferenceLogicalName = logicalName
auth = "@parameters('$authentication')"

flow_def = {
    "properties": {
        "connectionReferences": {
            "shared_commondataserviceforapps": {
                "runtimeSource": "embedded",
                "connection": {
                    "name": DV_CONN_ID,
                    "connectionReferenceLogicalName": DV_CONN_REF
                },
                "api": {"name": "shared_commondataserviceforapps"}
            },
            "shared_sharepointonline": {
                "runtimeSource": "embedded",
                "connection": {
                    "name": SP_CONN_ID,
                    "connectionReferenceLogicalName": SP_CONN_REF
                },
                "api": {"name": "shared_sharepointonline"}
            }
        },
        "definition": {
            "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {
                "$connections": {"defaultValue": {}, "type": "Object"},
                "$authentication": {"defaultValue": {}, "type": "SecureObject"}
            },
            "triggers": {
                "When_upload_action_is_performed": {
                    "type": "OpenApiConnectionWebhook",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                            "connectionName": "shared_commondataserviceforapps",
                            "operationId": "BusinessEventsTrigger"
                        },
                        "parameters": {
                            "catalog": "pmo_PMODocumentManagement",
                            "category": "pmo_DocumentActions",
                            "subscriptionRequest/entityname": "none",
                            "subscriptionRequest/sdkmessagename": "pmo_UploadDocumentToSharePoint"
                        },
                        "authentication": auth
                    }
                }
            },
            "actions": {
                "Create_file": {
                    "runAfter": {},
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                            "connectionName": "shared_sharepointonline",
                            "operationId": "CreateFile"
                        },
                        "parameters": {
                            "dataset": SP_SITE,
                            "folderPath": f"/{SP_LIB}",
                            "name": "@triggerOutputs()?['body/InputParameters/FileName']",
                            "body": "@base64ToBinary(triggerOutputs()?['body/InputParameters/FileContent'])"
                        },
                        "authentication": auth
                    }
                },
                "Update_properties": {
                    "runAfter": {"Create_file": ["Succeeded"]},
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                            "connectionName": "shared_sharepointonline",
                            "operationId": "PatchItem"
                        },
                        "parameters": {
                            "dataset": SP_SITE,
                            "table": SP_LIB,
                            "id": "@outputs('Create_file')?['body/ItemId']",
                            "item/Title": "@triggerOutputs()?['body/InputParameters/RecordName']",
                            "item/IntakeID": "@triggerOutputs()?['body/InputParameters/IntakeId']",
                            "item/ProgramID": "@triggerOutputs()?['body/InputParameters/ProgramId']",
                            "item/ProjectID": "@triggerOutputs()?['body/InputParameters/ProjectId']",
                            "item/TaskID": "@triggerOutputs()?['body/InputParameters/TaskId']",
                            "item/DocumentCategory": "@triggerOutputs()?['body/InputParameters/DocumentCategory']"
                        },
                        "authentication": auth
                    }
                }
            }
        }
    },
    "schemaVersion": "1.0.0.0"
}

print("\n=== Creating flow with existing connections ===")
body = json.dumps({
    "category": 5,
    "name": "PMO: Upload Document to SharePoint",
    "type": 1,
    "description": "Triggered by pmo_UploadDocumentToSharePoint. Uploads to Nexus-PMO/AppDocuments with metadata.",
    "primaryentity": "none",
    "clientdata": json.dumps(flow_def),
}).encode()

r2 = urllib.request.Request(BASE + "/workflows", data=body, method="POST", headers={
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "OData-MaxVersion": "4.0", "OData-Version": "4.0",
    "Prefer": "return=representation",
    "MSCRM.SolutionUniqueName": SOLUTION,
})
try:
    with urllib.request.urlopen(r2) as resp:
        data = json.loads(resp.read())
        flow_id = data["workflowid"]
        print(f"  Flow created: [{flow_id}]")
        print(f"  Trigger: BusinessEventsTrigger")
        print(f"  SP Connection: {SP_CONN_REF} ({SP_CONN_ID})")
        print(f"  DV Connection: {DV_CONN_REF} ({DV_CONN_ID})")
except urllib.error.HTTPError as e:
    print(f"  Failed: HTTP {e.code}")
    print(f"  {e.read().decode()[:500]}")
    sys.exit(1)

# Try to activate
print("\n=== Activating flow ===")
activate_body = json.dumps({"statecode": 1}).encode()
r3 = urllib.request.Request(BASE + f"/workflows({flow_id})", data=activate_body, method="PATCH", headers={
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "OData-MaxVersion": "4.0", "OData-Version": "4.0",
    "IF-MATCH": "*",
})
try:
    with urllib.request.urlopen(r3) as resp:
        print(f"  Activated: HTTP {resp.status}")
except urllib.error.HTTPError as e:
    err = e.read().decode()
    print(f"  Activation: HTTP {e.code}")
    if len(err) > 0:
        print(f"  {err[:300]}")
