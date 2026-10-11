# REFERÊNCIA DE CONTEÚDO (gerado por tools/listar_conteudo.py)

Não edite este arquivo à mão: rode `python tools/listar_conteudo.py` de novo para atualizar.

## Personagens

| ID | Nome | Classe | Desbloqueio | Imagem | Passiva | Habilidade | Estatísticas |
|---|---|---|---|---|---|---|---|
| `judge` | Juiz | — | liberado desde o início | (usa desenho) esperado: `juiz.png` | **Imparcialidade**: +10% de dano em todos os matches. | **Martelo da Justiça**: Causa 35 de dano e atrasa o próximo ataque do inimigo em 2,5 segundos. | HP 110 / energia 100 / custo 50 |
| `bard` | Tulipa | Bardo | derrotar no Modo Infinito | OK `bard.gif` | **Melodia Curativa**: Cada match recupera vida, mais ainda em chains. | **Canção Purificadora**: Remove teias e pedras do tabuleiro e atrasa o próximo ataque do inimigo. | HP 100 / energia 100 / custo 45 |
| `assassin` | Tali | Assassina | derrotar no Modo Infinito | OK `assassin.gif` | **Ritmo Letal**: Matches feitos logo após o anterior (até 2s) causam +30% de dano. | **Execução**: Mata inimigo com menos de 30% de vida. Senão, causa 30 de dano. | HP 100 / energia 100 / custo 60 |
| `cleric` | Maizona | Clériga | derrotar no Modo Infinito | (usa desenho) esperado: `maizona.png` | **Bênção Constante**: Recupera 0,8 de vida por segundo. | **Luz Divina**: Cura 25% da vida máxima e remove veneno, teias e pedras. | HP 110 / energia 100 / custo 50 |
| `blacksmith` | Caique | Ferreiro | derrotar no Modo Infinito | (usa desenho) esperado: `caique.png` | **Armadura Forjada**: Ataques inimigos causam 12% menos dano. | **Forja Reforçada**: Cura 10% da vida máxima e ganha +6% de defesa (até 4 vezes por run). | HP 130 / energia 100 / custo 55 |
| `mage` | Breno | Mago | derrotar no Modo Infinito | (usa desenho) esperado: `breno.png` | **Arcano Voraz**: Matches grandes geram energia adicional. | **Alquimia**: Pinta alguns blocos com a cor mais comum do tabuleiro. | HP 90 / energia 100 / custo 40 |
| `archer` | Romulo | Arqueiro | derrotar no Modo Infinito | (usa desenho) esperado: `romulo.png` | **Olhos de Águia**: 10% de chance de crítico. Chains x3+ restauram 8 de energia. | **Chuva de Flechas**: Dispara 5 flechas de 9 de dano cada (45 no total). | HP 95 / energia 100 / custo 50 |
| `warrior` | Matheuzim | Guerreiro | derrotar no Modo Infinito | (usa desenho) esperado: `matheuzim.png` | **Fúria**: Chains maiores causam mais dano. | **Golpe Poderoso**: Causa dano direto no inimigo. | HP 120 / energia 100 / custo 50 |
| `monk` | Yuko | Monge | derrotar no Modo Infinito | (usa desenho) esperado: `yuko.png` | **Chi em Fluxo**: Cada nível de chain acima de x1 gera 5 de energia extra. | **Palma Ressonante**: 20 de dano + 10 por nível da maior chain da batalha (até 5 níveis). | HP 100 / energia 100 / custo 45 |

## Inimigos

