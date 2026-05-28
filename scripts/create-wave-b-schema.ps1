# Wave B Schema Deployment — Creates pmo_projecttemplate and pmo_documentlink tables in Dataverse DEV
# Run this script in your own terminal (not the agent shell) so pac auth tokens are available.
#
# Usage: .\scripts\create-wave-b-schema.ps1

$ErrorActionPreference = 'Stop'

$orgUrl = 'https://nexusrcm-dev.crm.dynamics.com'
$solutionName = 'CFRProjectManagement'

# ─── Get token from pac auth ─────────────────────────────────────────────────
Write-Host "`n[1/6] Acquiring token via pac auth..." -ForegroundColor Cyan

# pac doesn't expose token directly — use client credentials flow
$clientId = Read-Host "Enter Service Principal Client ID (cc57f611-be88-4856-9d60-6ee9da06a32b)"
if (-not $clientId) { $clientId = 'cc57f611-be88-4856-9d60-6ee9da06a32b' }

$clientSecret = Read-Host "Enter Client Secret" -AsSecureString
$plainSecret = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientSecret)
)

$tenantId = 'fabb61b8-3afe-4e75-b934-a47f782b8cd7'

$tokenBody = @{
    client_id     = $clientId
    scope         = "$orgUrl/.default"
    grant_type    = 'client_credentials'
    client_secret = $plainSecret
}

$tokenResponse = Invoke-RestMethod -Method Post `
    -Uri "https://login.microsoftonline.com/$tenantId/oauth2/v2.0/token" `
    -Body $tokenBody

$token = $tokenResponse.access_token
Write-Host "  Token acquired." -ForegroundColor Green

$headers = @{
    'Authorization'          = "Bearer $token"
    'Content-Type'           = 'application/json'
    'OData-MaxVersion'       = '4.0'
    'OData-Version'          = '4.0'
    'MSCRM.SolutionUniqueName' = $solutionName
}

$apiBase = "$orgUrl/api/data/v9.2"

# ─── Helper: Create table ────────────────────────────────────────────────────
function New-DataverseTable {
    param([string]$Body, [string]$DisplayName)
    Write-Host "  Creating table: $DisplayName..." -NoNewline
    $response = Invoke-RestMethod -Method Post -Uri "$apiBase/EntityDefinitions" `
        -Headers $headers -Body $Body
    Write-Host " OK" -ForegroundColor Green
    return $response
}

# ─── Helper: Create column ───────────────────────────────────────────────────
function New-DataverseColumn {
    param([string]$TableLogicalName, [string]$Body, [string]$ColumnName)
    Write-Host "  Creating column: $TableLogicalName.$ColumnName..." -NoNewline
    Invoke-RestMethod -Method Post `
        -Uri "$apiBase/EntityDefinitions(LogicalName='$TableLogicalName')/Attributes" `
        -Headers $headers -Body $Body | Out-Null
    Write-Host " OK" -ForegroundColor Green
}

# ─── Helper: Create 1:N relationship ─────────────────────────────────────────
function New-DataverseRelationship {
    param([string]$Body, [string]$Name)
    Write-Host "  Creating relationship: $Name..." -NoNewline
    Invoke-RestMethod -Method Post `
        -Uri "$apiBase/RelationshipDefinitions" `
        -Headers $headers -Body $Body | Out-Null
    Write-Host " OK" -ForegroundColor Green
}

# ─── Table 1: pmo_projecttemplate ─────────────────────────────────────────────
Write-Host "`n[2/6] Creating pmo_projecttemplate table..." -ForegroundColor Cyan

$templateTableBody = @{
    '@odata.type' = '#Microsoft.Dynamics.CRM.EntityMetadata'
    SchemaName = 'pmo_ProjectTemplate'
    DisplayName = @{
        LocalizedLabels = @(@{ Label = 'Project Template'; LanguageCode = 1033 })
    }
    DisplayCollectionName = @{
        LocalizedLabels = @(@{ Label = 'Project Templates'; LanguageCode = 1033 })
    }
    Description = @{
        LocalizedLabels = @(@{ Label = 'Project template definitions with WBS task payloads'; LanguageCode = 1033 })
    }
    OwnershipType = 'OrganizationOwned'
    IsActivity = $false
    HasNotes = $false
    HasActivities = $false
    Attributes = @(
        @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.StringAttributeMetadata'
            SchemaName = 'pmo_Name'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'Name'; LanguageCode = 1033 }) }
            IsPrimaryName = $true
            RequiredLevel = @{ Value = 'ApplicationRequired' }
            MaxLength = 200
        }
    )
} | ConvertTo-Json -Depth 10

New-DataverseTable -Body $templateTableBody -DisplayName 'Project Template'

