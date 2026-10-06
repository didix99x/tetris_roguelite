"""board/chain.py - conta as CHAINS (matches em sequência)."""


class ChainTracker:
    def __init__(self):
        self.count = 0   # 0 = nenhuma chain em andamento
        self.best = 0    # maior chain da batalha

    def next(self):
        """Chamado a cada novo match na mesma sequência. Devolve o novo número."""
        self.count += 1
        self.best = max(self.best, self.count)
        return self.count

    def reset(self):
        self.count = 0
