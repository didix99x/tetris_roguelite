"""
ui/shop_screen.py - LOJA (pontos permanentes). Abas: CARTAS | UPGRADES | ÁLBUM | BESTIÁRIO | HISTÓRICO.

Controles: Q (habilidade) / PageUp / PageDown / LB-RB (L1-R1) = trocar de aba, setas = navegar, Enter/Espaço = comprar, Esc = voltar. Mouse também funciona.
Toda a lógica (custos, valores, compras) está em game/shop.py; aqui só se desenha e se lê a entrada.
"""
import types

import pygame

import config
from characters import unlock_hint
from game import shop as logic
from rewards.reward import rarity_color, rarity_name
from ui import theme
from ui.card_art import card_art, draw_card_thumb
from ui.character_select import _who
from ui.portraits import draw_portrait
from ui.widgets import controller_hint, draw_bar, draw_inner_box, draw_panel, draw_text, draw_wrapped

TABS = ("CARTAS", "UPGRADES", "ÁLBUM", "BESTIÁRIO", "HISTÓRICO")
RARITY_ORDER = {"common": 0, "rare": 1, "epic": 2, "legendary": 3}
PAGE_CARDS, COLS = 12, 3
ALBUM_COLS, ALBUM_PAGE = 13, 52          # 4 linhas por página (a 5ª sobreporia o rodapé)


