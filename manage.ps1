# ==========================================
# 1. Configuration Area (Modify paths as needed)
# ==========================================

# Conda Installation Path
# Note: Ensure this points to your actual Anaconda/Miniconda folder
$CONDA_ROOT = "D:\Programs\Anaconda" 
$CONDA_ENV_NAME = "py311_django"

# Project Paths
$BACKEND_DIR = "E:\_Codes\Warehouse_Sim23\backend"
$FRONTEND_DIR = "E:\_Codes\Warehouse_Sim23\frontend"

# Launch Commands
$BACKEND_CMD = "python manage.py runserver"
$FRONTEND_CMD = "npm run dev"

# ==========================================
# 2. Functions
# ==========================================

function Start-All {
    Write-Host "--- Starting Backend (Django) ---" -ForegroundColor Cyan
    # Initializes Conda and activates the environment before running the server
    $backend_script = @"
        & '$CONDA_ROOT\shell\condabin\conda-hook.ps1'
        conda activate $CONDA_ENV_NAME
        cd '$BACKEND_DIR'
        $BACKEND_CMD
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backend_script

    Write-Host "--- Starting Frontend (NPM) ---" -ForegroundColor Cyan
    $frontend_script = "cd '$FRONTEND_DIR'; $FRONTEND_CMD"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontend_script

    Write-Host "Services have been started in separate windows." -ForegroundColor Green
}

function Stop-All {
    Write-Host "--- Stopping all related processes ---" -ForegroundColor Yellow
    # Stop Python processes (Django)
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    # Stop Node processes (NPM)
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "Backend and Frontend processes have been terminated." -ForegroundColor Green
}

# ==========================================
# 3. Execution Entry Point
# ==========================================

Write-Host "=============================="
Write-Host "   Project Service Manager"
Write-Host "=============================="
Write-Host "1. Start Services"
Write-Host "2. Stop Services"
Write-Host "3. Restart Services"
$choice = Read-Host "Select an option [1/2/3]"

switch ($choice) {
    "1" { Start-All }
    "2" { Stop-All }
    "3" { Stop-All; Start-Sleep -Seconds 2; Start-All }
    Default { Write-Host "Invalid selection" -ForegroundColor Red }
}