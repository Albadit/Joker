@echo off
SETLOCAL EnableDelayedExpansion

:: The current directory of the batch file
SET "currentDir=%~dp0"
:: Remove the trailing backslash for consistency in path
SET "currentDir=%currentDir:~0,-1%"
SET "scriptFileName=SchoolEasy"

:: List of packages to check
:: if error openai pip install openai==0.28
SET "packages=pyinstaller psutil openai keyboard pyperclip"

:: Define your new paths
SET "newCommandPath=%currentDir%\dist\%scriptFileName%.exe"
SET "newWorkingDirectory=%currentDir%\dist"
SET "appPath=%currentDir%\app"

:: Check python version
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
  echo Python is not installed or not found in PATH.
  pause
  exit /b
)

:: Checking each package
for %%p in (%packages%) do (
  python -m pip show %%p >nul 2>&1
  if !ERRORLEVEL! neq 0 (
    echo Package %%p is not installed. Installing...
    python -m pip install %%p
    if !ERRORLEVEL! neq 0 (
      echo Failed to install %%p.
      pause
      exit /b
    )
  ) else (
    echo Package %%p is already installed.
  )
)

:: Ask for user confirmation before compiling
echo Do you want to compile the Python script to an executable? [Y/N]
choice /C YN /M "Press Y to confirm or N to cancel:"
if %ERRORLEVEL% equ 1 (
  echo Compiling the Python script to .exe...
  pyinstaller --noconfirm --onefile --noconsole --add-data "config.cfg;." --icon=src\app_icon.ico --hidden-import psutil --hidden-import openai --hidden-import keyboard --hidden-import pyperclip %scriptFileName%.py
  pyinstaller --noconfirm --onefile --icon=src\app_icon.ico %scriptFileName%_installer.py

  :: Copy config.conf in the dist
  COPY "%newWorkingDirectory%\SchoolEasy.exe" "%appPath%"
  COPY "%newWorkingDirectory%\SchoolEasy_installer.exe" "%appPath%"
) else (
  echo Compilation cancelled by user.
)

pause
exit