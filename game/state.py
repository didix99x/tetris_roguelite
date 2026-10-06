"""game/state.py - os ESTADOS (telas) do jogo. Evita texto solto espalhado."""


class GameState:
    MENU = "MENU"
    OPTIONS = "OPTIONS"
    CHARACTER_SELECT = "CHARACTER_SELECT"
    BATTLE = "BATTLE"
    REWARD = "REWARD"
    BOSS_OFFER = "BOSS_OFFER"      # "Um Boss especial apareceu! Enfrentar ou ignorar?"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"
