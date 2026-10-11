# COMO EDITAR O JOGO (Rogue Toca)

Regra de ouro: **quase tudo se muda nos arquivos de `data/` (JSON)**. Só mexa em `.py` quando a receita pedir.
Depois de qualquer mudança, rode:

```
python -m unittest discover -s tests -t . -v      (confere se nada quebrou)
python tools/listar_conteudo.py                    (atualiza REFERENCIA_DE_CONTEUDO.md)
python main.py                                     (joga)
```
`REFERENCIA_DE_CONTEUDO.md` mostra: ID, nome, tipo, imagem, habilidades e estatísticas de tudo, e a tabela
Andar -> Tema -> Inimigos -> Chefe -> Recompensas.

> **Cuidado com JSON:** vírgula faltando ou sobrando e aspas esquecidas são os erros mais comuns.
> O jogo avisa o arquivo e a linha. Faça uma cópia de segurança antes de editar.

---

## 1. PERSONAGENS

### Os 9 personagens
| ID interno | Nome | Classe | Começa |
|---|---|---|---|
| `judge` | Juiz | — | **desbloqueado** |
| `bard` | Tulipa | Bardo | bloqueado |
| `assassin` | Tali | Assassina | bloqueado |
| `cleric` | Maizona | Clériga | bloqueado |
| `blacksmith` | Caique | Ferreiro | bloqueado |
| `mage` | Breno | Mago | bloqueado |
| `archer` | Romulo | Arqueiro | bloqueado |
| `warrior` | Matheuzim | Guerreiro | bloqueado |
| `monk` | Yuko | Monge | bloqueado |

O nome exibido é `name` e a classe é `class` em `data/characters.json`; o ID interno nunca muda (o código e as imagens antigas dependem dele).
Desbloqueio: campo `"unlock"`: `"default"` (liberado desde o início) ou `"defeat_in_infinite"` (precisa derrotar o personagem como inimigo no Modo Infinito). O texto de como desbloquear é montado sozinho com o nome do personagem.

### Como adicionar um personagem
1. **`data/characters.json`**: copie um bloco existente (ex.: `"warrior"`) e mude o ID (minúsculas, sem espaço, ex.: `"paladin"`). Inclua `"class"`, `"image"` (nome do arquivo de arte) e `"unlock"`:
   ```json
   "paladin": {
       "name": "Paladino", "style": "Defesa", "max_hp": 140, "energy_max": 100,
       "passive": "x", "passive_name": "Fé", "passive_text": "Texto que aparece na tela.",
       "passive_params": { "meu_numero": 0.2 },
       "ability": "x", "ability_name": "Luz Sagrada", "ability_text": "Texto que aparece.",
       "ability_cost": 50, "ability_params": { "damage": 40 },
       "unlock_floor": 0, "color": [240, 220, 120]
   }
   ```
   Ele já aparece na seleção de personagem (sem passiva/habilidade especial, só com HP).
2. **`characters/paladin.py`** (opcional, para passiva e habilidade): copie `characters/warrior.py`. Os "ganchos" são:
   `damage_multiplier(chain_level, quick)` (passiva de dano), `energy_bonus(match_lengths)` (energia),
   `on_match(combat, level, match_lengths)` (reage a matches, como o Bardo) e `use_ability(combat)` (a habilidade).
3. **`characters/__init__.py`**: importe a classe e adicione `"paladin": Paladin` no `REGISTRY`.
4. **Para ele poder ser inimigo no Modo Infinito** (e ser desbloqueado derrotando-o): em `data/enemies.json` > `"character_bosses"` crie um bloco com a chave `"paladin"` (vida, dano, cooldown, habilidades e `mechanics`). Nome, classe, cor e arte vêm do `characters.json`.

**Passivas/habilidades prontas** (reutilize nos novos personagens): bônus em `self.mods[...]` (defesa, crítico, regeneração...), `damage_multiplier`, `energy_bonus`, `on_match`, `use_ability`. Exemplos: `characters/cleric.py`, `blacksmith.py`, `archer.py`, `monk.py`, `judge.py`.

### Como adicionar uma imagem de personagem
Coloque em `assets/images/characters/` (`.gif`, `.png`, `.webp` ou `.jpg`). O jogo procura primeiro o campo `"image"` (ex.: `tulipa.png`) e depois o ID (ex.: `bard.png`). A lista de nomes está em `assets/images/characters/LEIA-ME.txt`.
A mesma imagem aparece quando o personagem é seu inimigo. Sem arquivo, o jogo usa um desenho provisório.

---

## 2. INIMIGOS E CHEFES

### Como adicionar um inimigo (ex.: Orc)
1. **`data/enemies.json`**, dentro de `"enemies"`:
   ```json
   "orc": {
       "name": "Orc", "hp": 120, "damage": 9, "cooldown": 7.5, "min_floor": 1,
       "family": "goblin", "color": [90, 130, 60],
       "passive_name": "Pele Grossa", "passive_text": "Todos os matches causam 10% menos dano.",
       "passive_params": { "armor": 0.10 },
       "abilities": [ { "type": "break", "name": "Machadada", "amount": 3 } ]
   }
   ```
   - `hp`, `damage`, `cooldown`: valores do ANDAR 1; o jogo multiplica por andar (`data/floors.json` > `scaling`).
   - `family`: de qual inimigo ele "herda" a arte reserva: `goblin`, `spider`, `mage`, `golem` ou `void`.
   - **Passivas prontas** (`passive_params`): `armor` (reduz todo dano), `chain1_reduction` (reduz matches sem chain),
     `match3_reduction` (reduz matches de 3), `enrage_hp` + `enrage_factor` (abaixo dessa vida ataca mais rápido).
   - Para o Orc **só aparecer em grupos**, adicione `"group_only": true`.
2. Para ele aparecer num andar, veja a seção 4 ("Como adicionar inimigos a um andar").

### Como adicionar uma imagem de inimigo
`assets/images/enemies/orc.png` (ou `.gif`, `.webp`, `.jpg`). O nome é o ID.
Ordem de busca: `image` do JSON -> ID -> `family`. Ou seja, se existir só `goblin.png`, todos os inimigos com
`"family": "goblin"` usam essa arte até você criar a deles. Imagem ausente ou corrompida **nunca fecha o jogo**
(ele usa o desenho provisório e anota em `logs/game.log`).
Dica: fundo transparente, até ~300 px de lado.

### Como adicionar um chefe
Em `data/enemies.json`, dentro de `"bosses"`, a chave é o **número do andar** (múltiplo de 10):
```json
"60": {
    "name": "Rei Orc", "title": "Boss do Andar 60", "hp": 900, "damage": 22, "cooldown": 5.5,
    "color": [60, 110, 50], "mechanic_name": "Grito de Guerra",
    "mechanic_text": "Embaralha e destrói blocos.",
    "mechanics": { "enrage_hp": 0.5, "enrage_factor": 0.7 },
    "abilities": [ { "type": "break", "name": "Machado", "amount": 5 }, { "type": "shuffle", "name": "Grito", "amount": 8 } ]
}
```
`mechanics` aceitos: `chain_armor`, `enrage_hp`/`enrage_factor`, `phase_two_hp`/`phase_two_boost` (veja `bosses/boss.py`).
Para o jogo chegar nele, aumente `last_floor` em `data/floors.json` para 60.
Trocar um chefe existente = editar o bloco do mesmo andar (ex.: `"30"`).

### Como adicionar uma imagem de chefe
`assets/images/bosses/boss_60.png` (o nome é `boss_` + número do andar).

---

## 3. HABILIDADES (Nome -> Dano -> Cooldown -> Alcance -> Efeito)

A tabela completa está em `REFERENCIA_DE_CONTEUDO.md`. Resumo das habilidades de inimigo:

