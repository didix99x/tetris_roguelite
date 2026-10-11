"""
board/matcher.py - encontra os MATCHES (3 ou mais blocos iguais em linha).
Não mexe no tabuleiro: só olha e devolve o que encontrou.
"""
from dataclasses import dataclass

# Quantidade mínima de blocos iguais necessária para formar um Match.
MIN_MATCH = 3


@dataclass
class Match:
    cells: list        # lista de (x, y)
    color_id: int
    direction: str     # "h" (horizontal) ou "v" (vertical)

    @property
    def length(self):
        return len(self.cells)


def _same(a, b):
    """Dois blocos formam par se existem, não são pedra e têm a mesma cor."""
    return (a is not None and b is not None and not a.is_stone
            and not b.is_stone and a.color_id == b.color_id)


def find_matches(grid, width, height, min_match=MIN_MATCH):
    matches = []
    # Horizontais
    for y in range(height):
        x = 0
        while x < width:
            block = grid[y][x]
            if block is None or block.is_stone:
                x += 1
                continue
            end = x + 1
            while end < width and _same(block, grid[y][end]):
                end += 1
            if end - x >= min_match:
                matches.append(Match([(i, y) for i in range(x, end)], block.color_id, "h"))
            x = end
    # Verticais
    for x in range(width):
        y = 0
        while y < height:
            block = grid[y][x]
            if block is None or block.is_stone:
                y += 1
                continue
            end = y + 1
            while end < height and _same(block, grid[end][x]):
                end += 1
            if end - y >= min_match:
                matches.append(Match([(x, i) for i in range(y, end)], block.color_id, "v"))
            y = end
    return matches


def matched_cells(matches):
    """Junta as células de todos os matches (sem repetir)."""
    cells = set()
    for match in matches:
        cells.update(match.cells)
    return cells
