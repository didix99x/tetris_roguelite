"""game/state.py - os ESTADOS (telas) do jogo. Evita texto solto espalhado."""


class GameState:
    MENU = "MENU"
    OPTIONS = "OPTIONS"
<<<<<<< HEAD
    SHOP = "SHOP"                  # Loja (cartas, upgrades, álbum, bestiário, histórico)
    EVENT = "EVENT"                # eventos entre andares (descanso, troca arriscada, sala misteriosa)
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    CHARACTER_SELECT = "CHARACTER_SELECT"
    BATTLE = "BATTLE"
    REWARD = "REWARD"
    BOSS_OFFER = "BOSS_OFFER"      # "Um Boss especial apareceu! Enfrentar ou ignorar?"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"