| type | Dano | Cooldown | Alcance | Efeito |
|---|---|---|---|---|
| `break` | - | o do inimigo | `amount` blocos | destrói blocos |
| `web` | - | o do inimigo | `amount`, `duration` | prende blocos |
| `curse` | - | o do inimigo | `amount` | blocos viram pedra |
| `weight` | - | o do inimigo | `duration`, `speed` | inimigo ataca mais rápido |
| `shuffle` | - | o do inimigo | `amount` | troca cores |
| `poison` | `amount` HP/s | o do inimigo | `duration` | tira vida por segundo |
| `silence` | - | o do inimigo | `duration` | jogador sem habilidade |
| `armor` | - | o do inimigo | `percent`, `duration` | inimigo recebe menos dano |
| `heal` | - | o do inimigo | `amount` % | inimigo recupera vida |

O **dano** do inimigo é o campo `damage` dele; o **cooldown** é o campo `cooldown`. Cada ataque usa UMA habilidade da lista `abilities`, em ciclo.

### Como criar uma habilidade (ex.: fogo)
- **Sem programar:** combine as existentes. `{ "type": "break", "name": "Bola de Fogo", "amount": 4 }`.
- **Tipo novo:** em `combat/effects.py`, dentro de `apply_enemy_ability`, antes do `log.warning(...)`, adicione:
  ```python
  if kind == "fire":
      cells = break_blocks(board, int(ability.get("amount", 3)))
      combat.poison_dps = max(combat.poison_dps, float(ability.get("burn", 1.0)))
      combat.poison_time = max(combat.poison_time, float(ability.get("duration", 4.0)))
      return "gravity", cells
  ```
  Use no JSON: `{ "type": "fire", "name": "Chamas", "amount": 3, "burn": 1.5, "duration": 4 }`.
  Depois adicione `"fire"` em `VALID_ABILITIES` no `tests/test_regression.py`.
  O retorno diz ao jogo o que fazer: `"gravity"` (blocos sumiram), `"check"` (cores mudaram) ou `"none"`.

### Como adicionar uma habilidade a um personagem
O personagem tem UMA habilidade: seu `use_ability` em `characters/<id>.py` e os números em `ability_params` no JSON. Dentro dele você pode chamar:
`combat.deal_damage_to_enemy(valor, label=nome)`, funções de `combat/effects.py` (ex.: `cleanse_board`, `recolor_to_dominant`) e `combat.start_resolve("player")` (se mexer nas cores).

### Como adicionar uma habilidade a um inimigo
Acrescente um item na lista `abilities` do inimigo em `data/enemies.json`. Pronto.

---

## 4. CARTAS (recompensas)

### Como criar uma carta
Em `data/rewards.json` > `"rewards"`, adicione:
```json
{ "id": "meu_escudo", "name": "Escudo Mágico", "rarity": "rare", "category": "defesa",
  "min_floor": 3, "description": "Ataques do inimigo causam 12% menos dano.",
  "effects": [ { "type": "damage_reduction_pct", "value": 0.12 } ] }
```
- `id` único; `rarity`: `common`, `rare`, `epic`, `legendary`; `min_floor` (opcional): só aparece a partir desse andar;
  `category` é só organização. Uma carta pode ter vários efeitos.
- **Tipos de efeito (`type`):**

| type | O que faz | value de exemplo |
|---|---|---|
| `damage_pct` | +% de dano | 0.10 |
| `chain_damage_pct` | +% de dano em chains | 0.20 |
| `energy_gain_pct` | +% de energia ganha | 0.15 |
| `enemy_cooldown_pct` | inimigo ataca mais devagar | 0.10 |
| `ability_cost_pct` | habilidade mais barata (negativo) | -0.20 |
| `explosion_match5` / `explosion_chain` | blocos extras destruídos | 3 |
| `lifesteal_pct` | cura = % do dano | 0.05 |
| `regen_per_sec` | HP por segundo | 1.0 |
| `chain_start` | chains começam em nível maior | 1 |
| `max_hp` | vida máxima | 25 |
| `heal_pct` | cura na hora (% da vida) | 0.30 |
| `energy` | energia na hora | 40 |
| `damage_reduction_pct` | defesa (máx. 75%) | 0.10 |
| `crit_chance` | chance de crítico (0 a 1) | 0.15 |
| `crit_damage_pct` | crítico mais forte (base x1.5) | 0.20 |
| `ability_power_pct` | +% dano de habilidades | 0.30 |
| `low_hp_damage_pct` | +% dano com menos de 30% de vida | 0.50 |
| `boss_damage_pct` | +% dano contra bosses | 0.30 |
| `chain3_heal` | cura (HP) em chains x3+ | 6 |
| `floor_heal_pct` | cura extra ao vencer o andar | 0.15 |

Não existe **ouro** no jogo (não há loja para gastá-lo), por isso não há cartas de ouro.

### Como alterar uma carta
Edite o bloco dela em `data/rewards.json` (números em `effects` e o texto em `description`; mantenha os dois iguais).
Para mudar a **frequência** das raridades: `rarity_weights` no topo do arquivo.

---

## 5. ANDARES

`data/floors.json`:
- `last_floor` (quantos andares), `boss_every` (de quantos em quantos há chefe), `heal_after_floor_pct`, `scaling` (dificuldade por andar).
- `groups`: a lista de **grupos temáticos** (cada um = andares + tema + inimigos + chefe).

### Como criar um novo andar / adicionar inimigos a um andar
Num grupo, a lista `enemies` tem itens `{ "id": "orc", "floors": [3, 7] }`: o inimigo `orc` pode aparecer nos andares 3 a 7.
Para o Orc aparecer nos andares 1 a 5 do grupo "Ninho das Aranhas", adicione `{ "id": "orc", "floors": [1, 5] }`.
Em cada andar o jogo sorteia entre os inimigos cuja faixa inclui aquele andar. Recompensas: dependem de `min_floor` das cartas.

### Como criar um novo grupo de 10 andares
Em `groups`, adicione (ex.: andares 51 a 59, chefe 60):
```json
{ "id": "reino_orc", "name": "Reino Orc", "theme": "Orcs", "floors": [51, 59], "boss_floor": 60,
  "enemies": [ { "id": "orc", "floors": [51, 55] }, { "id": "orc_xama", "floors": [54, 59] } ] }
```
Crie os inimigos (seção 2), o chefe `"60"` e coloque `last_floor` em 60. Se um andar não tiver grupo, vale a regra antiga (`min_floor`).

### Como criar um novo chefe
Veja a seção 2 ("Como adicionar um chefe"). Exemplo "chefe do andar 30": edite `"30"` em `bosses` (hoje: Arquimago Sombrio).

---

## 6. O QUE CADA ARQUIVO FAZ

| Arquivo | Responsável por |
|---|---|
| `config.py` | tamanhos, cores, tempos gerais |
| `paths.py` | caminhos de pastas (funciona no .exe) |
| `data/characters.json` | personagens (vida, passiva, habilidade, cor) |
| `data/enemies.json` | inimigos comuns e chefes |
| `data/floors.json` | andares, grupos temáticos, dificuldade |
| `data/rewards.json` | cartas de recompensa |
| `characters/character.py` | jogador: vida, energia, bônus das cartas |
| `characters/warrior.py` `mage.py` `assassin.py` `bard.py` | passiva e habilidade de cada personagem |
| `characters/__init__.py` | registro dos personagens |
| `enemies/enemy.py` | inimigo base (passivas genéricas) |
| `enemies/goblin.py` `spider.py` `mage_enemy.py` `golem.py` | inimigos originais |
| `bosses/boss.py` | mecânicas dos chefes |
| `combat/combat.py` | a batalha: matches, dano, ataques do inimigo |
| `combat/damage.py` | números de dano do puzzle e do crítico |
| `combat/effects.py` | efeitos no tabuleiro / habilidades dos inimigos |
| `rewards/reward_pool.py` `reward.py` | sorteio das 3 cartas |
| `run/floor.py` | escolhe o inimigo/chefe de cada andar (grupos) |
| `run/progression.py` | crescimento de dificuldade por andar |
| `run/run_manager.py` | controla a run |
| `ui/boss_offer.py` | tela "Um Boss especial apareceu!" (ENFRENTAR / IGNORAR) |
| `characters/judge.py` `cleric.py` `blacksmith.py` `archer.py` `monk.py` | passiva e habilidade de Juiz, Maizona, Caique, Romulo e Yuko |
| `ui/portraits.py` | retratos: procura a imagem e, se não achar, desenha o provisório |
| `ui/gif_loader.py` | lê GIF/PNG/WEBP/JPG |
| `ui/hud.py` | HUD da batalha |
| `ui/battle_screen.py` | tela de batalha, sons e efeitos visuais |
| `ui/character_select.py` `reward_screen.py` `menu.py` `game_over.py` | demais telas |
| `game/game.py` | loop do jogo e troca de telas |
| `tools/listar_conteudo.py` | gera `REFERENCIA_DE_CONTEUDO.md` |
| `run/floor.py` (`build_infinite_floor`) | andares aleatórios do Modo Infinito |
| `game/music_map.py` | qual música toca em cada situação (nomes dos arquivos e reservas) |
| `game/audio.py` | toca músicas e efeitos sonoros |
| `game/save.py` | progresso permanente (inclui desbloqueio e recorde do infinito) |
| `tests/` | testes que garantem que o conteúdo antigo não mudou |