| ID | Nome | Tipo | Imagem | Habilidades | Estatísticas (base, andar 1) |
|---|---|---|---|---|---|
| `goblin` | Goblin | Inimigo | (usa desenho) esperado: `goblin.png` | **Break** (`break`) amount=3 | HP 80 / dano 6 / cooldown 7.0s |
| `spider` | Aranha | Inimigo | (usa desenho) esperado: `spider.png` | **Web** (`web`) amount=3 duration=8.0 | HP 70 / dano 5 / cooldown 6.5s |
| `mage` | Mago Sombrio | Inimigo | (usa desenho) esperado: `mage.png` | **Curse** (`curse`) amount=2 | HP 90 / dano 8 / cooldown 8.0s |
| `golem` | Golem | Inimigo | (usa desenho) esperado: `golem.png` | **Weight** (`weight`) duration=6.0 speed=1.8 | HP 150 / dano 10 / cooldown 9.0s |
| `spider_venom` | Aranha Venenosa | Inimigo | (usa desenho) esperado: `spider_venom.png` | **Picada Venenosa** (`poison`) amount=1.0 duration=5.0; **Web** (`web`) amount=2 duration=6.0 | HP 65 / dano 4 / cooldown 7.0s |
| `spider_jumper` | Aranha Saltadora | Inimigo | (usa desenho) esperado: `spider_jumper.png` | **Salto Confuso** (`shuffle`) amount=4 | HP 50 / dano 4 / cooldown 4.5s |
| `spider_weaver` | Aranha Tecelã | Inimigo | (usa desenho) esperado: `spider_weaver.png` | **Teia Grande** (`web`) amount=5 duration=7.0 | HP 75 / dano 4 / cooldown 8.0s |
| `spider_shadow` | Aranha Sombria | Inimigo | (usa desenho) esperado: `spider_shadow.png` | **Curse** (`curse`) amount=2; **Web** (`web`) amount=2 duration=6.0 | HP 80 / dano 6 / cooldown 7.0s |
| `spider_frost` | Aranha de Gelo | Inimigo | (usa desenho) esperado: `spider_frost.png` | **Gelo Silencioso** (`silence`) duration=4.0; **Web** (`web`) amount=3 duration=6.0 | HP 90 / dano 5 / cooldown 8.0s |
| `spider_elite` | Aranha Elite | Inimigo | (usa desenho) esperado: `spider_elite.png` | **Web** (`web`) amount=3 duration=7.0; **Break** (`break`) amount=2 | HP 120 / dano 7 / cooldown 6.5s |
| `spider_matriarch` | Matriarca | Inimigo | (usa desenho) esperado: `spider_matriarch.png` | **Web** (`web`) amount=4 duration=8.0; **Regenerar** (`heal`) amount=10; **Veneno** (`poison`) amount=1.0 duration=5.0 | HP 150 / dano 7 / cooldown 7.0s |
| `spider_guardian` | Guardiã | Inimigo | (usa desenho) esperado: `spider_guardian.png` | **Casca** (`armor`) percent=30 duration=6.0; **Web** (`web`) amount=4 duration=8.0 | HP 170 / dano 8 / cooldown 7.5s |
| `goblin_warrior` | Goblin Guerreiro | Inimigo | (usa desenho) esperado: `goblin_warrior.png` | **Break** (`break`) amount=3 | HP 100 / dano 7 / cooldown 7.5s |
| `goblin_archer` | Goblin Arqueiro | Inimigo | (usa desenho) esperado: `goblin_archer.png` | **Flechada** (`break`) amount=2 | HP 60 / dano 8 / cooldown 5.5s |
| `goblin_spearman` | Goblin Lanceiro | Inimigo | (usa desenho) esperado: `goblin_spearman.png` | **Estocada** (`break`) amount=3; **Rede** (`web`) amount=2 duration=6.0 | HP 85 / dano 8 / cooldown 6.5s |
| `goblin_shaman` | Goblin Xamã | Inimigo | (usa desenho) esperado: `goblin_shaman.png` | **Maldição Tribal** (`curse`) amount=2; **Cura Tribal** (`heal`) amount=8 | HP 75 / dano 5 / cooldown 8.0s |
| `goblin_berserker` | Goblin Berserker | Inimigo | (usa desenho) esperado: `goblin_berserker.png` | **Break** (`break`) amount=3 | HP 110 / dano 9 / cooldown 6.5s |
| `goblin_assassin` | Goblin Assassino | Inimigo | (usa desenho) esperado: `goblin_assassin.png` | **Faca nas Costas** (`silence`) duration=3.0; **Break** (`break`) amount=2 | HP 65 / dano 10 / cooldown 5.0s |
| `goblin_guard` | Goblin Guarda | Inimigo | (usa desenho) esperado: `goblin_guard.png` | **Postura de Escudo** (`armor`) percent=30 duration=6.0; **Break** (`break`) amount=2 | HP 150 / dano 6 / cooldown 8.5s |
| `goblin_champion` | Campeão Goblin | Inimigo | (usa desenho) esperado: `goblin_champion.png` | **Break** (`break`) amount=4; **Grito de Guerra** (`shuffle`) amount=5 | HP 180 / dano 10 / cooldown 6.5s |
| `mage_apprentice` | Aprendiz de Mago | Inimigo | (usa desenho) esperado: `mage_apprentice.png` | **Feitiço Desastrado** (`shuffle`) amount=3 | HP 60 / dano 5 / cooldown 7.0s |
| `mage_fire` | Mago de Fogo | Inimigo | (usa desenho) esperado: `mage_fire.png` | **Bola de Fogo** (`break`) amount=4 | HP 75 / dano 10 / cooldown 7.0s |
| `mage_ice` | Mago de Gelo | Inimigo | (usa desenho) esperado: `mage_ice.png` | **Tempestade Gélida** (`silence`) duration=4.0; **Prisão de Gelo** (`web`) amount=3 duration=6.0 | HP 85 / dano 7 / cooldown 8.0s |
| `mage_illusionist` | Ilusionista | Inimigo | (usa desenho) esperado: `mage_illusionist.png` | **Miragem** (`shuffle`) amount=6 | HP 80 / dano 6 / cooldown 7.0s |
| `mage_necromancer` | Necromante | Inimigo | (usa desenho) esperado: `mage_necromancer.png` | **Maldição** (`curse`) amount=3; **Praga** (`poison`) amount=1.5 duration=5.0 | HP 100 / dano 7 / cooldown 8.0s |
| `mage_storm` | Mago da Tempestade | Inimigo | (usa desenho) esperado: `mage_storm.png` | **Tempestade** (`weight`) duration=6.0 speed=1.6; **Raio** (`break`) amount=3 | HP 90 / dano 9 / cooldown 6.0s |
| `mage_warlock` | Bruxo | Inimigo | (usa desenho) esperado: `mage_warlock.png` | **Maldição** (`curse`) amount=3; **Dreno Vital** (`heal`) amount=8 | HP 120 / dano 9 / cooldown 7.5s |
| `mage_archon` | Arconte Arcano | Inimigo | (usa desenho) esperado: `mage_archon.png` | **Maldição** (`curse`) amount=3; **Caos** (`shuffle`) amount=6; **Silêncio Arcano** (`silence`) duration=3.0 | HP 150 / dano 11 / cooldown 7.0s |
| `golem_clay` | Golem de Argila | Inimigo | (usa desenho) esperado: `golem_clay.png` | **Peso** (`weight`) duration=5.0 speed=1.6 | HP 120 / dano 7 / cooldown 9.0s |
| `golem_iron` | Golem de Ferro | Inimigo | (usa desenho) esperado: `golem_iron.png` | **Endurecer** (`armor`) percent=25 duration=6.0; **Peso** (`weight`) duration=6.0 speed=1.7 | HP 190 / dano 10 / cooldown 9.5s |
| `golem_crystal` | Golem de Cristal | Inimigo | (usa desenho) esperado: `golem_crystal.png` | **Refração** (`shuffle`) amount=5; **Estilhaçar** (`break`) amount=2 | HP 130 / dano 9 / cooldown 8.0s |
| `gargoyle` | Gárgula | Inimigo | (usa desenho) esperado: `gargoyle.png` | **Garras** (`break`) amount=3; **Rede de Pedra** (`web`) amount=3 duration=7.0 | HP 140 / dano 11 / cooldown 7.0s |
| `golem_lava` | Golem de Lava | Inimigo | (usa desenho) esperado: `golem_lava.png` | **Queimadura** (`poison`) amount=1.5 duration=5.0; **Erupção** (`break`) amount=3 | HP 170 / dano 12 / cooldown 8.5s |
| `golem_moss` | Golem de Musgo | Inimigo | (usa desenho) esperado: `golem_moss.png` | **Fotossíntese** (`heal`) amount=10; **Enraizar** (`curse`) amount=2 | HP 200 / dano 8 / cooldown 9.0s |
| `golem_runic` | Golem Rúnico | Inimigo | (usa desenho) esperado: `golem_runic.png` | **Runa de Silêncio** (`silence`) duration=4.0; **Runa Maldita** (`curse`) amount=3 | HP 180 / dano 10 / cooldown 8.0s |
| `golem_sentinel` | Sentinela de Pedra | Inimigo | (usa desenho) esperado: `golem_sentinel.png` | **Peso** (`weight`) duration=7.0 speed=1.9; **Esmagar** (`break`) amount=3 | HP 240 / dano 12 / cooldown 8.5s |
| `void_wisp` | Fagulha do Vazio | Inimigo | (usa desenho) esperado: `void_wisp.png` | **Distorção** (`shuffle`) amount=5 | HP 70 / dano 7 / cooldown 5.5s |
| `void_crawler` | Rastejante | Inimigo | (usa desenho) esperado: `void_crawler.png` | **Fios do Vazio** (`web`) amount=4 duration=8.0; **Toque Frio** (`poison`) amount=1.0 duration=5.0 | HP 110 / dano 8 / cooldown 7.0s |
| `void_eater` | Devorador Menor | Inimigo | (usa desenho) esperado: `void_eater.png` | **Devorar** (`break`) amount=4; **Banquete** (`heal`) amount=6 | HP 130 / dano 9 / cooldown 7.0s |
| `void_mimic` | Mímico | Inimigo | (usa desenho) esperado: `void_mimic.png` | **Disfarce** (`shuffle`) amount=7; **Maldição** (`curse`) amount=2 | HP 120 / dano 8 / cooldown 6.5s |
| `void_shade` | Sombra Faminta | Inimigo | (usa desenho) esperado: `void_shade.png` | **Fome Gélida** (`poison`) amount=2.0 duration=5.0; **Sussurro** (`silence`) duration=3.0 | HP 100 / dano 10 / cooldown 6.0s |
| `void_warden` | Sentinela do Vazio | Inimigo | (usa desenho) esperado: `void_warden.png` | **Barreira** (`armor`) percent=30 duration=6.0; **Peso** (`weight`) duration=6.0 speed=1.8 | HP 200 / dano 10 / cooldown 8.5s |
| `void_maw` | Bocarra | Inimigo | (usa desenho) esperado: `void_maw.png` | **Mordida Abissal** (`break`) amount=6; **Maldição** (`curse`) amount=2 | HP 160 / dano 12 / cooldown 7.5s |
| `void_horror` | Horror Abissal | Inimigo | (usa desenho) esperado: `void_horror.png` | **Maldição** (`curse`) amount=3; **Terror** (`poison`) amount=2.0 duration=5.0; **Pesadelo** (`shuffle`) amount=6 | HP 190 / dano 13 / cooldown 7.0s |
| `void_herald` | Arauto do Devorador | Inimigo | (usa desenho) esperado: `void_herald.png` | **Devorar** (`break`) amount=4; **Teia Negra** (`web`) amount=4 duration=8.0; **Silêncio** (`silence`) duration=3.0; **Peso** (`weight`) duration=6.0 speed=1.8 | HP 220 / dano 14 / cooldown 6.5s |
| `fairy` | Fada | Inimigo | (usa desenho) esperado: `fairy.png` | **Pó de Fada** (`shuffle`) amount=4; **Bênção Fugaz** (`heal`) amount=6 | HP 55 / dano 5 / cooldown 4.8s |
| `zombie` | Zumbi | Inimigo | (usa desenho) esperado: `zombie.png` | **Mordida Infecciosa** (`poison`) amount=1.0 duration=6.0; **Putrefação** (`curse`) amount=2 | HP 140 / dano 7 / cooldown 8.5s |
| `necromancer` | Necromante | Inimigo | (usa desenho) esperado: `necromancer.png` | **Ressurgir Pedras** (`curse`) amount=3; **Drenar Vida** (`heal`) amount=8; **Maldição da Morte** (`poison`) amount=1.5 duration=5.0 | HP 100 / dano 8 / cooldown 7.5s |
| `dragon` | Dragão | Inimigo | (usa desenho) esperado: `dragon.png` | **Baforada de Fogo** (`break`) amount=5; **Chamas** (`poison`) amount=2.0 duration=4.0; **Rugido** (`weight`) duration=6.0 speed=1.7 | HP 220 / dano 14 / cooldown 8.0s |
| `vampire_bat` | Morcego Vampiro | Inimigo | OK `vampire_bat.png` | **Mordida** (`strike`) amount=40; **Sangria Energética** (`drain`) amount=8 | HP 55 / dano 5 / cooldown 4.8s |
| `slime_green` | Gosma Ácida | Inimigo | OK `slime_green.png` | **Gosma Pegajosa** (`web`) amount=3 duration=8.0; **Ácido** (`poison`) amount=1.0 duration=4.0 | HP 100 / dano 4 / cooldown 7.5s |
| `skeleton_archer` | Esqueleto Arqueiro | Inimigo | OK `skeleton_archer.png` | **Flecha Óssea** (`strike`) amount=45; **Chuva de Flechas** (`break`) amount=2 | HP 60 / dano 7 / cooldown 5.5s |
| `dire_wolf` | Lobo Atroz | Inimigo | OK `dire_wolf.png` | **Mordida Feroz** (`strike`) amount=50 | HP 70 / dano 7 / cooldown 4.6s |
| `spore_mushroom` | Cogumelo Esporulante | Inimigo | OK `spore_mushroom.png` | **Esporos** (`poison`) amount=1.5 duration=5.0; **Névoa Sonífera** (`silence`) duration=3.0 | HP 90 / dano 4 / cooldown 8.0s |
| `imp_flame` | Diabrete Flamejante | Inimigo | OK `imp_flame.png` | **Bola de Fogo** (`break`) amount=3; **Marca Infernal** (`curse`) amount=2 | HP 65 / dano 8 / cooldown 5.0s |
| `wail_ghost` | Espectro Lamentoso | Inimigo | OK `wail_ghost.png` | **Lamento** (`silence`) duration=3.5; **Assombração** (`shuffle`) amount=6 | HP 85 / dano 6 / cooldown 6.5s |
| `giant_scorpion` | Escorpião Gigante | Inimigo | OK `giant_scorpion.png` | **Ferrão Venenoso** (`poison`) amount=2.0 duration=5.0; **Pinça** (`break`) amount=3 | HP 110 / dano 9 / cooldown 6.5s |
| `shadow_thief` | Ladrão das Sombras | Inimigo | OK `shadow_thief.png` | **Roubar Energia** (`drain`) amount=14; **Punhalada** (`strike`) amount=55 | HP 80 / dano 9 / cooldown 5.2s |
| `elder_sapling` | Broto Ancestral | Inimigo | OK `elder_sapling.png` | **Raízes** (`web`) amount=4 duration=9.0; **Seiva Vital** (`heal`) amount=8 | HP 140 / dano 6 / cooldown 8.5s |
| `harpy` | Harpia Estridente | Inimigo | OK `harpy.png` | **Grito Desorientador** (`shuffle`) amount=7; **Guincho** (`silence`) duration=3.0 | HP 85 / dano 8 / cooldown 5.2s |
| `minotaur` | Minotauro Furioso | Inimigo | OK `minotaur.png` | **Investida** (`weight`) duration=6.0 speed=1.7; **Chifrada** (`break`) amount=4 | HP 170 / dano 11 / cooldown 8.0s |
| `spectral_knight` | Cavaleiro Espectral | Inimigo | OK `spectral_knight.png` | **Lâmina Fantasma** (`strike`) amount=60; **Pavor** (`curse`) amount=3 | HP 160 / dano 11 / cooldown 7.0s |
| `basilisk` | Basilisco | Inimigo | OK `basilisk.png` | **Olhar Petrificante** (`curse`) amount=4; **Veneno Mortal** (`poison`) amount=1.5 duration=5.0 | HP 150 / dano 10 / cooldown 7.5s |
| `lich_acolyte` | Acólito do Lich | Inimigo | OK `lich_acolyte.png` | **Mau-Olhado** (`curse`) amount=3; **Absorver Vida** (`heal`) amount=9; **Dreno Arcano** (`drain`) amount=12 | HP 130 / dano 9 / cooldown 7.0s |
| `mimic_chest` | Baú Mimic | Inimigo | OK `mimic_chest.png` | **Mordida do Baú** (`strike`) amount=70; **Isca Enganosa** (`shuffle`) amount=8 | HP 180 / dano 12 / cooldown 7.5s |
| `frost_elemental` | Elemental de Gelo | Inimigo | OK `frost_elemental.png` | **Congelar** (`silence`) duration=4.0; **Casca de Gelo** (`armor`) percent=35 duration=6.0 | HP 170 / dano 9 / cooldown 7.5s |
| `magma_elemental` | Elemental de Magma | Inimigo | OK `magma_elemental.png` | **Erupção** (`break`) amount=5; **Brasas** (`poison`) amount=2.0 duration=5.0 | HP 190 / dano 13 / cooldown 7.5s |
| `hydra_spawn` | Cria de Hidra | Inimigo | OK `hydra_spawn.png` | **Mordidas Múltiplas** (`web`) amount=4 duration=8.0; **Veneno** (`poison`) amount=2.0 duration=5.0; **Regeneração** (`heal`) amount=10 | HP 200 / dano 11 / cooldown 7.0s |
| `death_knight` | Cavaleiro da Morte | Inimigo | OK `death_knight.png` | **Golpe Sombrio** (`strike`) amount=75; **Decreto da Morte** (`curse`) amount=4; **Aura Profana** (`armor`) percent=30 duration=6.0 | HP 230 / dano 14 / cooldown 7.0s |
| `banshee` | Banshee | Inimigo | OK `banshee.png` | **Uivo Mortal** (`silence`) duration=4.5; **Grito Sugador** (`drain`) amount=16; **Lamúria** (`shuffle`) amount=8 | HP 160 / dano 11 / cooldown 6.2s |
| `chimera` | Quimera | Inimigo | OK `chimera.png` | **Garras** (`break`) amount=5; **Cauda Venenosa** (`poison`) amount=2.5 duration=5.0; **Rugido de Fúria** (`weight`) duration=6.0 speed=1.8 | HP 240 / dano 14 / cooldown 7.0s |
| `gorgon` | Górgona | Inimigo | OK `gorgon.png` | **Cabelo de Serpentes** (`web`) amount=5 duration=9.0; **Olhar de Pedra** (`curse`) amount=5; **Sibilo** (`silence`) duration=4.0 | HP 210 / dano 12 / cooldown 7.5s |
| `werewolf` | Lobisomem | Inimigo | OK `werewolf.png` | **Garras Selvagens** (`strike`) amount=70; **Rasgar** (`break`) amount=5 | HP 220 / dano 15 / cooldown 5.8s |
| `abyssal_horror` | Horror Abissal | Inimigo | OK `abyssal_horror.png` | **Tentáculos** (`shuffle`) amount=9; **Corrupção** (`curse`) amount=5; **Tinta Venenosa** (`poison`) amount=2.5 duration=5.0; **Devorar Energia** (`drain`) amount=18 | HP 260 / dano 15 / cooldown 7.0s |
| `ash_phoenix` | Fênix das Cinzas | Inimigo | OK `ash_phoenix.png` | **Chuva de Brasas** (`break`) amount=6; **Renascer** (`heal`) amount=12; **Cinzas Ardentes** (`poison`) amount=2.5 duration=5.0 | HP 240 / dano 16 / cooldown 6.8s |
| `dracolich_whelp` | Filhote de Dracolich | Inimigo | OK `dracolich_whelp.png` | **Sopro Gélido** (`break`) amount=6; **Maldição Óssea** (`curse`) amount=5; **Voo Predador** (`weight`) duration=6.0 speed=1.8 | HP 290 / dano 17 / cooldown 7.2s |
| `grim_reaper` | Ceifador | Inimigo | OK `grim_reaper.png` | **Ceifa** (`strike`) amount=85; **Colheita de Almas** (`drain`) amount=20; **Silêncio Eterno** (`silence`) duration=4.0 | HP 250 / dano 18 / cooldown 6.5s |
| `arch_demon` | Arquidemônio | Inimigo | OK `arch_demon.png` | **Chamas Infernais** (`break`) amount=7; **Pacto Sombrio** (`curse`) amount=6; **Tridente** (`strike`) amount=80; **Fúria Demoníaca** (`weight`) duration=6.0 speed=1.8 | HP 320 / dano 19 / cooldown 7.0s |
| `star_parasite` | Parasita Estelar | Inimigo | OK `star_parasite.png` | **Distorção** (`shuffle`) amount=10; **Sugar Estrelas** (`drain`) amount=20; **Radiação** (`poison`) amount=3.0 duration=5.0; **Teia Cósmica** (`web`) amount=5 duration=9.0 | HP 270 / dano 17 / cooldown 6.5s |

