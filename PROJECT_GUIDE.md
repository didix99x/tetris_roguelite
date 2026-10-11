# PROJECT_GUIDE - onde fica cada coisa

## Pastas
| Pasta | O que tem |
|---|---|
| `board/` | Tabuleiro: blocos, matches, gravidade, chains (lógica pura) |
| `combat/` | A batalha, dano (`damage.py`) e efeitos no tabuleiro (`effects.py`) |
| `characters/` | Jogador, passivas e habilidades (guerreiro, mago, assassino) |
| `enemies/` | Inimigos e suas passivas |
| `bosses/` | Mecânicas dos bosses |
| `rewards/` | Sorteio de recompensas |
| `run/` | Andares, escala de dificuldade, controle da run |
| `game/` | Loop, estados, entrada, save, configurações, áudio |
| `ui/` | Telas, HUD, desenho do tabuleiro, efeitos visuais |
| `data/` | JSON editáveis: personagens, inimigos, recompensas, andares |
| `assets/` | Imagens, sons, fontes (vazio por enquanto; `music.ogg` em `assets/sounds` toca em loop) |
| `tests/` | Testes da lógica |

Arquivos extras além do seu plano: `paths.py` (caminhos), `logger.py` (log), `game/data_loader.py`, `game/settings.py`, `game/save.py`, `game/audio.py`, `ui/battle_screen.py`, `ui/board_view.py`, `ui/widgets.py`, `ui/vfx.py`. Motivo: cada um tem uma função só, para não criar arquivos gigantes.

## QUERO MUDAR... (tabela)
| Quero mudar | Arquivo | Procurar |
|---|---|---|
| Tamanho do tabuleiro | `config.py` | `BOARD_WIDTH`, `BOARD_HEIGHT` |
| Tamanho dos blocos | `config.py` | `BLOCK_SIZE` |
| Resolução base | `config.py` | `SCREEN_WIDTH`, `SCREEN_HEIGHT` |
| Número de cores | `config.py` | `NUM_COLORS` (máx. 5 sem adicionar cor em `BLOCK_COLORS`) |
| Match mínimo | `board/matcher.py` | `MIN_MATCH` |
| Dano de match 3/4/5 | `combat/damage.py` | `MATCH_DAMAGE` |
| Multiplicador de chain | `combat/damage.py` | `CHAIN_MULTIPLIERS` |
| Dano de explosão | `combat/damage.py` | `EXPLOSION_DAMAGE_PER_BLOCK` |
| Energia por bloco | `config.py` | `ENERGY_PER_BLOCK` |
| Vida do jogador | `data/characters.json` | `max_hp` |
| Custo da habilidade | `data/characters.json` | `ability_cost` |
| Força de passiva/habilidade | `data/characters.json` | `passive_params`, `ability_params` |
| Vida do inimigo | `data/enemies.json` | `hp` |
| Velocidade do inimigo | `data/enemies.json` | `cooldown` (menor = mais rápido) |
| Dano do inimigo | `data/enemies.json` | `damage` |
| Habilidades do inimigo | `data/enemies.json` | `abilities` (`break`, `web`, `curse`, `weight`, `shuffle`, `poison`, `silence`, `armor`, `heal`, `drain`, `strike`) |
| Bosses | `data/enemies.json` | seção `bosses` |
| Bosses e Super Bosses do Infinito | `data/enemies.json` | seção `infinite_bosses` |
| Escalonamento do Infinito (andar + força do jogador) | `data/floors.json` + `run/progression.py` | `infinite` > `scaling` |
| Yoshi (personagem + boss andar 50 + boss supremo andar 100) | `characters/yoshi.py`, `bosses/yoshi.py`, `data/enemies.json > yoshi` | ver COMO_EDITAR_O_JOGO.md > YOSHI |
| HUD (posições, cores, fontes, barras, ícones) | `ui/theme.py`, `ui/hud.py`, `ui/widgets.py`, `ui/icons.py` | ver COMO_EDITAR_O_JOGO.md > Visual |
| Efeitos das habilidades e impactos | `ui/ability_fx.py` (+ `ui/vfx.py`) | `CHARACTER_STYLE`, `theme.EFFECTS` |
| Sprites dos novos inimigos/bosses | `tools/gerar_sprites.py` | `SPRITES` |
| Quantidade de andares | `data/floors.json` | `last_floor` |
| Dificuldade por andar | `data/floors.json` | `scaling` |
| Cura entre andares | `data/floors.json` | `heal_after_floor_pct` |
| Recompensas | `data/rewards.json` | `rewards` |
| Chance de raridade | `data/rewards.json` | `rarity_weights` |
| Tempo da animação | `config.py` | `CLEAR_TIME`, `BLOCK_MOVE_SPEED` |
| Volume / tela | `settings.json` (pasta do usuário) ou Opções | `music_volume`, `window_mode` |
| Controles | `settings.json` | `controls` (nomes de tecla do pygame) |
| HUD | `ui/hud.py` | posições em pixels |