---

## 7. MODO INFINITO

- **Desbloqueio:** o nome aparece no menu, mas fica **BLOQUEADO** até o jogador derrotar o chefe do último andar da história
  (`last_floor` em `data/floors.json`). O desbloqueio é salvo em `progress.json` (`infinite_unlocked`).
- **Como funciona:** não tem fim. Monstros e chefes são sorteados.
  - Monstros: a cada 10 andares entra um tema novo (aranhas, goblins, magos, golens, vazio); dentro de cada ciclo de 10 andares a dificuldade sobe como na história.
  - Chefes (andares 10, 20, 30...): sorteados entre os chefes da história já liberados e os **personagens jogáveis** (menos o que você está usando).
  - A força dos inimigos cresce sem limite (`scaling` em `data/floors.json`). Cartas de recompensa continuam sendo oferecidas a cada andar.
- **Recorde:** o melhor andar do infinito fica no menu e na tela de Game Over.
- **Testar sem zerar o jogo:** em `config.py` coloque `DEBUG_UNLOCK_INFINITE = True` (volte para `False` antes de entregar o jogo). Ou use `"last_floor": 10` em `data/floors.json` para zerar a história em 10 andares.

### Como mudar o Modo Infinito
| Quero mudar | Onde |
|---|---|
| Ligar/desligar chefes-personagem | `data/floors.json` > `infinite` > `include_character_bosses` |
| Chance de o chefe ser um personagem (padrão 0.3 = 30%) | `data/floors.json` > `infinite` > `character_boss_chance` |
| Andar a partir do qual personagens podem ser chefe (padrão 20 = só acima do andar 20, ou seja, do 30 em diante) | `data/floors.json` > `infinite` > `character_boss_after_floor` |
| Permitir o próprio personagem como chefe | `data/floors.json` > `infinite` > `exclude_own_character` = `false` |
| Dificuldade que cresce por andar | `data/floors.json` > `scaling` |
| Vida, dano e habilidades dos chefes-personagem | `data/enemies.json` > `character_bosses` |
| Chefes da história sorteados | `data/enemies.json` > `bosses` |
| Texto de parabéns da vitória | `ui/game_over.py` (`_draw_victory`) |
| Sorteio dos andares | `run/floor.py` (`build_infinite_floor`) |

### Como adicionar um novo chefe-personagem
1. Em `data/enemies.json` > `character_bosses`, copie um bloco (ex.: `"warrior"`) e use o **id do personagem** como chave.
2. A arte vem de `assets/images/characters/<id>.gif` (a mesma do personagem). Sem arquivo, usa o desenho provisório.

---

## 8. NOME DO JOGO

O nome (`GAME_TITLE`) e a versão (`VERSION`) ficam em `config.py`. Menu, janela, launcher e mensagens de erro usam esse valor.
O executável é `RogueToca.exe` (nome definido em `build_game.bat`, `--name RogueToca`, e em `launcher.py`).
Seus saves ficam em `%APPDATA%\RogueToca` (se existir a pasta antiga `TetrisRoguelite`, o progresso é copiado automaticamente na primeira vez).

---

## 9. MÚSICAS (BGM)

Cada situação tem a sua música. Coloque os arquivos em `assets/sounds/bgm/` (`.ogg`, `.mp3` ou `.wav`; prefira `.ogg`):

| Arquivo | Quando toca | Se não existir, usa |
|---|---|---|
| `menu` | menu, opções, escolha de personagem | `music` |
| `battle` | batalha normal | `music` |
| `boss` | batalha contra chefe | `battle` |
| `infinite` | batalha normal no Modo Infinito | `battle` |
| `infinite_boss` | chefe no Modo Infinito | `boss`, depois `infinite`, depois `battle` |
| `reward` | escolha de recompensa | `battle` |
| `victory` | tela de vitória | `music` |
| `game_over` | tela de game over | `music` |
| `music` | música geral (reserva de tudo) | silêncio |