## Chefes

| ID | Nome | Tipo | Imagem | Habilidades | Estatísticas (base, andar 1) |
|---|---|---|---|---|---|
| `boss_10` | Rainha Aranha | Chefe | (usa desenho) esperado: `boss_10.png` | **Ninho de Teias** (`web`) amount=5 duration=12.0; **Mordida** (`break`) amount=2 | HP 260 / dano 9 / cooldown 6.0s |
| `boss_20` | Lorde Goblin | Chefe | (usa desenho) esperado: `boss_20.png` | **Saque** (`break`) amount=5; **Confusão** (`shuffle`) amount=8 | HP 360 / dano 12 / cooldown 5.5s |
| `boss_30` | Arquimago Sombrio | Chefe | (usa desenho) esperado: `boss_30.png` | **Maldição** (`curse`) amount=4; **Inversão** (`shuffle`) amount=8 | HP 440 / dano 14 / cooldown 6.0s |
| `boss_40` | Golem Colossal | Chefe | (usa desenho) esperado: `boss_40.png` | **Peso Colossal** (`weight`) duration=7.0 speed=2.0; **Esmagar** (`break`) amount=4 | HP 600 / dano 16 / cooldown 7.0s |
| `boss_50` | Devorador de Puzzles | Chefe | (usa desenho) esperado: `boss_50.png` | **Devorar** (`break`) amount=4; **Teia Negra** (`web`) amount=4 duration=10.0; **Maldição** (`curse`) amount=3; **Peso** (`weight`) duration=6.0 speed=1.8; **Caos** (`shuffle`) amount=8 | HP 800 / dano 20 / cooldown 5.5s |

