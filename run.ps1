# Activate virtual environment for Study Planner AI
# Run this script with: .\activate.ps1

$venvPath = "$PSScriptRoot\myenv"

# Set environment variables
$env:VIRTUAL_ENV = $venvPath
$env:PATH = "$venvPath\Scripts;$env:PATH"

# Update prompt to show virtual environment
function global:prompt {
    "(myenv) " + (Get-Location) + "> "
}

Write-Host "Virtual environment 'myenv' activated!" -ForegroundColor Green
Write-Host "Python: $(python --version)" -ForegroundColor Cyan

# Run the Flask app
Write-Host "`nStarting Study Planner AI..." -ForegroundColor Yellow
python "$PSScriptRoot\app.py"
