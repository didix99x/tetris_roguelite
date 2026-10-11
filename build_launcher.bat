@echo off
REM ============================================================
REM  build_launcher.bat - cria o Launcher.exe em release\
REM ============================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo ERRO: ambiente virtual .venv nao encontrado.
    if not defined NO_PAUSE pause
    exit /b 1
)
call .venv\Scripts\activate.bat

echo [1/3] Limpando builds antigos do launcher...
if exist build\work_launcher rmdir /s /q build\work_launcher
if exist build\dist_launcher rmdir /s /q build\dist_launcher
if exist release\Launcher.exe del /q release\Launcher.exe

echo [2/3] Empacotando o launcher com PyInstaller...
pyinstaller --noconfirm --clean --onefile --windowed --name Launcher ^
    --distpath build\dist_launcher --workpath build\work_launcher launcher.py
if errorlevel 1 (
    echo ERRO: o PyInstaller falhou. Leia as mensagens acima.
    if not defined NO_PAUSE pause
    exit /b 1
)
if exist Launcher.spec move /y Launcher.spec build\ >nul

echo [3/3] Copiando para release\ ...
if not exist release mkdir release
copy /y build\dist_launcher\Launcher.exe release\Launcher.exe >nul

echo Pronto: release\Launcher.exe
if not defined NO_PAUSE pause
