"""
launcher.py - LAUNCHER do Rogue Toca (janela simples em tkinter).

Faz: mostra nome e versão, confere os arquivos, cria pastas, tem os botões
JOGAR / OPÇÕES / SAIR e inicia o jogo.

- Durante o desenvolvimento: python launcher.py  (abre o main.py)
- Depois do build: Launcher.exe abre Game/RogueToca.exe
Não exige Python do usuário final (o .exe leva tudo dentro).
"""
import logging
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

import config
from game.settings import RESOLUTIONS, WINDOW_MODE_NAMES, WINDOW_MODES, Settings
from logger import setup_logging
from paths import base_dir, is_frozen, user_data_dir

REQUIRED_DATA = ("characters.json", "enemies.json", "rewards.json", "floors.json")
BG = "#12121c"
FG = "#e6e6f0"
ACCENT = "#ffd250"


def game_dir():
    """Pasta onde estão o jogo, data/ e assets/."""
    return base_dir() / "Game" if is_frozen() else base_dir()


def game_command():
    """Comando que inicia o jogo (ou None se o EXE não existe)."""
    if is_frozen():
        exe = game_dir() / "RogueToca.exe"
        return [str(exe)] if exe.exists() else None
    main_py = base_dir() / "main.py"
    return [sys.executable, str(main_py)] if main_py.exists() else None


def ensure_folders():
    """Cria as pastas necessárias (logs e pasta de saves do usuário)."""
    try:
        (game_dir() / "logs").mkdir(parents=True, exist_ok=True)
    except OSError:          # pasta somente-leitura (ex.: Arquivos de Programas): o log vai para a pasta do usuário
        logging.warning("Sem permissão para criar logs/ ao lado do jogo.")
    user_data_dir()


def check_installation():
    """Devolve uma lista de textos de problemas (vazia = tudo certo)."""
    problems = []
    if game_command() is None:
        problems.append("Não foi possível encontrar o jogo.\n\n"
                        "Verifique se a instalação está completa.")
        return problems
    for name in REQUIRED_DATA:
        if not (game_dir() / "data" / name).exists():
            problems.append(f"Arquivo necessário não encontrado:\n\ndata/{name}")
    if not (game_dir() / "assets").exists():
        problems.append("Arquivo necessário não encontrado:\n\nassets/")
    return problems


class LauncherApp:
    def __init__(self, root):
        self.root = root
        root.title(f"{config.GAME_TITLE} - Launcher")
        root.geometry("480x440")
        root.resizable(False, False)
        root.configure(bg=BG)

        tk.Label(root, text=config.GAME_TITLE.upper(), font=("Segoe UI", 26, "bold"), bg=BG, fg=FG).pack(pady=(40, 0))
        tk.Label(root, text=f"v{config.VERSION}", font=("Segoe UI", 12), bg=BG, fg="#9696aa").pack(pady=(0, 30))
        self._button("JOGAR", self.play, "#3c7a3c")
        self._button("OPÇÕES", self.open_options, "#3c3c5a")
        self._button("SAIR", root.destroy, "#5a3c3c")

        self.status = tk.Label(root, text="", font=("Segoe UI", 10), bg=BG, fg="#9696aa")
        self.status.pack(side="bottom", pady=14)
        self.refresh_status()

    def _button(self, text, command, color):
        tk.Button(self.root, text=text, command=command, width=22, height=2,
                  font=("Segoe UI", 13, "bold"), bg=color, fg=FG, activebackground=ACCENT,
                  activeforeground="black", relief="flat", cursor="hand2").pack(pady=8)

    def refresh_status(self):
        problems = check_installation()
        self.status.config(text="Jogo encontrado." if not problems else "Atenção: instalação incompleta.",
                           fg="#78dc8c" if not problems else "#ff9680")

    def play(self):
        ensure_folders()
        problems = check_installation()
        if problems:
            logging.error("Problemas na instalação: %s", problems)
            messagebox.showerror(config.GAME_TITLE, "\n\n".join(problems))
            self.refresh_status()
            return
        try:
            subprocess.Popen(game_command(), cwd=str(game_dir()))
            logging.info("Jogo iniciado.")
            self.root.destroy()
        except Exception:
            logging.exception("Falha ao iniciar o jogo")
            messagebox.showerror(config.GAME_TITLE,
                                 "O jogo encontrou um erro ao iniciar.\n\nVerifique o arquivo:\n"
                                 "logs/launcher.log")

    def open_options(self):
        OptionsWindow(self.root)


class OptionsWindow:
    """Volume, modo de tela e tamanho da janela (grava o mesmo settings.json do jogo)."""

    def __init__(self, parent):
        self.settings = Settings()
        win = tk.Toplevel(parent)
        win.title("Opções")
        win.geometry("420x360")
        win.configure(bg=BG)
        win.transient(parent)
        win.grab_set()
        self.win = win

        self.music = tk.DoubleVar(value=self.settings.get("music_volume") * 100)
        self.sfx = tk.DoubleVar(value=self.settings.get("sfx_volume") * 100)
        self._label("Volume da música")
        tk.Scale(win, from_=0, to=100, orient="horizontal", variable=self.music, length=300,
                 bg=BG, fg=FG, highlightthickness=0).pack()
        self._label("Volume dos efeitos")
        tk.Scale(win, from_=0, to=100, orient="horizontal", variable=self.sfx, length=300,
                 bg=BG, fg=FG, highlightthickness=0).pack()

        self._label("Modo de tela")
        self.mode = ttk.Combobox(win, state="readonly", width=24,
                                 values=[WINDOW_MODE_NAMES[m] for m in WINDOW_MODES])
        self.mode.current(WINDOW_MODES.index(self.settings.get("window_mode")))
        self.mode.pack()

        self._label("Tamanho da janela")
        self.res = ttk.Combobox(win, state="readonly", width=24,
                                values=[f"{w}x{h}" for w, h in RESOLUTIONS])
        current = (self.settings.get("window_width"), self.settings.get("window_height"))
        self.res.current(RESOLUTIONS.index(current) if current in RESOLUTIONS else 0)
        self.res.pack()

        tk.Button(win, text="SALVAR", command=self.save, width=16, bg="#3c7a3c", fg=FG,
                  relief="flat", font=("Segoe UI", 11, "bold")).pack(pady=18)

    def _label(self, text):
        tk.Label(self.win, text=text, bg=BG, fg=FG, font=("Segoe UI", 10)).pack(pady=(10, 0))

    def save(self):
        s = self.settings
        s.set("music_volume", round(self.music.get() / 100, 2))
        s.set("sfx_volume", round(self.sfx.get() / 100, 2))
        s.set("window_mode", WINDOW_MODES[self.mode.current()])
        width, height = RESOLUTIONS[self.res.current()]
        s.set("window_width", width)
        s.set("window_height", height)
        s.save()
        self.win.destroy()


def main():
    setup_logging("launcher.log")
    try:
        ensure_folders()
        root = tk.Tk()
        LauncherApp(root)
        root.mainloop()
    except Exception:
        logging.exception("Erro no launcher")
        try:
            messagebox.showerror(config.GAME_TITLE, "O launcher encontrou um erro.\n\n"
                                 "Verifique o arquivo:\nlogs/launcher.log")
        except Exception:
            pass


if __name__ == "__main__":
    main()
