from __future__ import annotations

from components.base_component import BaseComponent


class Appearance(BaseComponent):
    def __init__(self):
        pass
    def render(self):
        return "?", (255, 255, 255)
    def move(self, dx: int, dy: int) -> None:
        pass
    def animate(self) -> None:
        pass


class Default(Appearance):
    def __init__(self):
        pass


class Static(Appearance):
    def __init__(self, char, color):
        self.char = char
        self.color = color
    def render(self):
        return self.char, self.color


class Directional(Appearance):
    """Pick left or right appearance depending on last horizontal motion."""
    def __init__(self, left: Appearance, right: Appearance):
        self.left = left
        self.right = right
        self.current = left # arbitrary

    def move(self, dx: int, dy: int) -> None:
        if dx < 0:
            self.current = self.left
        elif dx > 0:
            self.current = self.right
        # if no horizontal motion, don't change appearance

    def animate(self) -> None:
        self.left.animate()
        self.right.animate()

    def render(self):
        return self.current.render()


class Looped(Appearance):
    """Cycle through a sequence of different appearances on each render."""
    def __init__(self, loop):
        self.loop = loop
        self.pos = 0

    def move(self, dx: int, dy: int) -> None:
        for a in self.loop:
            a.move(dx, dy)

    def animate(self):
        self.pos += 1
        if self.pos >= len(self.loop):
            self.pos = 0

    def render(self):
        return self.loop[self.pos].render()