## Personagens como chefes (só no Modo Infinito)

| ID | Nome | Tipo | Imagem | Habilidades | Estatísticas (base, andar 1) |
|---|---|---|---|---|---|
| `boss_char_warrior` | Matheuzim - Guerreiro | Chefe (personagem) | (usa desenho) esperado: `matheuzim.png` | **Golpe Brutal** (`break`) amount=4; **Investida** (`weight`) duration=6.0 speed=1.8 | HP 330 / dano 12 / cooldown 6.0s |
| `boss_char_mage` | Breno - Mago | Chefe (personagem) | (usa desenho) esperado: `breno.png` | **Alquimia Sombria** (`shuffle`) amount=8; **Selo Arcano** (`silence`) duration=4.0; **Petrificar** (`curse`) amount=2 | HP 300 / dano 10 / cooldown 6.5s |
| `boss_char_assassin` | Tali - Assassina | Chefe (personagem) | OK `assassin.gif` | **Lâmina Envenenada** (`poison`) amount=1.5 duration=5.0; **Golpe no Pescoço** (`silence`) duration=3.0; **Corte Duplo** (`break`) amount=2 | HP 280 / dano 14 / cooldown 4.8s |
| `boss_char_bard` | Tulipa - Bardo | Chefe (personagem) | OK `bard.gif` | **Melodia Curativa** (`heal`) amount=8; **Canção do Silêncio** (`silence`) duration=4.0; **Desafino** (`shuffle`) amount=6 | HP 320 / dano 9 / cooldown 6.5s |
| `boss_char_judge` | Juiz | Chefe (personagem) | (usa desenho) esperado: `juiz.png` | **Ordem no Tribunal** (`silence`) duration=3.0; **Condenar** (`curse`) amount=2; **Martelada** (`break`) amount=3 | HP 320 / dano 11 / cooldown 6.5s |
| `boss_char_cleric` | Maizona - Clériga | Chefe (personagem) | (usa desenho) esperado: `maizona.png` | **Cura Divina** (`heal`) amount=10; **Escudo Sagrado** (`armor`) percent=30 duration=6.0; **Julgamento** (`curse`) amount=2 | HP 340 / dano 8 / cooldown 7.0s |
| `boss_char_blacksmith` | Caique - Ferreiro | Chefe (personagem) | (usa desenho) esperado: `caique.png` | **Armadura Forjada** (`armor`) percent=35 duration=7.0; **Martelo** (`break`) amount=3; **Forja Acelerada** (`weight`) duration=6.0 speed=1.7 | HP 380 / dano 10 / cooldown 7.5s |
| `boss_char_archer` | Romulo - Arqueiro | Chefe (personagem) | (usa desenho) esperado: `romulo.png` | **Chuva de Flechas** (`break`) amount=2; **Flecha Envenenada** (`poison`) amount=1.0 duration=4.0; **Tiro Certeiro** (`shuffle`) amount=4 | HP 270 / dano 13 / cooldown 4.8s |
| `boss_char_monk` | Yuko - Monge | Chefe (personagem) | (usa desenho) esperado: `yuko.png` | **Fluxo do Chi** (`shuffle`) amount=6; **Ponto de Pressão** (`silence`) duration=3.0; **Ritmo Acelerado** (`weight`) duration=5.0 speed=1.6 | HP 290 / dano 12 / cooldown 5.0s |

## Chefes exclusivos do Modo Infinito (15; 5 são SUPER BOSSES)

