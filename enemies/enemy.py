"""
enemies/enemy.py - base de TODOS os inimigos.

O inimigo é um MODIFICADOR do puzzle: de tempos em tempos ele ataca o
jogador (dano) e usa uma habilidade que interfere no tabuleiro.
"""
import copy


class Enemy:
    is_boss = False

    def __init__(self, enemy_id, data, stats):
        self.id = enemy_id
        self.family = data.get("family", enemy_id)    # "tipo" visual (arte reserva)
        self.image_id = data.get("image", enemy_id)  # nome do arquivo de imagem
        self.character_id = data.get("character_id")  # preenchido quando o inimigo é um PERSONAGEM jogável
        self.art_folder = data.get("art_folder")     # ex.: "characters" (bosses que são personagens)
        self.is_super = bool(data.get("super", False))  # SUPER BOSS do Modo Infinito (visual e dificuldade próprios)
        self.appearance_message = data.get("appearance_message")   # {"text", "seconds"}: aviso na tela quando o boss aparece
        self.reward = data.get("reward")                          # {"cards", "rarity"}: cartas extras ao derrotá-lo
        self.portrait = data.get("portrait")          # desenho provisório a usar se não houver arquivo de arte
        self.name = data["name"]
        self.color = tuple(data.get("color", (200, 90, 50)))
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.damage = stats["damage"]
        self.cooldown = stats["cooldown"]
        self.passive_name = data.get("passive_name", "")
        self.passive_text = data.get("passive_text", "")
        self.passive_params = data.get("passive_params", {})
        self.abilities = copy.deepcopy(data.get("abilities", []))
        for ability in self.abilities:
            if "amount" in ability:
                ability["amount"] += stats.get("ability_bonus", 0)
        self._ability_index = 0

    def hp_fraction(self):
        return self.hp / self.max_hp if self.max_hp else 0.0

    def attack_damage(self):
        return int(round(self.damage))

    def _traits(self):
        """Onde ficam as passivas genéricas (o Boss usa 'mechanics')."""
        return self.passive_params

    def regen_per_sec(self):
        """Regeneração de vida do inimigo (passiva opcional 'regen_pct' = fração da vida máx. por segundo)."""
        return self.max_hp * float(self._traits().get("regen_pct", 0.0))

    def attack_heal(self):
        """Vida que o inimigo recupera ao atacar (passiva opcional 'attack_heal_pct' = fração da vida máx.)."""
        return int(round(self.max_hp * float(self._traits().get("attack_heal_pct", 0.0))))

    def next_ability(self):
        if not self.abilities:
            return None
        ability = self.abilities[self._ability_index % len(self.abilities)]
        self._ability_index += 1
        return ability

    def cooldown_factor(self):
        """Multiplica o tempo entre ataques (menor = ataca mais rápido).
        Passiva genérica (opcional no JSON): enrage_hp + enrage_factor."""
        limit = self.passive_params.get("enrage_hp")
        if limit is not None and self.hp_fraction() < limit:
            return self.passive_params.get("enrage_factor", 0.75)
        return 1.0

    def current_cooldown(self, slow_pct=0.0):
        return self.cooldown * self.cooldown_factor() * (1.0 + slow_pct)

    def modify_incoming(self, amount, chain_level, biggest_match):
        """A PASSIVA pode reduzir o dano recebido dos matches.
        Passivas genéricas (opcionais no JSON): armor, chain1_reduction, match3_reduction."""
        p = self.passive_params
        if p.get("armor"):
            amount *= 1.0 - p["armor"]
        if p.get("chain1_reduction") and chain_level < 2:
            amount *= 1.0 - p["chain1_reduction"]
        if p.get("match3_reduction") and biggest_match <= 3:
            amount *= 1.0 - p["match3_reduction"]
        return int(round(amount))

    def passive_label(self):
        if self.passive_name:
            return f"{self.passive_name}: {self.passive_text}"
        return ""
