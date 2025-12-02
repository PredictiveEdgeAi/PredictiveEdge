# Complete API test script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NBA Prediction API - Complete Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if teams exist
Write-Host "1. Checking teams in database..." -ForegroundColor Yellow
python -c "
from src.database import get_session, Team, init_database
init_database()
db = get_session()
teams = db.query(Team).all()
print(f'Found {len(teams)} teams in database')
if teams:
    print('Sample teams:')
    for team in teams[:5]:
        print(f'  - {team.team_name} ({team.abbreviation})')
    if len(teams) > 5:
        print(f'  ... and {len(teams) - 5} more')
else:
    print('⚠️  No teams found. Run: python populate_teams.py')
db.close()
"

Write-Host ""

# Step 2: Health check
Write-Host "2. Testing API health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction Stop
    $healthData = $health.Content | ConvertFrom-Json
    Write-Host "   ✅ API is healthy: $($healthData.message)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ API is not running or not accessible" -ForegroundColor Red
    Write-Host "   Make sure the API server is running: python -m api.main" -ForegroundColor Yellow
    exit
}

Write-Host ""

# Step 3: Test prediction
Write-Host "3. Testing prediction endpoint..." -ForegroundColor Yellow

$body = @{
    home_team_name = "Los Angeles Lakers"
    away_team_name = "Golden State Warriors"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/predict" `
      -Method POST `
      -ContentType "application/json" `
      -Body $body `
      -ErrorAction Stop
    
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "   ✅ Prediction successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Game Details:" -ForegroundColor Cyan
    Write-Host "   ──────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "   Home Team: $($result.home_team)" -ForegroundColor White
    Write-Host "   Away Team: $($result.away_team)" -ForegroundColor White
    Write-Host ""
    Write-Host "   Prediction Results:" -ForegroundColor Cyan
    Write-Host "   ──────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "   Predicted Winner: $($result.predicted_winner)" -ForegroundColor Yellow
    Write-Host "   Home Win Probability: $([math]::Round($result.home_win_probability * 100, 1))%" -ForegroundColor Yellow
    Write-Host "   Away Win Probability: $([math]::Round($result.away_win_probability * 100, 1))%" -ForegroundColor Yellow
    Write-Host "   Confidence: $($result.confidence)" -ForegroundColor $(if ($result.confidence -eq "High") { "Green" } elseif ($result.confidence -eq "Medium") { "Yellow" } else { "Red" })
    
    if ($result.value_bet_recommendation) {
        Write-Host ""
        Write-Host "   Betting Recommendation:" -ForegroundColor Cyan
        Write-Host "   ──────────────────────────────────────" -ForegroundColor DarkGray
        Write-Host "   $($result.value_bet_recommendation)" -ForegroundColor $(if ($result.value_bet_recommendation -like "*No Value*") { "Gray" } else { "Green" })
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    
} catch {
    Write-Host "   ❌ Error making prediction" -ForegroundColor Red
    $errorMsg = $_.Exception.Message
    
    # Try to parse error response
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        try {
            $errorData = $responseBody | ConvertFrom-Json
            Write-Host "   Error: $($errorData.detail)" -ForegroundColor Red
        } catch {
            Write-Host "   Error: $responseBody" -ForegroundColor Red
        }
    } else {
        Write-Host "   Error: $errorMsg" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "   1. Make sure API server is running: python -m api.main" -ForegroundColor Yellow
    Write-Host "   2. Check if teams are in database: python populate_teams.py" -ForegroundColor Yellow
    Write-Host "   3. Verify model file exists: model_artifacts/xgboost_nba_model.pkl" -ForegroundColor Yellow
}

