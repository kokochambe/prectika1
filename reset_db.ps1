# Скрипт для полной очистки миграций и базы данных
# Запустите этот файл в PowerShell: .\reset_db.ps1

Write-Host "Удаление файла базы данных..." -ForegroundColor Yellow
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "db.sqlite3 удален" -ForegroundColor Green
} else {
    Write-Host "db.sqlite3 не найден" -ForegroundColor Gray
}

Write-Host "`nУдаление файлов миграций (кроме __init__.py)..." -ForegroundColor Yellow

$apps = @("accounts", "equipment", "inventory", "workorders")

foreach ($app in $apps) {
    $migrationPath = Join-Path $app "migrations"
    if (Test-Path $migrationPath) {
        Get-ChildItem -Path $migrationPath -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
        Write-Host "Миграции в $app очищены" -ForegroundColor Green
    } else {
        Write-Host "Папка миграций $app не найдена" -ForegroundColor Gray
    }
}

Write-Host "`nСоздание новых миграций..." -ForegroundColor Yellow
python manage.py makemigrations

Write-Host "`nПрименение миграций..." -ForegroundColor Yellow
python manage.py migrate --run-syncdb

Write-Host "`nСоздание суперпользователя admin_otir..." -ForegroundColor Yellow
$env:DJANGO_SUPERUSER_USERNAME = "admin_otir"
$env:DJANGO_SUPERUSER_EMAIL = "admin@example.com"
$env:DJANGO_SUPERUSER_PASSWORD = "admin"
python manage.py createsuperuser --noinput --username admin_otir --email admin@example.com 2>$null

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ВСЕ ГОТОВО!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Логин: admin_otir" -ForegroundColor White
Write-Host "Пароль: admin" -ForegroundColor White
Write-Host "URL: http://localhost:8000/" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nЗапуск сервера..." -ForegroundColor Yellow
python manage.py runserver
