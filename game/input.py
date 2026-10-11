"""
<<<<<<< HEAD
game/input.py - ENTRADA (teclado, mouse e CONTROLE).
=======
game/input.py - ENTRADA (teclado e mouse).
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

As teclas vêm de settings.json ("controls"). O resto do jogo não pergunta
"qual tecla?", pergunta "qual AÇÃO?": left, right, up, down, swap,
ability, back.

Quer mudar as teclas? Edite o "controls" do settings.json
(nomes de teclas do pygame: "left", "a", "return", "space", "escape"...).
<<<<<<< HEAD

CONTROLE (Xbox, PlayStation ou compatível reconhecido pelo Windows): o D-pad e o analógico esquerdo viram
left/right/up/down e os botões viram swap/ability/back (settings.json > "gamepad"). Assim TODAS as telas
funcionam com controle sem mudar nada nelas. O tipo (Xbox/PlayStation) é detectado pelo nome do controle.
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
"""
import logging

import pygame

log = logging.getLogger(__name__)

# Só estas ações repetem quando a tecla fica pressionada.
REPEATABLE = {"left", "right", "up", "down"}

<<<<<<< HEAD
# nomes que indicam um controle PlayStation (o resto é tratado como Xbox/genérico)
PLAYSTATION_WORDS = ("playstation", "ps3", "ps4", "ps5", "dualshock", "dualsense", "sony", "wireless controller")


def detect_pad_kind(name):
    """'ps' para controles PlayStation, 'xbox' para o resto."""
    low = (name or "").lower()
    return "ps" if any(word in low for word in PLAYSTATION_WORDS) else "xbox"


# Ações do controle que podem ter botões (D-pad e analógico sempre movem, além destes).
PAD_ACTIONS = ("up", "down", "left", "right", "swap", "back", "ability", "tab_prev", "tab_next")

# Nome de cada comando na tela CONTROLE / JOYSTICK (ordem da tela).
PAD_ACTION_NAMES = (("up", "Cima"), ("down", "Baixo"), ("left", "Esquerda"), ("right", "Direita"),
                    ("swap", "Confirmar / Trocar"), ("back", "Voltar / Pausar"), ("ability", "Habilidade"),
                    ("tab_prev", "Aba anterior"), ("tab_next", "Próxima aba"))

# Botões padrão das abas quando o jogador não escolheu outros (settings > gamepad > tab_prev/tab_next = None).
# Xbox: LB=4 RB=5. PlayStation: L1/R1 = 9/10 (SDL novo) ou 4/5 (SDL antigo). Qualquer botão pode ser trocado no remapeamento.
TAB_DEFAULTS = {"xbox": {"tab_prev": [4], "tab_next": [5]},
                "ps": {"tab_prev": [4, 9], "tab_next": [5, 10]},
                None: {"tab_prev": [4], "tab_next": [5]}}

# Nomes dos botões por tipo de controle (a fonte do jogo não tem os símbolos ✕ ○ □ △, então usamos texto).
BUTTON_NAMES = {
    "xbox": {0: "A", 1: "B", 2: "X", 3: "Y", 4: "LB", 5: "RB", 6: "Back", 7: "Start", 8: "L3", 9: "R3"},
    "ps": {0: "Cruz", 1: "Bola", 2: "Quadrado", 3: "Triângulo", 4: "L1", 5: "R1", 9: "L1", 10: "R1"},
}

# textos dos botões mostrados na barra de teclas (a fonte padrão não tem os símbolos ✕ ○ □ △)
PAD_PROMPTS = {
    "xbox": {"move": "D-Pad", "swap": "A", "ability": "X", "back": "Start", "cancel": "B"},
    "ps": {"move": "D-Pad", "swap": "Cruz", "ability": "Quadrado", "back": "Options", "cancel": "Bola"},
    None: {"move": "D-Pad", "swap": "Botão 1", "ability": "Botão 3", "back": "Start", "cancel": "Botão 2"},
}

=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

