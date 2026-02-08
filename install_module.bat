@echo off
REM ============================================================================
REM Script untuk Install Modul Odoo via Command Line
REM Gunakan script ini jika instalasi via UI tidak berhasil
REM ============================================================================

echo.
echo ============================================================================
echo INSTALL MODUL ODOO VIA COMMAND LINE
echo ============================================================================
echo.

if "%1"=="" (
    echo CARA PAKAI:
    echo   install_module.bat nama_modul
    echo.
    echo CONTOH:
    echo   install_module.bat account_dynamic_reports
    echo   install_module.bat project_task_timer
    echo.
    echo Module yang tersedia di C:\addon14:
    echo   - account_dynamic_reports
    echo   - accounting_pdf_reports
    echo   - project_enhancement
    echo   - dan lain-lain...
    echo.
    goto :end
)

set MODULE_NAME=%1
set ODOO_BIN=C:\odoo14c\server\odoo-bin
set PYTHON=c:\odoo14c\python\python.exe
set CONFIG=C:\addon14\odoo.conf
set DATABASE=manu14

echo Installing module: %MODULE_NAME%
echo Database: %DATABASE%
echo.
echo This will:
echo 1. Install the module
echo 2. Run all migrations
echo 3. Stop Odoo after installation
echo.

pause

echo.
echo Installing...
echo.

%PYTHON% %ODOO_BIN% --config=%CONFIG% -d %DATABASE% -i %MODULE_NAME% --stop-after-init

echo.
echo ============================================================================
echo Installation complete!
echo.
echo Next steps:
echo 1. Start Odoo
echo 2. Refresh browser (F5)
echo 3. Check the module in Apps
echo ============================================================================
echo.

:end
