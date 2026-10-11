@echo off
REM ============================================================
REM  Um clique so: prepara tudo e gera release\Launcher.exe
REM  Requisito: Python 3.11+ instalado (com "Add Python to PATH")
REM ============================================================
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado. Instale em python.org e marque "Add Python to PATH".
    pause
    exit /b 1
)

if not exist ".venv\Scripts\activate.bat" (
    echo [1/4] Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 ( echo ERRO ao criar .venv & pause & exit /b 1 )
)
call .venv\Scripts\activate.bat

echo [2/4] Instalando pygame e pyinstaller...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 ( echo ERRO ao instalar dependencias & pause & exit /b 1 )

echo [3/4] Testando a logica do jogo...
python -m unittest discover -s tests -t . -v
if errorlevel 1 ( echo ERRO: os testes falharam. Envie a mensagem acima. & pause & exit /b 1 )

echo [4/4] Gerando os executaveis...
call build_all.bat
