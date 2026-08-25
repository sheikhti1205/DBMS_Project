@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
set "PYTHONDONTWRITEBYTECODE=1"
set "BYTEFORGE_ASSUME_YES=0"
set "BYTEFORGE_REPLACE_DATABASE=0"

for %%A in (%*) do (
  if /i "%%~A"=="/yes" set "BYTEFORGE_ASSUME_YES=1"
  if /i "%%~A"=="/y" set "BYTEFORGE_ASSUME_YES=1"
  if /i "%%~A"=="/replace" set "BYTEFORGE_REPLACE_DATABASE=1"
  if /i "%%~A"=="/help" goto help
  if /i "%%~A"=="/?" goto help
)

if not defined BYTEFORGE_ENV set "BYTEFORGE_ENV=%USERPROFILE%\.byteforge\dbms_project\venv"
set "BYTEFORGE_PYTHON=%BYTEFORGE_ENV%\Scripts\python.exe"

call :find_python
if not defined BYTEFORGE_SYSTEM_PYTHON (
  echo A usable Python 3.10 or newer installation was not found.
  call :confirm "Install Python 3.12 for the current Windows user now?"
  if errorlevel 1 (
    echo Python installation was not approved. No system packages were changed.
    goto failed
  )
  call :install_python
  if errorlevel 1 goto failed
  call :find_python
)

if not defined BYTEFORGE_SYSTEM_PYTHON (
  echo Python was installed, but Python 3.10 or newer with SQLite support is still unavailable.
  goto failed
)

if exist "%BYTEFORGE_PYTHON%" (
  "%BYTEFORGE_PYTHON%" -c "import sqlite3, sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
  if not errorlevel 1 goto environment_ready
)

echo Preparing the ByteForge Python environment.
echo The first run may take a minute while Python prepares pip.
"%BYTEFORGE_SYSTEM_PYTHON%" %BYTEFORGE_SYSTEM_ARGS% -m venv --clear "%BYTEFORGE_ENV%"
if errorlevel 1 (
  echo The private Python environment could not be created.
  goto failed
)
if not exist "%BYTEFORGE_PYTHON%" (
  echo Python created the environment somewhere other than the requested folder.
  echo Set BYTEFORGE_ENV to a normal user folder and run setup again.
  goto failed
)

:environment_ready
"%BYTEFORGE_PYTHON%" -m pip --version >nul 2>nul
if errorlevel 1 (
  echo Preparing pip in the private environment.
  "%BYTEFORGE_PYTHON%" -m ensurepip --upgrade
  if errorlevel 1 (
    echo pip could not be prepared in the private environment.
    goto failed
  )
)

"%BYTEFORGE_PYTHON%" -c "from importlib.metadata import version; from pathlib import Path; lines=(line.strip() for line in Path('requirements.txt').read_text(encoding='utf-8').splitlines()); required=[line.split('==',1) for line in lines if line and not line.startswith('#')]; raise SystemExit(0 if required and all(version(name.strip())==expected.strip() for name,expected in required) else 1)" >nul 2>nul
if errorlevel 1 (
  echo The private environment needs the packages listed in requirements.txt.
  call :confirm "Install the project packages now?"
  if errorlevel 1 (
    echo Project package installation was not approved. The database was not changed.
    goto failed
  )
  echo Installing the project packages.
  "%BYTEFORGE_PYTHON%" -m pip install --disable-pip-version-check --quiet -r requirements.txt
  if errorlevel 1 (
    echo Required Python packages could not be installed. Check the internet connection and try again.
    goto failed
  )
) else (
  echo Required project packages are already available.
)

echo Preparing the database.
if "%BYTEFORGE_REPLACE_DATABASE%"=="1" (
  "%BYTEFORGE_PYTHON%" -m schema.scripts.setup.build_database --replace
) else (
  "%BYTEFORGE_PYTHON%" -m schema.scripts.setup.build_database
)
if errorlevel 1 goto failed

echo Checking the database.
"%BYTEFORGE_PYTHON%" -m schema.scripts.setup.verify_database
if errorlevel 1 goto failed

echo Opening the sample queries.
"%BYTEFORGE_PYTHON%" -m schema.scripts.queries.demo_database
if errorlevel 1 goto failed

echo.
echo ByteForge is ready.
if "%BYTEFORGE_ASSUME_YES%"=="0" pause
exit /b 0

