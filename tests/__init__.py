"""Isola os saves dos testes: nenhum teste pode ler/gravar o progress.json real do jogador.

Windows usa %APPDATA%; Linux/Mac usam XDG_DATA_HOME/HOME. Define todos para uma pasta temporária.
"""
import os
import tempfile

_SANDBOX = tempfile.mkdtemp(prefix="rogue_toca_tests_")
for _var in ("APPDATA", "XDG_DATA_HOME", "HOME", "USERPROFILE"):
    os.environ[_var] = _SANDBOX
