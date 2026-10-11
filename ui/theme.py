"""
ui/theme.py - PAINEL DE CONTROLE VISUAL do jogo (só aparência; nada aqui muda a gameplay).

Aqui ficam, num lugar só:
  1) FONTES              -> trocar a fonte e o tamanho geral do texto
  2) CORES da HUD        -> painéis, barras, textos, avisos
  3) POSIÇÕES E TAMANHOS -> onde cada painel/barra/retrato fica (base 1280x720)
  4) EFEITOS             -> ligar/desligar, intensidade, velocidade e tamanho dos efeitos das habilidades

As cores básicas (fundo, texto, vida, energia) continuam vindo de config.py.
"""
import config

# ======================================================================
# 1) FONTES
# ======================================================================
# None = fonte padrão do pygame. Para usar uma fonte sua, coloque o .ttf em assets/fonts/ e escreva, por exemplo:
#   FONT_PATH = "assets/fonts/MinhaFonte.ttf"
# (fontes diferentes têm tamanho diferente: se o texto ficar grande/pequeno, ajuste FONT_SCALE.)
FONT_PATH = None
FONT_SCALE = 1.0

# ======================================================================
# 2) CORES (R, G, B)
# ======================================================================
TEXT = config.TEXT_COLOR
TEXT_MUTED = config.MUTED_TEXT_COLOR
TEXT_DIM = (100, 100, 122)
ACCENT = config.ACCENT_COLOR

PANEL_TOP = (36, 36, 56)             # painéis: degradê do topo...
PANEL_BOTTOM = (24, 24, 38)          # ...até embaixo
PANEL_BORDER = (74, 74, 104)
PANEL_INNER = (22, 22, 34)           # caixas internas (habilidade, passiva...)
PANEL_INNER_BORDER = (52, 52, 78)
SHADOW = (8, 8, 14)

HP = config.HP_COLOR
HP_LOW = (255, 70, 70)               # barra de vida quando está baixa
ENERGY = config.ENERGY_COLOR
ENEMY_HP = config.ENEMY_HP_COLOR
BAR_BACK = (18, 18, 28)
BAR_BORDER = (150, 150, 175)
BAR_TRAIL = (255, 235, 200)          # "rastro" que mostra o dano sofrido
ATTACK_BAR = (230, 170, 60)
ATTACK_BAR_DANGER = (240, 80, 70)
READY = (120, 240, 140)              # habilidade pronta
STATUS = (255, 150, 120)             # efeitos negativos ativos
BONUS = (170, 220, 255)              # bônus da run
BOSS_TAG = (255, 170, 60)
SUPER_TAG = (255, 90, 70)

# ======================================================================
# 3) POSIÇÕES E TAMANHOS (x, y, largura, altura) - base 1280x720
# ======================================================================
ENEMY_PLATE = (330, 8, 620, 104)         # placa com nome, vida e passiva do inimigo (topo)
ENEMY_NAME_Y = 30
ENEMY_BAR = (380, 50, 520, 26)           # barra de vida do inimigo
ENEMY_PASSIVE_Y = 92

LEFT_PANEL = (30, 130, 330, 530)         # painel do jogador
PLAYER_PORTRAIT = (135, 174, 120)        # x, y, tamanho do retrato do jogador
PLAYER_HP_BAR = (66, 338, 274, 26)         # (o ícone fica 14 px à esquerda da barra)
PLAYER_ENERGY_BAR = (66, 402, 274, 22)
ABILITY_BOX = (44, 436, 302, 86)         # caixa da habilidade
PASSIVE_BOX = (44, 532, 302, 112)        # caixa da passiva

RIGHT_PANEL = (920, 130, 330, 530)       # painel do andar/inimigo
ENEMY_PORTRAIT = (1030, 174, 110)        # x, y, tamanho do retrato do inimigo
CHAIN_CENTER = (1085, 318)
ATTACK_BAR_RECT = (940, 374, 290, 18)    # barra "próximo ataque"
EFFECTS_TOP = 408                        # y onde começa a lista de efeitos ativos
BONUS_TOP = 522                          # y onde começa a lista de bônus da run

HINT_Y = 697                             # y da faixa de teclas, embaixo

# Símbolos desenhados nas peças (anel, triângulo, losango, estrela, cruz): ajudam a distinguir as cores. Só visual.
PIECE_SYMBOLS = True

# ======================================================================
# 4) EFEITOS VISUAIS
# ======================================================================
# Tudo aqui é só visual. Para um efeito mais discreto, diminua "intensity"/"size"; para mais rápido, aumente "speed".
EFFECTS = {
    "enabled": True,          # False desliga TODOS os efeitos novos (o jogo continua igual)
    "intensity": 1.0,         # 0.0 a 2.0: quantidade de partículas e força do brilho
    "speed": 1.0,             # 1.0 normal; 1.5 = efeitos mais rápidos; 0.7 = mais lentos
    "size": 1.0,              # tamanho geral dos efeitos
    "hit_effects": True,      # brilho/faíscas ao acertar ou ser acertado
    "flash_scale": 1.0,       # força do clarão de tela quando usa a habilidade (0 = sem clarão)
    "max_items": 170,         # limite de efeitos ao mesmo tempo (desempenho)
}

# Ajustes por personagem (opcional). Chaves: "duration", "size", "intensity" (multiplicam os valores acima).
# Exemplo:  "warrior": {"size": 1.3, "intensity": 0.8},
STYLE_TUNING = {}

# Cor de cada personagem nos efeitos (se não estiver aqui, usa a cor do personagem em data/characters.json)
STYLE_COLORS = {
    "warrior": (255, 120, 70),
    "mage": (150, 120, 255),
    "assassin": (190, 110, 255),
    "bard": (90, 230, 170),
    "judge": (255, 215, 90),
    "cleric": (255, 245, 190),
    "blacksmith": (255, 150, 70),
    "archer": (130, 220, 100),
    "monk": (255, 170, 70),
    "yoshi": (220, 70, 80),
}