:find_python
set "BYTEFORGE_SYSTEM_PYTHON="
set "BYTEFORGE_SYSTEM_ARGS="

where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sqlite3,sys; raise SystemExit(0 if sys.version_info.major == 3 and sys.version_info.minor in range(10, 100) else 1)" >nul 2>nul
  if not errorlevel 1 (
    set "BYTEFORGE_SYSTEM_PYTHON=py"
    set "BYTEFORGE_SYSTEM_ARGS=-3"
    exit /b 0
  )
)

where python >nul 2>nul
if not errorlevel 1 (
  python -c "import sqlite3,sys; raise SystemExit(0 if sys.version_info.major == 3 and sys.version_info.minor in range(10, 100) else 1)" >nul 2>nul
  if not errorlevel 1 (
    set "BYTEFORGE_SYSTEM_PYTHON=python"
    exit /b 0
  )
)

for %%P in ("%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%ProgramFiles%\Python312\python.exe") do (
  if exist "%%~P" (
    "%%~P" -c "import sqlite3,sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 set "BYTEFORGE_SYSTEM_PYTHON=%%~P"
  )
)
exit /b 0

:install_python
where winget >nul 2>nul
if not errorlevel 1 (
  echo Installing Python with Windows Package Manager.
  winget install --id Python.Python.3.12 --exact --source winget --scope user --accept-package-agreements --accept-source-agreements --silent
  if not errorlevel 1 (
    call :find_python
    if defined BYTEFORGE_SYSTEM_PYTHON exit /b 0
  )
  echo Windows Package Manager did not provide a usable Python. Trying the signed Python installer.
)

set "BYTEFORGE_INSTALLER_ARCH=amd64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "BYTEFORGE_INSTALLER_ARCH=arm64"
if /i "%PROCESSOR_ARCHITECTURE%"=="x86" set "BYTEFORGE_INSTALLER_ARCH=win32"
set "BYTEFORGE_INSTALLER=%TEMP%\byteforge-python-3.12.10-%BYTEFORGE_INSTALLER_ARCH%.exe"
set "BYTEFORGE_INSTALLER_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10-%BYTEFORGE_INSTALLER_ARCH%.exe"
if /i "%BYTEFORGE_INSTALLER_ARCH%"=="win32" set "BYTEFORGE_INSTALLER_URL=https://www.python.org/ftp/python/3.12.10/python-3.12.10.exe"

echo Downloading the signed Python installer from python.org.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri $env:BYTEFORGE_INSTALLER_URL -OutFile $env:BYTEFORGE_INSTALLER; Import-Module (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1') -Force; $signature=Get-AuthenticodeSignature -LiteralPath $env:BYTEFORGE_INSTALLER; if($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation'){Write-Error 'The Python installer signature is not valid.'; exit 1}"
if errorlevel 1 (
  if exist "%BYTEFORGE_INSTALLER%" del /q "%BYTEFORGE_INSTALLER%"
  echo The signed Python installer could not be downloaded or verified.
  exit /b 1
)

"%BYTEFORGE_INSTALLER%" /quiet InstallAllUsers=0 Include_launcher=1 Include_pip=1 Include_test=0 PrependPath=0 TargetDir="%LOCALAPPDATA%\Programs\Python\Python312"
set "BYTEFORGE_INSTALL_RESULT=%ERRORLEVEL%"
del /q "%BYTEFORGE_INSTALLER%"
if not "%BYTEFORGE_INSTALL_RESULT%"=="0" (
  echo The Python installer stopped with exit code %BYTEFORGE_INSTALL_RESULT%.
  exit /b 1
)
exit /b 0

:confirm
if "%BYTEFORGE_ASSUME_YES%"=="1" exit /b 0
set "BYTEFORGE_ANSWER="
set /p "BYTEFORGE_ANSWER=%~1 [y/N]: "
if /i "%BYTEFORGE_ANSWER%"=="y" exit /b 0
if /i "%BYTEFORGE_ANSWER%"=="yes" exit /b 0
exit /b 1

:help
echo Usage: setup_windows.bat [/yes] [/replace]
echo   /yes  Approve required installations without prompting.
echo   /replace  Replace a different or current database.
exit /b 0

:failed
echo.
echo Setup stopped before completion.
if "%BYTEFORGE_ASSUME_YES%"=="0" pause
exit /b 1
