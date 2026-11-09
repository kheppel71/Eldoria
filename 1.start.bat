@echo off
setlocal enabledelayedexpansion
title Evennia Server Supervisor - Eldoria MUD

:: ============================================================================
:: CONFIGURATION & PATH SETUP
:: ============================================================================
set "BASE_DIR=C:\Evennia"
set "GAME_DIR=%BASE_DIR%\mygame"
set "VENV_DIR=%BASE_DIR%\evennia-env"
set "BACKUP_DIR=%BASE_DIR%\backups"
set "LOCKFILE=%GAME_DIR%\server\.maintenance"
set "LOG_DIR=%GAME_DIR%\server\logs"
set "DOCS_FILE=%BASE_DIR%\SERVER_OPERATIONS.md"

:: Maximum allowable consecutive crashes before watchdog halts
set "MAX_CONSECUTIVE_CRASHES=3"

cd /d "%GAME_DIR%" || (
    echo [FATAL ERROR] Failed to change directory to %GAME_DIR%
    exit /b 1
)

:: Handle automated command-line arguments
if /i "%~1"=="--watchdog"   goto :watchdog_loop
if /i "%~1"=="--reload"     goto :sub_reload
if /i "%~1"=="--stop"       goto :sub_stop
if /i "%~1"=="--backup"     goto :sub_backup
if /i "%~1"=="--check" (
    call :sub_preflight --headless
    exit /b !ERRORLEVEL!
)
if /i "%~1"=="--help"       goto :sub_help

:: ============================================================================
:: INTERACTIVE SUPERVISOR MENU
:: ============================================================================
:menu
cls
echo ===============================================================================
echo                EVENNIA PRODUCTION SUPERVISOR ^& CONTROLLER
echo ===============================================================================
echo   Game Directory:   %GAME_DIR%
echo   Virtualenv:       %VENV_DIR%
echo   Documentation:    %DOCS_FILE%
echo ===============================================================================
echo.
echo   [1] Start Server (Standard Background Mode)
echo   [2] Start Server with Auto-Restart Watchdog (Daemon Mode)
echo   [3] Graceful Warm Reload (Zero Player Disconnects)
echo   [4] Graceful Server Shutdown
echo   [5] Create Instant Database Snapshot (Pre-Flight Backup)
echo   [6] Pre-Flight Port ^& Process Conflict Diagnostics
echo   [7] Toggle Maintenance Mode Lock (.maintenance)
echo   [8] Tail Live Server Log
echo   [9] View Operations Documentation
echo   [Q] Exit Controller
echo.
choice /c 123456789Q /n /m "Select management action [1-9, Q]: "
set "MENU_CHOICE=!ERRORLEVEL!"

if "!MENU_CHOICE!"=="1" goto :sub_start_standard
if "!MENU_CHOICE!"=="2" goto :watchdog_loop
if "!MENU_CHOICE!"=="3" goto :sub_reload
if "!MENU_CHOICE!"=="4" goto :sub_stop
if "!MENU_CHOICE!"=="5" goto :sub_backup
if "!MENU_CHOICE!"=="6" goto :sub_preflight
if "!MENU_CHOICE!"=="7" goto :sub_toggle_maintenance
if "!MENU_CHOICE!"=="8" goto :sub_view_log
if "!MENU_CHOICE!"=="9" goto :sub_help
if "!MENU_CHOICE!"=="10" exit /b 0

:: ============================================================================
:: SUBROUTINE: PRE-FLIGHT VERIFICATION
:: ============================================================================
:sub_preflight
echo.
echo [*] Running Pre-Flight Diagnostics...

:: 1. Verify Virtual Environment
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] Python virtualenv not found at %VENV_DIR%
    set "ERR_CODE=101"
    goto :error_handler
)
call "%VENV_DIR%\Scripts\activate.bat"

