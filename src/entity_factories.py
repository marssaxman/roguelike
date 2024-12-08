from components.ai import HostileEnemy, Passive, Epic_friend
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item
import graphics

player = Actor(
    char=graphics.PLAYER,
    color=(255, 255, 255),
    name="Player",
    ai_cls=Passive,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=10),
    level=Level(level_up_base=200),
)

orc = Actor(
    char=graphics.ORC,
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)

troll=Actor(
    char=graphics.TROLL,
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=0, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)

rat=Actor(
    char=graphics.RAT,
    color=(127, 127, 200),
    name="Rat",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=4, base_defense=0, base_power=3),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=10)
)

silly=Actor(
    char=ord("x"),
    color=(255, 0, 255),
    name="Helper",
    ai_cls=Epic_friend,
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=0)
)

confusion_scroll = Item(
    char=graphics.SCROLL,
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)

fireball_scroll = Item(
    char=graphics.SCROLL,
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)

health_potion = Item(
    char=graphics.POTION,
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)

lightning_scroll = Item(
    char=graphics.SCROLL,
    color=(255, 255, 0),
    name="Death Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5)
)

dagger = Item(
    char="/", color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

sword = Item(char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword())

leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)
