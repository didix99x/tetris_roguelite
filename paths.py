"""
paths.py - ÚNICO lugar que resolve caminhos de pastas e arquivos.

Funciona de dois jeitos:
- durante o desenvolvimento (python main.py): usa a pasta do projeto;
- depois de virar EXE (PyInstaller): usa a pasta onde o .exe está.

Nunca coloque caminhos como C:\\Users\\... em outros arquivos. Use estas funções.
"""
import os
import sys
from pathlib import Path

APP_FOLDER_NAME = "RogueToca"
OLD_APP_FOLDER_NAME = "TetrisRoguelite"   # nome antigo: o progresso é copiado de lá uma vez


def is_frozen():
    """True quando estamos rodando dentro de um .exe criado pelo PyInstaller."""
    return bool(getattr(sys, "frozen", False))


def base_dir():
    """Pasta base: onde ficam data/ e assets/."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_path(*parts):
    return base_dir().joinpath(*parts)


def asset_path(*parts):
    return resource_path("assets", *parts)


def data_path(name):
    return resource_path("data", name)


def _is_writable(folder):
    try:
        folder.mkdir(parents=True, exist_ok=True)
        return os.access(folder, os.W_OK)
    except OSError:
        return False


def user_data_dir():
    """Pasta onde ficam saves e configurações (não exige administrador)."""
    from config import USE_LOCAL_SAVES
    if USE_LOCAL_SAVES:
        folder = base_dir() / "saves"
    else:
        override = os.environ.get("XDG_DATA_HOME")      # vale em qualquer SO (testes usam para isolar o save)
        if override:
            root = override
        elif os.name == "nt":
            root = os.environ.get("APPDATA") or str(Path.home())
        else:
            root = str(Path.home() / ".local" / "share")
        folder = Path(root) / APP_FOLDER_NAME
    if not folder.exists() and not USE_LOCAL_SAVES:
        old = folder.parent / OLD_APP_FOLDER_NAME
        if old.exists():
            try:
                import shutil
                shutil.copytree(old, folder)
            except OSError:
                pass
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def logs_dir():
    """logs/ ao lado do jogo; se não der para escrever, usa a pasta do usuário."""
    folder = base_dir() / "logs"
    if _is_writable(folder):
        return folder
    fallback = user_data_dir() / "logs"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback
