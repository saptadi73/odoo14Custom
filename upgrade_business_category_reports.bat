@echo off
echo ================================================================
echo UPGRADE BUSINESS CATEGORY MODULES + REPORTS
echo ================================================================
echo.
echo Database  : kanjabung_MRP
echo Config    : C:\addon14\odoo.conf
echo.
echo Modules yang di-upgrade:
echo   1. grt_crm_business_category
echo   2. grt_sales_business_category
echo   3. grt_purchase_business_category
echo   4. grt_expense_business_category
echo   5. grt_inventory_business_category
echo.
pause

cd /d C:\odoo14c\server
c:\odoo14c\python\python.exe odoo-bin -c C:\addon14\odoo.conf -d kanjabung_MRP -u grt_crm_business_category,grt_sales_business_category,grt_purchase_business_category,grt_expense_business_category,grt_inventory_business_category --without-demo=all --stop-after-init

echo.
echo ================================================================
echo UPGRADE FINISHED
echo ================================================================
echo Lanjutkan verifikasi di file:
echo   C:\addon14\VERIFY_REPORTS_BUSINESS_CATEGORY.md
echo.
pause
