"""
config.py - CONFIGURAÇÕES GERAIS DO JOGO

Aqui ficam os números que mudam o comportamento geral do jogo.
Valores de BALANCEAMENTO (vida, dano, cooldown...) ficam nos arquivos
da pasta data/ (JSON). Valores de DANO DO PUZZLE ficam em combat/damage.py.
"""

GAME_TITLE = "Rogue Toca"
VERSION = "0.2.0"

# Se True, os saves vão para a pasta saves/ ao lado do jogo (bom para testes).
# Se False, vão para a pasta do usuário (ex.: %APPDATA%/RogueToca).
USE_LOCAL_SAVES = False

# Só para TESTES: True = o Modo Infinito fica liberado sem precisar zerar o jogo.
# Deixe False na versão que você entrega aos jogadores.
DEBUG_UNLOCK_INFINITE = False

# ---------------- TELA ----------------
# Resolução BASE. O jogo sempre desenha em 1280x720 e depois escala
# para o tamanho real da janela, mantendo a proporção.
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# ---------------- TABULEIRO ----------------
BOARD_WIDTH = 8        # colunas
BOARD_HEIGHT = 8       # linhas
BLOCK_SIZE = 64        # tamanho de cada bloco em pixels
BOARD_Y_OFFSET = 20    # empurra o tabuleiro para baixo (espaço para o inimigo)

# ---------------- BLOCOS ----------------
NUM_COLORS = 5         # quantas cores existem (1 a 5)
STONE_COLOR_ID = 6     # id usado pelos blocos de pedra (obstáculos)
BLOCK_COLORS = {
    1: (220, 60, 60),    # vermelho
    2: (60, 120, 230),   # azul
    3: (70, 190, 90),    # verde
    4: (240, 210, 60),   # amarelo
    5: (160, 80, 210),   # roxo
    6: (95, 95, 105),    # pedra
}

# ---------------- TEMPOS (segundos) ----------------
BLOCK_MOVE_SPEED = 14.0   # velocidade visual dos blocos (células por segundo)
CLEAR_TIME = 0.30         # tempo que um match "pisca" antes de sumir
FALL_SETTLE_TIME = 0.08   # pequena pausa depois da queda
MAX_STONES = 12           # máximo de pedras no tabuleiro ao mesmo tempo

<<<<<<< HEAD
# ---------------- HABILIDADE DO PERSONAGEM ----------------
ABILITY_COOLDOWN = 3.0    # segundos de recarga depois de usar a habilidade (3000 ms), contados pelo tempo real do jogo (dt)

=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
# ---------------- ENERGIA ----------------
ENERGY_PER_BLOCK = 2.0          # energia ganha por bloco destruído
ENERGY_PER_CHAIN_LEVEL = 2.0    # energia extra por nível de chain

# ---------------- CORES DA INTERFACE ----------------
BACKGROUND_COLOR = (18, 18, 28)
PANEL_COLOR = (30, 30, 46)
TEXT_COLOR = (230, 230, 240)
MUTED_TEXT_COLOR = (150, 150, 170)
ACCENT_COLOR = (255, 210, 80)
HP_COLOR = (210, 60, 70)
ENERGY_COLOR = (70, 150, 240)
ENEMY_HP_COLOR = (200, 90, 50)

RARITY_COLORS = {
    "common": (180, 180, 190),
    "rare": (80, 150, 255),
    "epic": (185, 95, 245),
    "legendary": (255, 170, 40),
}
RARITY_NAMES = {
    "common": "Comum",
    "rare": "Rara",
    "epic": "Épica",
    "legendary": "Lendária",
}
