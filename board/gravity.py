"""
board/gravity.py - GRAVIDADE e PREENCHIMENTO.

y = 0 é o topo do tabuleiro; y = height-1 é o fundo.
"""
from board.block import Block


def apply_gravity(grid, width, height):
    """Faz os blocos caírem para preencher buracos. Só muda a posição LÓGICA
    (a visual vai "perseguindo" depois, criando a animação de queda)."""
    for x in range(width):
        write_y = height - 1
        for y in range(height - 1, -1, -1):
            block = grid[y][x]
            if block is not None:
                if y != write_y:
                    grid[write_y][x] = block
                    grid[y][x] = None
                    block.grid_y = write_y
                write_y -= 1


def refill(grid, width, height, pick_color):
    """Cria blocos novos nos buracos do topo. 'pick_color(x, y)' escolhe a cor."""
    empty_per_column = [sum(1 for y in range(height) if grid[y][x] is None)
                        for x in range(width)]
    for y in range(height - 1, -1, -1):
        for x in range(width):
            if grid[y][x] is None:
                block = Block(pick_color(x, y), x, y)
                # Começa acima do tabuleiro para "cair" para dentro.
                block.visual_y = float(y - empty_per_column[x])
                grid[y][x] = block