:: 2. Check for Maintenance Lockfile
if exist "%LOCKFILE%" (
    echo.
    echo [WARNING] Maintenance lockfile detected at %LOCKFILE%!
    echo The server is marked as under maintenance.
    if /i "%~1"=="--headless" (
        echo [ERROR] Headless startup aborted due to active maintenance lock.
        exit /b 1
    )
    choice /c YN /m "Override lock and proceed anyway? [Y/N]: "
    if !ERRORLEVEL! NEQ 1 exit /b 0
)

:: 3. Check for Port Conflicts (Telnet: 4000, Web: 4001)
netstat -ano | findstr /R ":4000[ ] :4001[ ]" >nul 2>&1
if !ERRORLEVEL!==0 (
    echo.
    echo [WARNING] Port 4000 or 4001 is already bound by an existing socket!
    echo Checking for running Python/Twisted processes...
    tasklist /fi "imagename eq python.exe"
    if /i "%~1"=="--headless" (
        echo [INFO] Headless mode: Socket is currently in use.
    ) else (
        choice /c YN /m "Would you like to terminate orphan Python processes? [Y/N]: "
        if !ERRORLEVEL!==1 (
            taskkill /f /im python.exe /fi "imagename eq python.exe" >nul 2>&1
            timeout /t 2 >nul
            echo [INFO] Terminated existing processes.
        )
    )
)
echo [PASS] Pre-flight checks passed successfully.
if "%~1"=="" pause & goto :menu
exit /b 0

:: ============================================================================
:: SUBROUTINE: DATABASE SNAPSHOT / BACKUP
:: ============================================================================
:sub_backup
echo.
echo [*] Initiating Database Snapshot...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Timestamp generation (YYYY-MM-DD_HHMMSS)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "LDT=%%I"
if not defined LDT (
    set "TS=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
    set "TS=!TS: =0!"
) else (
    set "TS=!LDT:~0,4!-!LDT:~4,2!-!LDT:~6,2!_!LDT:~8,2!!LDT:~10,2!!LDT:~12,2!"
)

set "SNAPSHOT_FILE=%BACKUP_DIR%\evennia_backup_!TS!.db3"

if exist "%GAME_DIR%\server\evennia.db3" (
    copy /y "%GAME_DIR%\server\evennia.db3" "!SNAPSHOT_FILE!" >nul
    if !ERRORLEVEL!==0 (
        echo [SUCCESS] Database snapshot archived: !SNAPSHOT_FILE!
    ) else (
        echo [ERROR] Failed to copy database! Return code: !ERRORLEVEL!
    )
) else (
    echo [INFO] No evennia.db3 database file found to back up.
)
if "%~1"=="" pause & goto :menu
exit /b 0

:: ============================================================================
:: SUBROUTINE: STANDARD START
:: ============================================================================
:sub_start_standard
call :sub_preflight --headless
echo.
echo [*] Launching Evennia Portal and Server in background...
call "%VENV_DIR%\Scripts\evennia.exe" start
if !ERRORLEVEL! NEQ 0 (
    set "ERR_CODE=!ERRORLEVEL!"
    goto :error_handler
)
echo.
echo ===============================================================================
echo [SUCCESS] Evennia Server is running!
echo   - Telnet Access:    localhost:4000
echo   - Web Browser:      http://localhost:4001
echo   - WebSockets:       localhost:4002
echo ===============================================================================
pause
goto :menu

:: ============================================================================
:: SUBROUTINE: AUTO-RESTART WATCHDOG LOOP (DAEMON SUPERVISOR)
:: ============================================================================
:watchdog_loop
cls
echo ===============================================================================
echo                EVENNIA WATCHDOG SUPERVISOR ACTIVE
echo ===============================================================================
echo The watchdog monitors server execution and auto-restarts upon crashes.
echo Circuit breaker: Halts if %MAX_CONSECUTIVE_CRASHES% consecutive crashes occur.
echo Press [Ctrl+C] to abort the watchdog supervisor.
echo ===============================================================================

call :sub_preflight --headless
set "CRASH_COUNT=0"

:watchdog_cycle
echo.
echo [%TIME%] Starting Evennia in supervised foreground mode...
call "%VENV_DIR%\Scripts\evennia.exe" istart

