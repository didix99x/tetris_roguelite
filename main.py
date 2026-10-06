"""
main.py - PONTO DE ENTRADA do jogo. Só inicia; a lógica está em game/game.py.

Se algo der errado, grava o erro em logs/game.log e mostra uma mensagem amigável.
"""
import logging
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


def show_error(message):
    """Mostra uma janela de erro (Windows) ou imprime no terminal."""
    try:
        import ctypes
        from config import GAME_TITLE
        ctypes.windll.user32.MessageBoxW(0, message, GAME_TITLE, 0x10)
    except Exception:
        print(message)


def main():
    from logger import setup_logging
    log_path = setup_logging("game.log")
    try:
        try:  # evita janela borrada em telas com escala do Windows
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
        from game.data_loader import DataError
        try:
            from game.game import Game
            Game().run_loop()
        except DataError as err:
            logging.error("Erro de dados: %s", err)
            show_error(f"{err}\n\nVerifique se a instalação está completa.")
            sys.exit(1)
    except SystemExit:
        raise
    except Exception:
        logging.exception("Erro fatal")
        show_error("O jogo encontrou um erro.\n\n"
                   "Um arquivo de log foi criado em:\n"
                   f"{log_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
