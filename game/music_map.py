"""
game/music_map.py - QUAL MÚSICA toca em cada situação (não usa pygame).

Coloque os arquivos em assets/sounds/bgm/ com estes nomes (.ogg, .mp3 ou .wav):

  menu           menu, opções e escolha de personagem
  battle         batalha normal
  boss           batalha contra chefe
  infinite       batalha normal no Modo Infinito
  infinite_boss  chefe no Modo Infinito
  reward         tela de escolha de recompensa
  victory        tela de vitória
  game_over      tela de game over

Se o arquivo de uma situação não existir, o jogo tenta o "reserva" da lista abaixo
e, por último, a música geral "music" (assets/sounds/bgm/music.ogg ou assets/sounds/music.ogg).
Sem nenhum arquivo, fica em silêncio (o jogo continua normalmente).
"""
from game.state import GameState
from paths import asset_path

EXTENSIONS = (".ogg", ".mp3", ".wav")
GENERIC = "music"

# situação -> nomes de arquivo, na ordem de preferência
SITUATION_TRACKS = {
    "menu": ["menu"],
    "battle": ["battle"],
    "boss": ["boss", "battle"],
    "infinite": ["infinite", "battle"],
    "infinite_boss": ["infinite_boss", "boss", "infinite", "battle"],
    "reward": ["reward", "battle"],
    "victory": ["victory"],
    "game_over": ["game_over"],
}


def search_folders():
    return [asset_path("sounds", "bgm"), asset_path("sounds")]


def find_file(name, folders=None):
    """Procura <nome>.ogg/.mp3/.wav nas pastas de música. Devolve Path ou None."""
    for folder in (folders if folders is not None else search_folders()):
        for ext in EXTENSIONS:
            path = folder / (name + ext)
            if path.exists():
                return path
    return None


def find_track(situation, folders=None):
    """Arquivo de música para a situação (com reservas). None = silêncio."""
    for name in SITUATION_TRACKS.get(situation, []) + [GENERIC]:
        path = find_file(name, folders)
        if path is not None:
            return path
    return None


def detect_format(path):
    """Formato REAL do arquivo, pelo conteúdo (a extensão pode estar errada, ex.: .mp3 renomeado para .ogg).
    Devolve: 'ogg', 'opus', 'mp3', 'wav', 'flac', 'm4a' ou None (desconhecido)."""
    try:
        with open(path, "rb") as f:
            head = f.read(256)
    except OSError:
        return None
    if head[:4] == b"OggS":
        return "opus" if b"OpusHead" in head else "ogg"
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "wav"
    if head[:4] == b"fLaC":
        return "flac"
    if head[4:8] == b"ftyp":
        return "m4a"
    if head[:3] == b"ID3" or (len(head) > 1 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0):
        return "mp3"
    return None


def find_tracks(situation, folders=None):
    """TODOS os arquivos candidatos para a situação, em ordem de preferência (sem repetir)."""
    found = []
    for name in SITUATION_TRACKS.get(situation, []) + [GENERIC]:
        for folder in (folders if folders is not None else search_folders()):
            for ext in EXTENSIONS:
                path = folder / (name + ext)
                if path.exists() and path not in found:
                    found.append(path)
    return found


def situation_for(state, run=None, enemy_is_boss=False):
    """Traduz o estado do jogo na situação de música."""
    if state in (GameState.MENU, GameState.OPTIONS, GameState.CHARACTER_SELECT):
        return "menu"
    if state == GameState.BATTLE:
        infinite = run is not None and getattr(run, "mode", "story") == "infinite"
        if infinite:
            return "infinite_boss" if enemy_is_boss else "infinite"
        return "boss" if enemy_is_boss else "battle"
    if state in (GameState.REWARD, GameState.BOSS_OFFER, GameState.UNLOCK):
        return "reward"
    if state == GameState.VOID_FURY:
        return "infinite_boss"
    if state == GameState.VICTORY:
        return "victory"
    if state == GameState.GAME_OVER:
        return "game_over"
    return "menu"
