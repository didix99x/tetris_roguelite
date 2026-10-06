"""
Diagnóstico das músicas (BGM).

Uso (na pasta do projeto, com o .venv ativo):
    python tools\\diagnostico_musica.py                 -> confere assets\\sounds\\bgm do projeto
    python tools\\diagnostico_musica.py release\\Game    -> confere a pasta do jogo já compilado

Mostra os arquivos que existem, quais são reconhecidos, qual música toca em cada situação,
se o volume da música está zerado e (se o pygame estiver instalado) se cada arquivo carrega.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from game import music_map  # noqa: E402

EXT = music_map.EXTENSIONS
KNOWN = sorted({n for names in music_map.SITUATION_TRACKS.values() for n in names} | {music_map.GENERIC})


def main():
    game_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
    folders = [game_dir / "assets" / "sounds" / "bgm", game_dir / "assets" / "sounds"]
    print(f"Pasta do jogo analisada: {game_dir}\n")

    problems = 0
    if not folders[0].exists():
        print(f"[ERRO] A pasta não existe: {folders[0]}")
        print("       Confira o nome: assets (com 'ts'), sounds, bgm - nessa ordem, sem acento.\n")
        problems += 1

    print("Arquivos encontrados:")
    audio_files = []
    for folder in folders:
        if folder.exists():
            for p in sorted(folder.iterdir()):
                if p.is_file() and p.suffix.lower() in EXT + (".m4a", ".flac", ".wma", ".aac"):
                    audio_files.append(p)
    if not audio_files:
        print("  (nenhum arquivo de áudio .ogg/.mp3/.wav nessas pastas)")
        problems += 1
    for p in audio_files:
        stem = p.stem
        notes = []
        if p.suffix.lower() not in EXT:
            notes.append(f"FORMATO NÃO SUPORTADO ({p.suffix}) - converta para .ogg ou .mp3")
        elif stem != stem.lower() or stem not in KNOWN:
            if stem.lower() in KNOWN and stem != stem.lower():
                notes.append("ok no Windows" if os.name == "nt" else "use o nome em MINÚSCULAS")
                if os.name != "nt":
                    problems += 1
            elif Path(stem).suffix.lower() in EXT:
                notes.append(f"EXTENSÃO DUPLICADA ('{p.name}') - o Windows está escondendo a extensão; renomeie para '{Path(stem).stem}{Path(stem).suffix}'")
            else:
                notes.append("nome NÃO reconhecido - o jogo ignora. Nomes válidos: " + ", ".join(KNOWN))
        else:
            notes.append("ok")
        if p.stat().st_size == 0:
            notes.append("ARQUIVO VAZIO (0 bytes)")
        real = music_map.detect_format(p)
        if p.stat().st_size and real != p.suffix.lower().lstrip("."):
            if real in ("mp3", "wav", "flac", "ogg"):
                notes.append(f"CONTEÚDO REAL: {real.upper()} (extensão errada) - o jogo carrega mesmo assim; para limpar, renomeie para .{real}")
            elif real == "opus":
                notes.append("CONTEÚDO REAL: OGG OPUS - pode não carregar; converta para Vorbis ou MP3")
            elif real == "m4a":
                notes.append("CONTEÚDO REAL: M4A/AAC - NÃO carrega; converta para .ogg (Vorbis) ou .mp3")
            else:
                notes.append("CONTEÚDO REAL: não reconhecido como áudio - arquivo corrompido ou outro formato")
        if notes[0] not in ("ok", "ok no Windows") or len(notes) > 1:
            problems += 1
        print(f"  {p.name!r:38} {p.stat().st_size/1024:8.0f} KB  -> {'; '.join(notes)}")

    print("\nO que toca em cada situação:")
    for situation in music_map.SITUATION_TRACKS:
        track = music_map.find_track(situation, folders)
        print(f"  {situation:14} -> {track.name if track else '(silêncio)'}")

    # volume
    try:
        from paths import user_data_dir
        sp = user_data_dir() / "settings.json"
        if sp.exists():
            vol = json.loads(sp.read_text(encoding="utf-8")).get("music_volume", 0.5)
            print(f"\nVolume da música em {sp}: {vol}" + ("   <-- ZERADO! aumente em OPÇÕES" if float(vol) <= 0 else ""))
            problems += float(vol) <= 0
        else:
            print("\nVolume da música: padrão (0.5) - ainda não há settings.json.")
    except Exception as err:  # noqa: BLE001
        print("\n(não consegui ler o volume:", err, ")")

    # carregar de verdade
    try:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        import pygame
        pygame.mixer.init()
        print("\nTeste de carregamento no pygame:")
        for p in audio_files:
            if p.suffix.lower() in EXT:
                try:
                    pygame.mixer.music.load(str(p))
                    print(f"  OK     {p.name}")
                except pygame.error as err:
                    print(f"  FALHOU {p.name}: {err}  (reexporte como .ogg Vorbis padrão)")
                    problems += 1
    except Exception as err:  # noqa: BLE001
        print(f"\n(teste de carregamento pulado: {err})")

    print("\nRESULTADO:", "tudo certo com os arquivos." if not problems else f"{problems} problema(s) acima.")
    print("Se estiver usando o jogo compilado, lembre: o build COPIA assets\\ para release\\Game\\assets só na hora de gerar.")
    print("Músicas adicionadas depois precisam ser copiadas para release\\Game\\assets\\sounds\\bgm\\ (ou rode o build de novo).")


if __name__ == "__main__":
    main()
