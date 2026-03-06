@echo off
echo ================================================================
echo UPGRADE ODOO KPI SALES TRIGGER
echo ================================================================
echo.
echo Module  : odoo_kpi_sales_trigger
echo Database: kanjabung_MRP
echo Port    : 8070
echo.
pause

echo.
echo [1/2] Upgrading module...
c:\odoo14c\python\python.exe C:\odoo14c\server\odoo-bin -c C:\addon14\odoo.conf -d kanjabung_MRP -u odoo_kpi_sales_trigger --stop-after-init
if errorlevel 1 (
    echo.
    echo Upgrade gagal.
    pause
    exit /b 1
)

echo.
echo [2/2] Selesai.
echo Buka Odoo di http://localhost:8070 lalu cek menu Sales ^> KPI Sales Triggers
echo.
pause
