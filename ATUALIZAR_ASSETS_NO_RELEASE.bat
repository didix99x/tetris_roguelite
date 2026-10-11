@echo off
REM ============================================================
REM  Copia musicas, imagens e dados (assets\ e data\) do projeto para release\Game
REM  SEM precisar gerar o .exe de novo. Use depois de adicionar/trocar musicas ou GIFs.
REM ============================================================
cd /d "%~dp0"
if not exist "release\Game\RogueToca.exe" ( echo ERRO: release\Game ainda nao existe. Rode INSTALAR_E_GERAR_EXE.bat primeiro. & pause & exit /b 1 )
xcopy /e /i /y assets release\Game\assets >nul
xcopy /e /i /y data release\Game\data >nul
echo Pronto: assets\ e data\ atualizados em release\Game.
pause
