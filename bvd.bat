@echo off
setlocal

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set REQUIREMENTS=%SCRIPT_DIR%\src\requirements.txt
set SCRIPT=%SCRIPT_DIR%\src\main.py

set PATH=%PATH%;%SCRIPT_DIR% >nul

setx PATH "%PATH%;%SCRIPT_DIR%" >nul

if not exist "%PYTHON_EXE%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

"%PYTHON_EXE%" -m pip install --upgrade pip >nul
if exist "%REQUIREMENTS%" (
    "%PYTHON_EXE%" -m pip install -r "%REQUIREMENTS%" -q
) else (
    echo No requirements.txt found.
    exit /b 1
)

"%PYTHON_EXE%" "%SCRIPT%" %*

endlocal