@echo off
setlocal
cd /d "%~dp0"

set PORT=8085

REM Old webpack (5.14) uses a legacy OpenSSL hash that modern Node (17+) removed.
REM This flag re-enables it so the build doesn't crash with ERR_OSSL_EVP_UNSUPPORTED.
set NODE_OPTIONS=--openssl-legacy-provider

echo ===================================================
echo   Three.js FPS Demo - Local Dev Server
echo ===================================================
echo.

REM Install dependencies on first run
if not exist "node_modules" (
    echo node_modules not found. Installing dependencies...
    echo.
    call npm install
    if errorlevel 1 (
        echo.
        echo [ERROR] npm install failed. Make sure Node.js is installed.
        echo.
        pause
        exit /b 1
    )
    echo.
)

echo Starting server on port %PORT%...
echo.
echo   Play the game here:  http://localhost:%PORT%
echo.
echo   ( Press Ctrl+C to stop the server )
echo ===================================================
echo.

call npx webpack serve --port %PORT%

echo.
echo ===================================================
echo   Server stopped.
echo ===================================================
pause
endlocal
