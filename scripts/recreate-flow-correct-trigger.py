"""
Recreate the document upload flow with the correct trigger operation.

The previous flow used SubscribeWebhookTrigger (operationId for "When a row is
added/modified/deleted"), which requires a real Dataverse table name.

The correct trigger is BusinessEventsTrigger (operationId for "When an action
is performed"), which accepts catalog, category, entityname, and sdkmessagename.

Source: https://learn.microsoft.com/en-us/connectors/commondataserviceforapps/#when-an-action-is-performed
"""
import urllib.request
import urllib.parse
import json
import sys

TENANT = "fabb61b8-3afe-4e75-b934-a47f782b8cd7"
CLIENT_ID = "cc57f611-be88-4856-9d60-6ee9da06a32b"
ORG_URL = "https://nexusrcm-dev.crm.dynamics.com"
BASE = f"{ORG_URL}/api/data/v9.2"
SP_SITE = "https://aetnao365.sharepoint.com/sites/Nexus-PMO"
SP_LIB = "AppDocuments"
OLD_FLOW_ID = "5ec097d6-0c3f-f111-88b4-6045bdd9fd8a"
ROOT_CAT_ID = "84c339cc-0c3f-f111-88b4-6045bdd9f8fd"
CAT_ID = "4f6c32cf-0c3f-f111-88b4-6045bdd9fd8a"
SOLUTION = "CFRProjectManagement"

SECRET = sys.argv[1] if len(sys.argv) > 1 else None
if not SECRET:
    print("Usage: python recreate-flow-correct-trigger.py <client_secret>")
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


def api_delete(path):
    r = urllib.request.Request(BASE + path, method="DELETE", headers={
        "Authorization": f"Bearer {TOKEN}",
        "OData-MaxVersion": "4.0", "OData-Version": "4.0",
    })
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


def api_post(path, data, extra_headers=None):
    body = json.dumps(data).encode()
    hdrs = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0", "OData-Version": "4.0",
        "Prefer": "return=representation",
    }
    if extra_headers:
        hdrs.update(extra_headers)
    r = urllib.request.Request(BASE + path, data=body, method="POST", headers=hdrs)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# Step 1: Delete old flow
print("=== Deleting old flow ===")
print(f"  HTTP {api_delete(f'/workflows({OLD_FLOW_ID})')}")

# Step 2: Build correct flow definition
# Using BusinessEventsTrigger per:
# https://learn.microsoft.com/en-us/connectors/commondataserviceforapps/#when-an-action-is-performed
auth_expr = "@parameters('$authentication')"

flow_definition = {
    "properties": {
        "connectionReferences": {
            "shared_sharepointonline": {
                "runtimeSource": "embedded",
                "connection": {},
                "api": {"name": "shared_sharepointonline"}
            },
            "shared_commondataserviceforapps": {
                "runtimeSource": "embedded",
                "connection": {},
                "api": {"name": "shared_commondataserviceforapps"}
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
                            "catalog": ROOT_CAT_ID,
                            "category": CAT_ID,
                            "entityname": "none",
                            "sdkmessagename": "pmo_UploadDocumentToSharePoint"
                        },
                        "authentication": auth_expr
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
                        "authentication": auth_expr
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
                        "authentication": auth_expr
                    }
                }
            }
        }
    },
    "schemaVersion": "1.0.0.0"
}

# Step 3: Create new flow in solution
print("\n=== Creating flow with BusinessEventsTrigger ===")
code, resp = api_post("/workflows", {
    "category": 5,
    "name": "PMO: Upload Document to SharePoint",
    "type": 1,
    "description": "Triggered by pmo_UploadDocumentToSharePoint custom API. Uploads to Nexus-PMO/AppDocuments with metadata.",
    "primaryentity": "none",
    "clientdata": json.dumps(flow_definition),
}, {"MSCRM.SolutionUniqueName": SOLUTION})

if code in (200, 201) and isinstance(resp, dict):
    print(f"  Flow created: [{resp['workflowid']}]")
    print(f"  Trigger: BusinessEventsTrigger (correct)")
    print(f"  Catalog: {ROOT_CAT_ID}")
    print(f"  Category: {CAT_ID}")
    print(f"  Action: pmo_UploadDocumentToSharePoint")
else:
    print(f"  Failed: HTTP {code}")
    print(f"  {str(resp)[:500]}")

print("\nOpen the flow in the CFRProjectManagement solution to configure")
print("the SharePoint connection and turn it on.")