## ANTES / DEPOIS (exemplos)
- Goblin com mais vida: `data/enemies.json`, `"hp": 80` -> `"hp": 200`. O Goblin precisa de mais dano para morrer.
- Match 3 mais forte: `combat/damage.py`, `3: 10` -> `3: 15`. Todo match 3 causa 50% mais dano base.
- Testar só o boss rápido: `data/floors.json`, `"last_floor": 50` -> `10`. A run termina no primeiro boss.
- Inimigo ataca mais rápido: `"cooldown": 7.0` -> `5.0`.

## Como as peças se conectam
Adicionar uma recompensa nova: só `data/rewards.json` (use um `type` já existente: `damage_pct`, `chain_damage_pct`, `energy_gain_pct`, `enemy_cooldown_pct`, `ability_cost_pct`, `explosion_match5`, `explosion_chain`, `lifesteal_pct`, `regen_per_sec`, `chain_start`, `max_hp`, `heal_pct`). Um tipo novo exige também `characters/character.py` (lista `DEFAULT_MODS`) e a regra em `combat/combat.py`.
Novo tipo de bloco: `board/block.py` (define), `board/matcher.py` (como participa de matches), `ui/board_view.py` (aparência), `config.py` (cor).
Nova habilidade de inimigo: `combat/effects.py` (função + `apply_enemy_ability`) e `data/enemies.json`.

## PERSONALIZAÇÃO RÁPIDA
- Mais vida no jogador -> `characters.json`
- Inimigos mais difíceis -> `enemies.json` / `floors.json`
- Match mais forte -> `damage.py`
- Mais/menos andares -> `floors.json`
- Novas recompensas -> `rewards.json`
- Resolução -> `config.py`
- Controles -> `settings.json`
- Visual do HUD -> `hud.py`

## Regras de organização
Dados do jogo -> JSON. Configurações -> `config.py` / `settings.json`. Lógica -> board/combat/run. Visual -> ui/assets.

## ARTE ANIMADA (GIFs)
Coloque o GIF na pasta certa, com o nome igual ao **id**:
- Personagens: `assets/images/characters/<id>.gif` (`warrior`, `mage`, `assassin`, `bard`)
- Inimigos: `assets/images/enemies/<id>.gif` (`goblin`, `spider`, `mage`, `golem`)
- Bosses: `assets/images/bosses/boss_10.gif`, `boss_20.gif`, `boss_30.gif`, `boss_40.gif`, `boss_50.gif`

Sem o arquivo, o jogo usa o desenho provisório (`ui/portraits.py`). O GIF é ajustado ao quadro do retrato mantendo a proporção.
Dicas: fundo transparente, até ~300 px de lado e ~30 quadros. Leitura de GIF: `ui/gif_loader.py` (usa Pillow).
Tamanho do retrato no HUD: `ui/hud.py` (`draw_portrait`). Na seleção de personagem: `ui/character_select.py`.

## NOVA CLASSE (exemplo: Bardo)
1. `data/characters.json`: novo bloco com `max_hp`, `passive_params`, `ability_params`, `ability_cost`, `color`.
2. `characters/bard.py`: a lógica (passiva em `on_match` / `damage_multiplier` / `energy_bonus`; habilidade em `use_ability`).
3. `characters/__init__.py`: registrar no `REGISTRY`.
4. `assets/images/characters/bard.gif`: a arte.
Bardo: passiva Melodia Curativa (`heal_per_match`, `heal_per_chain_level`), habilidade Canção Purificadora (`delay` = segundos de atraso no inimigo).