| ID | Nome | Tipo | A partir do andar | Imagem | Habilidades | Mecânica | Estatísticas (base, andar 1) |
|---|---|---|---|---|---|---|---|
| `boss_inf_bone_colossus` | Colosso de Ossos | Chefe | 10 | OK `boss_inf_bone_colossus.png` | **Esmagar** (`break`) amount=4; **Maldição Óssea** (`curse`) amount=3; **Gaiola de Ossos** (`web`) amount=3 duration=7.0 | **Ossos Reforçados**: Chains x1 causam 30% menos dano. Esmaga, amaldiçoa e prende blocos. Com menos de 40% de vida ataca mais rápido. | HP 300 / dano 10 / cooldown 6.5s |
| `boss_inf_ember_witch` | Bruxa das Brasas | Chefe | 10 | OK `boss_inf_ember_witch.png` | **Labareda** (`break`) amount=4; **Brasa Viva** (`poison`) amount=1.5 duration=5.0; **Fumaça** (`shuffle`) amount=6 | **Chama Crescente**: Queima blocos e envenena. Abaixo de 50% de vida suas magias ficam mais fortes. | HP 270 / dano 10 / cooldown 6.0s |
| `boss_inf_frost_wyrm` | Serpe Glacial | Chefe | 20 | OK `boss_inf_frost_wyrm.png` | **Sopro Gélido** (`silence`) duration=3.5; **Escamas de Gelo** (`armor`) percent=30 duration=6.0; **Teia de Gelo** (`web`) amount=4 duration=8.0 | **Gelo Eterno**: Todos os matches causam 15% menos dano. Silencia e prende blocos em gelo. | HP 420 / dano 13 / cooldown 6.5s |
| `boss_inf_plague_doctor` | Médico da Peste | Chefe | 20 | OK `boss_inf_plague_doctor.png` | **Peste Negra** (`poison`) amount=2.0 duration=6.0; **Elixir Obscuro** (`heal`) amount=8; **Praga** (`curse`) amount=4 | **Epidemia**: Regenera vida, envenena e amaldiçoa. Com menos de 50% de vida ataca mais rápido. | HP 380 / dano 12 / cooldown 7.0s |
| `boss_inf_shadow_stalker` | Espreitador das Sombras | Chefe | 30 | OK `boss_inf_shadow_stalker.png` | **Emboscada** (`strike`) amount=60; **Véu de Trevas** (`silence`) duration=3.5; **Furto de Energia** (`drain`) amount=14 | **Passo Sombrio**: Matches de 3 blocos causam 35% menos dano. Golpeia, silencia e drena energia. | HP 470 / dano 15 / cooldown 5.2s |
| `boss_inf_stone_hydra` | Hidra de Pedra | Chefe | 30 | OK `boss_inf_stone_hydra.png` | **Mordida Tripla** (`break`) amount=5; **Olhar de Pedra** (`curse`) amount=5; **Pescoços Enrolados** (`web`) amount=4 duration=8.0 | **Cabeças de Pedra**: Reduz 15% do dano. Ganha fúria em DUAS fases: abaixo de 60% e de 30% de vida. | HP 560 / dano 14 / cooldown 6.5s |
| `boss_inf_crypt_lord` | Senhor da Cripta | Chefe | 40 | OK `boss_inf_crypt_lord.png` | **Selo da Cripta** (`curse`) amount=5; **Inversão Sepulcral** (`shuffle`) amount=8; **Banquete de Almas** (`heal`) amount=8 | **Pacto Mortal**: Recupera vida a cada ataque e a cada cura. Abaixo de 50% de vida suas magias ficam mais fortes. | HP 650 / dano 15 / cooldown 7.0s |
| `boss_inf_thunder_roc` | Rocnar da Tempestade | Chefe | 40 | OK `boss_inf_thunder_roc.png` | **Vendaval** (`weight`) duration=6.0 speed=1.9; **Relâmpago** (`shuffle`) amount=9; **Garras Elétricas** (`break`) amount=6 | **Tempestade**: Ataca rápido e acelera o tabuleiro. Com menos de 50% de vida fica ainda mais veloz. | HP 600 / dano 16 / cooldown 5.8s |
| `boss_inf_blighted_ancient` | Ancião Corrompido | Chefe | 50 | OK `boss_inf_blighted_ancient.png` | **Raízes Sufocantes** (`web`) amount=5 duration=9.0; **Seiva Tóxica** (`poison`) amount=2.5 duration=6.0; **Renovação** (`heal`) amount=8 | **Casca Antiga**: Reduz 25% do dano e regenera vida. Prende, envenena e se cura. | HP 850 / dano 18 / cooldown 7.5s |
| `boss_inf_iron_warden` | Carcereiro de Ferro | Chefe | 60 | OK `boss_inf_iron_warden.png` | **Placas de Ferro** (`armor`) percent=35 duration=6.0; **Marcha Pesada** (`weight`) duration=6.0 speed=1.8; **Golpe de Corrente** (`strike`) amount=80 | **Cela de Ferro**: Chains x1 causam 30% menos dano e todos os matches, 20% menos. Abaixo de 50% de vida, mais forte. | HP 950 / dano 20 / cooldown 7.0s |
| `boss_inf_lich_king` | Rei Lich Eterno | **SUPER BOSS** | 30 | OK `boss_inf_lich_king.png` | **Decreto Fúnebre** (`curse`) amount=5; **Dreno de Almas** (`drain`) amount=18; **Mordaça Sepulcral** (`silence`) duration=4.0; **Ressurgir** (`heal`) amount=8 | **Domínio dos Mortos**: Regenera e se cura a cada ataque. Entra em fúria abaixo de 60% e em desespero abaixo de 30%. | HP 900 / dano 15 / cooldown 6.0s |
| `boss_inf_ash_dragon` | Dragão das Cinzas | **SUPER BOSS** | 40 | OK `boss_inf_ash_dragon.png` | **Sopro de Fogo** (`break`) amount=7; **Cinzas Ardentes** (`poison`) amount=3.0 duration=6.0; **Rasante** (`weight`) duration=6.0 speed=1.9; **Garras de Fogo** (`strike`) amount=70 | **Fôlego Infernal**: Reduz 15% do dano. Abaixo de 50% de vida ataca bem mais rápido; abaixo de 25%, devasta o tabuleiro. | HP 1100 / dano 19 / cooldown 6.5s |
| `boss_inf_ruin_titan` | Titã da Ruína | **SUPER BOSS** | 50 | OK `boss_inf_ruin_titan.png` | **Punho da Ruína** (`strike`) amount=90; **Abalo Sísmico** (`break`) amount=8; **Pele de Rocha** (`armor`) percent=40 duration=7.0; **Passos do Titã** (`weight`) duration=6.0 speed=1.8 | **Muralha Viva**: Chains x1 causam 25% menos dano e todos os matches, 20% menos. Abaixo de 50% de vida, mais forte; abaixo de 25%, desaba em fúria. | HP 1400 / dano 21 / cooldown 7.5s |
| `boss_inf_void_empress` | Imperatriz do Vazio | **SUPER BOSS** | 60 | OK `boss_inf_void_empress.png` | **Distorção Real** (`shuffle`) amount=10; **Decreto do Vazio** (`curse`) amount=6; **Dreno Cósmico** (`drain`) amount=20; **Silêncio Absoluto** (`silence`) duration=4.5; **Fios do Destino** (`web`) amount=6 duration=9.0 | **Coroa do Vazio**: Matches de 3 blocos causam 30% menos dano. Distorce o tabuleiro e drena energia. Três fases. | HP 1250 / dano 21 / cooldown 5.8s |
| `boss_inf_world_serpent` | Serpente do Fim dos Tempos | **SUPER BOSS** | 70 | OK `boss_inf_world_serpent.png` | **Veneno do Fim** (`poison`) amount=3.5 duration=6.0; **Constrição** (`break`) amount=8; **Maldição Eterna** (`curse`) amount=6; **Presas Temporais** (`strike`) amount=90; **Espiral** (`shuffle`) amount=10 | **Ouroboros**: Regenera, se cura ao atacar e reduz 15% do dano. Abaixo de 50% fica furiosa; abaixo de 25%, implacável. | HP 1600 / dano 23 / cooldown 6.5s |

## Inimigos exclusivos do Modo Infinito: em quais andares aparecem

| ID | Nome | De | Até | Peso | Passiva |
|---|---|---|---|---|---|
| `fairy` | Fada | 1 | sem fim | 2 | **Brilho Evasivo**: Matches sem chain causam 20% menos dano. |
| `zombie` | Zumbi | 5 | sem fim | 2 | **Carne Podre**: Todos os matches causam 15% menos dano. |
| `necromancer` | Necromante | 15 | sem fim | 2 | **Pacto Sombrio**: Com menos de 40% de vida, ataca mais rápido. |
| `dragon` | Dragão | 25 | sem fim | 2 | **Escamas**: Todos os matches causam 20% menos dano. |
| `vampire_bat` | Morcego Vampiro | 1 | 35 | 2 | **Sede de Sangue**: Recupera um pouco de vida a cada ataque. |
| `slime_green` | Gosma Ácida | 1 | 30 | 2 | **Corpo Gelatinoso**: Matches de 3 blocos causam 35% menos dano. |
| `skeleton_archer` | Esqueleto Arqueiro | 3 | 40 | 1 | **Ossos Duros**: Todos os matches causam 10% menos dano. |
| `dire_wolf` | Lobo Atroz | 3 | 40 | 1 | **Instinto de Caça**: Com menos de 50% de vida, ataca bem mais rápido. |
| `spore_mushroom` | Cogumelo Esporulante | 5 | 45 | 1 | **Micélio**: Regenera vida lentamente. |
| `imp_flame` | Diabrete Flamejante | 8 | 50 | 1 | **Pele Ardente**: Chains x1 causam 15% menos dano. |
| `wail_ghost` | Espectro Lamentoso | 10 | 55 | 2 | **Intangível**: Chains x1 causam 35% menos dano. |
| `giant_scorpion` | Escorpião Gigante | 12 | 60 | 1 | **Carapaça**: Todos os matches causam 20% menos dano. |
| `shadow_thief` | Ladrão das Sombras | 14 | 60 | 1 | **Mãos Leves**: Chains x1 causam 20% menos dano. |
| `elder_sapling` | Broto Ancestral | 16 | 65 | 1 | **Raízes Profundas**: Regenera vida continuamente. |
| `harpy` | Harpia Estridente | 18 | 65 | 1 | **Voo Errático**: Matches de 3 blocos causam 25% menos dano. |
| `minotaur` | Minotauro Furioso | 20 | 75 | 1 | **Fúria Bovina**: Com menos de 50% de vida, ataca bem mais rápido. |
| `spectral_knight` | Cavaleiro Espectral | 25 | 85 | 1 | **Armadura Etérea**: Todos os matches causam 20% menos dano. |
| `basilisk` | Basilisco | 28 | 90 | 1 | **Escamas Rígidas**: Matches de 3 blocos causam 30% menos dano. |
| `lich_acolyte` | Acólito do Lich | 30 | 95 | 1 | **Filactério Menor**: Recupera vida a cada ataque. |
| `mimic_chest` | Baú Mimic | 32 | 100 | 1 | **Madeira Maciça**: Matches de 3 blocos e chains x1 causam menos dano. |
| `frost_elemental` | Elemental de Gelo | 35 | 105 | 1 | **Pele Cristalina**: Todos os matches causam 20% menos dano. |
| `magma_elemental` | Elemental de Magma | 35 | 105 | 1 | **Núcleo Incandescente**: Com menos de 40% de vida, ataca mais rápido. |
| `hydra_spawn` | Cria de Hidra | 45 | 120 | 1 | **Cabeças Renascentes**: Regenera vida continuamente. |
| `death_knight` | Cavaleiro da Morte | 50 | 130 | 1 | **Armadura Profana**: Todos os matches causam 25% menos dano. |
| `banshee` | Banshee | 50 | 130 | 1 | **Espírito Evasivo**: Chains x1 causam 30% menos dano. |
| `chimera` | Quimera | 55 | 135 | 1 | **Três Cabeças**: Com menos de 50% de vida, ataca mais rápido. |
| `gorgon` | Górgona | 60 | 140 | 1 | **Escamas de Serpente**: Matches de 3 blocos causam 30% menos dano; todos, 10% menos. |
| `werewolf` | Lobisomem | 60 | 140 | 1 | **Maldição da Lua**: Regenera vida e, com menos de 50%, ataca bem mais rápido. |
| `abyssal_horror` | Horror Abissal | 70 | sem fim | 1 | **Carne Insondável**: Todos os matches causam 15% menos dano; chains x1, 20% menos. |
| `ash_phoenix` | Fênix das Cinzas | 75 | sem fim | 1 | **Renascimento**: Recupera vida a cada ataque. |
| `dracolich_whelp` | Filhote de Dracolich | 80 | sem fim | 1 | **Ossos de Dragão**: Todos os matches causam 25% menos dano. |
| `grim_reaper` | Ceifador | 85 | sem fim | 1 | **Manto da Morte**: Chains x1 causam 30% menos dano; todos, 10% menos. |
| `arch_demon` | Arquidemônio | 90 | sem fim | 1 | **Pele Infernal**: Todos os matches causam 25% menos dano; com menos de 40% de vida, ataca mais rápido. |
| `star_parasite` | Parasita Estelar | 95 | sem fim | 1 | **Casca Cósmica**: Regenera vida; chains x1 causam 25% menos dano. |

