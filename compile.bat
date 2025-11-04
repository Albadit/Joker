@echo off
SETLOCAL EnableDelayedExpansion

echo ================================================
echo       JOKER - Build Script
echo ================================================
echo.

:: The current directory of the batch file
SET "currentDir=%~dp0"
:: Remove the trailing backslash for consistency in path
SET "currentDir=%currentDir:~0,-1%"
SET "customFileName=joker"
SET "configFile=config.ini"
SET "requirementsFile=requirements.txt"

:: Define paths
SET "distPath=%currentDir%\dist"
SET "buildPath=%currentDir%\build"
SET "appPath=%currentDir%\app"

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Python is not installed or not found in PATH.
  echo Please install Python and add it to PATH.
  pause
  exit /b 1
)
python --version
echo [OK] Python found.
echo.

echo [2/5] Checking requirements file...
:: Check if requirements.txt exists
if not exist "%requirementsFile%" (
  echo [ERROR] %requirementsFile% not found!
  echo Please create requirements.txt in the project directory.
  pause
  exit /b 1
)
echo [OK] Requirements file found.
echo.

echo [3/5] Installing dependencies...
:: Install packages from requirements.txt
echo Installing packages from %requirementsFile%...
python -m pip install -r "%requirementsFile%" --quiet --disable-pip-version-check
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Failed to install packages from %requirementsFile%.
  pause
  exit /b 1
)
echo [OK] All packages installed successfully.
echo.

echo [3.5/5] Checking for UPX compressor...
:: Check if UPX is available (optional but recommended for smaller file size)
where upx >nul 2>&1
if %ERRORLEVEL% equ 0 (
  echo [OK] UPX found - will use compression.
  set HAS_UPX=1
) else (
  echo [INFO] UPX not found - skipping compression.
  echo [INFO] Install UPX from https://upx.github.io/ for smaller executables.
  set HAS_UPX=0
)
echo.

echo [4/5] Checking config file...
:: Check if config.ini exists
if not exist "%configFile%" (
  echo [WARNING] %configFile% not found!
  echo The compiled executable will need config.ini to run.
  echo.
)

:: Ask for user confirmation before compiling
echo [5/5] Ready to compile...
echo.
echo Select what to compile:
echo   1. Main application only (joker.exe)
echo   2. Setup installer only (joker_installer.exe)
echo   3. Both (all)
echo   4. Cancel
echo.
choice /C 1234 /M "Enter your choice"
set compileChoice=%ERRORLEVEL%

if %compileChoice% equ 4 (
  echo.
  echo Compilation cancelled by user.
  pause
  exit /b 0
)

echo.
echo ================================================
echo       Starting Compilation Process
echo ================================================
echo.

:: Create app directory if it doesn't exist
if not exist "%appPath%" (
  mkdir "%appPath%"
  echo Created app directory: %appPath%
  echo.
)

:: Compile based on user choice
if %compileChoice% equ 2 goto CompileInstaller
if %compileChoice% equ 3 goto CompileBoth
if %compileChoice% equ 1 goto CompileMain

:CompileMain
echo Compiling main application...
echo Using optimized build with size reduction...
pyinstaller joker.spec
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Failed to compile main application.
  pause
  exit /b 1
)
echo [OK] Main application compiled.
echo.

echo Moving executable to app folder...
move /Y "%distPath%\%customFileName%.exe" "%appPath%" >nul
if %ERRORLEVEL% neq 0 (
  echo [WARNING] Failed to move %customFileName%.exe
)
echo [OK] Executable moved to: %appPath%
echo.
goto Cleanup

:CompileInstaller
echo Compiling setup installer...
echo Using optimized build with size reduction...
pyinstaller joker_installer.spec
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Failed to compile setup installer.
  pause
  exit /b 1
)
echo [OK] Setup installer compiled.
echo.

echo Moving executable to app folder...
move /Y "%distPath%\%customFileName%_installer.exe" "%appPath%" >nul
if %ERRORLEVEL% neq 0 (
  echo [WARNING] Failed to move %customFileName%_installer.exe
)
echo [OK] Executable moved to: %appPath%
echo.
goto Cleanup

:CompileBoth
echo Compiling setup installer...
echo Using optimized build with size reduction...
pyinstaller joker_installer.spec
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Failed to compile setup installer.
  pause
  exit /b 1
)
echo [OK] Setup installer compiled.
echo.

echo Compiling main application...
echo Using optimized build with size reduction...
pyinstaller joker.spec
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Failed to compile main application.
  pause
  exit /b 1
)
echo [OK] Main application compiled.
echo.

echo Moving executables to app folder...
move /Y "%distPath%\%customFileName%.exe" "%appPath%" >nul
if %ERRORLEVEL% neq 0 (
  echo [WARNING] Failed to move %customFileName%.exe
)

move /Y "%distPath%\%customFileName%_installer.exe" "%appPath%" >nul
if %ERRORLEVEL% neq 0 (
  echo [WARNING] Failed to move %customFileName%_installer.exe
)
echo [OK] Executables moved to: %appPath%
echo.

:Cleanup
echo Cleaning up temporary files...
if exist "%distPath%" (
  rd /s /q "%distPath%"
)
if exist "%buildPath%" (
  rd /s /q "%buildPath%"
)
echo [OK] Cleanup completed.
echo.

echo ================================================
echo       Build Completed Successfully!
echo ================================================
echo.
echo Output files:
if %compileChoice% equ 1 (
  echo   - %appPath%\%customFileName%.exe
) else if %compileChoice% equ 2 (
  echo   - %appPath%\%customFileName%_installer.exe
) else (
  echo   - %appPath%\%customFileName%.exe
  echo   - %appPath%\%customFileName%_installer.exe
)
echo.
echo Next steps:
echo   1. Test the executables
if %compileChoice% neq 2 (
  echo   2. Ensure config.ini is in the same folder as the .exe
)
if %compileChoice% neq 1 (
  echo   3. Run %customFileName%_installer.exe to install
)
echo ================================================

pause
exit /b 0