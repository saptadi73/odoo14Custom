@echo off
echo ================================================================
echo RESTART ODOO WITH MODULE UPGRADE
echo ================================================================
echo.
echo Langkah yang akan dilakukan:
echo 1. Kill semua proses Odoo yang berjalan
echo 2. Start Odoo dengan upgrade module grt_scada
echo.
pause

echo.
echo [1/2] Stopping Odoo processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Odoo*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *odoo-bin*" 2>nul
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting Odoo with module upgrade...
echo.
cd C:\odoo14c\server
start "Odoo Server" c:\odoo14c\python\python.exe odoo-bin -c C:\addon14\odoo.conf -d manukanjabung -u grt_scada --without-demo=all

echo.
echo ================================================================
echo Odoo sedang starting dengan upgrade module grt_scada...
echo Tunggu sekitar 30-60 detik hingga Odoo fully loaded
echo ================================================================
echo.
echo Setelah selesai, test endpoint dengan:
echo     python test_mo_consumption_api.py
echo.
pause