## Andares, temas, inimigos, chefe e recompensas

| Andar | Tema | Inimigos possíveis | Chefe | Cartas disponíveis (comum/rara/épica/lendária) |
|---|---|---|---|---|
| 1 | Ninho das Aranhas | Aranha | - | 23/19/0/0 |
| 2 | Ninho das Aranhas | Aranha, Aranha Venenosa | - | 26/19/0/0 |
| 3 | Ninho das Aranhas | Aranha, Aranha Venenosa, Aranha Saltadora | - | 26/31/5/0 |
| 4 | Ninho das Aranhas | Aranha, Aranha Venenosa, Aranha Saltadora, Aranha Tecelã | - | 26/33/15/0 |
| 5 | Ninho das Aranhas | Aranha Venenosa, Aranha Saltadora, Aranha Tecelã, Aranha Sombria | - | 26/33/29/4 |
| 6 | Ninho das Aranhas | Aranha Saltadora, Aranha Tecelã, Aranha Sombria, Aranha de Gelo | - | 26/33/29/11 |
| 7 | Ninho das Aranhas | Aranha Tecelã, Aranha Sombria, Aranha de Gelo, Aranha Elite | - | 26/33/29/14 |
| 8 | Ninho das Aranhas | Aranha Sombria, Aranha de Gelo, Aranha Elite, Matriarca | - | 26/33/29/17 |
| 9 | Ninho das Aranhas | Aranha de Gelo, Aranha Elite, Matriarca, Guardiã | - | 26/33/29/17 |
| 10 | CHEFE | - | **Rainha Aranha** | 26/33/29/17 |
| 11 | Horda Goblin | Goblin | - | 26/33/29/17 |
| 12 | Horda Goblin | Goblin, Goblin Guerreiro | - | 26/33/29/17 |
| 13 | Horda Goblin | Goblin, Goblin Guerreiro, Goblin Arqueiro | - | 26/33/29/17 |
| 14 | Horda Goblin | Goblin, Goblin Guerreiro, Goblin Arqueiro, Goblin Lanceiro | - | 26/33/29/17 |
| 15 | Horda Goblin | Goblin Guerreiro, Goblin Arqueiro, Goblin Lanceiro, Goblin Xamã | - | 26/33/29/17 |
| 16 | Horda Goblin | Goblin Arqueiro, Goblin Lanceiro, Goblin Xamã, Goblin Berserker | - | 26/33/29/17 |
| 17 | Horda Goblin | Goblin Lanceiro, Goblin Xamã, Goblin Berserker, Goblin Assassino | - | 26/33/29/17 |
| 18 | Horda Goblin | Goblin Xamã, Goblin Berserker, Goblin Assassino, Goblin Guarda | - | 26/33/29/17 |
| 19 | Horda Goblin | Goblin Berserker, Goblin Assassino, Goblin Guarda, Campeão Goblin | - | 26/33/29/17 |
| 20 | CHEFE | - | **Lorde Goblin** | 26/33/29/17 |
| 21 | Torre Arcana | Aprendiz de Mago | - | 26/33/29/17 |
| 22 | Torre Arcana | Aprendiz de Mago, Mago Sombrio | - | 26/33/29/17 |
| 23 | Torre Arcana | Aprendiz de Mago, Mago Sombrio, Mago de Fogo | - | 26/33/29/17 |
| 24 | Torre Arcana | Aprendiz de Mago, Mago Sombrio, Mago de Fogo, Mago de Gelo | - | 26/33/29/17 |
| 25 | Torre Arcana | Mago Sombrio, Mago de Fogo, Mago de Gelo, Ilusionista | - | 26/33/29/17 |
| 26 | Torre Arcana | Mago de Fogo, Mago de Gelo, Ilusionista, Necromante | - | 26/33/29/17 |
| 27 | Torre Arcana | Mago de Gelo, Ilusionista, Necromante, Mago da Tempestade | - | 26/33/29/17 |
| 28 | Torre Arcana | Ilusionista, Necromante, Mago da Tempestade, Bruxo | - | 26/33/29/17 |
| 29 | Torre Arcana | Necromante, Mago da Tempestade, Bruxo, Arconte Arcano | - | 26/33/29/17 |
| 30 | CHEFE | - | **Arquimago Sombrio** | 26/33/29/17 |
| 31 | Forja de Pedra | Golem de Argila | - | 26/33/29/17 |
| 32 | Forja de Pedra | Golem de Argila, Golem | - | 26/33/29/17 |
| 33 | Forja de Pedra | Golem de Argila, Golem, Golem de Ferro | - | 26/33/29/17 |
| 34 | Forja de Pedra | Golem de Argila, Golem, Golem de Ferro, Golem de Cristal | - | 26/33/29/17 |
| 35 | Forja de Pedra | Golem, Golem de Ferro, Golem de Cristal, Gárgula | - | 26/33/29/17 |
| 36 | Forja de Pedra | Golem de Ferro, Golem de Cristal, Gárgula, Golem de Lava | - | 26/33/29/17 |
| 37 | Forja de Pedra | Golem de Cristal, Gárgula, Golem de Lava, Golem de Musgo | - | 26/33/29/17 |
| 38 | Forja de Pedra | Gárgula, Golem de Lava, Golem de Musgo, Golem Rúnico | - | 26/33/29/17 |
| 39 | Forja de Pedra | Golem de Lava, Golem de Musgo, Golem Rúnico, Sentinela de Pedra | - | 26/33/29/17 |
| 40 | CHEFE | - | **Golem Colossal** | 26/33/29/17 |
| 41 | O Vazio Faminto | Fagulha do Vazio | - | 26/33/29/17 |
| 42 | O Vazio Faminto | Fagulha do Vazio, Rastejante | - | 26/33/29/17 |
| 43 | O Vazio Faminto | Fagulha do Vazio, Rastejante, Devorador Menor | - | 26/33/29/17 |
| 44 | O Vazio Faminto | Fagulha do Vazio, Rastejante, Devorador Menor, Mímico | - | 26/33/29/17 |
| 45 | O Vazio Faminto | Rastejante, Devorador Menor, Mímico, Sombra Faminta | - | 26/33/29/17 |
| 46 | O Vazio Faminto | Devorador Menor, Mímico, Sombra Faminta, Sentinela do Vazio | - | 26/33/29/17 |
| 47 | O Vazio Faminto | Mímico, Sombra Faminta, Sentinela do Vazio, Bocarra | - | 26/33/29/17 |
| 48 | O Vazio Faminto | Sombra Faminta, Sentinela do Vazio, Bocarra, Horror Abissal | - | 26/33/29/17 |
| 49 | O Vazio Faminto | Sentinela do Vazio, Bocarra, Horror Abissal, Arauto do Devorador | - | 26/33/29/17 |
| 50 | CHEFE | - | **Devorador de Puzzles** | 26/33/29/17 |

