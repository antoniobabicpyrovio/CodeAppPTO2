"""
Register pmo_UploadDocumentToSharePoint custom API and create the backing cloud flow.

The custom API accepts a base64 file + metadata, and the flow uploads it to the
AppDocuments SharePoint library with the correct metadata columns.

Sources:
- Custom API creation: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/create-custom-api-with-code
- Cloud flow creation: https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
"""
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
    print("Usage: python seed-sharepoint-document-api.py <client_secret>")
    sys.exit(1)

# Auth
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
        return e.code, e.read().decode()


def patch(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(BASE + path, data=body, method="PATCH", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "IF-MATCH": "*",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# ============================================================================
# Step 1: Create the Custom API
# ============================================================================
print("=== Step 1: Register Custom API ===\n")

# Parameter type codes (from CustomAPIRequestParameter.Type):
# 0=Boolean, 1=DateTime, 2=Decimal, 3=Entity, 4=EntityCollection,
# 5=EntityReference, 6=Float, 7=Integer, 8=Money, 9=Picklist, 10=String,
# 11=StringArray, 12=Guid

CUSTOM_API_PAYLOAD = {
    "uniquename": "pmo_UploadDocumentToSharePoint",
    "name": "pmo_UploadDocumentToSharePoint",
    "displayname": "Upload Document to SharePoint",
    "description": "Uploads a file to the AppDocuments SharePoint library with PMO metadata columns.",
    "bindingtype": 0,        # Global (unbound)
    "isfunction": False,
    "isprivate": False,
    "allowedcustomprocessingsteptype": 2,  # Sync and Async (allows flow binding)
    "executeprivilegename": None,
    "workflowsdkstepenabled": True,        # Enable for workflow/flow binding
    "iscustomizable": {"Value": True},
    "CustomAPIRequestParameters": [
        {"uniquename": "FileName",         "name": "pmo_UploadDocumentToSharePoint.FileName",         "displayname": "File Name",          "type": 10, "isoptional": False, "description": "Original file name",                    "iscustomizable": {"Value": True}},
        {"uniquename": "FileContent",      "name": "pmo_UploadDocumentToSharePoint.FileContent",      "displayname": "File Content",       "type": 10, "isoptional": False, "description": "Base64-encoded file content",            "iscustomizable": {"Value": True}},
        {"uniquename": "RecordType",       "name": "pmo_UploadDocumentToSharePoint.RecordType",       "displayname": "Record Type",        "type": 10, "isoptional": False, "description": "Intake Request / Program / Project / Task", "iscustomizable": {"Value": True}},
        {"uniquename": "RecordId",         "name": "pmo_UploadDocumentToSharePoint.RecordId",         "displayname": "Record ID",          "type": 10, "isoptional": False, "description": "GUID of the parent Dataverse record",   "iscustomizable": {"Value": True}},
        {"uniquename": "RecordName",       "name": "pmo_UploadDocumentToSharePoint.RecordName",       "displayname": "Record Name",        "type": 10, "isoptional": False, "description": "Display name for Title column",          "iscustomizable": {"Value": True}},
        {"uniquename": "DocumentCategory", "name": "pmo_UploadDocumentToSharePoint.DocumentCategory", "displayname": "Document Category",  "type": 10, "isoptional": True,  "description": "Category label (free text)",             "iscustomizable": {"Value": True}},
        {"uniquename": "ProjectId",        "name": "pmo_UploadDocumentToSharePoint.ProjectId",        "displayname": "Project ID",         "type": 10, "isoptional": True,  "description": "GUID for cross-reference",               "iscustomizable": {"Value": True}},
        {"uniquename": "ProgramId",        "name": "pmo_UploadDocumentToSharePoint.ProgramId",        "displayname": "Program ID",         "type": 10, "isoptional": True,  "description": "GUID for cross-reference",               "iscustomizable": {"Value": True}},
        {"uniquename": "IntakeId",         "name": "pmo_UploadDocumentToSharePoint.IntakeId",         "displayname": "Intake ID",          "type": 10, "isoptional": True,  "description": "GUID for cross-reference",               "iscustomizable": {"Value": True}},
        {"uniquename": "TaskId",           "name": "pmo_UploadDocumentToSharePoint.TaskId",           "displayname": "Task ID",            "type": 10, "isoptional": True,  "description": "GUID for cross-reference",               "iscustomizable": {"Value": True}},
    ],
    "CustomAPIResponseProperties": [
        {"uniquename": "SharePointItemId", "name": "pmo_UploadDocumentToSharePoint.SharePointItemId", "displayname": "SharePoint Item ID", "type": 7,  "description": "List item ID in SharePoint",             "iscustomizable": {"Value": True}},
        {"uniquename": "SharePointUrl",    "name": "pmo_UploadDocumentToSharePoint.SharePointUrl",    "displayname": "SharePoint URL",     "type": 10, "description": "Direct URL to the uploaded file",        "iscustomizable": {"Value": True}},
        {"uniquename": "Success",          "name": "pmo_UploadDocumentToSharePoint.Success",          "displayname": "Success",            "type": 0,  "description": "Whether the upload succeeded",           "iscustomizable": {"Value": True}},
        {"uniquename": "ErrorMessage",     "name": "pmo_UploadDocumentToSharePoint.ErrorMessage",     "displayname": "Error Message",      "type": 10, "description": "Error detail if failed",                 "iscustomizable": {"Value": True}},
    ],
}

code, resp = post("/customapis", CUSTOM_API_PAYLOAD)
if code in (200, 201):
    api_id = resp.get("customapiid", "???") if isinstance(resp, dict) else "???"
    print(f"  Custom API created: HTTP {code} [{api_id}]")
else:
    print(f"  Custom API creation failed: HTTP {code}")
    if isinstance(resp, str) and "DuplicateRecord" in resp:
        print("  (Already exists - continuing)")
    else:
        print(f"  {str(resp)[:500]}")


# ============================================================================
# Step 2: Create the Cloud Flow
# ============================================================================
print("\n=== Step 2: Create Cloud Flow ===\n")

# The flow definition uses the SharePoint connector to upload files
# and update metadata. It triggers on the custom API action.
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
                            "item/RecordType": "@triggerOutputs()?['body/RecordType']",
                            "item/IntakeID": "@triggerOutputs()?['body/IntakeId']",
                            "item/ProgramID": "@triggerOutputs()?['body/ProgramId']",
                            "item/ProjectID": "@triggerOutputs()?['body/ProjectId']",
                            "item/TaskID": "@triggerOutputs()?['body/TaskId']",
                            "item/DocumentCategory": "@triggerOutputs()?['body/DocumentCategory']"
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

flow_payload = {
    "category": 5,           # Modern Flow
    "name": "PMO: Upload Document to SharePoint AppDocuments",
    "type": 1,               # Definition
    "description": "Backing flow for pmo_UploadDocumentToSharePoint custom API. Uploads files to the Nexus-PMO/AppDocuments library with metadata.",
    "primaryentity": "none",
    "clientdata": json.dumps(flow_definition),
}

code2, resp2 = post("/workflows", flow_payload)
if code2 in (200, 201):
    flow_id = resp2.get("workflowid", "???") if isinstance(resp2, dict) else "???"
    print(f"  Cloud flow created: HTTP {code2} [{flow_id}]")

    # Step 3: Activate the flow
    print("\n=== Step 3: Activate Flow ===\n")
    code3, resp3 = patch(f"/workflows({flow_id})", {"statecode": 1})
    print(f"  Flow activation: HTTP {code3}")
else:
    print(f"  Flow creation failed: HTTP {code2}")
    print(f"  {str(resp2)[:500]}")
    flow_id = None


# ============================================================================
print("\n=== Summary ===")
print(f"  Custom API: pmo_UploadDocumentToSharePoint")
print(f"  Parameters: 10 request (5 required, 5 optional), 4 response")
print(f"  Cloud flow: PMO: Upload Document to SharePoint AppDocuments")
print(f"  SharePoint target: {SP_SITE_URL}/{SP_LIBRARY}")
print(f"\n  The app calls executeAction('pmo_UploadDocumentToSharePoint', payload)")
print(f"  and the flow handles the SharePoint upload + metadata update.\n")
if flow_id:
    print(f"  IMPORTANT: Open the flow in Power Automate and configure the")
    print(f"  SharePoint connection reference if prompted.\n")
