@echo off
chcp 65001 >nul
echo Starting NHS Personalised Care Server
echo ======================================

REM Check for Python 3.10 specifically
echo Checking Python version...

python --version 2>nul | find "3.10" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Python 3.10 found
    set PYTHON_CMD=python
) else (
    python3.10 --version 2>nul | find "3.10" >nul
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Python 3.10 found
        set PYTHON_CMD=python3.10
    ) else (
        echo ❌ Python 3.10 not found!
        echo Please install Python 3.10 from: https://www.python.org/downloads/
        echo Or use: py -3.10 -m pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo Using: %PYTHON_CMD%

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies with retry
echo Installing dependencies...
set ATTEMPT=1
:install_loop
echo Attempt %ATTEMPT%...
python -m pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 goto install_done
if %ATTEMPT% EQU 3 (
    echo Failed after 3 attempts. Installing without cache...
    python -m pip install --no-cache-dir -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Please install dependencies manually:
        echo pip install flask flask-cors flask-socketio pandas numpy scikit-learn Pillow
        pause
        exit /b 1
    )
    goto install_done
)
set /a ATTEMPT+=1
goto install_loop
:install_done

REM Create directories
if not exist static mkdir static
if not exist templates mkdir templates

REM Generate icons
if not exist static\icons\icon-192.png (
    echo Generating icons...
    python generate_icons.py
)

REM Run server
echo Starting server...
python nhs_care_server.py
pause