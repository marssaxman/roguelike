from components.ai import HostileEnemy, Passive, Epic_friend, HostileArcher
from components import consumable, equippable, mechanism
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.appearance import Static
from entity import Actor, Item, Fixture
import graphics


player = Actor(
    appearance=graphics.player,
    name="Player",
    ai_cls=Passive,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=10),
    level=Level(level_up_base=200),
)

orc = Actor(
    appearance=graphics.orc,
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)

troll=Actor(
    appearance=graphics.troll,
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=0, base_power=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)

rat=Actor(
    appearance=graphics.rat,
    name="Rat",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=4, base_defense=0, base_power=3),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=10)
)

archer=Actor(
    appearance=graphics.archer,
    name="Archer",
    ai_cls=HostileArcher,
    fighter=Fighter(hp=3, base_defense=0, base_power=4), # This damage is ranged, also when people get close this enemy should run away
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=40)
)

wizard=Actor(
    appearance=Static(char=ord("w"), color=(255, 0, 255)),
    name="Wizard",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=6, base_defense=0, base_power=0), # The power doesn't matter, It's based on the spells she uses, which is based on the floor.
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=50)
)

silly=Actor(
    appearance=Static(char=ord("x"), color=(255, 0, 255)),
    name="Helper",
    ai_cls=Epic_friend,
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=0)
)

armored_rat=Actor(
    appearance=graphics.armored_rat,
    name="Armored Rat",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=8, base_defense=1, base_power=4),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=30)

)

soldier=Actor(
    appearance=graphics.soldier,
    name="Soldier",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=20, base_defense=1, base_power=6),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=30)

)

giant=Actor(
    appearance=graphics.giant,
    name="Giant",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, base_defense=0, base_power=8),
    equipment=Equipment(),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=30)

)

confusion_scroll = Item(
    appearance=Static(char=graphics.SCROLL, color=(207, 63, 255)),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)

fireball_scroll = Item(
    appearance=Static(char=graphics.SCROLL, color=(255, 0, 0)),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)

health_potion = Item(
    appearance=Static(char=graphics.POTION, color=(127, 0, 255)),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)

Death_Scroll = Item(
    appearance=Static(char=graphics.SCROLL, color=(255, 255, 0)),
    name="Death Scroll",
    consumable=consumable.DeathDamageConsumable(damage=20, maximum_range=5)
)

dagger = Item(
    appearance=Static(char=ord("/"), color=(0, 191, 255)),
    name="Dagger",
    equippable=equippable.Dagger(),
)

sword = Item(
    appearance=Static(char=ord("/"), color=(0, 191, 255)),
    name="Sword",
    equippable=equippable.Sword()
)

leather_armor = Item(
    appearance=Static(char=ord("["), color=(139, 69, 19)),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    appearance=Static(char=ord("["), color=(139, 69, 19)),
    name="Chain Mail",
    equippable=equippable.ChainMail(),
)

door_outside = Fixture(
    appearance=graphics.door_outside,
    name="tower entrance",
    mechanism=mechanism.DoorOutside(),
)

downward_stairs = Fixture(
    appearance=graphics.stairs_down,
    name="downward stairs",
    mechanism=mechanism.DownStairs(),
)

upward_stairs = Fixture(
    appearance=graphics.stairs_up,
    name="upward stairs",
    mechanism=mechanism.UpStairs(),
)

amulet_of_yendor = Item(
    appearance=graphics.amulet_of_yendor,
    name="Bob's life savings",
)
