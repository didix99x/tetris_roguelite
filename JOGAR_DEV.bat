@echo off
REM Abre o launcher em modo desenvolvimento (sem gerar .exe).
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
    echo Rode primeiro INSTALAR_E_GERAR_EXE.bat ou crie o .venv (veja README.md).
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python launcher.py
if errorlevel 1 pause
