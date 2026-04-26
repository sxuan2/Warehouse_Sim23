# ==========================================
# 1. 配置区域 (请根据你的电脑实际路径修改)
# ==========================================

# Conda 安装路径 (可以通过在CMD输入 where conda 找到)
# 注意：路径末尾要指向 shell.powershell 所在的文件夹
$CONDA_ROOT = "D:\anaconda" # 请修改为你的实际安装目录
$CONDA_ENV_NAME = "py310"

# 项目路径
$BACKEND_DIR = "F:\_Code\Warehouse_Sim23\backend"
$FRONTEND_DIR = "F:\_Code\Warehouse_Sim23\frontend" # 请确认前端文件夹名

# 启动命令
$BACKEND_CMD = "python manage.py runserver"
$FRONTEND_CMD = "npm run dev"

# ==========================================
# 2. 功能函数
# ==========================================

function Start-All {
    Write-Host "--- 正在启动后端 (Django) ---" -ForegroundColor Cyan
    # 使用 Conda 的完整路径初始化并启动，确保环境能正确激活
    $backend_script = @"
        & '$CONDA_ROOT\shell\condabin\conda-hook.ps1'
        conda activate $CONDA_ENV_NAME
        cd '$BACKEND_DIR'
        $BACKEND_CMD
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backend_script

    Write-Host "--- 正在启动前端 (NPM) ---" -ForegroundColor Cyan
    $frontend_script = "cd '$FRONTEND_DIR'; $FRONTEND_CMD"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontend_script

    Write-Host "服务已在独立窗口中启动。" -ForegroundColor Green
}

function Stop-All {
    Write-Host "--- 正在停止所有相关进程 ---" -ForegroundColor Yellow
    # 停止 Python 进程 (Django)
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    # 停止 Node 进程 (NPM)
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "后端和前端进程已关闭。" -ForegroundColor Green
}

# ==========================================
# 3. 执行入口
# ==========================================

Write-Host "=============================="
Write-Host "   项目服务管理器 (Win)"
Write-Host "=============================="
Write-Host "1. 启动服务"
Write-Host "2. 关闭服务"
Write-Host "3. 重启服务"
$choice = Read-Host "请选择操作 [1/2/3]"

switch ($choice) {
    "1" { Start-All }
    "2" { Stop-All }
    "3" { Stop-All; Start-Sleep -Seconds 2; Start-All }
    Default { Write-Host "无效选择" -ForegroundColor Red }
}