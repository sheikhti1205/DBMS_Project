@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHONDONTWRITEBYTECODE=1"

set "BYTEFORGE_ENV=%LOCALAPPDATA%\ByteForge\DBMS_Project\venv"
set "BYTEFORGE_PYTHON=%BYTEFORGE_ENV%\Scripts\python.exe"

if exist "%BYTEFORGE_PYTHON%" goto prepare

echo Preparing the ByteForge Python environment.
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
  if errorlevel 1 goto old_python
  py -3 -m venv "%BYTEFORGE_ENV%"
) else (
  where python >nul 2>nul
  if errorlevel 1 goto no_python
  python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
  if errorlevel 1 goto old_python
  python -m venv "%BYTEFORGE_ENV%"
)
if errorlevel 1 goto venv_failed

:prepare
echo Checking required Python packages.
"%BYTEFORGE_PYTHON%" -m pip install --disable-pip-version-check --quiet -r requirements.txt
if errorlevel 1 goto packages_failed

echo Preparing the database.
"%BYTEFORGE_PYTHON%" -m schema.scripts.setup.build_database --replace
if errorlevel 1 goto failed

echo Checking the database.
"%BYTEFORGE_PYTHON%" -m schema.scripts.setup.verify_database
if errorlevel 1 goto failed

echo Opening the sample queries.
"%BYTEFORGE_PYTHON%" -m schema.scripts.queries.demo_database
if errorlevel 1 goto failed

echo.
echo ByteForge is ready.
pause
exit /b 0

:no_python
echo Python 3.10 or newer was not found. Install Python, then run this file again.
goto failed

:old_python
echo The available Python version is too old. Python 3.10 or newer is required.
goto failed

:venv_failed
echo The Python environment could not be created.
goto failed

:packages_failed
echo Required Python packages could not be installed. Check the internet connection and try again.
goto failed

:failed
echo.
echo Setup stopped before completion.
pause
exit /b 1
