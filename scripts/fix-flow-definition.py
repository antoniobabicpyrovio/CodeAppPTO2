"""Update the flow definition to fix RecordType and UploadedBy."""
import urllib.request
import urllib.parse
import json
import sys

TENANT = "fabb61b8-3afe-4e75-b934-a47f782b8cd7"
CLIENT_ID = "cc57f611-be88-4856-9d60-6ee9da06a32b"
ORG_URL = "https://nexusrcm-dev.crm.dynamics.com"
BASE = f"{ORG_URL}/api/data/v9.2"
SP_SITE_URL = "https://aetnao365.sharepoint.com/sites/Nexus-PMO"
SP_LIBRARY = "AppDocuments"

SECRET = sys.argv[1] if len(sys.argv) > 1 else None
if not SECRET:
    print("Usage: python fix-flow-definition.py <client_secret>")
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

FLOW_ID = "75f700c1-9f3e-f111-88b4-6045bdd9f8fd"

# New flow definition:
# - Removed item/RecordType from Update_file_properties (Choice column not in PatchItem schema)
# - Added UploadedBy via claims string constructed from UserEmail
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
                "When_pmo_UploadDocumentToSharePoint_is_called": {
                    "type": "OpenApiConnectionWebhook",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                            "connectionName": "shared_commondataserviceforapps",
                            "operationId": "SubscribeWebhookTrigger"
                        },
                        "parameters": {
                            "subscriptionRequest/message": 4,
                            "subscriptionRequest/entityname": "none",
                            "subscriptionRequest/scope": 4,
                            "subscriptionRequest/name": "pmo_UploadDocumentToSharePoint"
                        },
                        "authentication": "@parameters('$authentication')"
                    }
                }
            },
            "actions": {
                "Create_file_in_SharePoint": {
                    "runAfter": {},
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                            "connectionName": "shared_sharepointonline",
                            "operationId": "CreateFile"
                        },
                        "parameters": {
                            "dataset": SP_SITE_URL,
                            "folderPath": f"/{SP_LIBRARY}",
                            "name": "@triggerOutputs()?['body/FileName']",
                            "body": "@base64ToBinary(triggerOutputs()?['body/FileContent'])"
                        },
                        "authentication": "@parameters('$authentication')"
                    }
                },
                "Update_file_properties": {
                    "runAfter": {"Create_file_in_SharePoint": ["Succeeded"]},
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                            "connectionName": "shared_sharepointonline",
                            "operationId": "PatchItem"
                        },
                        "parameters": {
                            "dataset": SP_SITE_URL,
                            "table": SP_LIBRARY,
                            "id": "@outputs('Create_file_in_SharePoint')?['body/ItemId']",
                            "item/Title": "@triggerOutputs()?['body/RecordName']",
                            "item/IntakeID": "@triggerOutputs()?['body/IntakeId']",
                            "item/ProgramID": "@triggerOutputs()?['body/ProgramId']",
                            "item/ProjectID": "@triggerOutputs()?['body/ProjectId']",
                            "item/TaskID": "@triggerOutputs()?['body/TaskId']",
                            "item/DocumentCategory": "@triggerOutputs()?['body/DocumentCategory']",
                            "item/UploadedByClaims": "@concat('i:0#.f|membership|', triggerOutputs()?['body/UserEmail'])"
                        },
                        "authentication": "@parameters('$authentication')"
                    }
                },
                "Respond_with_success": {
                    "runAfter": {"Update_file_properties": ["Succeeded"]},
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                            "connectionName": "shared_commondataserviceforapps",
                            "operationId": "PerformUnboundAction"
                        },
                        "parameters": {
                            "actionName": "pmo_UploadDocumentToSharePointResponse",
                            "item/SharePointItemId": "@outputs('Create_file_in_SharePoint')?['body/ItemId']",
                            "item/SharePointUrl": "@outputs('Create_file_in_SharePoint')?['body/{Link}']",
                            "item/Success": True,
                            "item/ErrorMessage": ""
                        },
                        "authentication": "@parameters('$authentication')"
                    }
                }
            }
        }
    },
    "schemaVersion": "1.0.0.0"
}

# PATCH the flow with updated clientdata
body = json.dumps({
    "clientdata": json.dumps(flow_definition),
}).encode()

patch_req = urllib.request.Request(
    f"{BASE}/workflows({FLOW_ID})",
    data=body, method="PATCH",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "IF-MATCH": "*",
    },
)
try:
    with urllib.request.urlopen(patch_req) as resp:
        print(f"Flow updated: HTTP {resp.status}")
except urllib.error.HTTPError as e:
    print(f"Flow update failed: HTTP {e.code}")
    print(e.read().decode()[:500])

print("\nChanges:")
print("  - Removed item/RecordType from Update_file_properties")
print("  - Added item/UploadedByClaims with claims format: i:0#.f|membership|<email>")
print("  - UploadedBy populated from new UserEmail parameter")
print("\nOpen the flow in Power Automate to configure the SharePoint connection and activate.")
