"""
bosses/boss.py - BOSSES.

Um boss NÃO é só "inimigo com mais vida": cada um tem MECÂNICAS que
interferem no puzzle (definidas em data/enemies.json, seção "bosses"):

  chain_armor      dano de chains x1 é reduzido (ex.: 0.4 = -40%)
  enrage_hp        abaixo dessa fração de vida o boss ataca mais rápido...
  enrage_factor    ...multiplicando o cooldown por este valor
  phase_two_hp     abaixo dessa fração de vida as habilidades ficam mais fortes...
  phase_two_boost  ...multiplicando a quantidade por este valor
  cycle_all        (nas habilidades) o boss alterna entre todas elas

Mecânicas extras (opcionais; usadas pelos bosses do Modo Infinito):
  armor              dano de TODOS os matches reduzido (0.2 = -20%)
  match3_reduction   matches de 3 blocos causam menos dano
  phase_three_hp     abaixo dessa fração de vida entra na FASE 3...
  phase_three_factor ...multiplicando o cooldown por este valor (ataca mais rápido)
  phase_three_boost  ...e multiplicando a quantidade das habilidades por este valor
  regen_pct          regenera esta fração da vida máxima por segundo
  attack_heal_pct    recupera esta fração da vida máxima a cada ataque
"""
import copy

from enemies.enemy import Enemy


class Boss(Enemy):
    is_boss = True

    def __init__(self, enemy_id, data, stats):
        super().__init__(enemy_id, data, stats)
        self.mechanics = data.get("mechanics", {})
        self.title = data.get("title", "")
        self.mechanic_name = data.get("mechanic_name", "")
        self.mechanic_text = data.get("mechanic_text", "")

    def _traits(self):
        return self.mechanics

    def cooldown_factor(self):
        factor = 1.0
        hp_limit = self.mechanics.get("enrage_hp")
        if hp_limit is not None and self.hp_fraction() < hp_limit:
            factor = self.mechanics.get("enrage_factor", 0.7)
        phase3 = self.mechanics.get("phase_three_hp")
        if phase3 is not None and self.hp_fraction() < phase3:
            factor *= self.mechanics.get("phase_three_factor", 0.8)
        return factor

    def modify_incoming(self, amount, chain_level, biggest_match):
        armor = self.mechanics.get("chain_armor")
        if armor and chain_level < 2:
            amount = amount * (1.0 - armor)
        if self.mechanics.get("armor"):
            amount = amount * (1.0 - self.mechanics["armor"])
        if self.mechanics.get("match3_reduction") and biggest_match <= 3:
            amount = amount * (1.0 - self.mechanics["match3_reduction"])
        return int(round(amount))

    def next_ability(self):
        ability = super().next_ability()
        if ability is None:
            return None
        boost = 1.0
        limit = self.mechanics.get("phase_two_hp")
        if limit is not None and self.hp_fraction() < limit:
            boost = self.mechanics.get("phase_two_boost", 1.5)
        limit3 = self.mechanics.get("phase_three_hp")
        if limit3 is not None and self.hp_fraction() < limit3:
            boost = self.mechanics.get("phase_three_boost", boost)
        if boost != 1.0 and "amount" in ability:
            ability = copy.deepcopy(ability)
            ability["amount"] = int(round(ability["amount"] * boost))
        return ability

    def passive_label(self):
        if self.mechanic_name:
            return f"{self.mechanic_name}: {self.mechanic_text}"
        return super().passive_label()
