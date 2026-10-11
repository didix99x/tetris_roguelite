@echo off
REM ============================================================
REM  Cria RogueToca_jogavel.zip (o arquivo que voce envia aos jogadores).
REM  Rode DEPOIS do INSTALAR_E_GERAR_EXE.bat (precisa da pasta release\).
REM ============================================================
cd /d "%~dp0"

if not exist "release\Launcher.exe" ( echo ERRO: release\Launcher.exe nao existe. Rode INSTALAR_E_GERAR_EXE.bat primeiro. & pause & exit /b 1 )
if not exist "release\Game\RogueToca.exe" ( echo ERRO: release\Game\RogueToca.exe nao existe. Rode INSTALAR_E_GERAR_EXE.bat primeiro. & pause & exit /b 1 )
if not exist "release\Game\data\floors.json" ( echo ERRO: release\Game\data esta incompleta. & pause & exit /b 1 )
if not exist "release\Game\assets" ( echo ERRO: release\Game\assets nao existe. & pause & exit /b 1 )

copy /y "LEIA-ME_JOGADOR.txt" "release\LEIA-ME_JOGADOR.txt" >nul
if exist "release\Game\logs\*.log" del /q "release\Game\logs\*.log"
if exist "RogueToca_jogavel.zip" del /q "RogueToca_jogavel.zip"

echo Compactando...
powershell -NoProfile -Command "Compress-Archive -Path 'release\*' -DestinationPath 'RogueToca_jogavel.zip' -Force"
if errorlevel 1 ( echo ERRO ao compactar. & pause & exit /b 1 )

echo.
echo Pronto: %~dp0RogueToca_jogavel.zip
echo Envie esse arquivo. O jogador extrai e abre Launcher.exe.
pause