## Habilidades de inimigo (tipos disponíveis)

| Nome (type) | Dano | Cooldown | Alcance | Efeito |
|---|---|---|---|---|
| `break` | - | o do inimigo | `amount` blocos | Destrói blocos aleatórios |
| `web` | - | o do inimigo | `amount` blocos, `duration` s | Prende blocos (não podem ser trocados) |
| `curse` | - | o do inimigo | `amount` blocos | Transforma blocos em pedra |
| `weight` | - | o do inimigo | `duration` s, `speed` | O inimigo ataca mais rápido por um tempo |
| `shuffle` | - | o do inimigo | `amount` blocos | Troca a cor de blocos |
| `poison` (novo) | `amount` HP/s | o do inimigo | `duration` s | Tira vida do jogador por segundo |
| `silence` (novo) | - | o do inimigo | `duration` s | Jogador não pode usar a habilidade |
| `armor` (novo) | - | o do inimigo | `percent` %, `duration` s | Inimigo recebe menos dano dos matches |
| `heal` (novo) | - | o do inimigo | `amount` % da vida máx. | Inimigo recupera vida |
| `drain` (Infinito) | - | o do inimigo | `amount` de energia | Tira energia do jogador (a habilidade fica mais longe) |
| `strike` (Infinito) | `amount` % do ataque do inimigo | o do inimigo | - | Golpe extra de dano direto (escala com o andar) |

O cooldown é o do INIMIGO (campo `cooldown`): cada ataque dele usa UMA habilidade da lista, em ciclo.

## Cartas (recompensas)

