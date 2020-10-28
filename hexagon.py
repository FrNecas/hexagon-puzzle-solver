from __future__ import annotations
from typing import Dict, List, Tuple


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


class HexMap:
    """Represents a hexagonal map of hexagons."""
    def __init__(self, radius: int):
        self._map: Dict[Hex, int] = {}
        self.radius: int = radius
        self.diameter: int = 2 * radius + 1

        # Create a hexagon shape from hexagons
        for q in range(-radius, radius + 1):
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)
            for r in range(r1, r2 + 1):
                self._map[Hex(q, r, -q - r)] = 0

    def get_direction(self, start: Hex, direction: int):
        """Creates an iterator over a row/diagonal in the given direction."""
        # Rollback to the start of the row
        while start in self._map:
            start = start.neighbour(direction + 3)
        start = start.neighbour(direction)

        # Yield the row
        while start in self._map:
            yield start
            start = start.neighbour(direction)

    def print(self):
        """Prints the text representation of the map."""
        min_row_len = current_row_len = self.diameter - self.radius
        # start in the top left corner
        starting_hexagon = Hex(0, -self.radius, self.radius)
        shift = 1
        while current_row_len > min_row_len - 1:
            starting_spaces = self.diameter - current_row_len
            print(starting_spaces * ' ', end='')
            for hexagon in self.get_direction(starting_hexagon, 0):
                print(self._map[hexagon], end=' ')
            print()

            if current_row_len == self.diameter:
                # We've reached the middle row, the rows are shrinking
                shift = -1
            current_row_len += shift
            if shift == 1:
                starting_hexagon = starting_hexagon.neighbour(2)
            else:
                starting_hexagon = starting_hexagon.neighbour(1)
        print()

