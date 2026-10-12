"""
tools/aplicar_novas_artes.py - aplica as artes de inimigos/chefes em assets/images/.

Uso (na pasta do projeto):
    python tools/aplicar_novas_artes.py "C:\\caminho\\da\\pasta\\inimigos"
    python tools/aplicar_novas_artes.py "C:\\caminho\\inimigos" --simular     (só mostra, não copia)

A pasta de origem tem subpastas (Horda Goblin, Ninho das Aranhas...). Quem vai para
qual ID está em tools/mapa_artes_inimigos.json. As imagens são copiadas SEM alteração
(sem mexer em cor, tamanho ou transparência). Antes de sobrescrever, a arte antiga é
guardada em arte_antiga_backup/ (só se ainda não existir lá).
Não mexe em assets/images/characters (personagens jogáveis).
"""
import json
import os
import re
import shutil
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPA = os.path.join(ROOT, "tools", "mapa_artes_inimigos.json")
DESTINO = os.path.join(ROOT, "assets", "images")
BACKUP = os.path.join(ROOT, "arte_antiga_backup")


def normalizar(texto):
    """Ignora acentos, maiúsculas, espaços sobrando e o '#U00e3' que alguns descompactadores criam."""
    texto = re.sub(r"#U([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    partes = [re.sub(r"\s+", " ", p).strip().lower() for p in texto.replace("\\", "/").split("/")]
    nome = partes[-1]
    base, ext = os.path.splitext(nome)
    partes[-1] = base.strip() + ext
    return "/".join(p.strip() for p in partes)


def carregar_mapa():
    with open(MAPA, encoding="utf-8") as f:
        bruto = json.load(f)["mapa"]
    return {normalizar(origem): destino for origem, destino in bruto.items()}


def listar_origem(pasta):
    achados = {}
    for atual, _, arquivos in os.walk(pasta):
        for nome in arquivos:
            if not nome.lower().endswith((".png", ".gif", ".webp", ".jpg", ".jpeg")):
                continue
            caminho = os.path.join(atual, nome)
            rel = os.path.relpath(caminho, pasta).replace("\\", "/")
            achados[normalizar(rel)] = (rel, caminho)
    return achados


def main(argv):
    simular = "--simular" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args or not os.path.isdir(args[0]):
        print(__doc__)
        return 1
    mapa = carregar_mapa()
    origem = listar_origem(args[0])
    copiados, sem_destino = 0, []
    for chave, (rel, caminho) in sorted(origem.items()):
        destino = mapa.get(chave)
        if destino is None:
            sem_destino.append(rel)
            continue
        pasta, art_id = destino.split("/")
        saida = os.path.join(DESTINO, pasta, art_id + ".png")
        print(("[simulação] " if simular else "") + f"{rel}  ->  assets/images/{pasta}/{art_id}.png")
        if simular:
            copiados += 1
            continue
        os.makedirs(os.path.dirname(saida), exist_ok=True)
        if os.path.exists(saida):
            copia = os.path.join(BACKUP, pasta, art_id + ".png")
            if not os.path.exists(copia):
                os.makedirs(os.path.dirname(copia), exist_ok=True)
                shutil.copy2(saida, copia)
        shutil.copyfile(caminho, saida)
        copiados += 1
    faltando = sorted(d for k, d in mapa.items() if k not in origem)
    print(f"\n{copiados} arte(s) {'a copiar' if simular else 'copiada(s)'}.")
    if sem_destino:
        print("\nArquivos da origem SEM destino no mapa (nada foi feito com eles):")
        for rel in sem_destino:
            print("  -", rel)
    if faltando:
        print("\nItens do mapa sem arquivo na origem:")
        for d in faltando:
            print("  -", d)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