- **Trocar uma música:** substitua o arquivo (mesmo nome) e abra o jogo de novo. Na versão pronta, troque em `release\Game\assets\sounds\bgm\` (não precisa fazer o build de novo).
- **Mudar qual música toca em cada situação:** `game/music_map.py` (`SITUATION_TRACKS` = nomes e reservas; `situation_for` = em que estado cada uma toca).
- **Adicionar uma situação nova** (ex.: uma música para o andar 50): em `situation_for` devolva um nome novo (ex.: `"final_boss"`), e em `SITUATION_TRACKS` adicione `"final_boss": ["final_boss", "boss"]`.
- A música só reinicia quando o arquivo muda: vários andares seguidos de batalha não cortam a música. A troca tem uma entrada suave de 0,4 s.
- Volume: tela de Opções ou `music_volume` no `settings.json`. Sem arquivo nenhum o jogo fica em silêncio, sem erro.

---

## 10. DESBLOQUEIO DE PERSONAGENS

- Fica em `game/save.py` (`unlock_character`, `update_unlocks`) e é salvo em `progress.json` (campo `unlocked`) na pasta de saves. É progressão **permanente**: perder a run, morrer para um Boss ou fechar o jogo **não** remove desbloqueios.
- Como se desbloqueia: derrotar o personagem **como inimigo no Modo Infinito**. A verificação está em `game/game.py` (`_unlock_defeated_character`, chamada em `on_battle_won`): se o inimigo derrotado tem `character_id`, o personagem é desbloqueado e salvo na hora; a tela de recompensa mostra "NOME DESBLOQUEADO(A)!".
- Os personagens aparecem no Infinito **somente como CHEFE**, nunca como monstro comum, e **só depois do andar 20** (andares de chefe 30, 40, 50...): nesses andares há **30% de chance** de o chefe ser um personagem (e 70% de ser um chefe da história). Valores em `data/floors.json` > `infinite` > `character_boss_chance` e `character_boss_after_floor`. Quando o chefe é um personagem, os ainda bloqueados têm mais chance de ser o escolhido: `locked_character_boss_weight` (2 = o dobro; 1 = igual; aumente para desbloquear mais rápido). O Boss especial (2%) segue a mesma regra (personagem só acima do andar 20).
- Saves antigos (da versão em que todos eram liberados) são ajustados uma vez: ficam liberados só os "default"; o resto do progresso é mantido (`save_version` em `progress.json`).
- Para testar rápido: use `DEBUG_UNLOCK_INFINITE = True` em `config.py` e, em `data/floors.json` > `infinite`, `"character_boss_after_floor": 0` e `"character_boss_chance": 1.0` (todo chefe vira personagem, desde o andar 10).

## 11. INIMIGOS EXCLUSIVOS DO MODO INFINITO

Fada, Zumbi, Necromante e Dragão estão em `data/enemies.json` (`infinite_only`, `group_only`) e entram no sorteio por `data/floors.json` > `infinite` > `exclusive_enemies` (`from_floor` = a partir de qual andar; `weight` = quantas "fichas" no sorteio). Para adicionar outro: crie o inimigo em `enemies.json` e uma linha em `exclusive_enemies`.

## 12. BOSS ESPECIAL (2%)

- **Chance:** `data/floors.json` > `infinite` > `special_boss_chance` (`0.02` = 2%). Para mudar, altere esse número (ex.: `0.10` = 10%; `1.0` para testar).
- **Quando:** depois que você escolhe a carta da fase no Modo Infinito (`game/game.py`, `on_reward_chosen` e `roll_special_boss`).
- **Escolha ENFRENTAR / IGNORAR:** `ui/boss_offer.py` (tela) e `on_boss_offer` em `game/game.py`.
- **IGNORAR:** nada acontece; a run segue para o próximo andar.
- **ENFRENTAR:** usa o sistema normal de Boss (`run/floor.py` > `build_special_boss`, um pouco mais forte: `special_boss_hp_factor`, `special_boss_damage_factor`).
- **Vitória:** 3 cartas **lendárias** (`rewards/reward_pool.py`, parâmetro `only_rarity`), aplicadas pelo mesmo sistema de cartas; a run continua no mesmo andar.
- **Derrota:** Game Over normal (mesma tela de sempre), sem recompensa; desbloqueios permanentes continuam.


---
## EXPANSÃO DO MODO INFINITO (15 bosses, 30 inimigos, escalonamento, 45 cartas)

Tudo é **dado** em `data/` (a lista completa e gerada fica em `REFERENCIA_DE_CONTEUDO.md`).

### Bosses exclusivos do Infinito (`data/enemies.json` > `infinite_bosses`)
- 15 chefes, **5 deles Super Bosses** (`"super": true`). Cada um tem `min_floor` (só aparece a partir desse andar).
- Chefes normais entram no mesmo sorteio dos chefes da história. Super Bosses são raros: `data/floors.json` > `infinite` > `super_boss_chance` (padrão 0.15 = 15% dos andares de chefe em que algum já esteja liberado).
- Para criar mais um: copie um bloco, mude a chave (o id vira `boss_inf_<chave>`) e crie a arte `assets/images/bosses/boss_inf_<chave>.png|gif`.
- Mecânicas (campo `mechanics`) além das antigas (`chain_armor`, `enrage_hp/factor`, `phase_two_hp/boost`):
  `armor`, `match3_reduction`, `phase_three_hp/factor/boost` (fase 3), `regen_pct` (vida/seg), `attack_heal_pct` (cura ao atacar).

### Inimigos exclusivos do Infinito (`enemies.json` > `enemies`, ids com `infinite_only`)
- 30 novos. Em quais andares aparecem: `floors.json` > `infinite` > `exclusive_enemies` (`from_floor`, `to_floor` opcional, `weight`).
- Passivas extras (`passive_params`): `regen_pct`, `attack_heal_pct` (além de `armor`, `chain1_reduction`, `match3_reduction`, `enrage_hp/factor`).
- Habilidades novas: `drain` (tira `amount` de energia do jogador) e `strike` (golpe extra: `amount` = % do ataque do inimigo, então escala com o andar).
- `portrait` = desenho provisório usado só se o arquivo de arte não existir.

### Escalonamento (`floors.json` > `infinite` > `scaling`)
O inimigo considera o **andar** e a **força do jogador** (`run/progression.py`):
- Até `knee_floor` (50) cresce igual ao modo normal; depois mais devagar (`tail_rate`), com tetos `hp_mult_cap`, `damage_mult_cap`, `ability_bonus_cap` e `min_cooldown_seconds`.
- `player_power`: mede ataque (dano, crítico, chain, explosões, habilidades, condicionais) e defesa (vida máx., defesa, esquiva, vampirismo, regeneração...) usando só os bônus que o jogador já tem. A vida do inimigo sobe com o ataque (`hp_per_offense`, teto `hp_cap`), o dano sobe com a defesa (`damage_per_defense`, teto `damage_cap`), e inimigos ficam um pouco mais rápidos (`cooldown_per_power`) e com habilidades mais fortes (`ability_per_power`, `ability_cap`). Nunca fica mais fácil que só pelo andar. `"enabled": false` desliga a adaptação.

### Cartas novas (`data/rewards.json`, ids `i_*`)
Efeitos novos (todos em `characters/character.py` > `DEFAULT_MODS`, regras em `combat/combat.py`):
`big_match_damage_pct`, `quick_damage_pct`, `execute_damage_pct`, `opener_damage_pct`, `momentum_pct`, `floor_damage_pct`, `chain_energy`, `crit_energy`, `crit_heal`, `match_heal`, `ability_refund_pct`, `ability_heal`, `block_chance`, `thorns_pct`, `status_resist_pct`, `boss_cooldown_pct`, `second_wind_pct`.
Limites (`combat/damage.py`): impulso máx. 8 acúmulos, dano por andar máx. +60%, esquiva máx. 50%, espinhos máx. 100%, resistência máx. 75%. `damage_reduction_pct` e `max_hp` negativos viram cartas de risco.

### Arte (sprites)
Os 45 sprites novos são PNGs animados (4 quadros) em `assets/images/enemies/` e `assets/images/bosses/`, gerados por `python tools/gerar_sprites.py` (edite a receita da criatura e rode de novo; `--sheet` gera `tools/sprites_preview.png`). Para usar a SUA arte, coloque um `.gif` com o mesmo nome: o jogo procura `.gif` antes de `.png`.


---
## VISUAL: HUD E EFEITOS DAS HABILIDADES

> Tudo desta seção é **só aparência**. Nenhum valor de gameplay (dano, vida, custo, cooldown, regras) é lido para decidir nada nem alterado.
> Capturas: `docs/visual/antes_hud.png`, `docs/visual/depois_hud.png`, `docs/visual/efeitos_das_habilidades.png`.

### Onde fica a HUD
| O quê | Arquivo |
|---|---|
| Desenho da HUD (placa do inimigo, painel do jogador, painel do andar, teclas) | `ui/hud.py` |
| Barras, painéis, caixas, texto com sombra, fonte | `ui/widgets.py` (`draw_bar`, `draw_panel`, `draw_inner_box`, `draw_text`, `get_font`) |
| Ícones (coração, raio, relógio, escudo, gota, teia...) | `ui/icons.py` |
| Cores, fontes, posições, tamanhos e ajustes dos efeitos | `ui/theme.py` |

### Passo a passo: mudar a HUD
1. **Posição e tamanho:** abra `ui/theme.py`, seção `3) POSIÇÕES E TAMANHOS`. Cada item é `(x, y, largura, altura)` em pixels (tela 1280x720). Ex.: `PLAYER_HP_BAR = (66, 338, 274, 26)` é a barra de vida; `ENEMY_BAR` a do inimigo; `LEFT_PANEL`/`RIGHT_PANEL` os painéis. Cuidado para não invadir o tabuleiro (x de 384 a 896).
2. **Cores:** `ui/theme.py`, seção `2) CORES` (`HP`, `ENERGY`, `PANEL_TOP`, `READY`, `STATUS`...). As cores de vida/energia/texto base também podem ser mudadas em `config.py`.
3. **Fontes:** `ui/theme.py`, seção `1) FONTES`. Ponha um `.ttf` em `assets/fonts/` e escreva `FONT_PATH = "assets/fonts/MinhaFonte.ttf"`. Se o texto ficar grande/pequeno, ajuste `FONT_SCALE` (ex.: `0.85`). Se o arquivo não existir, o jogo volta para a fonte padrão sozinho. Tamanhos individuais de texto ficam nas chamadas `draw_text(..., tamanho, ...)` em `ui/hud.py`.
4. **Barras:** o desenho (degradê, brilho, divisões de 10%, rastro do dano, marcador do custo da habilidade, brilho de vida baixa) está em `ui/widgets.py > draw_bar`. Opções por barra: `key=` (liga o rastro), `marker=` (marcação), `glow=` (cor do brilho pulsante), `icon=` (ícone ao lado).
5. **Ícones:** `ui/icons.py`. Cada ícone é `draw_xxx(superfície, (x, y), tamanho, cor)`. Para criar outro: copie um, mude as formas e registre em `ICONS`. Para trocar o ícone de uma barra, mude o `icon=(icons.draw_heart, cor)` em `ui/hud.py`. O ícone de cada efeito de status é escolhido por palavra do texto em `icons.status_icon`.
6. **Painéis e caixas:** `draw_panel` (painéis grandes) e `draw_inner_box` (caixas de habilidade/passiva) em `ui/widgets.py`.

### Onde ficam os efeitos
| O quê | Arquivo |
|---|---|
| Efeitos das habilidades e impactos (anéis, brilhos, cortes, flechas, notas, pilares...) | `ui/ability_fx.py` |
| Textos flutuantes, partículas, tremor e clarão de tela (já existiam) | `ui/vfx.py` |
| Liga os eventos do combate (`ability`, `damage_enemy`, `heal`...) aos efeitos | `ui/battle_screen.py > _process_events` |

### Passo a passo: duração, tamanho e intensidade
1. **Geral:** `ui/theme.py > EFFECTS`:
   - `enabled` (`False` desliga todos os efeitos novos), `intensity` (quantidade/força), `speed` (velocidade: `1.5` = mais rápido, `0.7` = mais lento), `size` (tamanho), `hit_effects` (faíscas ao acertar), `flash_scale` (clarão de tela, `0` = sem clarão), `max_items` (limite para não pesar).
2. **Por personagem:** `ui/theme.py > STYLE_TUNING`, por exemplo `"warrior": {"size": 1.3, "intensity": 0.8}`.
3. **Cor do efeito de cada personagem:** `ui/theme.py > STYLE_COLORS`.
4. **Detalhe de um efeito:** abra o estilo em `ui/ability_fx.py` (ex.: `style_slash_heavy`). Cada linha `fx.add("tipo", delay=..., life=..., ...)` é um pedaço do efeito: `delay` = quando começa (s), `life` = quanto dura (s), e os números de raio/largura/cor definem tamanho e aparência. Multiplique por `s` (tamanho) e use `fx.n(quantidade)` (intensidade) para respeitar os ajustes do tema.

### Passo a passo: associar um efeito a uma habilidade existente
1. Em `ui/ability_fx.py`, o dicionário `CHARACTER_STYLE` liga cada personagem (id de `data/characters.json`) a um estilo. Estilos prontos: `slash_heavy` (Guerreiro), `slash_cross` (Assassina), `arcane_swirl` (Mago), `song_waves` (Bardo), `holy_light` (Clériga), `forge_sparks` (Ferreiro), `arrow_volley` (Arqueiro), `gavel_strike` (Juiz), `resonant_palm` (Monge).
2. Para trocar, mude o valor: `"warrior": "gavel_strike"`. Personagem sem estilo usa um brilho simples (`style_generic`).
3. Um personagem novo: acrescente `"id_novo": "nome_do_estilo"` em `CHARACTER_STYLE` e a cor em `theme.STYLE_COLORS`.

### Passo a passo: criar uma variação visual nova
1. Copie um estilo (ex.: `style_arrow_volley`) para `style_minha_variacao(fx, ctx)` em `ui/ability_fx.py`.
2. `ctx` tem os pontos da tela: `P` (jogador), `E` (inimigo), `B` (centro do tabuleiro), `color`, `enemy_rect`, `player_rect`, `attack_bar`.
3. Tipos disponíveis em `fx.add`: `ring`, `glow`, `slash`, `orb`, `arrow`, `spark`, `mote`, `note`, `pillar`, `rune`, `wave`, `flash_rect`, `rays` (veja cada `_d_*` para os parâmetros).
4. Registre: `STYLES["minha_variacao"] = style_minha_variacao` e aponte `CHARACTER_STYLE["personagem"] = "minha_variacao"`.
5. Para um tipo de partícula totalmente novo: crie `_d_xxx(layer, u, p)` (u vai de 0 a 1 durante a vida do efeito) e registre em `DRAW`.

### Como testar visualmente sem abrir o jogo
`python -c "from tests.visual_harness import *; s=make_screen('warrior'); step(s,30); cast(s,12); shot(s,'captura.png')"` gera uma imagem PNG da batalha no instante do efeito (usa o pygame oficial se instalado; senão o mini-pygame de `tests/pygame_lite.py`, que é só uma ferramenta de desenvolvimento).

### Arquivos modificados (parte visual)
`ui/hud.py` (reescrito), `ui/widgets.py` (barras, painéis, texto com sombra, fonte configurável), `ui/vfx.py` (sombra no texto, partículas redondas, força do clarão), `ui/battle_screen.py` (liga os efeitos; textos de dano nascem abaixo da placa do inimigo), `COMO_EDITAR_O_JOGO.md`, `PROJECT_GUIDE.md`.
### Arquivos criados
`ui/theme.py`, `ui/icons.py`, `ui/ability_fx.py`, `tests/test_visual.py`, `tests/visual_harness.py`, `tests/pygame_lite.py`, `docs/visual/antes_hud.png`, `docs/visual/depois_hud.png`, `docs/visual/efeitos_das_habilidades.png`.

### O que mudou visualmente
- **Placa do inimigo** no topo: nome com sombra, etiqueta BOSS/SUPER BOSS com ícone, barra de vida com degradê, brilho e rastro do dano.
- **Painel do jogador:** retrato com aura na cor do personagem; barras de vida (coração) e energia (raio) com degradê, divisões e rastro; **marcador do custo da habilidade** na barra de energia; caixa da habilidade que **pulsa em verde quando está pronta** e mostra "faltam X" quando não está; caixa da passiva; vida baixa faz a barra pulsar em vermelho.
- **Painel do andar:** progresso da torre (modo história), etiqueta INFINITO, retrato com aura (dourada para Super Boss), pílula de CHAIN que brilha em chains altos, barra "próximo ataque" que pisca quando está perto, efeitos ativos com ícones (teia, pedra, veneno, silêncio...), bônus com marcadores.
- **Teclas** embaixo viraram "teclas" desenhadas.
- **Efeitos das 9 habilidades:** cada personagem tem o seu (corte, X, runa e orbes, ondas e notas, pilar de luz, faíscas de forja, flechas, martelo de luz, ondas de palma), com cor própria e clarão na mesma cor.
- **Impactos:** brilho e faíscas no inimigo ao acertar (maiores em dano alto), anel e clarão vermelho no jogador ao ser atingido, raios no crítico, partículas verdes na cura, anéis ao inimigo usar habilidade, explosão ao vencer, brilhos nos blocos afetados por Alquimia/Canção/Luz.

### Confirmação: gameplay NÃO foi alterada
- Os 61 arquivos de lógica e dados (`combat/`, `characters/`, `enemies/`, `bosses/`, `board/`, `run/`, `rewards/`, `game/`, `data/*.json`, `config.py`...) estão **byte a byte idênticos** aos de antes da parte visual (verificado por hash).
- Só `ui/` foi modificado. Os módulos novos não importam o combate e só leem valores (teste automático confere).
- `tests/test_visual.py` roda a mesma batalha com e sem a interface (e com os efeitos desligados) para os 9 personagens e exige estado final **idêntico** (vida, energia, vida do inimigo, tabuleiro, resultado).


---
## YOSHI (personagem jogável + boss do andar 50 + boss supremo do andar 100)

### Regra em uma linha
- **Andar 50 (Modo Normal)** → Yoshi é um **boss comum** → derrotá-lo **NÃO desbloqueia** o personagem.
- **Andar 100 (Modo Infinito)** → Yoshi é o **boss supremo** → derrotá-lo **desbloqueia o personagem Yoshi + 3 cartas lendárias**.

O jogo decide pelo campo `character_id`: só o Yoshi do andar 100 tem `"character_id": "yoshi"`, e o mecanismo que já existia (`Game._unlock_defeated_character`) desbloqueia quem tem esse campo. O do andar 50 não tem, então nada é desbloqueado. Yoshi nunca é sorteado: aparece **somente** no andar 100 (e o andar 100 nunca é trocado por um Boss especial).

### Onde está cada coisa
| O quê | Onde |
|---|---|
| Código do **personagem jogável** (passiva e habilidade) | `characters/yoshi.py` (registrado em `characters/__init__.py`) |
| Código do **boss supremo** (passivas combinadas) | `bosses/yoshi.py` |
| Atributos, passiva e habilidade do personagem | `data/characters.json` > `yoshi` |
| **Boss do andar 50** | `data/enemies.json` > `yoshi` > `story` |
| **Boss do andar 100** | `data/enemies.json` > `yoshi` > `infinite` |
| **Sprite/animação** (GIF de 32 quadros, serve de personagem e de boss) | `assets/images/characters/yoshi.gif` |
| Mensagem de aparição (texto, tempo) | `data/enemies.json` > `yoshi` > `infinite` > `appearance_message` |
| Aparência da mensagem (cor, tamanhos, animação) | `ui/boss_warning.py` (constantes no topo) |
| Cegueira (habilidade e duração) | habilidade `blind` em `data/enemies.json` > `yoshi` > `infinite` > `abilities` (`"duration": 2.0`) |
| Desenho da cegueira (escurecer a área de jogo) | `ui/battle_screen.py` > `_draw_blind` |
| 3 cartas lendárias | `data/enemies.json` > `yoshi` > `infinite` > `reward` (`"cards": 3, "rarity": "legendary"`) e `game/game.py` (`_roll_bonus_rewards`) |
| Desbloqueio | `data/characters.json` > `yoshi` > `unlock` (`"defeat_yoshi_infinite_100"`) |
| Andares do Yoshi | `data/enemies.json` > `yoshi` > `story` / `infinite` > `floor` (50 e 100) |

### Passo a passo
1. **Atributos do personagem:** `data/characters.json` > `yoshi`: `max_hp`, `energy_max`, `ability_cost`, `ability_params` (`damage` 42, `boss_bonus_pct` 0.25 = +25% contra bosses, `heal` 6), `passive_params` (`unhurried_bonus` 0.3 = +30% de dano em matches sem pressa, `quick_window` 2.0 s). Ao mudar números, ajuste também os textos `passive_text` / `ability_text`.
2. **Passiva e habilidade (comportamento):** `characters/yoshi.py` (`damage_multiplier` e `use_ability`).
3. **Boss do andar 50:** `data/enemies.json` > `yoshi` > `story` (vida, dano, cooldown, habilidades, mecânicas). É um boss comum; no Modo Normal ele **substitui** o boss antigo do andar 50 (o "Devorador de Puzzles" continua nos dados e segue aparecendo no Infinito).
4. **Boss do andar 100:** `data/enemies.json` > `yoshi` > `infinite`. A ordem de `abilities` é o ciclo de ataques dele (a Cegueira aparece 2 vezes no ciclo; para ficar mais/menos frequente, repita/remova a linha `blind`).
5. **Passivas dos inimigos:** o Yoshi supremo recebe, na hora, a **combinação das passivas de todos os inimigos** de `data/enemies.json > enemies` (o maior valor de cada passiva; nada nos inimigos é alterado). Se você criar um inimigo com passiva nova, a chave precisa estar em `SUPPORTED_PASSIVES` (`bosses/yoshi.py`); um teste avisa se faltar. As passivas de **cura** (`regen_pct`, `attack_heal_pct`) são reduzidas por `passive_scale` (para ele não ser imbatível); mude aqui para ficar mais fácil/difícil.
6. **Cegueira:** é **só visual**. A habilidade `blind` liga um temporizador (`combat.blind_time`, 2 s) que apenas a tela lê para escurecer a área de jogo; o jogo continua funcionando por baixo e volta ao normal sozinho. Para mudar o tempo: `"duration"` da habilidade. A aparência (escuridão, texto "CEGO!") está em `ui/battle_screen.py > _draw_blind`.
7. **Mensagem de aparição:** texto e segundos em `appearance_message`. Cor, tamanho e animação em `ui/boss_warning.py` (`COLOR`, `BIG_SIZE`, `ENTER_TIME`, `FADE_TIME`...). Ela é só um aviso desenhado por cima (o combate não pausa nem muda).
8. **3 cartas lendárias:** ao derrotar o Yoshi do andar 100 aparecem **3 telas de escolha seguidas** ("ESCOLHA UMA CARTA LENDÁRIA (1/3)", 2/3, 3/3), cada uma com 3 lendárias que você ainda não tem. Quantidade/raridade: `reward`. Depois a run continua normalmente no Modo Infinito.
9. **Desbloqueio:** acontece na hora da vitória (aviso "YOSHI DESBLOQUEADO!" na tela de recompensa) e é salvo no progresso, então fica **permanente**. Na seleção de personagem ele aparece bloqueado com a dica "Derrote Yoshi, o Rei do Tetris, no andar 100 do Modo Infinito."

### Arquivos modificados
`combat/combat.py` (temporizador de cegueira + texto de status), `combat/effects.py` (habilidade `blind`), `enemies/enemy.py` (campos `appearance_message` e `reward`), `characters/__init__.py` (registro do Yoshi e dica de desbloqueio), `run/floor.py` (Yoshi no andar 50 e 100), `run/run_manager.py` (`roll_rewards(count=)`), `game/game.py` (3 lendárias, sem Boss especial no andar 100), `ui/battle_screen.py`, `ui/reward_screen.py`, `ui/character_select.py` (miniaturas se ajustam a 10 personagens), `ui/icons.py`, `ui/ability_fx.py`, `ui/theme.py`, `data/characters.json`, `data/enemies.json`, `tests/test_final_update.py` e `tests/test_infinite_expansion.py` (2 testes ajustados: "9 personagens" virou "9 originais + Yoshi" e "andar 50 = boss antigo" virou "andar 50 = Yoshi"), `COMO_EDITAR_O_JOGO.md`.
### Arquivos criados
`characters/yoshi.py`, `bosses/yoshi.py`, `ui/boss_warning.py`, `assets/images/characters/yoshi.gif`, `tests/test_yoshi.py`, `docs/visual/yoshi_aviso_cegueira_selecao.png`.

### Garantias
Os 9 personagens, os bosses, cartas, passivas e dados antigos não foram alterados (o único boss que "perde" lugar é o do andar 50 do Modo Normal, por pedido). O Yoshi do andar 50 não desbloqueia, o do andar 100 desbloqueia, ele nunca aparece em outro andar, e a cegueira não altera a lógica (testado).


---
# ATUALIZAÇÃO: QUALIDADE, CONTEÚDO E PROGRESSÃO (Loja, pontos, upgrades, cartas com arte, fundos, eventos, controle)

Formato de cada receita: **ARQUIVO → FUNÇÃO → O QUE ALTERAR → COMO ALTERAR → EXEMPLO**.
Nada aqui mudou as regras do puzzle: tabuleiro 8x8, combinação mínima 3, match 3/4/5 = 10/18/28 de dano, chains 1.0/1.5/2.0/2.5.

## Mapa do que foi adicionado
| Sistema | Onde | Observação |
|---|---|---|
| Pontos, Loja, upgrades (lógica) | `game/shop.py` + `data/shop.json` | sem pygame; a tela e o jogo usam as MESMAS funções |
| Tela da Loja (CARTAS, UPGRADES, ÁLBUM, BESTIÁRIO, HISTÓRICO) | `ui/shop_screen.py` | botão LOJA no menu |
| Save (pontos, compras, upgrades, bestiário, histórico) | `game/save.py` (mesmo `progress.json`) | campos novos opcionais: saves antigos funcionam |
| Cartas novas da Loja, exclusivas e sinergias | `data/rewards.json` (`"shop": true`, `"character"`, `"synergies"`) | cartas antigas não foram alteradas |
| Arte das cartas | `assets/cards/<raridade>/<id>.png` + `ui/card_art.py` | gerador: `tools/gerar_artes_cartas.py` |
| Eventos entre andares | `run/events.py` + `ui/event_screen.py` | números em `data/shop.json > events` |
| Fundos por tema | `assets/backgrounds/<tema>/` + `data/backgrounds.json` + `ui/backgrounds.py` | gerador: `tools/gerar_fundos.py` |
| Símbolos nas peças | `ui/board_view.py > _draw_symbol` + `ui/theme.py > PIECE_SYMBOLS` | só visual |
| Dica de jogada | `ui/hint.py` + `data/shop.json > hint` | só visual |
| Sons | `game/audio.py > SOUND_DEFS` | sintetizados; trocáveis por arquivos |
| Controle (Xbox/PlayStation) | `game/input.py` + `settings.json > gamepad` | mesmas ações do teclado |
| Introdução de chefe | `ui/battle_screen.py` (bloco `banner_time`) | faixa + retrato + nome |

## Como alterar os PONTOS recebidos
- **Arquivo:** `data/shop.json` → `points`. **Função:** quanto cada conquista paga.
- **Alterar:** `floor_clear` (andar no Normal), `floor_clear_infinite`, `boss_defeat`, `super_boss_defeat`, `story_victory`, `milestones` (marco: uma vez só).
- **Exemplo:** para chefes pagarem 150: `"boss_defeat": 150`. Os pontos são salvos na hora e **permanecem** depois de perder, vencer ou sair.

## Como alterar CUSTOS e LIMITES da Loja
- **Cartas:** `data/shop.json > card_costs` (`common 100, rare 250, epic 500, legendary 1000`). Uma carta específica pode ter preço próprio com `"cost": 350` na carta em `data/rewards.json`.
- **Upgrades:** `data/shop.json > upgrades`: `max_level` (15), `cost_table` (15 custos crescentes) e `attributes.<vida|dano|defesa|passiva>.cost_mult` (multiplica a tabela).
- **Exemplo:** DANO mais caro: `"dano": {..., "cost_mult": 1.5}`.

## Como alterar VIDA, DANO, DEFESA e PASSIVA dos upgrades
- **Arquivo:** `data/shop.json > upgrades.attributes` e `upgrades.passive`. A tela e o jogo leem os mesmos números (`game/shop.py > upgrade_value`).
- **VIDA** `per_level` = HP por nível (4 → +60 HP no nível 15). **DANO** `per_level` = soma em `damage_pct` (0.02 → +30%). **DEFESA** `per_level` = soma em `damage_reduction_pct` (0.01 → 15%); o combate já limita a redução (nunca 100%).
- **PASSIVA:** `upgrades.passive.<personagem>` → `param` (qual número de `passive_params` melhora), `per_level`, `fmt` (`pct`, `hp`, `hps`, `en`) e `what` (texto). O valor base vem de `data/characters.json`.
- **Exemplo:** passiva do Juiz mais forte: `"judge": {"param": "damage_bonus", "per_level": 0.015, ...}`.
- **Limite de níveis:** `max_level` e o tamanho de `cost_table` precisam ser iguais.
- **Novo personagem:** ele precisa de uma entrada em `upgrades.passive` (um teste avisa se faltar) e a sua passiva deve ler o número de `passive_params`.

## Como a Loja funciona
1. Menu → **LOJA**. **Q** troca de aba, setas navegam, **Enter** compra, **Esc** volta; mouse também.
2. **CARTAS:** mostra as cartas `shop`. Estados: BLOQUEADA (faltam pontos), DISPONÍVEL (dá para comprar), DESBLOQUEADA. Comprar verifica pontos, desconta, desbloqueia para sempre e salva na hora. Sem pontos: **PONTOS INSUFICIENTES**. Carta já comprada não é comprada de novo.
3. Carta da Loja **só entra nas recompensas das runs depois de comprada**; as 105 cartas antigas continuam livres. Carta exclusiva só aparece para o personagem dela.
4. **UPGRADES:** setas ←/→ trocam de personagem, ↑/↓ de atributo. Mostra nível, ATUAL, PRÓXIMO, AUMENTO e CUSTO. No nível 15: **MÁXIMO** (compra desativada). Personagem bloqueado aparece escurecido com **BLOQUEADO** e a mensagem *DESBLOQUEIE ESTE PERSONAGEM PARA LIBERAR OS UPGRADES*; não gasta pontos. As condições de desbloqueio não mudaram.
5. **ÁLBUM:** todas as cartas com arte (bloqueadas da Loja aparecem escurecidas). **BESTIÁRIO:** inimigos derrotados (imagem, passiva, habilidades, quantas vezes). **HISTÓRICO:** últimas 30 runs.

## Como adicionar uma CARTA (e raridade, arte, exclusiva)
- **Arquivo:** `data/rewards.json > rewards` → copie uma carta e mude: `id` (único), `name`, `rarity`, `category`, `description` (até ~90 caracteres), `effects` (tipos em `characters/character.py > DEFAULT_MODS`), `min_floor`.
- **Carta da Loja:** acrescente `"shop": true` e `"art": "flame"` (motivo do desenho). **Exclusiva de personagem:** acrescente também `"character": "id_do_personagem"`.
- **Arte:** salve `assets/cards/<raridade>/<id>.png` (**200x200 a 256x256, quadrada 1:1, PNG**). Trocar o arquivo troca a arte, sem mexer em código. Para gerar a arte das cartas novas automaticamente: `python tools/gerar_artes_cartas.py` (não sobrescreve as existentes; `--force` recria todas). Motivos disponíveis: `flame ice heal shield poison speed star sword bolt rune crown tower dice thorns clock eye links fang heart feather hammer bow book palm katana scales daggers notes halo axe skull wind burst`.
- **Alterar raridade de uma carta:** mude `rarity` e mova o PNG para a pasta da nova raridade (o jogo também procura o id nas outras pastas).
- **Nova raridade:** (1) `data/rewards.json > rarity_weights` ganha a chave; (2) `config.py > RARITY_COLORS` e `RARITY_NAMES`; (3) `data/shop.json > card_costs`; (4) crie `assets/cards/<nova>/`; (5) inclua a raridade em `RARITY_FOLDERS` (`ui/card_art.py`) e em `RARITIES` (`tools/gerar_artes_cartas.py`).
- **Exemplo:** carta comum de fogo da Loja → `{"id": "s_minha_chama", "name": "Minha Chama", "rarity": "common", "category": "dano", "description": "+12% de dano.", "effects": [{"type": "damage_pct", "value": 0.12}], "min_floor": 1, "shop": true, "art": "flame"}` + `python tools/gerar_artes_cartas.py`.
- **Cartas com arte própria:** um teste (`tests/test_progression.py > CardArt`) falha se alguma carta ficar sem arquivo ou se duas cartas tiverem a mesma imagem.

## Como adicionar SINERGIAS
- **Arquivo:** `data/rewards.json > synergies`. **Formato:** `{"id", "name", "text", "cards": ["id_a", "id_b"], "effects": [{"type", "value"}]}`.
- Quando o jogador tem **todas** as cartas do conjunto na run, recebe o bônus **uma vez**, o nome aparece em "BÔNUS DA RUN" (HUD) e um aviso na batalha. **Exemplo:** Fogo e Gelo = `s_fire_burst` + `s_ice_shield` → +5% de dano e +3% de defesa.

## Como alterar os EVENTOS entre andares
- **Arquivo:** `data/shop.json > events`. `every_floors` (a cada 4 andares; nunca depois de chefe nem nos 2 últimos andares da história), `chance`, `rest_heal_pct`, `rest_energy`, `swap_max_per_run` (troca de carta: **1 por run**), `swap_fail_chance` (risco), `mystery_weights` (pesos de bênção, barganha, armadilha, nada).
- **Troca arriscada:** a carta oferecida vira outra de raridade acima (ou abaixo, se falhar); os efeitos da antiga são desfeitos. **Sem ouro** em nenhum evento.
- **Novo evento:** `run/events.py` (lógica) + `ui/event_screen.py` (`TITLES`, `INTRO`, `_options`, `choose`); inclua o tipo em `pick_event`.

## Como alterar os FUNDOS (COMO ALTERAR OS FUNDOS)
1. **Onde ficam:** `assets/backgrounds/<tema>/`. Temas: `spiders` (aranhas), `goblins`, `mages` (magos), `golems`, `bosses` (todos os chefes), `infinite` (Vazio e inimigos exclusivos do Infinito, também o fallback).
2. **Qual arquivo é de qual tema:** a pasta é o tema. Dentro dela o jogo alterna entre as imagens (ordem alfabética) conforme o andar. Hoje: `default.jpg` e `variacao.jpg`.
3. **Substituir:** salve sua imagem com o mesmo nome (ex.: `assets/backgrounds/mages/default.jpg`). Pronto, sem mexer em código.
4. **Adicionar:** coloque mais arquivos `.png/.jpg/.webp` na pasta do tema.
5. **Formato/resolução/proporção:** JPG ou PNG, **1280x720, 16:9** (outras resoluções são esticadas). O jogo escurece a imagem (`data/backgrounds.json > dim`, 0-255) para a HUD e as peças ficarem legíveis; prefira fundos escuros e sem detalhes fortes no centro.
6. **Fundo de um andar específico:** `data/backgrounds.json > floors`: `"7": "mages"` (tema) ou `"7": "mages/variacao.jpg"` (arquivo); no Infinito: `"infinite:100": "bosses"`.
7. **Novo tema:** crie `assets/backgrounds/<novo>/` com imagens e ligue em `data/backgrounds.json > families` (família do inimigo → tema), por exemplo `"zombie": "cemiterio"`. A família de cada inimigo é o campo `family` em `data/enemies.json`.
8. **Regenerar os fundos de exemplo:** `python tools/gerar_fundos.py` (não sobrescreve os seus; `--force` recria).

## Como alterar os SÍMBOLOS das peças
- **Arquivo:** `ui/board_view.py > _draw_symbol`. Cada cor tem um símbolo (1 anel, 2 triângulo, 3 losango, 4 estrela, 5 cruz). Para trocar, edite as formas desse método. Desligar tudo: `ui/theme.py > PIECE_SYMBOLS = False`.
- É só desenho: a combinação continua usando o `color_id`, exatamente como antes.

## Como alterar a DICA de jogada
- **Arquivo:** `data/shop.json > hint > idle_seconds` (6 s). `ui/hint.py` procura a jogada numa **cópia** do tabuleiro (o real nunca é tocado), destaca com contorno azul e seta, e a dica some quando o jogador age. Não executa nada.

## Como alterar os SONS e o TREMOR
- **Sons:** `game/audio.py > SOUND_DEFS`. Cada som é uma lista de notas `_n(freq_Hz, duração_s, to=freq_final, w="sine|square|saw|tri", v=volume, h=[(múltiplo, volume)], n=ruído)`. **Chains:** `chain_2`, `chain_3`, `chain_4` (x4 ou mais) ficam cada vez mais agudos e fortes; `chain_sound(level)` escolhe. Há sons para troca, match, match grande (4+), golpe, dano, habilidade, habilidade do inimigo, recompensa, vitória, derrota e entrada de chefe.
- **Usar o SEU som:** coloque `assets/sounds/sfx/<nome>.wav` (ou `.ogg`) com o nome do som (ex.: `chain_3.wav`); ele substitui o sintetizado. **Adicionar som novo:** crie a entrada em `SOUND_DEFS` e chame `audio.play("nome")` onde quiser.
- **Volumes:** Opções → MÚSICA e EFEITOS (independentes, 0-100%, salvos em `settings.json`). **Tremor:** Opções → TREMOR DE TELA ON/OFF (`screen_shake`); todo tremor passa por `VFX.add_shake`, que respeita a opção.
- **Música:** nada mudou (`game/music_map.py`).

## Como configurar CONTROLES e ACESSIBILIDADE
- **Teclado:** `settings.json > controls` (ação → lista de teclas), como antes. **Não há tela de remapeamento ainda** (ver "Pendências").
- **Controle (Xbox, PlayStation e compatíveis):** funciona sozinho ao conectar. D-pad e analógico esquerdo movem; botões em `settings.json > gamepad` (`swap` [0] = A/Cruz, `back` [1, 6, 7] = B/Bola/Select/Start/Options, `ability` [2, 3] = X/Quadrado e Y/Triângulo, `deadzone`). O tipo (Xbox/PlayStation) é detectado pelo nome do controle; a barra de teclas mostra os botões certos (sem tipo reconhecido: nomes genéricos).
- **Acessibilidade:** símbolos nas peças (para quem não distingue cores), tremor desligável, volumes separados, dica de jogada.

## Como funciona o SAVE
Tudo continua em **um** arquivo (`progress.json`, pasta de dados do usuário): `points`, `purchased_cards`, `upgrades` (por personagem), `claimed_milestones`, `bestiary`, `history` (30 últimas). Saves antigos carregam normalmente (campos novos começam vazios).

## Relatório: arquivos
**Modificados:** `game/save.py` (pontos, compras, upgrades, bestiário, histórico), `game/game.py` (pontos, eventos, histórico, upgrades na run), `game/data_loader.py` (carrega `shop.json`), `game/settings.py` (tremor, controle), `game/input.py` (controle), `game/audio.py` (sons novos, chains, arquivos), `game/state.py` (SHOP, EVENT), `run/run_manager.py` (upgrades, sinergias, cartas bloqueadas, trocas), `rewards/reward_pool.py` (cartas bloqueadas), `characters/character.py` (sinergias na HUD), `ui/menu.py` (botão LOJA, TREMOR), `ui/battle_screen.py` (fundo, dica, introdução, sons), `ui/board_view.py` (símbolos), `ui/hud.py` (botões do controle), `ui/reward_screen.py` (arte das cartas), `ui/game_over.py` (pontos), `ui/vfx.py` (opção de tremor), `ui/theme.py`, `data/rewards.json` (24 cartas da Loja + sinergias), `tests/test_infinite_expansion.py` e `tests/test_logic.py` (ajustes).
**Criados:** `game/shop.py`, `data/shop.json`, `data/backgrounds.json`, `run/events.py`, `ui/shop_screen.py`, `ui/event_screen.py`, `ui/card_art.py`, `ui/hint.py`, `ui/backgrounds.py`, `tools/gerar_artes_cartas.py`, `tools/gerar_fundos.py`, `assets/cards/` (129 artes), `assets/backgrounds/` (12 fundos), `tests/test_progression.py`.
**Sistemas importantes NÃO alterados:** regras do puzzle e valores de dano/chain, combate (`combat/`), personagens e suas habilidades, inimigos e chefes, cartas existentes (105), balanceamento original, desbloqueio de personagens, formato do save (mesmo arquivo e versão).

## Pendências (não feitas nesta atualização)
- **Tela de remapeamento** de teclas/botões dentro das Opções (hoje só pelo `settings.json`).
- **Conquistas** (o Bestiário e o Histórico de runs já existem e são salvos).
- **Tooltips** de informações dos inimigos (a HUD já mostra passiva, habilidades em efeitos ativos e status).
- Arte das cartas e fundos são gerados por código (estilo vetorial); para arte feita à mão, basta substituir os arquivos.
