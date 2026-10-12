"""game/data_loader.py - lê os JSON de data/ com mensagens de erro amigáveis."""
import json

from paths import data_path

DATA_FILES = ("characters", "enemies", "rewards", "floors", "shop")


class DataError(Exception):
    """Erro de arquivo ausente/quebrado. A mensagem já é amigável."""


def load_json(name):
    path = data_path(name)
    if not path.exists():
        raise DataError(f"Arquivo necessário não encontrado:\n\ndata/{name}")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as err:
        raise DataError(f"O arquivo data/{name} tem um erro de formato "
                        f"(linha {err.lineno}).\nConfira vírgulas e aspas.")


def load_all():
    return {name: load_json(name + ".json") for name in DATA_FILES}
