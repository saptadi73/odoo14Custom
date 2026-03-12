# Test script untuk verify SILO equipment OEE records setelah deployment
# Jalankan: .\test_silo_oee_after_deployment.ps1

$base = 'https://kanjabung.web.id'
$db = 'kanjabung_MRP'
$login = 'admin'
$password = 'admin'

Write-Host "=== SILO OEE Equipment Verification Test ===" -ForegroundColor Cyan
Write-Host "Server: $base" -ForegroundColor Gray
Write-Host "Database: $db" -ForegroundColor Gray
Write-Host ""

# Authenticate
Write-Host "[1/3] Authenticating..." -ForegroundColor Yellow
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$authBody = @{
    jsonrpc = '2.0'
    method = 'call'
    params = @{
        db = $db
        login = $login
        password = $password
    }
} | ConvertTo-Json -Depth 6

try {
    $authResp = Invoke-RestMethod -Uri "$base/web/session/authenticate" `
        -Method Post `
        -ContentType 'application/json' `
        -Body $authBody `
        -WebSession $session `
        -TimeoutSec 60
    Write-Host "✓ Authentication successful (UID: $($authResp.result.uid))" -ForegroundColor Green
} catch {
    Write-Host "✗ Authentication failed: $_" -ForegroundColor Red
    exit 1
}

# Test OEE equipment avg endpoint with date range
Write-Host "[2/3] Fetching OEE equipment data (24/02/2026 - 13/03/2026)..." -ForegroundColor Yellow
$payload = @{
    jsonrpc = '2.0'
    method = 'call'
    params = @{
        date_from = '2026-02-24'
        date_to = '2026-03-13'
        limit = 100
        offset = 0
    }
} | ConvertTo-Json -Depth 8

try {
    $response = Invoke-RestMethod -Uri "$base/api/scada/oee-equipment-avg" `
        -Method Post `
        -ContentType 'application/json' `
        -Body $payload `
        -WebSession $session `
        -TimeoutSec 60
    
    Write-Host "✓ API call successful" -ForegroundColor Green
    Write-Host ""
    
    # Show summary
    $total = $response.result.count
    $equipWithData = @($response.result.data | Where-Object { $_.oee_records_count -gt 0 })
    
    Write-Host "=== RESULTS ===" -ForegroundColor Cyan
    Write-Host "Total Equipment: $total"
    Write-Host "Equipment with OEE records: $($equipWithData.Count)"
    Write-Host ""
    
    # Show equipment with OEE records
    Write-Host "Equipment with OEE Data:" -ForegroundColor Yellow
    $equipWithData | ForEach-Object {
        $name = $_.equipment.name
        $code = $_.equipment.code
        $count = $_.oee_records_count
        $yield = [math]::Round($_.avg_summary.yield_percent, 2)
        Write-Host "  • $name ($code)" -ForegroundColor Cyan
        Write-Host "    - OEE Records: $count" -ForegroundColor Gray
        Write-Host "    - Avg Yield: $yield%" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "=== VERIFICATION ===" -ForegroundColor Cyan
    
    # Check if SILO equipment have records
    $siloEquip = @($equipWithData | Where-Object { $_.equipment.code -match 'silo' })
    $lqEquip = @($equipWithData | Where-Object { $_.equipment.code -match 'lq' })
    $plcEquip = @($equipWithData | Where-Object { $_.equipment.code -match 'plc' })
    
    Write-Host "SILO equipment with data: $($siloEquip.Count)" -ForegroundColor $(if($siloEquip.Count -gt 0) { 'Green' } else { 'Yellow' })
    Write-Host "LQ equipment with data: $($lqEquip.Count)" -ForegroundColor $(if($lqEquip.Count -gt 0) { 'Green' } else { 'Yellow' })
    Write-Host "PLC equipment with data: $($plcEquip.Count)" -ForegroundColor $(if($plcEquip.Count -gt 0) { 'Green' } else { 'Yellow' })
    
    if ($siloEquip.Count -gt 0) {
        Write-Host ""
        Write-Host "✓ SUCCESS: SILO equipment sekarang muncul dengan OEE records!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠ WARNING: SILO equipment masih belum ada OEE records" -ForegroundColor Yellow
        Write-Host "  Kemungkinan: deployment maybe belum selesai atau code belum di-reload" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "✗ API call failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/3] Test completed" -ForegroundColor Yellow
