@echo off
echo ==============================================
echo        Starting Wordulary...
echo ==============================================

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in your PATH. Please install Python 3.8+ first.
    pause
    exit /b
)

:: Create Virtual Environment if it doesn't exist
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate Virtual Environment
call venv\Scripts\activate.bat

:: Install Requirements
echo Installing dependencies...
pip install -r requirements.txt >nul 2>&1

:: Check for .env file
IF NOT EXIST ".env" (
    echo Creating a template .env file...
    echo DEEPL_API_KEY="your_actual_deepl_api_key_here" > .env
    echo -------------------------------------------------------------------
    echo ATTENTION: A new .env file has been created.
    echo Please open the .env file and add your DEEPL_API_KEY!
    echo Then, run this script again.
    echo -------------------------------------------------------------------
    pause
    exit /b
)

:: Open browser
echo Opening browser...
start http://127.0.0.1:8000

:: Run the app
echo Starting the server...
python -m uvicorn app:app --reload
