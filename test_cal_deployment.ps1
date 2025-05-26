# PowerShell script to test Cal.com MCP Server deployment
# Usage: .\test_cal_deployment.ps1 <service-url>
# Example: .\test_cal_deployment.ps1 https://cal-com-mcp-xxxx.onrender.com

param(
    [Parameter(Mandatory=$true)]
    [string]$ServiceUrl
)

# Remove trailing slash if present
$ServiceUrl = $ServiceUrl.TrimEnd('/')

Write-Host "🧪 Testing Cal.com MCP Server at: $ServiceUrl" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

# Test 1: Root endpoint
Write-Host "`n1️⃣ Testing root endpoint (/)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$ServiceUrl/" -Method Get
    Write-Host "   Status: 200 OK" -ForegroundColor Green
    Write-Host "   Response:" -ForegroundColor Gray
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
    if ($response.message -like "*Cal.com MCP Server*") {
        Write-Host "   ✅ Root endpoint working correctly!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Unexpected response format" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test 2: Health endpoint
Write-Host "`n2️⃣ Testing health endpoint (/health)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$ServiceUrl/health" -Method Get
    Write-Host "   Status: 200 OK" -ForegroundColor Green
    Write-Host "   Response:" -ForegroundColor Gray
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
    if ($response.status -eq "healthy") {
        Write-Host "   ✅ Health endpoint working correctly!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Service might not be fully healthy" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test 3: MCP endpoint availability
Write-Host "`n3️⃣ Testing MCP endpoint (/mcp) availability..." -ForegroundColor Yellow
try {
    # This will likely fail with 405 or similar, which is expected
    $response = Invoke-WebRequest -Uri "$ServiceUrl/mcp" -Method Get -ErrorAction Stop
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Gray
} catch {
    if ($_.Exception.Response.StatusCode -eq 405) {
        Write-Host "   ✅ MCP endpoint exists (requires POST with proper protocol)" -ForegroundColor Green
    } else {
        Write-Host "   Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Gray
    }
}

# Test 4: Check deployment mode
Write-Host "`n4️⃣ Checking deployment mode..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$ServiceUrl/" -Method Get
    $mode = $response.mode
    
    if ($mode -eq "basic") {
        Write-Host "   ℹ️  Server running in basic mode (MCP fully functional)" -ForegroundColor Cyan
        Write-Host "   ✅ This is the expected mode for successful deployment!" -ForegroundColor Green
    } elseif ($mode -eq "fallback") {
        Write-Host "   ⚠️  Server running in fallback mode (MCP imports failed)" -ForegroundColor Yellow
        Write-Host "   ⚠️  Check deployment logs for MCP installation issues" -ForegroundColor Yellow
    } else {
        Write-Host "   ℹ️  Server mode: $mode" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Error checking mode: $_" -ForegroundColor Red
}

# Test 5: Response time
Write-Host "`n5️⃣ Testing response time..." -ForegroundColor Yellow
try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-RestMethod -Uri "$ServiceUrl/health" -Method Get
    $stopwatch.Stop()
    
    $responseTime = $stopwatch.ElapsedMilliseconds
    Write-Host "   Response time: $responseTime ms" -ForegroundColor Gray
    
    if ($responseTime -lt 500) {
        Write-Host "   ✅ Excellent response time!" -ForegroundColor Green
    } elseif ($responseTime -lt 1000) {
        Write-Host "   ✅ Good response time" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Slow response time (might be cold start)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Summary
Write-Host "`n" ("=" * 60) -ForegroundColor Gray
Write-Host "🏁 Testing complete!" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. If all tests passed, the Cal.com MCP server is ready for use"
Write-Host "2. Save the service URL for bridge_server configuration"
Write-Host "3. The MCP endpoint URL will be: $ServiceUrl/mcp" -ForegroundColor Yellow

Write-Host "`nAdd to bridge_server/.env:" -ForegroundColor Cyan
Write-Host "CAL_COM_MCP_SERVER_URL=$ServiceUrl/mcp" -ForegroundColor White