class Input:
    def __init__(self, settings, to_canvas):
        self.settings = settings
        self.to_canvas = to_canvas    # converte posição da janela -> posição do jogo
        self.keymap = {}
        self.rebuild_keymap()
        self._held = set()
        self.actions = set()
        self.click = None             # posição do clique deste frame (ou None)
        self.mouse_pos = (0, 0)
<<<<<<< HEAD
        self.pads = {}                # controles conectados: instance_id -> joystick
        self.pad_kind = None          # 'xbox', 'ps' ou None (nenhum controle)
        self._axis_dir = {}           # direção atual do analógico (para gerar 1 ação por empurrão)
        self._active_pad = None       # id do controle usado por último
        self.last_device = "keyboard"  # último dispositivo usado: "keyboard" (teclado/mouse) ou "pad" (controle)
        self.capture_pad = False      # True durante o remapeamento: botões NÃO viram ações de jogo
        self.pad_pressed = []         # botões do controle pressionados neste quadro (para o remapeamento)

    def init_gamepads(self):
        """Procura controles já conectados (os que forem ligados depois chegam por evento)."""
        try:
            pygame.joystick.init()
            for i in range(pygame.joystick.get_count()):
                self._add_pad(pygame.joystick.Joystick(i))
        except Exception:                                  # sem suporte a controle: o jogo segue só com teclado
            log.exception("Controles indisponíveis")

    def _add_pad(self, joystick):
        try:
            joystick.init()
        except Exception:
            pass
        key = joystick.get_instance_id() if hasattr(joystick, "get_instance_id") else id(joystick)
        self.pads[key] = joystick
        self.pad_kind = detect_pad_kind(joystick.get_name())
        self._active_pad = key
        log.info("Controle conectado: %s (%s)", joystick.get_name(), self.pad_kind)

    def _set_active(self, instance_id):
        """O controle que acabou de ser usado vira o 'ativo' (muda os símbolos mostrados se for de outro tipo)."""
        pad = self.pads.get(instance_id)
        if pad is not None:
            self._active_pad = instance_id
            self.pad_kind = detect_pad_kind(pad.get_name())

    def pad_connected(self):
        return bool(self.pads)

    def pad_active(self):
        """True se há controle conectado E o jogador está usando o controle (senão as dicas continuam sendo as do teclado)."""
        return self.pad_connected() and self.last_device == "pad"

    def pad_name(self):
        pad = self.pads.get(getattr(self, "_active_pad", None)) or next(iter(self.pads.values()), None)
        if pad is None:
            return None
        try:
            return pad.get_name()
        except Exception:
            return "Controle"

    def pad_prompts(self):
        return PAD_PROMPTS.get(self.pad_kind, PAD_PROMPTS[None])

    # ---- botões configurados ----
    def pad_buttons(self, action):
        """Lista de botões da ação (o escolhido pelo jogador; ou o padrão do tipo de controle, nas abas)."""
        value = self.settings.get("gamepad").get(action)
        if value is None:
            return list(TAB_DEFAULTS.get(self.pad_kind, TAB_DEFAULTS[None]).get(action, []))
        return [int(b) for b in value]

    def button_name(self, button):
        names = BUTTON_NAMES.get(self.pad_kind, {})
        return names.get(button, f"Botão {button + 1}")

    def button_text(self, action):
        """Texto dos botões da ação para a tela ('A / B / Start' ou '(nenhum)')."""
        buttons = self.pad_buttons(action)
        return " / ".join(self.button_name(b) for b in buttons) if buttons else "(nenhum)"

    def pad_labels(self):
        """Textos para as dicas (barra de baixo, rodapés) conforme o controle ATIVO e os botões configurados."""
        def first(action, fallback):
            buttons = self.pad_buttons(action)
            return self.button_name(buttons[0]) if buttons else fallback
        base = self.pad_prompts()
        return {"move": base["move"], "swap": first("swap", "-"), "ability": first("ability", "-"),
                "back": first("back", "-"), "tab_prev": first("tab_prev", "-"), "tab_next": first("tab_next", "-")}

    def set_pad_button(self, action, button):
        """Associa `button` à ação (substitui os botões antigos dela). Devolve (ok, mensagem).
        REGRA: se o botão já pertence a OUTRO comando, nada é alterado e o jogador é avisado (sem sobrescrever em silêncio)."""
        for other, label in PAD_ACTION_NAMES:
            if other != action and button in self.pad_buttons(other):
                return False, f"{self.button_name(button)} já é usado em \"{label}\". Escolha outro botão (ou mude aquele comando antes)."
        cfg = self.settings.get("gamepad")
        cfg[action] = [int(button)]
        self.settings.save()
        label = dict(PAD_ACTION_NAMES)[action]
        return True, f"{label}: agora é {self.button_name(button)}."

    def reset_pad_defaults(self):
        """Volta os botões do controle ao padrão (só quando o jogador pedir)."""
        from game.settings import DEFAULT_SETTINGS
        cfg = self.settings.get("gamepad")
        for action in PAD_ACTIONS:
            default = DEFAULT_SETTINGS["gamepad"][action]
            cfg[action] = list(default) if default is not None else None
        self.settings.save()
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

    def rebuild_keymap(self):
        self.keymap = {}
        for action, names in self.settings.get("controls").items():
            for name in names:
                try:
                    code = pygame.key.key_code(name)
                except ValueError:
                    log.warning("Tecla desconhecida em settings.json: %s", name)
                    continue
                self.keymap.setdefault(code, []).append(action)

    def begin_frame(self):
        self.actions.clear()
