@echo off
REM ============================================================
REM  build_all.bat - gera a versao distribuivel completa em release\
REM ============================================================
cd /d "%~dp0"
set NO_PAUSE=1

call build_game.bat
if errorlevel 1 goto fail
call build_launcher.bat
if errorlevel 1 goto fail

echo.
echo ===== BUILD COMPLETO =====
echo Pasta pronta para distribuir: %~dp0release
echo   Launcher.exe
echo   Game\RogueToca.exe
echo Para jogar: abra release\Launcher.exe
pause
exit /b 0

:fail
echo.
echo ===== O BUILD FALHOU - leia as mensagens acima =====
pause
exit /b 1