set "EXIT_CODE=!ERRORLEVEL!"
echo.
echo [%TIME%] Server process exited with return code: !EXIT_CODE!

:: Clean exit code (0 = Normal administrative shutdown, no restart needed)
if "!EXIT_CODE!"=="0" (
    echo [INFO] Clean administrative shutdown detected. Exiting watchdog.
    pause
    exit /b 0
)

:: Abnormal exit detected
set /a CRASH_COUNT+=1
echo [ALERT] Server crashed or halted unexpectedly (Crash incident !CRASH_COUNT! of %MAX_CONSECUTIVE_CRASHES%)

if !CRASH_COUNT! GEQ %MAX_CONSECUTIVE_CRASHES% (
    echo.
    echo ===========================================================================
    echo [FATAL ERROR] CRASH THRESHOLD EXCEEDED!
    echo %MAX_CONSECUTIVE_CRASHES% consecutive crashes occurred without stabilizing.
    echo Watchdog halted to prevent database damage. Check server logs!
    echo ===========================================================================
    pause
    exit /b !EXIT_CODE!
)

echo [*] Archiving automatic crash snapshot...
call :sub_backup --headless

echo [*] Re-initiating server in 5 seconds...
timeout /t 5
goto :watchdog_cycle

:: ============================================================================
:: SUBROUTINE: WARM RELOAD
:: ============================================================================
:sub_reload
echo.
echo [*] Triggering zero-downtime warm reload...
call "%VENV_DIR%\Scripts\evennia.exe" reload
if !ERRORLEVEL!==0 (
    echo [SUCCESS] Game Server reloaded. Portal maintained all active connections.
) else (
    echo [ERROR] Reload failed with code: !ERRORLEVEL!
)
if "%~1"=="" pause & goto :menu
exit /b 0

:: ============================================================================
:: SUBROUTINE: STOP SERVER
:: ============================================================================
:sub_stop
echo.
echo [*] Shutting down Evennia Portal and Server...
call "%VENV_DIR%\Scripts\evennia.exe" stop
if !ERRORLEVEL!==0 (
    echo [SUCCESS] Server halted gracefully.
) else (
    echo [WARNING] Shutdown returned code: !ERRORLEVEL!
)
if "%~1"=="" pause & goto :menu
exit /b 0

:: ============================================================================
:: SUBROUTINE: TOGGLE MAINTENANCE LOCK
:: ============================================================================
:sub_toggle_maintenance
if exist "%LOCKFILE%" (
    del "%LOCKFILE%"
    echo.
    echo [INFO] Maintenance lock removed. Server open for normal operation.
) else (
    echo MAINTENANCE ACTIVE > "%LOCKFILE%"
    echo.
    echo [INFO] Maintenance lockfile created at %LOCKFILE%.
    echo Pre-flight checks will now warn before booting.
)
pause
goto :menu

:: ============================================================================
:: SUBROUTINE: LIVE LOG MONITOR
:: ============================================================================
:sub_view_log
echo.
echo Displaying latest server log entries (Press Ctrl+C to return)...
powershell -Command "if (Test-Path '%LOG_DIR%\server.log') { Get-Content -Path '%LOG_DIR%\server.log' -Tail 35 -Wait } else { Write-Host 'No server.log file found yet.' }"
goto :menu

:: ============================================================================
:: SUBROUTINE: HELP & DOCUMENTATION
:: ============================================================================
:sub_help
cls
if exist "%DOCS_FILE%" (
    type "%DOCS_FILE%" | more
) else (
    echo Documentation file not found at %DOCS_FILE%
)
pause
goto :menu

:: ============================================================================
:: ERROR HANDLER ROUTINE
:: ============================================================================
:error_handler
echo.
echo ===========================================================================
echo [ERROR HANDLER TRAP ACTIVATED]
echo Process encountered failure code: !ERR_CODE!
echo Suggestions:
echo   - Check if database is locked by another process (sqlite3 lock).
echo   - Ensure Python syntax in mygame\ is error-free (run test scripts).
echo   - Verify ports 4000/4001 are free using option [6].
echo ===========================================================================
pause
goto :menu
