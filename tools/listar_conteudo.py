"""
tools/listar_conteudo.py - gera REFERENCIA_DE_CONTEUDO.md

Mostra, a partir dos arquivos de data/, a organização do jogo:
  ID -> Nome -> Tipo -> Imagem -> Habilidades -> Estatísticas
  Andar -> Tema -> Inimigos -> Chefe -> Recompensas

Rodar (na pasta do projeto):  python tools/listar_conteudo.py
Não usa pygame; não altera nada do jogo, só lê data/ e escreve o .md.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from game.data_loader import load_all  # noqa: E402
from paths import asset_path  # noqa: E402

EXTENSIONS = (".gif", ".png", ".webp", ".jpg", ".jpeg")


def find_image(folder, names):
    """Procura a imagem; devolve o caminho relativo ou None."""
    for name in names:
        for ext in EXTENSIONS:
            if asset_path("images", folder, name + ext).exists():
                return f"assets/images/{folder}/{name}{ext}"
    return None


def image_cell(folder, names):
    found = find_image(folder, names)
    return f"OK `{found.split('/')[-1]}`" if found else f"(usa desenho) esperado: `{names[0]}.png`"


def ability_text(a):
    kind = a["type"]
    parts = [f"**{a.get('name', kind)}** (`{kind}`)"]
    for key in ("amount", "percent", "duration", "speed"):
        if key in a:
            parts.append(f"{key}={a[key]}")
    return " ".join(parts)


def enemy_row(eid, e, folder, boss=False):
    names = [e.get("image", eid), eid] + ([] if boss else [e.get("family", eid)])
    abil = "; ".join(ability_text(a) for a in e.get("abilities", [])) or "-"
    stats = f"HP {e['hp']} / dano {e['damage']} / cooldown {e['cooldown']}s"
    return f"| `{eid}` | {e['name']} | {'Chefe' if boss else 'Inimigo'} | {image_cell(folder, names)} | {abil} | {stats} |"


def main():
    data = load_all()
    out = ["# REFERÊNCIA DE CONTEÚDO (gerado por tools/listar_conteudo.py)", "",
           "Não edite este arquivo à mão: rode `python tools/listar_conteudo.py` de novo para atualizar.", ""]

    out += ["## Personagens", "",
            "| ID | Nome | Classe | Desbloqueio | Imagem | Passiva | Habilidade | Estatísticas |",
            "|---|---|---|---|---|---|---|---|"]
    for cid, c in data["characters"].items():
        stats = f"HP {c['max_hp']} / energia {c.get('energy_max', 100)} / custo {c['ability_cost']}"
        rule = "liberado desde o início" if c.get("unlock") == "default" else "derrotar no Modo Infinito"
        out.append(f"| `{cid}` | {c['name']} | {c.get('class', '-')} | {rule} | "
                   f"{image_cell('characters', [c.get('image', cid), cid])} | "
                   f"**{c['passive_name']}**: {c['passive_text']} | "
                   f"**{c['ability_name']}**: {c['ability_text']} | {stats} |")

    out += ["", "## Inimigos", "",
            "| ID | Nome | Tipo | Imagem | Habilidades | Estatísticas (base, andar 1) |", "|---|---|---|---|---|---|"]
    for eid, e in data["enemies"]["enemies"].items():
        out.append(enemy_row(eid, e, "enemies"))

    out += ["", "## Chefes", "",
            "| ID | Nome | Tipo | Imagem | Habilidades | Estatísticas (base, andar 1) |", "|---|---|---|---|---|---|"]
    for floor, b in data["enemies"]["bosses"].items():
        out.append(enemy_row(f"boss_{floor}", b, "bosses", boss=True))

    out += ["", "## Personagens como chefes (só no Modo Infinito)", "",
            "| ID | Nome | Tipo | Imagem | Habilidades | Estatísticas (base, andar 1) |", "|---|---|---|---|---|---|"]
    for cid, b in data["enemies"].get("character_bosses", {}).items():
        char = data["characters"].get(cid, {"name": cid, "class": ""})
        title = f"{char['name']} - {char['class']}" if char.get("class") and char["class"] != "—" else char["name"]
        names = [char.get("image", cid), cid]
        abil = "; ".join(ability_text(a) for a in b.get("abilities", [])) or "-"
        stats = f"HP {b['hp']} / dano {b['damage']} / cooldown {b['cooldown']}s"
        out.append(f"| `boss_char_{cid}` | {title} | Chefe (personagem) | "
                   f"{image_cell('characters', names)} | {abil} | {stats} |")

    out += ["", "## Chefes exclusivos do Modo Infinito (15; 5 são SUPER BOSSES)", "",
            "| ID | Nome | Tipo | A partir do andar | Imagem | Habilidades | Mecânica | Estatísticas (base, andar 1) |",
            "|---|---|---|---|---|---|---|---|"]
    for key, b in data["enemies"].get("infinite_bosses", {}).items():
        abil = "; ".join(ability_text(a) for a in b.get("abilities", [])) or "-"
        stats = f"HP {b['hp']} / dano {b['damage']} / cooldown {b['cooldown']}s"
        out.append(f"| `boss_inf_{key}` | {b['name']} | {'**SUPER BOSS**' if b.get('super') else 'Chefe'} | {b.get('min_floor', 10)} | "
                   f"{image_cell('bosses', [f'boss_inf_{key}'])} | {abil} | **{b['mechanic_name']}**: {b['mechanic_text']} | {stats} |")

    out += ["", "## Inimigos exclusivos do Modo Infinito: em quais andares aparecem", "",
            "| ID | Nome | De | Até | Peso | Passiva |", "|---|---|---|---|---|---|"]
    for entry in data["floors"].get("infinite", {}).get("exclusive_enemies", []):
        e = data["enemies"]["enemies"][entry["id"]]
        out.append(f"| `{entry['id']}` | {e['name']} | {entry.get('from_floor', 1)} | {entry.get('to_floor', 'sem fim')} | "
                   f"{entry.get('weight', 1)} | **{e.get('passive_name', '-')}**: {e.get('passive_text', '-')} |")

    out += ["", "## Andares, temas, inimigos, chefe e recompensas", "",
            "| Andar | Tema | Inimigos possíveis | Chefe | Cartas disponíveis (comum/rara/épica/lendária) |",
            "|---|---|---|---|---|"]
    rewards = data["rewards"]["rewards"]
    groups = data["floors"].get("groups", [])
    last = data["floors"]["last_floor"]
    for floor in range(1, last + 1):
        boss = data["enemies"]["bosses"].get(str(floor))
        counts = {r: sum(1 for c in rewards if c["rarity"] == r and c.get("min_floor", 1) <= floor)
                  for r in ("common", "rare", "epic", "legendary")}
        cards = "/".join(str(counts[r]) for r in ("common", "rare", "epic", "legendary"))
        if floor % data["floors"]["boss_every"] == 0:
            name = boss["name"] if boss else "(boss não definido)"
            out.append(f"| {floor} | CHEFE | - | **{name}** | {cards} |")
            continue
        theme, names = "-", []
        for g in groups:
            if g["floors"][0] <= floor <= g["floors"][1]:
                theme = g["name"]
                names = [data["enemies"]["enemies"][e["id"]]["name"] for e in g["enemies"]
                         if e["floors"][0] <= floor <= e["floors"][1]]
        out.append(f"| {floor} | {theme} | {', '.join(names) or '(regra antiga por min_floor)'} | - | {cards} |")

    out += ["", "## Habilidades de inimigo (tipos disponíveis)", "",
            "| Nome (type) | Dano | Cooldown | Alcance | Efeito |", "|---|---|---|---|---|",
            "| `break` | - | o do inimigo | `amount` blocos | Destrói blocos aleatórios |",
            "| `web` | - | o do inimigo | `amount` blocos, `duration` s | Prende blocos (não podem ser trocados) |",
            "| `curse` | - | o do inimigo | `amount` blocos | Transforma blocos em pedra |",
            "| `weight` | - | o do inimigo | `duration` s, `speed` | O inimigo ataca mais rápido por um tempo |",
            "| `shuffle` | - | o do inimigo | `amount` blocos | Troca a cor de blocos |",
            "| `poison` (novo) | `amount` HP/s | o do inimigo | `duration` s | Tira vida do jogador por segundo |",
            "| `silence` (novo) | - | o do inimigo | `duration` s | Jogador não pode usar a habilidade |",
            "| `armor` (novo) | - | o do inimigo | `percent` %, `duration` s | Inimigo recebe menos dano dos matches |",
            "| `heal` (novo) | - | o do inimigo | `amount` % da vida máx. | Inimigo recupera vida |",
            "| `drain` (Infinito) | - | o do inimigo | `amount` de energia | Tira energia do jogador (a habilidade fica mais longe) |",
            "| `strike` (Infinito) | `amount` % do ataque do inimigo | o do inimigo | - | Golpe extra de dano direto (escala com o andar) |",
            "", "O cooldown é o do INIMIGO (campo `cooldown`): cada ataque dele usa UMA habilidade da lista, em ciclo.", ""]

    out += ["## Cartas (recompensas)", "",
            "| ID | Nome | Raridade | Categoria | A partir do andar | Efeito |", "|---|---|---|---|---|---|"]
    for c in rewards:
        out.append(f"| `{c['id']}` | {c['name']} | {c['rarity']} | {c.get('category', '-')} | "
                   f"{c.get('min_floor', 1)} | {c['description']} |")

    from game import music_map
    out += ["", "## Músicas (assets/sounds/bgm/)", "",
            "| Situação | Arquivo esperado | Status |", "|---|---|---|"]
    for situation in music_map.SITUATION_TRACKS:
        track = music_map.find_track(situation)
        status = f"toca `{track.name}`" if track else "silêncio (nenhum arquivo)"
        specific = music_map.find_file(music_map.SITUATION_TRACKS[situation][0])
        out.append(f"| {situation} | `{music_map.SITUATION_TRACKS[situation][0]}.ogg` | "
                   f"{'OK, próprio' if specific else 'sem arquivo próprio: ' + status} |")

    path = os.path.join(ROOT, "REFERENCIA_DE_CONTEUDO.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("Gerado:", path)


if __name__ == "__main__":
    main()
