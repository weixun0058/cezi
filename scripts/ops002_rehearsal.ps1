[CmdletBinding()]
param(
    [string]$CurrentImage = "zhugeshensuan:local",
    [string]$RollbackImage = "zhugeshensuan:final-audit"
)

$ErrorActionPreference = "Stop"

function Invoke-Docker {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $output = & docker @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "docker $($Arguments -join ' ') failed:`n$($output -join [Environment]::NewLine)"
    }
    return $output
}

function Assert-IsolatedName {
    param([Parameter(Mandatory = $true)][string]$Name)

    if (-not $Name.StartsWith("zhugeshensuan-ops002-", [StringComparison]::Ordinal)) {
        throw "Refusing to operate on non-OPS002 resource: $Name"
    }
    if ($Name -eq "zhugeshensuan_runtime-data") {
        throw "Refusing to operate on the production runtime volume."
    }
}

function Wait-Ready {
    param(
        [Parameter(Mandatory = $true)][string]$ContainerName,
        [Parameter(Mandatory = $true)][int]$Port
    )

    for ($attempt = 1; $attempt -le 60; $attempt++) {
        $body = & curl.exe --silent --show-error --fail "http://127.0.0.1:$Port/readyz" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return ($body -join "")
        }
        Start-Sleep -Milliseconds 500
    }

    $logs = Invoke-Docker -Arguments @("logs", "--tail", "100", $ContainerName)
    throw "Container $ContainerName did not become ready:`n$($logs -join [Environment]::NewLine)"
}

function Start-IsolatedApp {
    param(
        [Parameter(Mandatory = $true)][string]$ContainerName,
        [Parameter(Mandatory = $true)][string]$Image,
        [Parameter(Mandatory = $true)][string]$Volume
    )

    Assert-IsolatedName $ContainerName
    Assert-IsolatedName $Volume

    Invoke-Docker -Arguments @(
        "run", "-d",
        "--name", $ContainerName,
        "--read-only",
        "--tmpfs", "/tmp:size=64m,mode=1777",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges:true",
        "--mount", "type=volume,src=$Volume,dst=/app/instance",
        "-p", "127.0.0.1::8000",
        "-e", "APP_ENV=production",
        "-e", "APP_DEBUG=false",
        "-e", "APP_PORT=8000",
        "-e", "SITE_BASE_URL=https://ops002.invalid",
        "-e", "CONTACT_EMAIL=ops002@getwiseoracle.com",
        "-e", "SECRET_KEY=ops002-rehearsal-secret-key-000000000000",
        "-e", "AI_API_KEY=ops002-dummy-key",
        "-e", "AI_BASE_URL=http://127.0.0.1:9",
        "-e", "AI_GLOBAL_DAILY_LIMIT=100",
        $Image
    ) | Out-Null

    $binding = ((Invoke-Docker -Arguments @("port", $ContainerName, "8000/tcp")) -join "").Trim()
    $port = [int]($binding.Split(":")[-1])
    $body = Wait-Ready -ContainerName $ContainerName -Port $port
    return [PSCustomObject]@{ container = $ContainerName; image = $Image; port = $port; readyz = $body }
}

function Remove-IsolatedContainer {
    param([Parameter(Mandatory = $true)][string]$Name)

    Assert-IsolatedName $Name
    & docker rm -f $Name 2>$null | Out-Null
}

function Remove-IsolatedVolume {
    param([Parameter(Mandatory = $true)][string]$Name)

    Assert-IsolatedName $Name
    & docker volume rm $Name 2>$null | Out-Null
}

Invoke-Docker -Arguments @("version", "--format", "{{.Server.Version}}") | Out-Null
$currentImageId = ((Invoke-Docker -Arguments @("image", "inspect", $CurrentImage, "--format", "{{.Id}}")) -join "").Trim()
$rollbackImageId = ((Invoke-Docker -Arguments @("image", "inspect", $RollbackImage, "--format", "{{.Id}}")) -join "").Trim()
if ($currentImageId -eq $rollbackImageId) {
    throw "CurrentImage and RollbackImage resolve to the same immutable image ID."
}

$productionVolumeName = "zhugeshensuan_runtime-data"
$productionVolumeBefore = (& docker volume inspect $productionVolumeName --format "{{.Name}}|{{.CreatedAt}}|{{.Mountpoint}}" 2>$null) -join ""

$stamp = Get-Date -Format "yyyyMMddHHmmss"
$sourceVolume = "zhugeshensuan-ops002-source-$stamp"
$restoredVolume = "zhugeshensuan-ops002-restored-$stamp"
$currentContainer = "zhugeshensuan-ops002-current-$stamp"
$rollbackContainer = "zhugeshensuan-ops002-rollback-$stamp"
$helperContainer = "zhugeshensuan-ops002-helper-$stamp"
$backupDir = Join-Path ([System.IO.Path]::GetTempPath()) "zhugeshensuan-ops002-$stamp"
$backupFile = Join-Path $backupDir "runtime.db"

@($sourceVolume, $restoredVolume, $currentContainer, $rollbackContainer, $helperContainer) |
    ForEach-Object { Assert-IsolatedName $_ }
[System.IO.Directory]::CreateDirectory($backupDir) | Out-Null

