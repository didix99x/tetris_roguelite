"""
characters/character.py - o JOGADOR (HP, energia, bônus da run).

O personagem existe para ALTERAR o puzzle: passiva e habilidade vêm das
classes filhas (warrior.py, mage.py, assassin.py).
"""
import logging

log = logging.getLogger(__name__)

# Bônus que as recompensas podem aumentar durante a run.
DEFAULT_MODS = {
    "damage_pct": 0.0,           # +% de dano geral
    "chain_damage_pct": 0.0,     # +% de dano nas chains (x2 ou mais)
    "energy_gain_pct": 0.0,      # +% de energia ganha
    "enemy_cooldown_pct": 0.0,   # +% de tempo entre ataques do inimigo
    "ability_cost_pct": 0.0,     # negativo = habilidade mais barata
    "explosion_match5": 0,       # blocos destruídos extra em match 5+
    "explosion_chain": 0,        # blocos destruídos extra em chains
    "lifesteal_pct": 0.0,        # cura = % do dano causado
    "regen_per_sec": 0.0,        # HP recuperado por segundo
    "chain_start": 0,            # chains começam neste nível a mais
    # ---- bônus das cartas novas ----
    "damage_reduction_pct": 0.0, # defesa: reduz o dano dos ataques do inimigo
    "crit_chance": 0.0,          # chance (0 a 1) de um match causar crítico
    "crit_damage_pct": 0.0,      # bônus extra no multiplicador de crítico
    "ability_power_pct": 0.0,    # +% de dano das habilidades do personagem
    "low_hp_damage_pct": 0.0,    # +% de dano com vida baixa
    "boss_damage_pct": 0.0,      # +% de dano contra bosses
    "chain3_heal": 0,            # cura (HP) quando a chain chega a x3 ou mais
    "floor_heal_pct": 0.0,       # cura extra (% da vida máx.) ao vencer um andar
    # ---- cartas da expansão do Modo Infinito ----
    "big_match_damage_pct": 0.0, # +% de dano em matches de 4 ou mais blocos
    "quick_damage_pct": 0.0,     # +% de dano em matches feitos em sequência rápida
    "execute_damage_pct": 0.0,   # +% de dano contra inimigo com menos de 30% de vida
    "opener_damage_pct": 0.0,    # +% de dano contra inimigo com mais de 70% de vida
    "momentum_pct": 0.0,         # +% de dano por jogada seguida sem ser atingido (acumula até 8x)
    "floor_damage_pct": 0.0,     # +% de dano por andar já vencido (limite de +60%)
    "chain_energy": 0.0,         # energia extra por nível de chain acima de x1
    "crit_energy": 0.0,          # energia ganha a cada crítico
    "crit_heal": 0.0,            # HP recuperado a cada crítico
    "match_heal": 0.0,           # HP recuperado a cada rodada de match
    "ability_refund_pct": 0.0,   # devolve % do custo da habilidade (em energia) ao usá-la
    "ability_heal": 0.0,         # HP recuperado ao usar a habilidade
    "block_chance": 0.0,         # chance (0 a 0.5) de ignorar o dano de um ataque inimigo
    "thorns_pct": 0.0,           # devolve % do dano recebido ao inimigo (espinhos)
    "status_resist_pct": 0.0,    # reduz a duração de veneno, silêncio, pressão e teias
    "boss_cooldown_pct": 0.0,    # +% de tempo entre ataques de BOSSES
    "second_wind_pct": 0.0,      # 1x por andar: ao morrer, volta com esta fração da vida máx.
}