class ShopScreen:
    def __init__(self, game):
        self.game = game
        self.data = game.data
        self.shop = game.data["shop"]
        self.progress = game.progress
        self.tab = 0
        self.index = [0, 0, 0, 0, 0]          # seleção de cada aba
        self.attr = 0                          # atributo selecionado na aba UPGRADES
        self.message, self.message_time = "", 0.0
        self.mouse = (-9999, -9999)            # posição do mouse (coordenadas do jogo): só para o DESTAQUE, nunca compra sozinho
        self.tab_rects = [pygame.Rect(40 + i * 218, 92, 208, 44) for i in range(len(TABS))]
        self.buy_rect = pygame.Rect(1030, 600, 210, 54)
        self.cards = sorted(logic.shop_cards(self.data["rewards"]), key=lambda c: (RARITY_ORDER[c["rarity"]], c["name"]))
        self.all_cards = sorted(self.data["rewards"]["rewards"], key=lambda c: (RARITY_ORDER[c["rarity"]], c["name"]))
        self.chars = list(self.data["characters"].keys())

    # ------------------------------------------------------------ ações (também usadas pelos testes)
    def say(self, text):
        self.message, self.message_time = text, 2.2

    def selected_card(self):
        return self.cards[self.index[0]] if self.cards else None

    def buy_selected(self):
        if self.tab == 0 and self.selected_card():
            ok, msg = logic.buy_card(self.progress, self.shop, self.selected_card())
            self.game.audio.play("reward" if ok else "select")
            self.say(msg)
        elif self.tab == 1:
            attr = logic.ATTRIBUTES[self.attr]
            ok, msg = logic.buy_upgrade(self.progress, self.shop, self.data["characters"], self.chars[self.index[1]], attr)
            self.game.audio.play("reward" if ok else "select")
            self.say(msg)

    # ------------------------------------------------------------ entrada
    def hovered(self, rect):
        """True se o mouse está sobre o retângulo (o destaque some sozinho quando o mouse sai)."""
        return rect.collidepoint(self.mouse)

    def _hover_glow(self, surface, rect, radius=10):
        """Destaque discreto do mouse: leve clareada + contorno claro (não cobre texto, imagem nem preço)."""
        glow = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glow, (255, 255, 255, 26), glow.get_rect(), border_radius=radius)
        surface.blit(glow, rect.topleft)
        pygame.draw.rect(surface, (255, 240, 190), rect, width=2, border_radius=radius)

    def handle_input(self, inp):
        self.mouse = inp.mouse_pos
        if inp.pressed("back"):
            self.game.audio.play("select")
            self.game.change_state("MENU")
            return
        if inp.pressed("ability") or inp.pressed("tab_next"):          # LB/RB (L1/R1) ou PageUp/PageDown: uma aba por toque
            self.tab = (self.tab + 1) % len(TABS)
        elif inp.pressed("tab_prev"):
            self.tab = (self.tab - 1) % len(TABS)
        step = {"left": -1, "right": 1}
        for name, delta in step.items():
            if inp.pressed(name):
                self._move(delta, 0)
        for name, delta in (("up", -1), ("down", 1)):
            if inp.pressed(name):
                self._move(0, delta)
        if inp.pressed("swap"):
            self.buy_selected()
        if inp.click:
            for i, rect in enumerate(self.tab_rects):
                if rect.collidepoint(inp.click):
                    self.tab = i
            if self.tab in (0, 1) and self.buy_rect.collidepoint(inp.click):
                self.buy_selected()
            self._click_select(inp.click)

    def _move(self, dx, dy):
        t = self.tab
        if t == 0 and self.cards:
            self.index[0] = max(0, min(len(self.cards) - 1, self.index[0] + dx + dy * COLS))
        elif t == 1:
            if dx:
                self.index[1] = (self.index[1] + dx) % len(self.chars)
            if dy:
                self.attr = (self.attr + dy) % len(logic.ATTRIBUTES)
        elif t == 2:
            self.index[2] = max(0, min(len(self.all_cards) - 1, self.index[2] + dx + dy * ALBUM_COLS))
        elif t in (3, 4):
            n = len(self._bestiary()) if t == 3 else len(self.progress.history)
            self.index[t] = max(0, min(max(0, n - 1), self.index[t] + dx + dy))

    def _click_select(self, pos):
        if self.tab == 0:
            for i, rect in self._card_rects():
                if rect.collidepoint(pos):
                    self.index[0] = i
        elif self.tab == 2:
            for i, rect in self._album_rects():
                if rect.collidepoint(pos):
                    self.index[2] = i
        elif self.tab == 1:
            for k in range(4):
                if pygame.Rect(60, 400 + k * 52, 520, 44).collidepoint(pos):
                    self.attr = k

    def update(self, dt):
        self.message_time = max(0.0, self.message_time - dt)

    # ------------------------------------------------------------ desenho
    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
        draw_text(surface, "LOJA", 56, config.ACCENT_COLOR, (640, 46), shadow=True)
        draw_text(surface, f"PONTOS: {self.progress.points}", 34, (255, 215, 90), (1180, 46), "center", shadow=True)
        for i, (name, rect) in enumerate(zip(TABS, self.tab_rects)):
            active = i == self.tab
            pygame.draw.rect(surface, (58, 58, 96) if active else (30, 30, 46), rect, border_radius=10)
            pygame.draw.rect(surface, config.ACCENT_COLOR if active else (80, 80, 110), rect, width=3 if active else 2, border_radius=10)
            draw_text(surface, name, 26, config.TEXT_COLOR if active else config.MUTED_TEXT_COLOR, rect.center)
            if self.hovered(rect) and not active:
                self._hover_glow(surface, rect)
        [self._draw_cards, self._draw_upgrades, self._draw_album, self._draw_bestiary, self._draw_history][self.tab](surface)
        if self.message_time > 0:
            bad = "INSUFICIENTES" in self.message or "MÁXIMO" in self.message or "DESBLOQUEIE" in self.message or "JÁ" in self.message
            draw_text(surface, self.message, 34, (255, 110, 110) if bad else (130, 240, 150), (640, 672), shadow=True)
        draw_text(surface, controller_hint(self.game, "Q / PgUp / PgDn: abas    Setas: navegar    Enter: comprar    Esc: voltar",
                                           (("tabs", "abas"), ("move", "navegar"), ("swap", "comprar"), ("back", "voltar"))),
                  22, config.MUTED_TEXT_COLOR, (640, 704))

    # ---- CARTAS ----
    def _card_rects(self):
        page = self.index[0] // PAGE_CARDS
        out = []
        for n, i in enumerate(range(page * PAGE_CARDS, min(len(self.cards), (page + 1) * PAGE_CARDS))):
            out.append((i, pygame.Rect(34 + (n % COLS) * 408, 150 + (n // COLS) * 104, 396, 92)))
        return out

    def _draw_cards(self, surface):
        for i, rect in self._card_rects():
            card = self.cards[i]
            state = logic.card_display_state(self.progress, self.shop, card)
            owned, active = state == "DESBLOQUEADA", i == self.index[0]
            pygame.draw.rect(surface, (50, 50, 78) if active else (30, 30, 46), rect, border_radius=10)
            pygame.draw.rect(surface, rarity_color(card), rect, width=4 if active else 2, border_radius=10)
            draw_card_thumb(surface, pygame.Rect(rect.x + 4, rect.y + 4, 84, 84), card, locked=(state == "BLOQUEADA"))
            draw_text(surface, card["name"], 26, config.TEXT_COLOR, (rect.x + 100, rect.y + 16), "midleft")
            tag = rarity_name(card).upper() + ("  -  EXCLUSIVA" if card.get("character") else "")
            draw_text(surface, tag, 18, rarity_color(card), (rect.x + 100, rect.y + 42), "midleft")
            color = {"DESBLOQUEADA": (130, 240, 150), "DISPONÍVEL": (255, 215, 90), "BLOQUEADA": (150, 150, 170)}[state]
            label = state if owned else f"{state}  -  {logic.card_cost(self.shop, card)} pts"
            draw_text(surface, label, 20, color, (rect.x + 100, rect.y + 68), "midleft")
            if self.hovered(rect):
                self._hover_glow(surface, rect)
        pages = max(1, (len(self.cards) + PAGE_CARDS - 1) // PAGE_CARDS)
        draw_text(surface, f"Página {self.index[0] // PAGE_CARDS + 1}/{pages}", 20, config.MUTED_TEXT_COLOR, (640, 570))
        card = self.selected_card()
        if card:
            self._draw_card_info(surface, card)

    def _draw_card_info(self, surface, card):
        box = pygame.Rect(34, 590, 980, 86)
        draw_inner_box(surface, box)
        draw_text(surface, f"{card['name']}  ({rarity_name(card)})", 26, config.TEXT_COLOR, (box.x + 14, box.y + 8), "topleft")
        draw_wrapped(surface, card["description"], 22, config.MUTED_TEXT_COLOR, (box.x + 14, box.y + 38), box.width - 28, 24)
        ok, why = logic.can_buy_card(self.progress, self.shop, card)
        state = logic.card_display_state(self.progress, self.shop, card)
        self._draw_buy_button(surface, f"COMPRAR ({logic.card_cost(self.shop, card)})" if state != "DESBLOQUEADA" else "DESBLOQUEADA", ok)

    def _draw_buy_button(self, surface, text, enabled):
        pygame.draw.rect(surface, (40, 110, 60) if enabled else (50, 50, 64), self.buy_rect, border_radius=12)
        pygame.draw.rect(surface, (130, 240, 150) if enabled else (90, 90, 110), self.buy_rect, width=3, border_radius=12)
        draw_text(surface, text, 26, config.TEXT_COLOR if enabled else (130, 130, 150), self.buy_rect.center)
        if enabled and self.hovered(self.buy_rect):
            self._hover_glow(surface, self.buy_rect, 12)

    # ---- UPGRADES ----
    def _draw_upgrades(self, surface):
        cid = self.chars[self.index[1]]
        cdata = self.data["characters"][cid]
        unlocked = self.progress.is_unlocked(cid)
        draw_panel(surface, (40, 150, 560, 500))
        draw_text(surface, "<", 60, config.ACCENT_COLOR, (70, 250))
        draw_text(surface, ">", 60, config.ACCENT_COLOR, (570, 250))
        draw_portrait(surface, (260, 170), 160, _who(cid, cdata))
        if not unlocked:
            shade = pygame.Surface((160, 160), pygame.SRCALPHA)
            shade.fill((8, 8, 16, 190))
            surface.blit(shade, (260, 170))
        draw_text(surface, cdata["name"].upper(), 38, config.TEXT_COLOR if unlocked else (140, 140, 160), (320, 355), shadow=True)
        draw_text(surface, f"{cdata.get('class', '')}", 22, config.MUTED_TEXT_COLOR, (320, 382))
        if not unlocked:
            draw_text(surface, "BLOQUEADO", 28, (255, 120, 120), (320, 420))
            draw_wrapped(surface, "DESBLOQUEIE ESTE PERSONAGEM PARA LIBERAR OS UPGRADES.", 22, config.MUTED_TEXT_COLOR, (70, 450), 500, 26)
            draw_wrapped(surface, unlock_hint(cdata), 22, (255, 215, 90), (70, 520), 500, 26)
        for k, attr in enumerate(logic.ATTRIBUTES):
            info = logic.upgrade_info(self.progress, self.shop, self.data["characters"], cid, attr)
            y = 400 + k * 52
            if unlocked:
                if k == self.attr:
                    pygame.draw.rect(surface, (60, 60, 98), (60, y - 4, 520, 44), border_radius=8)
                draw_text(surface, info["label"], 24, config.TEXT_COLOR, (74, y + 18), "midleft")
                draw_bar(surface, (200, y + 4, 280, 24), info["level"], info["max"], (110, 190, 255), key=None)
                draw_text(surface, f"{info['level']}/{info['max']}", 22, config.TEXT_COLOR, (520, y + 18), "midleft")
                if self.hovered(pygame.Rect(60, y - 4, 520, 44)):
                    self._hover_glow(surface, pygame.Rect(60, y - 4, 520, 44), 8)
        if unlocked:
            self._draw_upgrade_detail(surface, cid)

    def _draw_upgrade_detail(self, surface, cid):
        attr = logic.ATTRIBUTES[self.attr]
        info = logic.upgrade_info(self.progress, self.shop, self.data["characters"], cid, attr)
        box = pygame.Rect(640, 150, 600, 430)
        draw_panel(surface, box)
        title = info["label"] + (f" ({info['what']})" if info["what"] else "")
        draw_text(surface, f"{title} - NÍVEL {info['level']}/{info['max']}", 28, config.ACCENT_COLOR, (box.x + 24, box.y + 24), "midleft", shadow=True)
        draw_wrapped(surface, info["text"], 24, config.MUTED_TEXT_COLOR, (box.x + 24, box.y + 60), box.width - 48, 28)
        if info["at_max"]:
            draw_text(surface, f"ATUAL: {info['current']}", 34, config.TEXT_COLOR, (box.x + 24, box.y + 160), "midleft")
            draw_text(surface, "MÁXIMO", 44, (130, 240, 150), (box.centerx, box.y + 260), shadow=True)
        else:
            for n, (label, value) in enumerate((("ATUAL", info["current"]), ("PRÓXIMO", info["next"]), ("AUMENTO", info["increase"]),
                                                  ("CUSTO", f"{info['cost']} pts"))):
                draw_text(surface, f"{label}:", 28, config.MUTED_TEXT_COLOR, (box.x + 24, box.y + 150 + n * 52), "midleft")
                draw_text(surface, value, 34, (255, 215, 90) if label == "CUSTO" else config.TEXT_COLOR, (box.x + 220, box.y + 150 + n * 52), "midleft", shadow=True)
        ok, why = logic.can_upgrade(self.progress, self.shop, self.data["characters"], cid, attr)
        self._draw_buy_button(surface, "COMPRAR" if not info["at_max"] else "MÁXIMO", ok)
        if not ok and why and why != "MÁXIMO":
            draw_text(surface, why, 22, (255, 130, 130), (box.centerx, box.y + 380))

    # ---- ÁLBUM ----
    def _album_rects(self):
        page = self.index[2] // ALBUM_PAGE
        out = []
        for n, i in enumerate(range(page * ALBUM_PAGE, min(len(self.all_cards), (page + 1) * ALBUM_PAGE))):
            out.append((i, pygame.Rect(34 + (n % ALBUM_COLS) * 94, 150 + (n // ALBUM_COLS) * 92, 84, 84)))
        return out

    def _album_state(self, card):
        if card.get("shop") and card["id"] not in self.progress.purchased_cards:
            return "BLOQUEADA"
        return "COMPRADA" if card.get("shop") else "DESBLOQUEADA"

    def _draw_album(self, surface):
        for i, rect in self._album_rects():
            card = self.all_cards[i]
            state = self._album_state(card)
            draw_card_thumb(surface, rect, card, badge="LOJA" if state == "COMPRADA" else None, locked=(state == "BLOQUEADA"), active=(i == self.index[2]))
            if self.hovered(rect):
                self._hover_glow(surface, rect, 6)
        card = self.all_cards[self.index[2]]
        state = self._album_state(card)
        total = len(self.all_cards)
        have = sum(1 for c in self.all_cards if self._album_state(c) != "BLOQUEADA")
        draw_text(surface, f"COLEÇÃO: {have}/{total} cartas desbloqueadas   (página {self.index[2] // ALBUM_PAGE + 1}/{(total + ALBUM_PAGE - 1) // ALBUM_PAGE})",
                  22, config.MUTED_TEXT_COLOR, (640, 570))
        box = pygame.Rect(34, 590, 1210, 80)
        draw_inner_box(surface, box)
        draw_text(surface, f"{card['name']}  ({rarity_name(card)})  -  {state}", 26, rarity_color(card), (box.x + 14, box.y + 8), "topleft")
        draw_wrapped(surface, card["description"] if state != "BLOQUEADA" else f"Desbloqueie na aba CARTAS por {logic.card_cost(self.shop, card)} pontos.",
                     22, config.MUTED_TEXT_COLOR, (box.x + 14, box.y + 40), box.width - 28, 24)

    # ---- BESTIÁRIO ----
    def _entity_data(self, eid):
        e = self.data["enemies"]
        if eid in e["enemies"]:
            return e["enemies"][eid]
        if eid.startswith("boss_inf_"):
            return e["infinite_bosses"].get(eid[len("boss_inf_"):])
        if eid == "boss_yoshi":
            return e["yoshi"]["story"]
        if eid == "boss_yoshi_supreme":
            return e["yoshi"]["infinite"]
        if eid.startswith("boss_char_"):
            c = self.data["characters"].get(eid[len("boss_char_"):])
            cid = eid[len("boss_char_"):]       # character_id/family: sem eles a arte de quem tem outro nome de imagem (Tali -> assassin.gif) não era achada
            return {"name": c["name"], "color": c.get("color", (150, 150, 150)), "image": c.get("image"), "art_folder": "characters",
                    "character_id": cid, "family": cid} if c else None
        if eid.startswith("boss_"):
            return e["bosses"].get(eid[len("boss_"):])
        return None

    def _bestiary(self):
        rows = []
        for eid, count in sorted(self.progress.bestiary.items(), key=lambda kv: (-kv[1], kv[0])):
            data = self._entity_data(eid)
            if data:
                rows.append((eid, data, count))
        return rows

    def _draw_bestiary(self, surface):
        rows = self._bestiary()
        if not rows:
            draw_text(surface, "Nenhum inimigo derrotado ainda. Jogue para preencher o Bestiário!", 28, config.MUTED_TEXT_COLOR, (640, 360))
            return
        first = (self.index[3] // 6) * 6
        for n, (eid, data, count) in enumerate(rows[first:first + 6]):
            rect = pygame.Rect(40, 150 + n * 82, 1200, 74)
            active = first + n == self.index[3]
            pygame.draw.rect(surface, (50, 50, 78) if active else (30, 30, 46), rect, border_radius=10)
            pygame.draw.rect(surface, (110, 110, 160) if active else (70, 70, 100), rect, width=2, border_radius=10)
            ent = types.SimpleNamespace(id=eid, color=tuple(data.get("color", (150, 150, 150))), name=data["name"], image_id=data.get("image", eid),
                                        art_folder=data.get("art_folder"), family=data.get("family", eid), portrait=data.get("portrait"),
                                        is_boss=eid.startswith("boss_"), is_super=bool(data.get("super")), character_id=data.get("character_id"))
            draw_portrait(surface, (rect.x + 6, rect.y + 5), 64, ent)
            draw_text(surface, data["name"], 26, config.TEXT_COLOR, (rect.x + 84, rect.y + 18), "midleft")
            draw_text(surface, f"Derrotado {count}x", 20, (255, 215, 90), (rect.x + 84, rect.y + 48), "midleft")
            abil = ", ".join(a.get("name", a["type"]) for a in data.get("abilities", [])[:4]) or "-"
            passive = data.get("passive_name") or data.get("mechanic_name") or "-"
            draw_text(surface, f"Passiva: {passive}", 20, config.MUTED_TEXT_COLOR, (rect.x + 420, rect.y + 18), "midleft")
            draw_text(surface, f"Habilidades: {abil}"[:70], 20, config.MUTED_TEXT_COLOR, (rect.x + 420, rect.y + 48), "midleft")
            if self.hovered(rect):
                self._hover_glow(surface, rect)
        draw_text(surface, f"{self.index[3] + 1}/{len(rows)} inimigos no Bestiário", 20, config.MUTED_TEXT_COLOR, (640, 660))

    # ---- HISTÓRICO ----
    def _draw_history(self, surface):
        hist = self.progress.history
        if not hist:
            draw_text(surface, "Nenhuma run registrada ainda.", 28, config.MUTED_TEXT_COLOR, (640, 360))
            return
        names = {k: v["name"] for k, v in self.data["characters"].items()}
        for n, h in enumerate(hist[:10]):
            y = 160 + n * 48
            color = {"vitória": (130, 240, 150), "derrota": (255, 130, 130)}.get(h.get("result"), config.MUTED_TEXT_COLOR)
            line = (f"{h.get('date', '')}   {names.get(h.get('character'), h.get('character'))}   "
                    f"{'Infinito' if h.get('mode') == 'infinite' else 'Normal'}   andar {h.get('floor')}   {h.get('cards', 0)} cartas   +{h.get('points', 0)} pts")
            pygame.draw.rect(surface, (30, 30, 46), (40, y - 18, 1200, 40), border_radius=8)
            draw_text(surface, h.get("result", "").upper(), 22, color, (60, y), "midleft")
            draw_text(surface, line, 22, config.TEXT_COLOR, (220, y), "midleft")