# Add columns to pmo_projecttemplate
$templateColumns = @(
    @{
        name = 'pmo_Description'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.MemoAttributeMetadata'
            SchemaName = 'pmo_Description'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'Description'; LanguageCode = 1033 }) }
            RequiredLevel = @{ Value = 'None' }
            MaxLength = 10000
        }
    },
    @{
        name = 'pmo_CfrCategory'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.PicklistAttributeMetadata'
            SchemaName = 'pmo_CfrCategory'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'CFR Category'; LanguageCode = 1033 }) }
            RequiredLevel = @{ Value = 'None' }
            OptionSet = @{
                '@odata.type' = '#Microsoft.Dynamics.CRM.OptionSetMetadata'
                IsGlobal = $false
                OptionSetType = 'Picklist'
                Options = @(
                    @{ Value = 893460050; Label = @{ LocalizedLabels = @(@{ Label = 'IT Infrastructure'; LanguageCode = 1033 }) } }
                    @{ Value = 893460051; Label = @{ LocalizedLabels = @(@{ Label = 'Finance Systems'; LanguageCode = 1033 }) } }
                    @{ Value = 893460052; Label = @{ LocalizedLabels = @(@{ Label = 'Compliance'; LanguageCode = 1033 }) } }
                    @{ Value = 893460053; Label = @{ LocalizedLabels = @(@{ Label = 'Data & Analytics'; LanguageCode = 1033 }) } }
                    @{ Value = 893460054; Label = @{ LocalizedLabels = @(@{ Label = 'Operations'; LanguageCode = 1033 }) } }
                    @{ Value = 893460055; Label = @{ LocalizedLabels = @(@{ Label = 'Other'; LanguageCode = 1033 }) } }
                )
            }
        }
    },
    @{
        name = 'pmo_TaskPayload'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.MemoAttributeMetadata'
            SchemaName = 'pmo_TaskPayload'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'Task Payload'; LanguageCode = 1033 }) }
            Description = @{ LocalizedLabels = @(@{ Label = 'JSON array of TemplateTask objects'; LanguageCode = 1033 }) }
            RequiredLevel = @{ Value = 'ApplicationRequired' }
            MaxLength = 100000
        }
    },
    @{
        name = 'pmo_IsSystemDefault'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.BooleanAttributeMetadata'
            SchemaName = 'pmo_IsSystemDefault'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'Is System Default'; LanguageCode = 1033 }) }
            RequiredLevel = @{ Value = 'None' }
            OptionSet = @{
                '@odata.type' = '#Microsoft.Dynamics.CRM.BooleanOptionSetMetadata'
                TrueOption = @{ Value = 1; Label = @{ LocalizedLabels = @(@{ Label = 'Yes'; LanguageCode = 1033 }) } }
                FalseOption = @{ Value = 0; Label = @{ LocalizedLabels = @(@{ Label = 'No'; LanguageCode = 1033 }) } }
            }
        }
    }
)

foreach ($col in $templateColumns) {
    New-DataverseColumn -TableLogicalName 'pmo_projecttemplate' `
        -Body ($col.body | ConvertTo-Json -Depth 10) `
        -ColumnName $col.name
}

# ─── Table 2: pmo_documentlink ────────────────────────────────────────────────
Write-Host "`n[3/6] Creating pmo_documentlink table..." -ForegroundColor Cyan

$docLinkTableBody = @{
    '@odata.type' = '#Microsoft.Dynamics.CRM.EntityMetadata'
    SchemaName = 'pmo_DocumentLink'
    DisplayName = @{
        LocalizedLabels = @(@{ Label = 'Document Link'; LanguageCode = 1033 })
    }
    DisplayCollectionName = @{
        LocalizedLabels = @(@{ Label = 'Document Links'; LanguageCode = 1033 })
    }
    Description = @{
        LocalizedLabels = @(@{ Label = 'Project/program document metadata linked to SharePoint'; LanguageCode = 1033 })
    }
    OwnershipType = 'OrganizationOwned'
    IsActivity = $false
    HasNotes = $false
    HasActivities = $false
    Attributes = @(
        @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.StringAttributeMetadata'
            SchemaName = 'pmo_Name'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'Name'; LanguageCode = 1033 }) }
            IsPrimaryName = $true
            RequiredLevel = @{ Value = 'ApplicationRequired' }
            MaxLength = 200
        }
    )
} | ConvertTo-Json -Depth 10

New-DataverseTable -Body $docLinkTableBody -DisplayName 'Document Link'