try {
    Invoke-Docker -Arguments @("volume", "create", $sourceVolume) | Out-Null
    Invoke-Docker -Arguments @("volume", "create", $restoredVolume) | Out-Null

    $currentResult = Start-IsolatedApp -ContainerName $currentContainer -Image $CurrentImage -Volume $sourceVolume
    $seedCode = @"
import sqlite3
db = sqlite3.connect('/app/instance/runtime.db')
db.execute('CREATE TABLE IF NOT EXISTS ops002_rehearsal (marker TEXT PRIMARY KEY)')
db.execute('INSERT OR REPLACE INTO ops002_rehearsal(marker) VALUES (?)', ('present-in-backup',))
db.commit()
db.close()
"@
    Invoke-Docker -Arguments @("exec", $currentContainer, "python", "-c", $seedCode) | Out-Null
    Invoke-Docker -Arguments @("stop", "--time", "35", $currentContainer) | Out-Null

    Invoke-Docker -Arguments @("cp", "${currentContainer}:/app/instance/runtime.db", $backupFile) | Out-Null
    $backupHash = (Get-FileHash -LiteralPath $backupFile -Algorithm SHA256).Hash.ToLowerInvariant()
    $backupSize = (Get-Item -LiteralPath $backupFile).Length

    Invoke-Docker -Arguments @(
        "create", "--name", $helperContainer,
        "--user", "0:0",
        "--mount", "type=volume,src=$restoredVolume,dst=/data",
        "--entrypoint", "sh", $CurrentImage, "-c", "exit 0"
    ) | Out-Null
    Invoke-Docker -Arguments @("cp", $backupFile, "${helperContainer}:/data/runtime.db") | Out-Null
    Invoke-Docker -Arguments @("rm", $helperContainer) | Out-Null

    $checkBackupCode = @"
import os, sqlite3
os.chown('/data/runtime.db', 10001, 10001)
db = sqlite3.connect('file:/data/runtime.db?mode=ro', uri=True)
assert db.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
assert db.execute('SELECT marker FROM ops002_rehearsal').fetchall() == [('present-in-backup',)]
db.close()
print('backup-integrity=ok')
"@
    $backupCheck = Invoke-Docker -Arguments @(
        "run", "--rm", "--name", $helperContainer,
        "--user", "0:0",
        "--mount", "type=volume,src=$restoredVolume,dst=/data",
        "--entrypoint", "python", $CurrentImage, "-c", $checkBackupCode
    )

    $mutateSourceCode = @"
import sqlite3
db = sqlite3.connect('/data/runtime.db')
db.execute('INSERT INTO ops002_rehearsal(marker) VALUES (?)', ('created-after-backup',))
db.commit()
db.close()
"@
    Invoke-Docker -Arguments @(
        "run", "--rm", "--name", $helperContainer,
        "--mount", "type=volume,src=$sourceVolume,dst=/data",
        "--entrypoint", "python", $CurrentImage, "-c", $mutateSourceCode
    ) | Out-Null

    $restoreCode = @"
import sqlite3
db = sqlite3.connect('/data/runtime.db')
assert db.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
assert db.execute('SELECT marker FROM ops002_rehearsal ORDER BY marker').fetchall() == [('present-in-backup',)]
db.close()
print('restore-integrity=ok')
"@
    $restoreCheck = Invoke-Docker -Arguments @(
        "run", "--rm", "--name", $helperContainer,
        "--mount", "type=volume,src=$restoredVolume,dst=/data",
        "--entrypoint", "python", $CurrentImage, "-c", $restoreCode
    )

    $rollbackResult = Start-IsolatedApp -ContainerName $rollbackContainer -Image $RollbackImage -Volume $restoredVolume
    $restoredMarkersCode = @"
import json, sqlite3
db = sqlite3.connect('/app/instance/runtime.db')
print(json.dumps([row[0] for row in db.execute('SELECT marker FROM ops002_rehearsal ORDER BY marker')]))
db.close()
"@
    $restoredMarkers = (Invoke-Docker -Arguments @("exec", $rollbackContainer, "python", "-c", $restoredMarkersCode)) -join ""

    $productionVolumeAfter = (& docker volume inspect $productionVolumeName --format "{{.Name}}|{{.CreatedAt}}|{{.Mountpoint}}" 2>$null) -join ""
    $evidence = [ordered]@{
        rehearsal_started_at = $stamp
        current_image = $CurrentImage
        current_image_id = $currentImageId
        rollback_image = $RollbackImage
        rollback_image_id = $rollbackImageId
        backup_sha256 = $backupHash
        backup_size_bytes = $backupSize
        backup_check = ($backupCheck -join "")
        restore_check = ($restoreCheck -join "")
        restored_markers = ($restoredMarkers | ConvertFrom-Json)
        current_readyz = ($currentResult.readyz | ConvertFrom-Json)
        rollback_readyz = ($rollbackResult.readyz | ConvertFrom-Json)
        production_volume_present_before = [bool]$productionVolumeBefore
        production_volume_identity_unchanged = ($productionVolumeBefore -eq $productionVolumeAfter)
        production_volume_mounted = $false
    }
    $evidence | ConvertTo-Json -Depth 8
}
finally {
    Remove-IsolatedContainer $currentContainer
    Remove-IsolatedContainer $rollbackContainer
    Remove-IsolatedContainer $helperContainer
    Remove-IsolatedVolume $sourceVolume
    Remove-IsolatedVolume $restoredVolume

    if (Test-Path -LiteralPath $backupFile) {
        Remove-Item -LiteralPath $backupFile -Force
    }
    if (Test-Path -LiteralPath $backupDir) {
        Remove-Item -LiteralPath $backupDir -Force
    }
}
