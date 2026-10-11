"""characters/ - cria o personagem certo a partir do id (data/characters.json)."""
from characters.archer import Archer
from characters.assassin import Assassin
from characters.bard import Bard
from characters.blacksmith import Blacksmith
from characters.character import Player
from characters.cleric import Cleric
from characters.judge import Judge
from characters.mage import Mage
from characters.monk import Monk
from characters.warrior import Warrior
from characters.yoshi import Yoshi

REGISTRY = {
    "judge": Judge,          # Juiz
    "bard": Bard,            # Tulipa (Bardo)
    "assassin": Assassin,    # Tali (Assassina)
    "cleric": Cleric,        # Maizona (Clériga)
    "blacksmith": Blacksmith,  # Caique (Ferreiro)
    "mage": Mage,            # Breno (Mago)
    "archer": Archer,        # Romulo (Arqueiro)
    "warrior": Warrior,      # Matheuzim (Guerreiro)
    "monk": Monk,            # Yuko (Monge)
    "yoshi": Yoshi,          # Yoshi (Samurai) - desbloqueio especial: boss do andar 100 do Infinito
}


def create_character(char_id, data):
    return REGISTRY.get(char_id, Player)(char_id, data)


def character_title(data):
    """Nome + classe para mostrar ao jogador: 'Tulipa - Bardo' (o Juiz não tem classe)."""
    cls = data.get("class", "")
    return f"{data['name']} - {cls}" if cls and cls != "—" else data["name"]


def unlock_hint(data):
    """Texto dinâmico de como desbloquear (muda conforme o personagem)."""
    rule = data.get("unlock", "default")
    if rule == "defeat_in_infinite":
        return f"Derrote {data['name']} no Modo Infinito para desbloquear este personagem."
    if rule == "defeat_yoshi_infinite_100":
        return f"Derrote {data['name']}, o Rei do Tetris, no andar 100 do Modo Infinito."
    if rule == "default":
        return ""
    return "Personagem bloqueado."