# Add columns to pmo_documentlink
$docLinkColumns = @(
    @{
        name = 'pmo_SharePointUrl'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.StringAttributeMetadata'
            SchemaName = 'pmo_SharePointUrl'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'SharePoint URL'; LanguageCode = 1033 }) }
            RequiredLevel = @{ Value = 'ApplicationRequired' }
            MaxLength = 2000
        }
    },
    @{
        name = 'pmo_Category'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.PicklistAttributeMetadata'
            SchemaName = 'pmo_Category'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'Category'; LanguageCode = 1033 }) }
            RequiredLevel = @{ Value = 'None' }
            OptionSet = @{
                '@odata.type' = '#Microsoft.Dynamics.CRM.OptionSetMetadata'
                IsGlobal = $false
                OptionSetType = 'Picklist'
                Options = @(
                    @{ Value = 893460080; Label = @{ LocalizedLabels = @(@{ Label = 'Charter'; LanguageCode = 1033 }) } }
                    @{ Value = 893460081; Label = @{ LocalizedLabels = @(@{ Label = 'SOW'; LanguageCode = 1033 }) } }
                    @{ Value = 893460082; Label = @{ LocalizedLabels = @(@{ Label = 'Budget'; LanguageCode = 1033 }) } }
                    @{ Value = 893460083; Label = @{ LocalizedLabels = @(@{ Label = 'Status Report'; LanguageCode = 1033 }) } }
                    @{ Value = 893460084; Label = @{ LocalizedLabels = @(@{ Label = 'Meeting Notes'; LanguageCode = 1033 }) } }
                    @{ Value = 893460085; Label = @{ LocalizedLabels = @(@{ Label = 'Other'; LanguageCode = 1033 }) } }
                )
            }
        }
    },
    @{
        name = 'pmo_Description'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.MemoAttributeMetadata'
            SchemaName = 'pmo_Description'
            DisplayName = @{ LocalizedLabels = @(@{ Label = 'Description'; LanguageCode = 1033 }) }
            RequiredLevel = @{ Value = 'None' }
            MaxLength = 10000
        }
    }
)

foreach ($col in $docLinkColumns) {
    New-DataverseColumn -TableLogicalName 'pmo_documentlink' `
        -Body ($col.body | ConvertTo-Json -Depth 10) `
        -ColumnName $col.name
}

# ─── Lookup relationships ────────────────────────────────────────────────────
Write-Host "`n[4/6] Creating lookup relationships..." -ForegroundColor Cyan

$relationships = @(
    @{
        name = 'pmo_msdyn_project_documentlink_Project'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata'
            SchemaName = 'pmo_msdyn_project_documentlink_Project'
            ReferencedEntity = 'msdyn_project'
            ReferencingEntity = 'pmo_documentlink'
            Lookup = @{
                '@odata.type' = '#Microsoft.Dynamics.CRM.LookupAttributeMetadata'
                SchemaName = 'pmo_Project'
                DisplayName = @{ LocalizedLabels = @(@{ Label = 'Project'; LanguageCode = 1033 }) }
                RequiredLevel = @{ Value = 'None' }
            }
        }
    },
    @{
        name = 'pmo_msdyn_projectprogram_documentlink_Program'
        body = @{
            '@odata.type' = '#Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata'
            SchemaName = 'pmo_msdyn_projectprogram_documentlink_Program'
            ReferencedEntity = 'msdyn_projectprogram'
            ReferencingEntity = 'pmo_documentlink'
            Lookup = @{
                '@odata.type' = '#Microsoft.Dynamics.CRM.LookupAttributeMetadata'
                SchemaName = 'pmo_Program'
                DisplayName = @{ LocalizedLabels = @(@{ Label = 'Program'; LanguageCode = 1033 }) }
                RequiredLevel = @{ Value = 'None' }
            }
        }
    }
)

foreach ($rel in $relationships) {
    New-DataverseRelationship -Body ($rel.body | ConvertTo-Json -Depth 10) -Name $rel.name
}

# ─── Publish customizations ──────────────────────────────────────────────────
Write-Host "`n[5/6] Publishing customizations..." -ForegroundColor Cyan
Invoke-RestMethod -Method Post -Uri "$apiBase/PublishAllXml" -Headers $headers -Body '{}' | Out-Null
Write-Host "  Published." -ForegroundColor Green

# ─── Verify ──────────────────────────────────────────────────────────────────
Write-Host "`n[6/6] Verifying tables exist..." -ForegroundColor Cyan

$verifyHeaders = @{
    'Authorization' = "Bearer $token"
    'OData-MaxVersion' = '4.0'
    'OData-Version' = '4.0'
}

try {
    $tmpl = Invoke-RestMethod -Uri "$apiBase/EntityDefinitions(LogicalName='pmo_projecttemplate')?`$select=LogicalName,DisplayName" -Headers $verifyHeaders
    Write-Host "  pmo_projecttemplate: EXISTS" -ForegroundColor Green
} catch {
    Write-Host "  pmo_projecttemplate: MISSING" -ForegroundColor Red
}

try {
    $doc = Invoke-RestMethod -Uri "$apiBase/EntityDefinitions(LogicalName='pmo_documentlink')?`$select=LogicalName,DisplayName" -Headers $verifyHeaders
    Write-Host "  pmo_documentlink: EXISTS" -ForegroundColor Green
} catch {
    Write-Host "  pmo_documentlink: MISSING" -ForegroundColor Red
}

Write-Host "`nWave B schema deployment complete." -ForegroundColor Green
Write-Host "Both tables are registered in the $solutionName solution via MSCRM.SolutionUniqueName header." -ForegroundColor Gray
