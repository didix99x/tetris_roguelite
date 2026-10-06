"""
board/block.py - UM bloco do tabuleiro.

Separa duas coisas:
- posição LÓGICA: grid_x, grid_y (a regra do jogo usa só isso);
- posição VISUAL: visual_x, visual_y (só para animar; "persegue" a lógica).
"""
import config


def _approach(current, target, step):
    """Move 'current' em direção a 'target' sem passar dele."""
    if current < target:
        return min(current + step, target)
    return max(current - step, target)


class Block:
    def __init__(self, color_id, grid_x, grid_y, kind="normal"):
        self.color_id = color_id     # 1..5 = cores, 6 = pedra
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.kind = kind             # "normal" ou "stone"
        self.web_time = 0.0          # segundos restantes de teia (0 = livre)
        self.visual_x = float(grid_x)
        self.visual_y = float(grid_y)
        self.clearing = False        # True enquanto o match está "piscando"
        self.clear_progress = 0.0    # 0 -> 1 durante a animação de sumir

    @property
    def is_stone(self):
        return self.kind == "stone"

    @property
    def is_webbed(self):
        return self.web_time > 0

    def is_moving(self):
        return (abs(self.visual_x - self.grid_x) > 0.001
                or abs(self.visual_y - self.grid_y) > 0.001)

    def update(self, dt):
        step = config.BLOCK_MOVE_SPEED * dt
        self.visual_x = _approach(self.visual_x, self.grid_x, step)
        self.visual_y = _approach(self.visual_y, self.grid_y, step)
        if self.web_time > 0:
            self.web_time = max(0.0, self.web_time - dt)
        if self.clearing:
            self.clear_progress = min(1.0, self.clear_progress + dt / config.CLEAR_TIME)
