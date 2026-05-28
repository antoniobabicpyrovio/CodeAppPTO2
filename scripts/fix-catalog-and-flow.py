"""
Fix the SharePoint document upload integration:
1. Create Catalog + Category for the custom API
2. Create CatalogAssignment linking custom API to the category
3. Delete and recreate the flow with correct trigger
4. Add all to CFRProjectManagement solution

Sources:
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/catalog-catalogassignment
- https://learn.microsoft.com/en-us/power-automate/dataverse/action-trigger
- https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
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
SP_SITE_URL = "https://aetnao365.sharepoint.com/sites/Nexus-PMO"
SP_LIBRARY = "AppDocuments"
API_ID = "4c2006bb-9f3e-f111-88b4-6045bdd9f8fd"
OLD_FLOW_ID = "75f700c1-9f3e-f111-88b4-6045bdd9f8fd"

SECRET = sys.argv[1] if len(sys.argv) > 1 else None
if not SECRET:
    print("Usage: python fix-catalog-and-flow.py <client_secret>")
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


def api_post(path, data, headers_extra=None):
    body = json.dumps(data).encode()
    hdrs = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Prefer": "return=representation",
    }
    if headers_extra:
        hdrs.update(headers_extra)
    r = urllib.request.Request(BASE + path, data=body, method="POST", headers=hdrs)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def api_delete(path):
    r = urllib.request.Request(BASE + path, method="DELETE", headers={
        "Authorization": f"Bearer {TOKEN}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
    })
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


# ============================================================================
# Step 1: Create Root Catalog
# ============================================================================
print("=== Step 1: Create Root Catalog ===")
code, resp = api_post("/catalogs", {
    "name": "PMO Document Management",
    "uniquename": "pmo_PMODocumentManagement",
    "displayname": "PMO Document Management",
    "description": "Root catalog for PMO document management actions",
    "iscustomizable": {"Value": True},
}, {"MSCRM.SolutionUniqueName": SOLUTION})

if code in (200, 201) and isinstance(resp, dict):
    root_cat_id = resp["catalogid"]
    print(f"  Root catalog created: [{root_cat_id}]")
elif isinstance(resp, str) and "DuplicateRecord" in resp:
    print("  Root catalog already exists, looking up...")
    r = urllib.request.Request(
        BASE + "/catalogs?" + urllib.parse.urlencode({"$filter": "uniquename eq 'pmo_PMODocumentManagement'", "$select": "catalogid"}),
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "OData-MaxVersion": "4.0", "OData-Version": "4.0"},
    )
    with urllib.request.urlopen(r) as rr:
        root_cat_id = json.loads(rr.read())["value"][0]["catalogid"]
    print(f"  Found: [{root_cat_id}]")
else:
    print(f"  Failed: HTTP {code} - {str(resp)[:300]}")
    sys.exit(1)

# ============================================================================
# Step 2: Create Category (sub-catalog)
# ============================================================================
print("\n=== Step 2: Create Category Sub-Catalog ===")
code, resp = api_post("/catalogs", {
    "name": "PMO Document Actions",
    "uniquename": "pmo_DocumentActions",
    "displayname": "Document Actions",
    "description": "Document upload and management actions for the PMO app",
    "iscustomizable": {"Value": True},
    "ParentCatalogId@odata.bind": f"/catalogs({root_cat_id})",
}, {"MSCRM.SolutionUniqueName": SOLUTION})

if code in (200, 201) and isinstance(resp, dict):
    cat_id = resp["catalogid"]
    print(f"  Category created: [{cat_id}]")
elif isinstance(resp, str) and "DuplicateRecord" in resp:
    print("  Category already exists, looking up...")
    r = urllib.request.Request(
        BASE + "/catalogs?" + urllib.parse.urlencode({"$filter": "uniquename eq 'pmo_DocumentActions'", "$select": "catalogid"}),
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "OData-MaxVersion": "4.0", "OData-Version": "4.0"},
    )
    with urllib.request.urlopen(r) as rr:
        cat_id = json.loads(rr.read())["value"][0]["catalogid"]
    print(f"  Found: [{cat_id}]")
else:
    print(f"  Failed: HTTP {code} - {str(resp)[:300]}")
    sys.exit(1)

# ============================================================================
# Step 3: Create CatalogAssignment linking custom API to category
# ============================================================================
print("\n=== Step 3: Create CatalogAssignment ===")
code, resp = api_post("/catalogassignments", {
    "name": "pmo_UploadDocumentToSharePoint",
    "CatalogId@odata.bind": f"/catalogs({cat_id})",
    "CustomAPIId@odata.bind": f"/customapis({API_ID})",
    "iscustomizable": {"Value": True},
}, {"MSCRM.SolutionUniqueName": SOLUTION})

if code in (200, 201):
    print(f"  CatalogAssignment created: HTTP {code}")
elif isinstance(resp, str) and "DuplicateRecord" in resp:
    print("  CatalogAssignment already exists")
else:
    print(f"  Failed: HTTP {code} - {str(resp)[:300]}")

# ============================================================================
# Step 4: Delete old broken flow
# ============================================================================
print("\n=== Step 4: Delete old flow ===")
del_code = api_delete(f"/workflows({OLD_FLOW_ID})")
print(f"  Delete old flow: HTTP {del_code}")

# ============================================================================
# Step 5: Create new flow with correct trigger
# ============================================================================
print("\n=== Step 5: Create new flow ===")

# The correct trigger for "When an action is performed" uses the
# SubscribeWebhookTrigger with proper catalog/category/action references
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
                "When_action_is_performed": {
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
                            "subscriptionRequest/name": "pmo_UploadDocumentToSharePoint",
                            "subscriptionRequest/catalogassignment": f"{cat_id}"
                        },
                        "authentication": "@parameters('$authentication')"
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
                            "dataset": SP_SITE_URL,
                            "folderPath": f"/{SP_LIBRARY}",
                            "name": "@triggerOutputs()?['body/InputParameters/FileName']",
                            "body": "@base64ToBinary(triggerOutputs()?['body/InputParameters/FileContent'])"
                        },
                        "authentication": "@parameters('$authentication')"
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
                            "dataset": SP_SITE_URL,
                            "table": SP_LIBRARY,
                            "id": "@outputs('Create_file')?['body/ItemId']",
                            "item/Title": "@triggerOutputs()?['body/InputParameters/RecordName']",
                            "item/IntakeID": "@triggerOutputs()?['body/InputParameters/IntakeId']",
                            "item/ProgramID": "@triggerOutputs()?['body/InputParameters/ProgramId']",
                            "item/ProjectID": "@triggerOutputs()?['body/InputParameters/ProjectId']",
                            "item/TaskID": "@triggerOutputs()?['body/InputParameters/TaskId']",
                            "item/DocumentCategory": "@triggerOutputs()?['body/InputParameters/DocumentCategory']",
                            "item/UploadedByClaims": "@concat('i:0#.f|membership|', triggerOutputs()?['body/InputParameters/UserEmail'])"
                        },
                        "authentication": "@parameters('$authentication')"
                    }
                },
                "Set_output_parameters": {
                    "runAfter": {"Update_properties": ["Succeeded"]},
                    "type": "OpenApiConnection",
                    "inputs": {
                        "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
                            "connectionName": "shared_commondataserviceforapps",
                            "operationId": "PerformUnboundAction"
                        },
                        "parameters": {
                            "actionName": "pmo_UploadDocumentToSharePoint",
                            "item/SharePointItemId": "@outputs('Create_file')?['body/ItemId']",
                            "item/SharePointUrl": "@outputs('Create_file')?['body/{Link}']",
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

code, resp = api_post("/workflows", {
    "category": 5,
    "name": "PMO: Upload Document to SharePoint",
    "type": 1,
    "description": "Uploads files to Nexus-PMO/AppDocuments via pmo_UploadDocumentToSharePoint custom API",
    "primaryentity": "none",
    "clientdata": json.dumps(flow_definition),
}, {"MSCRM.SolutionUniqueName": SOLUTION})

if code in (200, 201) and isinstance(resp, dict):
    new_flow_id = resp["workflowid"]
    print(f"  Flow created in solution: [{new_flow_id}]")
else:
    print(f"  Flow creation failed: HTTP {code}")
    print(f"  {str(resp)[:500]}")
    new_flow_id = None

# ============================================================================
print("\n=== Summary ===")
print(f"  Root Catalog: pmo_PMODocumentManagement [{root_cat_id}]")
print(f"  Category: pmo_DocumentActions [{cat_id}]")
print(f"  Custom API: pmo_UploadDocumentToSharePoint [{API_ID}]")
print(f"  CatalogAssignment: linked to category")
if new_flow_id:
    print(f"  New Flow: [{new_flow_id}]")
    print(f"\n  Open the flow in Power Automate (CFRProjectManagement solution)")
    print(f"  -> Configure the SharePoint connection")
    print(f"  -> Turn on the flow")
