# Rogue Toca v0.2.0

Puzzle estilo Tetris Attack + roguelite. O puzzle é o combate.

## Atalho de 1 clique (Windows)
- `INSTALAR_E_GERAR_EXE.bat`: cria o .venv, instala tudo, roda os testes e gera `release\Launcher.exe`.
- `JOGAR_DEV.bat`: abre o launcher sem gerar .exe (precisa do .venv).

## Jogar (versão pronta)
Abra `Launcher.exe` (pasta `release/` depois do build) e clique em JOGAR.

## Desenvolvimento (VS Code)
1. Instale o Python 3.11+ (marque "Add Python to PATH").
2. Abra a pasta do projeto no VS Code e abra o terminal (Terminal > Novo Terminal).
3. Crie o ambiente virtual:   `python -m venv .venv`
4. Ative:                     `.venv\Scripts\activate`
5. Instale:                   `pip install -r requirements.txt`
6. Rode o jogo:               `python main.py`   (ou o launcher: `python launcher.py`)
7. Teste a lógica (opcional): `python -m unittest discover -s tests -t . -v`

## Controles
- Setas / WASD: mover o cursor (ele cobre 2 blocos lado a lado)
- Enter / Espaço: trocar os 2 blocos
- Q / E: habilidade do personagem (precisa de energia)
- Esc: pausa / voltar
- Mouse: clique move o cursor; clicar de novo no mesmo par troca
- F11: tela cheia

## Build (gerar os .exe)
Execute `build_all.bat` (duplo clique). Ele:
1. empacota o jogo com PyInstaller em `build\dist_game`;
2. copia para `release\Game\` (com `data\` e `assets\` ao lado do .exe);
3. empacota o launcher em `release\Launcher.exe`.

Resultado:
```
release/
  Launcher.exe
  Game/RogueToca.exe  (+ data/, assets/, _internal/)
```
Testar: abra `release\Launcher.exe`. Se o jogo fechar sozinho, olhe `release\Game\logs\game.log`.
Para ver erros no console, remova `--windowed` em `build_game.bat` e rode `release\Game\RogueToca.exe` pelo terminal.
Erros de empacotamento: aparecem no terminal do build (módulo faltando = "ModuleNotFoundError").

## Saves
Ficam em `%APPDATA%\RogueToca` (settings.json e progress.json).
Veja PROJECT_GUIDE.md para saber o que mudar e onde.

## Documentação extra
- `COMO_EDITAR_O_JOGO.md`: receitas para adicionar personagens, inimigos, chefes, imagens, habilidades, cartas e andares.
- `REFERENCIA_DE_CONTEUDO.md`: tabelas de IDs, imagens, habilidades, estatísticas e andares (gerado por `python tools/listar_conteudo.py`).
- `PROJECT_GUIDE.md`: guia geral de pastas.

## Modo Infinito
Aparece no menu como **MODO INFINITO**, bloqueado até você zerar a história. Depois: monstros e chefes aleatórios (até os personagens jogáveis), sem fim.
Para testar sem zerar: `DEBUG_UNLOCK_INFINITE = True` em `config.py` (volte para `False` na versão final). Detalhes em `COMO_EDITAR_O_JOGO.md`.

## Músicas
Uma música por situação (menu, batalha, chefe, Modo Infinito, recompensa, vitória, game over): veja `assets/sounds/bgm/LEIA-ME.txt` e a seção 9 de `COMO_EDITAR_O_JOGO.md`.

## Personagens e desbloqueio
Juiz começa liberado; os outros 8 são desbloqueados derrotando-os como chefes no Modo Infinito. Nomes dos arquivos de arte: `assets/images/characters/LEIA-ME.txt`.