<<<<<<< HEAD
        self.pad_pressed = []
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        self.click = None
        self.mouse_pos = self.to_canvas(pygame.mouse.get_pos())

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
<<<<<<< HEAD
            self.last_device = "keyboard"
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
            for action in self.keymap.get(event.key, []):
                if event.key in self._held and action not in REPEATABLE:
                    continue
                self.actions.add(action)
            self._held.add(event.key)
        elif event.type == pygame.KEYUP:
            self._held.discard(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
<<<<<<< HEAD
            self.last_device = "keyboard"
            self.click = self.to_canvas(event.pos)
        else:
            self._handle_pad_event(event)

    # ---- controle ----
    def _handle_pad_event(self, event):
        pad_cfg = self.settings.get("gamepad")
        if event.type == pygame.JOYDEVICEADDED:
            try:
                self._add_pad(pygame.joystick.Joystick(event.device_index))
            except Exception:
                log.exception("Não foi possível abrir o controle")
        elif event.type == pygame.JOYDEVICEREMOVED:
            self.pads.pop(getattr(event, "instance_id", None), None)
            self._axis_dir.clear()                         # nada de direção "presa" de um controle que sumiu
            if not self.pads:
                self.pad_kind = None
                self.capture_pad = False
                self.last_device = "keyboard"
            else:
                self._set_active(next(iter(self.pads)))
        elif event.type == pygame.JOYBUTTONDOWN:
            self.last_device = "pad"
            self._set_active(getattr(event, "instance_id", None))
            self.pad_pressed.append(event.button)
            if self.capture_pad:                           # remapeando: o botão só é lido, não executa nada no jogo
                return
            for action in PAD_ACTIONS:
                if event.button in self.pad_buttons(action):
                    self.actions.add(action)
        elif event.type == pygame.JOYHATMOTION:
            self.last_device = "pad"
            self._set_active(getattr(event, "instance_id", None))
            if self.capture_pad:
                return
            x, y = event.value
            for action, hit in (("left", x < 0), ("right", x > 0), ("up", y > 0), ("down", y < 0)):
                if hit:
                    self.actions.add(action)
        elif event.type == pygame.JOYAXISMOTION and event.axis in (0, 1):
            dead = float(pad_cfg.get("deadzone", 0.55))
            direction = None
            if abs(event.value) >= dead:
                direction = ("right" if event.value > 0 else "left") if event.axis == 0 else ("down" if event.value > 0 else "up")
                self.last_device = "pad"
                self._set_active(getattr(event, "instance_id", None))
            if direction and self._axis_dir.get(event.axis) != direction and not self.capture_pad:   # só no momento em que empurra
                self.actions.add(direction)
            self._axis_dir[event.axis] = direction
=======
            self.click = self.to_canvas(event.pos)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

    def pressed(self, action):
        return action in self.actions
