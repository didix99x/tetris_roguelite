"""
combat/combat.py - A BATALHA (puzzle = combate).

Controla: troca de blocos, matches, chains, dano no inimigo, ataques do
inimigo e fim da batalha. NÃO desenha nada; a interface lê o estado daqui
e consome os "eventos" (pop_events) para mostrar efeitos e tocar sons.

Fases do puzzle:
  IDLE      -> jogador pode mexer
  CLEARING  -> matches piscando antes de sumir
  FALLING   -> blocos caindo; depois procura novos matches (chain)
"""
import random

import config
from board.board import Board
from board.chain import ChainTracker
from board.matcher import matched_cells
from combat import damage, effects

IDLE = "idle"
CLEARING = "clearing"
FALLING = "falling"


class Combat:
    def __init__(self, player, enemy, floor_number, rng=None):
        self.rng = rng or random.Random()
        self.player = player
        self.enemy = enemy
        self.floor_number = floor_number
        self.board = Board(rng=self.rng)
        self.chain = ChainTracker()

        self.phase = IDLE
        self.phase_timer = 0.0
        self.source = "player"        # quem causou o match atual: "player" ou "enemy"
        self.clearing_cells = set()
        self.result = None            # None, "win" ou "lose"
        self.events = []
        self.elapsed = 0.0

        self.momentum = 0             # cartas "Impulso": jogadas seguidas sem ser atingido
        self.second_wind_used = False  # cartas "Segunda chance": 1x por andar
        self._enemy_regen = 0.0
        self.enemy_timer = enemy.current_cooldown(self._slow_pct())
        self.enemy_cooldown_total = self.enemy_timer
        self.haste_time = 0.0         # efeito "Pressão" (Golem)
        self.haste_factor = 1.0
        # efeitos novos de habilidades de inimigo
        self.poison_time = 0.0
        self.poison_dps = 0.0
        self.silence_time = 0.0
        self.ability_cd = 0.0         # recarga da habilidade do jogador (segundos restantes; config.ABILITY_COOLDOWN)
        self.blind_time = 0.0         # cegueira (só visual): segundos restantes
        self.blind_total = 0.0
        self.enemy_armor_time = 0.0
        self.enemy_armor_pct = 0.0

        self.last_player_match_time = -999.0
        self.quick_active = False
        self.chain_level = 0          # nível de chain mostrado (com bônus)
        self.chain_display_level = 0
        self.chain_display_time = 0.0

    def _slow_pct(self):
        """Quanto o inimigo fica mais lento entre ataques (cartas gerais + cartas contra boss)."""
        mods = self.player.mods
        return mods["enemy_cooldown_pct"] + (mods["boss_cooldown_pct"] if self.enemy.is_boss else 0.0)

    # ------------------------------------------------------------ eventos
    def emit(self, kind, **data):
        data["type"] = kind
        self.events.append(data)

    def pop_events(self):
        events, self.events = self.events, []
        return events

    # ------------------------------------------------------------ ações do jogador
    def move_cursor(self, dx, dy):
        self.board.move_cursor(dx, dy)

    def set_cursor(self, x, y):
        self.board.set_cursor(x, y)

    def try_swap(self):
        if self.result or self.phase != IDLE:
            return False
        if not self.board.swap_cursor():
            self.emit("swap_fail")
            return False
        self.emit("swap")
        self.start_resolve("player")
        return True

    def use_ability(self):
        if self.result or self.phase != IDLE:
            return False
        if self.ability_cd > 0 or self.silence_time > 0 or not self.player.can_use_ability():
            self.emit("ability_fail")            # em recarga (ou sem energia / silenciado): não ativa, não gasta energia
            return False
        self.ability_cd = config.ABILITY_COOLDOWN
        cost = self.player.current_ability_cost()
        self.player.spend_ability()
        mods = self.player.mods
        if mods["ability_refund_pct"] > 0:              # cartas de habilidade: devolve parte da energia
            self.player.add_energy(cost * min(1.0, mods["ability_refund_pct"]))
        if mods["ability_heal"] > 0:
            self.player.heal(mods["ability_heal"])
            self.emit("heal", amount=int(mods["ability_heal"]))
        self.emit("ability", name=self.player.ability_name)
        self.player.use_ability(self)
        return True

    # ------------------------------------------------------------ dano
    def deal_damage_to_enemy(self, amount, label=None):
        if label:   # dano de HABILIDADE (cartas "Habilidade +%")
            amount *= 1.0 + self.player.mods["ability_power_pct"]
        amount = int(round(amount))
        if amount <= 0 or self.result:
            return
        amount = min(amount, self.enemy.hp)
        self.enemy.hp -= amount
        self.emit("damage_enemy", amount=amount, label=label)
        steal = self.player.mods["lifesteal_pct"]
        if steal > 0:
            self.player.heal(amount * steal)
        if self.enemy.hp <= 0:
            self.result = "win"
            self.emit("win")

    # ------------------------------------------------------------ resolução de matches
    def start_resolve(self, source):
        """Procura matches no tabuleiro. Se achar, começa a limpar; senão, termina a chain."""
        self.source = source
        matches = self.board.find_matches()
        if not matches:
            self._end_chain()
            return

        count = self.chain.next()
        cells = matched_cells(matches)
        lengths = [m.length for m in matches]
        player = self.player
        level = count + (player.mods["chain_start"] if source == "player" else 0)
        self.chain_level = level

        cell_info = [(x, y, self.board.grid[y][x].color_id) for (x, y) in cells]
        self.emit("match", cells=cell_info, source=source, lengths=lengths)
        if source == "player" and level >= 2:
            self.emit("chain", level=level)

        extra_cells = set()
        if source == "player":
            if count == 1:
                window = player.passive_params.get("quick_window", 2.0)
                self.quick_active = (self.elapsed - self.last_player_match_time) <= window
                self.last_player_match_time = self.elapsed
            player.on_match(self, level, lengths)
            if player.mods["match_heal"]:
                player.heal(player.mods["match_heal"])
            if level >= 3 and player.mods["chain3_heal"]:
                player.heal(player.mods["chain3_heal"])
                self.emit("heal", amount=int(player.mods["chain3_heal"]))
            extra_cells = self._pick_explosion_cells(lengths, level, cells)
            self._deal_match_damage(lengths, level, len(extra_cells))
            self._give_energy(len(cells), lengths, level)
            if extra_cells:
                info = [(x, y, self.board.grid[y][x].color_id) for (x, y) in extra_cells]
                self.emit("explosion", cells=info)

        self.clearing_cells = cells | extra_cells
        for (x, y) in self.clearing_cells:
            self.board.grid[y][x].clearing = True
        self.phase = CLEARING
        self.phase_timer = config.CLEAR_TIME

    def _pick_explosion_cells(self, lengths, level, already):
        mods = self.player.mods
        amount = 0
        if max(lengths) >= 5:
            amount += mods["explosion_match5"]
        if level >= 2:
            amount += mods["explosion_chain"]
        if amount <= 0:
            return set()
        candidates = [(b.grid_x, b.grid_y) for b in self.board.blocks()
                      if not b.is_stone and (b.grid_x, b.grid_y) not in already]
        self.rng.shuffle(candidates)
        return set(candidates[:int(amount)])

    def _deal_match_damage(self, lengths, level, explosion_blocks):
        player = self.player
        mods = player.mods
        damage_pct = mods["damage_pct"]
        if player.hp < player.max_hp * damage.LOW_HP_THRESHOLD:
            damage_pct += mods["low_hp_damage_pct"]
        if self.enemy.is_boss:
            damage_pct += mods["boss_damage_pct"]
        # ---- cartas condicionais / de build da expansão ----
        if max(lengths) >= 4:
            damage_pct += mods["big_match_damage_pct"]
        if self.quick_active:
            damage_pct += mods["quick_damage_pct"]
        fraction = self.enemy.hp_fraction()
        if fraction < damage.EXECUTE_THRESHOLD:
            damage_pct += mods["execute_damage_pct"]
        elif fraction > damage.OPENER_THRESHOLD:
            damage_pct += mods["opener_damage_pct"]
        if mods["momentum_pct"]:
            damage_pct += mods["momentum_pct"] * self.momentum
            if self.chain.count == 1:                    # +1 acúmulo por jogada (não por chain)
                self.momentum = min(damage.MOMENTUM_MAX_STACKS, self.momentum + 1)
        if mods["floor_damage_pct"]:
            damage_pct += min(damage.FLOOR_DAMAGE_CAP, mods["floor_damage_pct"] * self.floor_number)
        total = damage.calculate_damage(
            lengths, level,
            damage_pct=damage_pct,
            chain_damage_pct=mods["chain_damage_pct"],
            extra_multiplier=player.damage_multiplier(level, self.quick_active),
        )
        total = self.enemy.modify_incoming(total, level, max(lengths))
        if self.enemy_armor_time > 0:
            total = int(round(total * (1.0 - self.enemy_armor_pct / 100.0)))
        if mods["crit_chance"] > 0 and self.rng.random() < min(1.0, mods["crit_chance"]):
            total = int(round(total * (damage.CRIT_BASE_MULTIPLIER + mods["crit_damage_pct"])))
            self.emit("crit")
            if mods["crit_energy"]:
                player.add_energy(mods["crit_energy"])
            if mods["crit_heal"]:
                player.heal(mods["crit_heal"])
        total += explosion_blocks * damage.EXPLOSION_DAMAGE_PER_BLOCK
        self.deal_damage_to_enemy(total)

    def _give_energy(self, blocks, lengths, level):
        gain = blocks * config.ENERGY_PER_BLOCK + level * config.ENERGY_PER_CHAIN_LEVEL
        gain += max(0, level - 1) * self.player.mods["chain_energy"]
        gain *= 1.0 + self.player.mods["energy_gain_pct"]
        gain += self.player.energy_bonus(lengths)
        self.player.add_energy(gain)

    def _finish_clear(self):
        self.board.remove_cells(self.clearing_cells)
        self.clearing_cells = set()
        self.board.gravity_and_refill()
        self.phase = FALLING
        self.phase_timer = config.FALL_SETTLE_TIME

    def _end_chain(self):
        if self.chain.count > 0 and self.source == "player":
            self.chain_display_level = self.chain_level
            self.chain_display_time = 1.2
            if self.chain_level >= 2:
                self.emit("chain_end", level=self.chain_level)
        self.chain.reset()
        self.chain_level = 0
        self.phase = IDLE
        if not self.board.has_possible_move():
            self.board.reshuffle()
            self.emit("shuffle")

    # ------------------------------------------------------------ inimigo
    def _enemy_attack(self):
        enemy = self.enemy
        self.enemy_timer = enemy.current_cooldown(self._slow_pct())
        self.enemy_cooldown_total = self.enemy_timer
        self.hurt_player(enemy.attack_damage())
        if self.result:
            return
        healed = min(enemy.max_hp - enemy.hp, enemy.attack_heal())     # passiva "attack_heal_pct"
        if healed > 0:
            enemy.hp += healed
            self.emit("enemy_heal", amount=healed)
        ability = enemy.next_ability()
        if ability is None:
            return
        mode, cells = effects.apply_enemy_ability(self, ability)
        self.emit("enemy_ability", name=ability.get("name", ability["type"]), cells=cells)
        if self.result:
            return
        if mode == "gravity":
            self.source = "enemy"
            self.board.gravity_and_refill()
            self.phase = FALLING
            self.phase_timer = config.FALL_SETTLE_TIME
        elif mode == "check":
            self.start_resolve("enemy")

    def hurt_player(self, amount):
        """Dano de um ATAQUE inimigo no jogador. Aplica defesa (ou vulnerabilidade), esquiva, espinhos
        e segunda chance. Devolve o dano causado (0 se esquivou)."""
        mods = self.player.mods
        reduction = min(damage.MAX_DAMAGE_REDUCTION, mods["damage_reduction_pct"])
        if reduction != 0:
            amount = max(1, int(round(amount * (1.0 - reduction))))
        chance = min(damage.MAX_BLOCK_CHANCE, mods["block_chance"])
        if chance > 0 and self.rng.random() < chance:
            self.emit("block")
            return 0
        self.player.take_damage(amount)
        self.emit("damage_player", amount=amount)
        self.momentum = 0
        if self.player.hp <= 0 and self._player_dies():
            return amount
        thorns = min(damage.MAX_THORNS, mods["thorns_pct"])
        if thorns > 0 and amount > 0:
            self.deal_damage_to_enemy(int(round(amount * thorns)))
        return amount

    def _player_dies(self):
        """True se o jogador realmente morreu. A carta 'Segunda chance' salva 1x por andar."""
        wind = self.player.mods["second_wind_pct"]
        if wind > 0 and not self.second_wind_used:
            self.second_wind_used = True
            self.player.hp = max(1.0, self.player.max_hp * min(1.0, wind))
            self.emit("heal", amount=int(self.player.hp))
            self.emit("second_wind")
            return False
        self.result = "lose"
        self.emit("lose")
        return True

    def enemy_progress(self):
        """0.0 (acabou de atacar) até 1.0 (vai atacar). Para a barra do HUD."""
        if self.enemy_cooldown_total <= 0:
            return 1.0
        return max(0.0, min(1.0, 1.0 - self.enemy_timer / self.enemy_cooldown_total))

    # ------------------------------------------------------------ atualização
    def update(self, dt):
        self.board.update(dt)
        if self.result:
            return
        self.elapsed += dt
        if self.ability_cd > 0:
            self.ability_cd = max(0.0, self.ability_cd - dt)
        if self.chain_display_time > 0:
            self.chain_display_time -= dt
        self.player.update(dt)
        if self.poison_time > 0:
            self.poison_time -= dt
            self.player.take_damage(self.poison_dps * dt)
            if self.player.hp <= 0 and self._player_dies():
                return
        regen = self.enemy.regen_per_sec()                  # passiva "regen_pct" (inimigos e bosses)
        if regen > 0 and self.enemy.hp < self.enemy.max_hp:
            self._enemy_regen += regen * dt
            whole = int(self._enemy_regen)
            if whole >= 1:
                self._enemy_regen -= whole
                self.enemy.hp = min(self.enemy.max_hp, self.enemy.hp + whole)
        if self.blind_time > 0:
            self.blind_time = max(0.0, self.blind_time - dt)
        if self.silence_time > 0:
            self.silence_time -= dt
        if self.enemy_armor_time > 0:
            self.enemy_armor_time -= dt

        if self.phase == CLEARING:
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                self._finish_clear()
        elif self.phase == FALLING:
            self.phase_timer -= dt
            if self.phase_timer <= 0 and not self.board.any_moving():
                self.start_resolve(self.source)
        if self.result:
            return

        speed = self.haste_factor if self.haste_time > 0 else 1.0
        if self.haste_time > 0:
            self.haste_time -= dt
        self.enemy_timer -= dt * speed
        if self.enemy_timer <= 0 and self.phase == IDLE:
            self._enemy_attack()

    def status_effects(self):
        """Textos curtos para o HUD."""
        out = []
        webs = self.board.count_webbed()
        stones = self.board.count_stones()
        if webs:
            out.append(f"Teias: {webs}")
        if stones:
            out.append(f"Pedras: {stones}")
        if self.haste_time > 0:
            out.append(f"Pressão: {self.haste_time:.0f}s")
        if self.poison_time > 0:
            out.append(f"Veneno: {self.poison_time:.0f}s")
        if self.silence_time > 0:
            out.append(f"Silêncio: {self.silence_time:.0f}s")
        if self.blind_time > 0:
            out.append(f"Cegueira: {self.blind_time:.0f}s")
        if self.enemy_armor_time > 0:
            out.append(f"Inimigo blindado: {self.enemy_armor_time:.0f}s")
        return out