| ID | Nome | Raridade | Categoria | A partir do andar | Efeito |
|---|---|---|---|---|---|
| `dmg_10` | Força Bruta | common | - | 1 | +10% de dano. |
| `hp_10` | Couro Reforçado | common | - | 1 | +10 HP máximo. |
| `heal_30` | Poção Menor | common | - | 1 | Recupera 30% do HP máximo. |
| `energy_15` | Centelha | common | - | 1 | +15% de energia ganha. |
| `slow_8` | Grilhões Leves | common | - | 1 | Inimigos atacam 8% mais devagar. |
| `chain_20` | Corrente de Fogo | rare | - | 1 | +20% de dano de chain. |
| `hp_25` | Armadura de Ferro | rare | - | 1 | +25 HP máximo. |
| `boom5_3` | Pólvora | rare | - | 1 | Match 5+ explode: destrói 3 blocos extras. |
| `energy_30` | Cristal de Mana | rare | - | 1 | +30% de energia ganha. |
| `cost_20` | Foco Mental | rare | - | 1 | Habilidade custa 20% menos energia. |
| `chain_boom` | Reação em Cadeia | epic | - | 3 | Chains x2+ explodem: destroem 4 blocos extras. |
| `dmg_30` | Fúria Sangrenta | epic | - | 3 | +30% de dano. |
| `steal_5` | Sede de Sangue | epic | - | 3 | Cura 5% do dano causado. |
| `boom5_6` | Detonação | epic | - | 3 | Match 5+ explode: destrói 6 blocos extras. |
| `regen_1` | Pele Regenerativa | epic | - | 3 | Recupera 1 HP por segundo. |
| `legend_chain` | Chain Perpétuo | legendary | - | 5 | Todas as chains começam em x2. |
| `legend_time` | Relógio Quebrado | legendary | - | 5 | Inimigos 30% mais lentos e habilidade 40% mais barata. |
| `legend_storm` | Tempestade | legendary | - | 5 | Match 5+ e chains explodem: 6 blocos extras em cada. |
| `legend_vamp` | Vampiro | legendary | - | 5 | Cura 12% do dano causado e +15% de dano. |
| `n_atk_c1` | Golpe Firme | common | ataque | 1 | +12% de dano. |
| `n_atk_r1` | Fio Cortante | rare | ataque | 1 | +22% de dano. |
| `n_atk_e1` | Sede de Batalha | epic | ataque | 4 | +40% de dano. |
| `n_chain_c1` | Ritmo de Combate | common | ataque | 1 | +12% de dano de chain. |
| `n_chain_e1` | Furacão | epic | ataque | 4 | +40% de dano de chain. |
| `n_def_c1` | Escudo de Madeira | common | defesa | 1 | Ataques do inimigo causam 5% menos dano. |
| `n_def_r1` | Escudo de Aço | rare | defesa | 1 | Ataques do inimigo causam 10% menos dano. |
| `n_def_e1` | Muralha | epic | defesa | 4 | Ataques do inimigo causam 18% menos dano. |
| `n_def_l1` | Pele de Dragão | legendary | defesa | 6 | Ataques do inimigo causam 25% menos dano e +20 HP máximo. |
| `n_hp_c1` | Vigor | common | vida | 1 | +15 HP máximo. |
| `n_hp_r1` | Coração Forte | rare | vida | 1 | +35 HP máximo. |
| `n_hp_e1` | Vitalidade | epic | vida | 4 | +60 HP máximo e recupera 20% da vida. |
| `n_crit_c1` | Olho Atento | common | crítico | 1 | 8% de chance de crítico (dano x1.5). |
| `n_crit_r1` | Golpe Certeiro | rare | crítico | 1 | 15% de chance de crítico e críticos causam +20% a mais. |
| `n_crit_e1` | Mestre dos Críticos | epic | crítico | 4 | 20% de chance de crítico e críticos causam +50% a mais. |
| `n_crit_l1` | Sorte do Apostador | legendary | crítico | 6 | 30% de chance de crítico e críticos causam +50% a mais. |
| `n_ab_c1` | Mente Clara | common | habilidade | 1 | Habilidade custa 10% menos energia. |
| `n_ab_c2` | Carga Inicial | common | habilidade | 1 | Ganha 40 de energia agora. |
| `n_ab_r1` | Poder Concentrado | rare | habilidade | 1 | Habilidades causam +30% de dano. |
| `n_ab_e1` | Maestria | epic | habilidade | 4 | Habilidades causam +60% de dano e +15% de energia ganha. |
| `n_cd_c1` | Correntes Frouxas | common | cooldown | 1 | Inimigos atacam 6% mais devagar. |
| `n_cd_r1` | Tempo Lento | rare | cooldown | 1 | Inimigos atacam 14% mais devagar. |
| `n_cd_e1` | Congelar o Tempo | epic | cooldown | 4 | Inimigos atacam 22% mais devagar. |
| `n_boom_c1` | Faísca | common | especial | 1 | Match 5+ explode: destrói 2 blocos extras. |
| `n_boom_r1` | Estilhaços | rare | especial | 1 | Chains x2+ explodem: destroem 3 blocos extras. |
| `n_boom_e1` | Supernova | epic | especial | 5 | Match 5+ e chains explodem: 5 blocos extras em cada. |
| `n_chain_l1` | Eco Infinito | legendary | especial | 6 | Chains começam em x2 e causam +20% de dano de chain. |
| `n_heal_c1` | Bandagem | common | cura | 1 | Recupera 20% do HP máximo. |
| `n_heal_r1` | Poção Maior | rare | cura | 1 | Recupera 50% do HP máximo. |
| `n_regen_c1` | Ervas Medicinais | common | regeneração | 1 | Recupera 0.5 HP por segundo. |
| `n_regen_r1` | Fonte Viva | rare | regeneração | 1 | Recupera 1.5 HP por segundo. |
| `n_regen_e1` | Árvore da Vida | epic | regeneração | 5 | Recupera 2.5 HP por segundo e +20 HP máximo. |
| `n_floorheal_r1` | Acampamento | rare | cura | 1 | Ao vencer um andar, recupera 15% a mais de vida. |
| `n_steal_r1` | Mordida Vital | rare | cura | 1 | Cura 4% do dano causado. |
| `n_steal_l1` | Sanguessuga Real | legendary | cura | 6 | Cura 15% do dano causado. |
| `n_low_r1` | Último Fôlego | rare | condicional | 1 | Com menos de 30% de vida, causa +50% de dano. |
| `n_low_e1` | Fúria do Desesperado | epic | condicional | 4 | Com menos de 30% de vida, +100% de dano. Sempre: ataques inimigos -5%. |
| `n_boss_r1` | Caçador de Chefes | rare | condicional | 1 | +30% de dano contra bosses. |
| `n_boss_e1` | Matador de Reis | epic | condicional | 4 | +60% de dano contra bosses. |
| `n_chain3_r1` | Triunfo | rare | condicional | 1 | Chains x3 ou mais curam 6 HP. |
| `n_chain3_e1` | Canto da Vitória | epic | condicional | 4 | Chains x3 ou mais curam 12 HP. |
| `i_quick_c1` | Mãos Ágeis | common | velocidade | 1 | Jogadas rápidas em sequência causam +20% de dano. |
| `i_big_c1` | Golpe Pesado | common | combo | 1 | Matches de 4 ou mais blocos causam +20% de dano. |
| `i_chainen_c1` | Faísca em Cadeia | common | energia | 1 | Cada nível de chain acima de x1 dá +4 de energia. |
| `i_matchheal_c1` | Fôlego | common | cura | 1 | Cada rodada de match cura 2 HP. |
| `i_resist_c1` | Pele Dura | common | defesa | 1 | Veneno, silêncio, pressão e teias duram 25% menos. |
| `i_block_c1` | Reflexos | common | defesa | 2 | 8% de chance de ignorar o dano de um ataque. |
| `i_refund_c1` | Economia de Mana | common | habilidade | 1 | Usar a habilidade devolve 20% do custo em energia. |
| `i_opener_c1` | Primeiro Golpe | common | condicional | 1 | +25% de dano contra inimigos com mais de 70% de vida. |
| `i_floor_c1` | Experiência de Batalha | common | infinito | 2 | +0,4% de dano por andar já vencido (máximo +60%). |
| `i_critheal_c1` | Sorte Curativa | common | crítico | 2 | +5% de crítico. Cada crítico cura 2 HP. |
| `i_exec_r1` | Carrasco | rare | condicional | 3 | +45% de dano contra inimigos com menos de 30% de vida. |
| `i_mom_r1` | Ritmo de Combate | rare | combo | 3 | Cada jogada seguida sem ser atingido dá +4% de dano (até 8x). |
| `i_thorns_r1` | Armadura de Espinhos | rare | defesa | 3 | Devolve 25% do dano recebido ao inimigo e reduz 5% do dano. |
| `i_critenergy_r1` | Pulso Crítico | rare | crítico | 3 | +8% de crítico. Cada crítico dá +6 de energia. |
| `i_abheal_r1` | Magia Restauradora | rare | habilidade | 3 | Usar a habilidade cura 12 HP. Habilidade +15% de dano. |
| `i_quickcrit_r1` | Foco Afiado | rare | velocidade | 3 | Jogadas rápidas causam +25% de dano. +5% de crítico. |
| `i_boss_r1` | Caçador de Chefes | rare | boss | 4 | +30% de dano contra bosses. Eles atacam 15% mais devagar. |
| `i_dodge_r1` | Dança das Sombras | rare | defesa | 3 | 12% de chance de ignorar um ataque. Efeitos duram 15% menos. |
| `i_tide_r1` | Maré Viva | rare | sinergia | 3 | Chains dão +6 de energia por nível extra. Chain x3+ cura 6 HP. |
| `i_rest_r1` | Descanso do Viajante | rare | infinito | 3 | Ao vencer um andar, cura +10% da vida. Regenera 0,5 HP/s. |
| `i_hammer_r1` | Martelo de Guerra | rare | combo | 3 | Match 4+: +40% de dano. Match 5+ explode 2 blocos extras. |
| `i_gamble_r1` | Aposta Arriscada | rare | risco | 3 | +30% de dano, mas você recebe 10% a mais de dano. |
| `i_ambush_r1` | Emboscada | rare | condicional | 4 | +55% de dano contra inimigos com mais de 70% de vida. Inimigo 8% mais lento. |
| `i_reserve_r1` | Reserva Arcana | rare | habilidade | 3 | Habilidade devolve 35% do custo. +15% de energia ganha. |
| `i_exec_e1` | Sentença Final | epic | condicional | 5 | +90% de dano contra inimigos com menos de 30% de vida. +8% de crítico. |
| `i_mom_e1` | Avalanche | epic | combo | 5 | Jogada seguida sem ser atingido: +7% de dano (até 8x). Jogadas rápidas +20%. |
| `i_wall_e1` | Muralha Retaliadora | epic | defesa | 5 | Devolve 50% do dano recebido. Reduz 12% do dano. 5% de esquiva. |
| `i_feast_e1` | Banquete Sangrento | epic | cura | 5 | Cura 6% do dano causado. +6% de crítico. Cada crítico cura 4 HP. |
| `i_engine_e1` | Motor de Combos | epic | sinergia | 5 | Chains: +8 de energia por nível extra e +25% de dano. Habilidade devolve 15%. |
| `i_titan_e1` | Matador de Titãs | epic | boss | 5 | +55% de dano contra bosses, que atacam 20% mais devagar. Finalizar +25%. |
| `i_mind_e1` | Mente de Aço | epic | defesa | 5 | Efeitos duram 50% menos. 10% de esquiva. +15 HP máximo. |
| `i_veteran_e1` | Veterano do Infinito | epic | infinito | 5 | +0,8% de dano por andar vencido (máx. +60%). Cura +12% ao vencer andar. |
| `i_pact_e1` | Pacto Sanguíneo | epic | risco | 5 | +55% de dano e vampirismo 5%, mas perde 25 HP máximo. |
| `i_glass_e1` | Canhão de Vidro | epic | risco | 5 | +25% de crítico e críticos +60% mais fortes, mas recebe 15% a mais de dano. |
| `i_master_e1` | Mestre das Habilidades | epic | habilidade | 5 | Habilidade +50% de dano, 20% mais barata e cura 8 HP ao usar. |
| `i_clock_e1` | Relojoeiro | epic | velocidade | 5 | Inimigos 15% mais lentos. Jogadas rápidas +30% de dano. +15% de energia. |
| `i_phoenix_l1` | Pena de Fênix | legendary | especial | 6 | 1x por andar: ao morrer, volta com 50% da vida. Regenera 1 HP/s. |
| `i_juggernaut_l1` | Colosso Imparável | legendary | especial | 6 | Jogada seguida sem ser atingido: +9% de dano (até 8x). Defesa 10%, espinhos 20%. |
| `i_mirror_l1` | Espelho Vingativo | legendary | especial | 6 | Devolve 80% do dano recebido. 15% de esquiva. Reduz 10% do dano. |
| `i_algoz_l1` | Algoz do Infinito | legendary | especial | 7 | +150% de dano com inimigo abaixo de 30% de vida. +10% de crítico; crítico cura 6 HP. |
| `i_crown_l1` | Coroa do Infinito | legendary | infinito | 7 | +1,2% de dano por andar (máx. +60%). Cura +18% ao vencer andar. +20 HP máximo. |
| `i_storm_l1` | Tempestade de Energia | legendary | especial | 7 | Chain: +10 de energia por nível extra. Habilidade +40% de dano e devolve 50% do custo. |
| `i_bane_l1` | Flagelo dos Chefes | legendary | boss | 8 | +80% de dano contra bosses, que atacam 35% mais devagar. |
| `i_bloodsteel_l1` | Sangue e Aço | legendary | risco | 8 | +70% de dano, vampirismo 12% e críticos curam 3 HP, mas perde 30 HP máximo. |
| `i_timewarp_l1` | Tempo Dobrado | legendary | velocidade | 8 | Jogadas rápidas +60% de dano. Inimigos 20% mais lentos. +30% de energia ganha. |

## Músicas (assets/sounds/bgm/)

| Situação | Arquivo esperado | Status |
|---|---|---|
| menu | `menu.ogg` | sem arquivo próprio: silêncio (nenhum arquivo) |
| battle | `battle.ogg` | sem arquivo próprio: silêncio (nenhum arquivo) |
| boss | `boss.ogg` | sem arquivo próprio: silêncio (nenhum arquivo) |
| infinite | `infinite.ogg` | sem arquivo próprio: silêncio (nenhum arquivo) |
| infinite_boss | `infinite_boss.ogg` | sem arquivo próprio: silêncio (nenhum arquivo) |
| reward | `reward.ogg` | sem arquivo próprio: silêncio (nenhum arquivo) |
| victory | `victory.ogg` | sem arquivo próprio: silêncio (nenhum arquivo) |
| game_over | `game_over.ogg` | sem arquivo próprio: silêncio (nenhum arquivo) |
