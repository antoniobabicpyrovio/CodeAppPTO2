"""Patch a DEV-exported managed CFRProjectManagement solution zip for PROD import.

Why this exists
---------------
The previous PowerShell patch used a regex to strip the
`item/pmo_convertedproject@odata.bind` parameter from the conversion flow JSON.
That value contains an embedded `@concat('/msdyn_projects(', ..., ')')` whose
arguments are comma-separated — the regex matched only up to the first inner
comma and left mangled JSON behind, which caused the import to fail with:

    Flow clientdata is in invalid format. Details: "Invalid JavaScript
    property identifier character: (. Path 'properties.definition.actions
    .Check_status_is_Approved.actions.Update_request_converted.inputs
    .parameters['item/pmo_converteddate']', line 94, position 64.".

This script parses the flow JSON, mutates the Python dict, and re-serialises.
There is no regex applied to JSON content.

What it does
------------
1. Mira action data — swap `nexusrcm-dev.crm.dynamics.com` → `rcm.crm.dynamics.com`.
2. PMO CFR Intake to Project conversion flow JSON:
   - Swap the three DEV P4W GUIDs (calendar, work-hours template, org unit)
     for their PROD equivalents — raw string replace inside the JSON.
   - Drop the three parameter keys the PROD connector schema doesn't accept:
       item/msdyn_schedulemode
       item/msdyn_copy_teammembers_options
       item/pmo_convertedproject@odata.bind
3. customizations.xml — strip msdyn_project LocalizedNames /
   LocalizedCollectionNames / Descriptions because PROD's P4W version has
   IsRenameable=0 and rejects them.

Usage
-----
    python scripts/patch-managed-solution-for-prod.py <src.zip> <dst.zip>

Example (from a PowerShell prompt):
    pac auth select --index 1
    pac solution export --name CFRProjectManagement `
        --path "$env:TEMP\CFRManaged.zip" --managed
    python scripts/patch-managed-solution-for-prod.py `
        "$env:TEMP\CFRManaged.zip" "$env:TEMP\CFRPatched.zip"
    pac auth select --name "Nexus-PROD"
    pac solution import --path "$env:TEMP\CFRPatched.zip" --async --activate-plugins
    pac solution publish

Editing
-------
GUID_MAP and DROP_KEYS are the only knobs. Update GUID_MAP when DEV or PROD
P4W reference data changes; update DROP_KEYS only if the PROD Dataverse
connector schema accepts/rejects different fields.
"""
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

GUID_MAP = {
    "75f05144-1cb0-f011-bbd3-6045bdeb6f62": "6138f6d6-f570-ef11-a670-0022482c38a9",  # calendar
    "71f05144-1cb0-f011-bbd3-6045bdeb6f62": "6038f6d6-f570-ef11-a670-0022482c38a9",  # work hours template
    "67f05144-1cb0-f011-bbd3-6045bdeb6f62": "5638f6d6-f570-ef11-a670-0022482c38a9",  # org unit
}

DROP_KEYS = {
    "item/msdyn_schedulemode",
    "item/msdyn_copy_teammembers_options",
    "item/pmo_convertedproject@odata.bind",
}


def patch_flow(content_bytes: bytes) -> bytes:
    """Patch a Power Automate flow JSON: swap GUIDs, drop unsupported fields."""
    text = content_bytes.decode("utf-8")
    for old, new in GUID_MAP.items():
        text = text.replace(old, new)
    obj = json.loads(text)

    def walk(node):
        if isinstance(node, dict):
            inputs = node.get("inputs")
            if isinstance(inputs, dict):
                params = inputs.get("parameters")
                if isinstance(params, dict):
                    for k in list(params.keys()):
                        if k in DROP_KEYS:
                            del params[k]
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(obj)
    return json.dumps(obj, indent=2).encode("utf-8")


def patch_mira_data(content_bytes: bytes) -> bytes:
    text = content_bytes.decode("utf-8")
    text = text.replace(
        "https://nexusrcm-dev.crm.dynamics.com/",
        "https://rcm.crm.dynamics.com/",
    )
    return text.encode("utf-8")


def strip_msdyn_project_localizednames(content_bytes: bytes) -> bytes:
    """Remove <LocalizedNames>, <LocalizedCollectionNames>, <Descriptions> from
    the msdyn_project entity block so PROD's P4W (IsRenameable=0) accepts it."""
    text = content_bytes.decode("utf-8")
    pattern = re.compile(
        r'(<entity Name="msdyn_project">)\s*'
        r'(<LocalizedNames>.*?</LocalizedNames>)?\s*'
        r'(<LocalizedCollectionNames>.*?</LocalizedCollectionNames>)?\s*'
        r'(<Descriptions>.*?</Descriptions>)?\s*'
        r'(<attributes>)',
        re.DOTALL,
    )
    text = pattern.sub(r'\1\5', text)
    return text.encode("utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        print(f"\nusage: {argv[0]} <src-managed.zip> <dst-patched.zip>", file=sys.stderr)
        return 2

    src = Path(argv[1])
    dst = Path(argv[2])
    if not src.is_file():
        print(f"error: source zip not found: {src}", file=sys.stderr)
        return 1
    if dst.exists():
        dst.unlink()
    shutil.copy(src, dst)

    with zipfile.ZipFile(dst, "r") as zin:
        entries = {e.filename: zin.read(e.filename) for e in zin.infolist()}

    flow_keys = [
        k for k in entries
        if "Workflows/" in k
        and k.lower().endswith(".json")
        and "intaketoproject" in k.lower()
    ]
    mira_keys = [k for k in entries if k == "botcomponents/pmo_mira.action.CreateIntakeRecord/data"]
    cust_keys = [k for k in entries if k == "customizations.xml"]

    for k in flow_keys:
        entries[k] = patch_flow(entries[k])
        print(f"  patched flow: {k}")
    for k in mira_keys:
        entries[k] = patch_mira_data(entries[k])
        print(f"  patched mira data: {k}")
    for k in cust_keys:
        entries[k] = strip_msdyn_project_localizednames(entries[k])
        print(f"  stripped msdyn_project LocalizedNames in {k}")

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries.items():
            zout.writestr(name, data)

    print(f"OK wrote {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
