from __future__ import annotations

from components.base_component import BaseComponent


class Appearance(BaseComponent):
    def __init__(
        self,
        equipment_type: EquipmentType,
        power_bonus: int = 0,
        defense_bonus: int = 0,
    ):
        self.equipment_type = equipment_type

        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus


class Default(Appearance):
    def __init__(self):
        pass
    def render(self):
        return "?", (255, 255, 255)


class Static(Appearance):
    def __init__(self, char, color):
        self.char = char
        self.color = color
    def render(self):
        return self.char, self.color


class Directional(Appearance):
    def __init__(self, left, right, color):
        self.left = left
        self.right = right
        self.color = color
    def render(self):
        return self.left, self.color