class Player:
    def __init__(self, char_id, data):
        self.char_id = char_id
        self.name = data["name"]
        self.color = tuple(data.get("color", (150, 150, 150)))
        self.image_id = data.get("image")          # nome do arquivo de arte (opcional)
        self.char_class = data.get("class", "")
        self.max_hp = data["max_hp"]
        self.hp = float(self.max_hp)
        self.energy_max = data.get("energy_max", 100)
        self.energy = 0.0
        self.passive_name = data.get("passive_name", "")
        self.passive_text = data.get("passive_text", "")
        self.passive_params = data.get("passive_params", {})
        self.ability_name = data.get("ability_name", "")
        self.ability_text = data.get("ability_text", "")
        self.ability_cost = data.get("ability_cost", 50)
        self.ability_params = data.get("ability_params", {})
        self.mods = dict(DEFAULT_MODS)

    # ----- ganchos que cada personagem sobrescreve -----
    def damage_multiplier(self, chain_level, quick):
        """Multiplicador de dano da PASSIVA."""
        return 1.0

    def energy_bonus(self, match_lengths):
        """Energia extra da PASSIVA."""
        return 0.0

    def on_match(self, combat, level, match_lengths):
        """Chamado a cada rodada de match do jogador (passivas que reagem a matches)."""

    def use_ability(self, combat):
        """Efeito da HABILIDADE."""

    # ----- energia e habilidade -----
    def current_ability_cost(self):
        cost = self.ability_cost * (1.0 + self.mods["ability_cost_pct"])
        return max(10, int(round(cost)))

    def can_use_ability(self):
        return self.energy >= self.current_ability_cost()

    def spend_ability(self):
        self.energy -= self.current_ability_cost()

    def add_energy(self, amount):
        self.energy = min(self.energy_max, self.energy + amount)

    # ----- vida -----
    def take_damage(self, amount):
        self.hp = max(0.0, self.hp - amount)

    def heal(self, amount):
        self.hp = min(float(self.max_hp), self.hp + amount)

    def update(self, dt):
        if self.mods["regen_per_sec"] > 0 and self.hp > 0:
            self.heal(self.mods["regen_per_sec"] * dt)

    # ----- recompensas -----
    def apply_reward(self, reward):
        for effect in reward.get("effects", []):
            kind, value = effect["type"], effect["value"]
            if kind == "max_hp":
                self.max_hp = max(1, self.max_hp + value)       # cartas de risco podem reduzir a vida máxima
                self.hp = min(float(self.max_hp), max(1.0, self.hp + value))
            elif kind == "heal_pct":
                self.heal(self.max_hp * value)
            elif kind == "energy":
                self.add_energy(value)
            elif kind in self.mods:
                self.mods[kind] += value
            else:
                log.warning("Efeito de recompensa desconhecido: %s", kind)

    def mod_lines(self):
        """Resumo dos bônus ativos para o HUD."""
        m = self.mods
        lines = []
        if m["damage_pct"]:
            lines.append(f"Dano +{round(m['damage_pct'] * 100)}%")
        if m["chain_damage_pct"]:
            lines.append(f"Dano de chain +{round(m['chain_damage_pct'] * 100)}%")
        if m["energy_gain_pct"]:
            lines.append(f"Energia +{round(m['energy_gain_pct'] * 100)}%")
        if m["enemy_cooldown_pct"]:
            lines.append(f"Inimigo {round(m['enemy_cooldown_pct'] * 100)}% mais lento")
        if m["explosion_match5"]:
            lines.append(f"Match 5+: explosão ({m['explosion_match5']})")
        if m["explosion_chain"]:
            lines.append(f"Chain: explosão ({m['explosion_chain']})")
        if m["lifesteal_pct"]:
            lines.append(f"Vampirismo {round(m['lifesteal_pct'] * 100)}%")
        if m["regen_per_sec"]:
            lines.append(f"Regeneração {m['regen_per_sec']:g}/s")
        if m["chain_start"]:
            lines.append(f"Chains começam em x{1 + m['chain_start']}")
        if m["damage_reduction_pct"]:
            lines.append(f"Defesa {round(m['damage_reduction_pct'] * 100)}%")
        if m["crit_chance"]:
            lines.append(f"Crítico {round(m['crit_chance'] * 100)}%")
        if m["ability_power_pct"]:
            lines.append(f"Habilidade +{round(m['ability_power_pct'] * 100)}%")
        if m["low_hp_damage_pct"]:
            lines.append(f"Vida baixa: dano +{round(m['low_hp_damage_pct'] * 100)}%")
        if m["boss_damage_pct"]:
            lines.append(f"Contra boss +{round(m['boss_damage_pct'] * 100)}%")
        if m["chain3_heal"]:
            lines.append(f"Chain x3+: cura {m['chain3_heal']}")
        if m["floor_heal_pct"]:
            lines.append(f"Cura de andar +{round(m['floor_heal_pct'] * 100)}%")
        pct = lambda key: f"{round(m[key] * 100)}%"
        extra = (("big_match_damage_pct", "Match 4+: dano +"), ("quick_damage_pct", "Jogada rápida: dano +"),
                 ("execute_damage_pct", "Finalizar (<30%): dano +"), ("opener_damage_pct", "Abertura (>70%): dano +"),
                 ("momentum_pct", "Impulso: dano +"), ("floor_damage_pct", "Por andar: dano +"),
                 ("block_chance", "Esquiva "), ("thorns_pct", "Espinhos "), ("status_resist_pct", "Resist. a efeitos "),
                 ("boss_cooldown_pct", "Boss ataca mais lento +"), ("second_wind_pct", "Segunda chance "),
                 ("ability_refund_pct", "Habilidade devolve "))
        for key, label in extra:
            if m[key]:
                lines.append(label + pct(key) + ("/golpe" if key == "momentum_pct" else "/andar" if key == "floor_damage_pct" else ""))
        flat = (("chain_energy", "Chain: energia +"), ("crit_energy", "Crítico: energia +"), ("crit_heal", "Crítico: cura "),
                ("match_heal", "Match: cura "), ("ability_heal", "Habilidade: cura "))
        for key, label in flat:
            if m[key]:
                lines.append(f"{label}{m[key]:g}")
        return lines
