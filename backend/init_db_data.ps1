# ==========================================
# 仓库系统：强制重置数据库与数据导入脚本
# ==========================================

$DB_FILE = "db.sqlite3"
$MIGRATIONS_DIR = "warehouses\migrations"

$ADMIN_USER = "admin"
$ADMIN_EMAIL = "admin@example.com"
$ADMIN_PASS = "admin123"

Write-Host ">>> Starting Full System Reset..." -ForegroundColor Magenta
Write-Host ">>> This will generate user and fake data" -ForegroundColor Magenta

# 1. 删除旧的数据库文件
if (Test-Path $DB_FILE) {
    Write-Host "Cleaning: Removing $DB_FILE..." -ForegroundColor Yellow
    Remove-Item $DB_FILE
}

# 2. 清理迁移记录文件 (保留 __init__.py)
Write-Host "Cleaning: Removing old migration files in $MIGRATIONS_DIR..." -ForegroundColor Yellow
Get-ChildItem -Path $MIGRATIONS_DIR -Exclude "__init__.py" -File | Remove-Item

# 3. 重新生成迁移文件
Write-Host "`n>>> Generating new migrations..." -ForegroundColor Cyan
python manage.py makemigrations warehouses
if ($LASTEXITCODE -ne 0) { Write-Host "Error during makemigrations!" -ForegroundColor Red; exit }

# 4. 执行数据库同步
Write-Host ">>> Applying migrations (Creating tables)..." -ForegroundColor Cyan
python manage.py migrate
if ($LASTEXITCODE -ne 0) { Write-Host "Error during migrate!" -ForegroundColor Red; exit }

# 5. 导入地理数据
Write-Host "`n>>> Running import_geo.py..." -ForegroundColor Cyan
if (Test-Path "import_geo.py") {
    python import_geo.py
} else {
    Write-Host "Warning: import_geo.py not found, skipping." -ForegroundColor Yellow
}

# 6. 导入模拟种子数据
Write-Host "`n>>> Running seed_data.py..." -ForegroundColor Cyan
if (Test-Path "seed_data.py") {
    # 如果你的脚本改名了，请在这里修改文件名，如 seed_full_wms.py
    python seed_data.py
} else {
    Write-Host "Warning: seed_data.py not found, skipping." -ForegroundColor Yellow
}


Write-Host "`n>>> Creating Superuser ($ADMIN_USER)..." -ForegroundColor Cyan
$env:DJANGO_SUPERUSER_PASSWORD = $ADMIN_PASS
python manage.py createsuperuser --noinput --username $ADMIN_USER --email $ADMIN_EMAIL
$env:DJANGO_SUPERUSER_PASSWORD = ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Superuser created!" -ForegroundColor Green
    Write-Host "Login: $ADMIN_USER / $ADMIN_PASS" -ForegroundColor Green
} else {
    Write-Host "`n[WARNING] Superuser creation skipped (might already exist)." -ForegroundColor Yellow
}


Write-Host "`n==========================================" -ForegroundColor Green
Write-Host " Initialization Successful! Please enjoy!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green