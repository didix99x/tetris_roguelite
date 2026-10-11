@echo off
REM ============================================================
REM  build_game.bat - cria o RogueToca.exe em release\Game
REM ============================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo ERRO: ambiente virtual .venv nao encontrado.
    echo Crie com:  python -m venv .venv
    echo Depois:    .venv\Scripts\activate  e  pip install -r requirements.txt
    if not defined NO_PAUSE pause
    exit /b 1
)
call .venv\Scripts\activate.bat

echo [1/4] Limpando builds antigos do jogo...
if exist build\work_game rmdir /s /q build\work_game
if exist build\dist_game rmdir /s /q build\dist_game
if exist release\Game rmdir /s /q release\Game

echo [2/4] Empacotando o jogo com PyInstaller (pode demorar)...
pyinstaller --noconfirm --clean --windowed --name RogueToca ^
    --distpath build\dist_game --workpath build\work_game main.py
if errorlevel 1 (
    echo ERRO: o PyInstaller falhou. Leia as mensagens acima.
    if not defined NO_PAUSE pause
    exit /b 1
)
if exist RogueToca.spec move /y RogueToca.spec build\ >nul

echo [3/4] Copiando para release\Game ...
if not exist release mkdir release
mkdir release\Game
xcopy /e /i /y build\dist_game\RogueToca release\Game >nul
xcopy /e /i /y data release\Game\data >nul
xcopy /e /i /y assets release\Game\assets >nul
mkdir release\Game\logs

echo [4/4] Pronto: release\Game\RogueToca.exe
if not defined NO_PAUSE pause
