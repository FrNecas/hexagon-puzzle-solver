from __future__ import annotations
from typing import List, Tuple


class Hex:
    NEIGHBOURS: List[Tuple[int]] = [
        (1, 0, -1),  # right
        (0, 1, -1),  # bottom right
        (-1, 1, 0),  # bottom left
        (-1, 0, 1),  # left
        (0, -1, 1),  # top left
        (1, -1, 0),  # top right
    ]

    def __init__(self, q: int, r: int, s: int):
        assert(q + r + s == 0)
        self.q = q
        self.r = r
        self.s = s

    def __eq__(self, other: Hex):
        """Checks if 2 hexagons in a map are the same."""
        return self.q == other.q and self.r == other.r and self.s == other.s

    def __key(self):
        return self.q, self.r, self.s

    def __hash__(self):
        return hash(self.__key())

    @classmethod
    def hex_add(cls, a: Hex, b: Hex):
        """Adds coordinates of 2 hexagons."""
        return Hex(a.q + b.q, a.r + b.r, a.s + b.s)

    def neighbour(self, direction: int):
        """Calculates the next hexagon in the specified direction.

        Args:
            direction: Direction to step in, must be between 0 and 5
        """
        return self.hex_add(self, Hex(*self.NEIGHBOURS[direction]))
