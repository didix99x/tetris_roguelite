"""game/state.py - os ESTADOS (telas) do jogo. Evita texto solto espalhado."""


class GameState:
    MENU = "MENU"
    OPTIONS = "OPTIONS"
    SHOP = "SHOP"                  # Loja (cartas, upgrades, álbum, bestiário, histórico)
    EVENT = "EVENT"                # eventos entre andares (descanso, troca arriscada, sala misteriosa)
    CHARACTER_SELECT = "CHARACTER_SELECT"
    BATTLE = "BATTLE"
    REWARD = "REWARD"
    BOSS_OFFER = "BOSS_OFFER"      # "Um Boss especial apareceu! Enfrentar ou ignorar?"
    UNLOCK = "UNLOCK"              # tela exclusiva de PERSONAGEM DESBLOQUEADO (vem antes das cartas de recompensa)
    VOID_FURY = "VOID_FURY"        # "O VAZIO ESTÁ FURIOSO..." (depois de concluir o andar 100, 200, 300...)
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"
