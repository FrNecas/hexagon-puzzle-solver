from __future__ import annotations
from typing import Dict, List, Tuple, Set


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

        # Hash maps used for quickly checking whether the map satisfies the condition
        self.rows: List[Set[int]] = [set() for _ in range(self.diameter)]
        self.diags1: List[Set[int]] = [set() for _ in range(self.diameter)]
        self.diags2: List[Set[int]] = [set() for _ in range(self.diameter)]

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

    def check_condition(self, choices: List[int]):
        """Checks whether the current state satisfies the task condition."""
        for sets in (self.rows, self.diags1, self.diags2):
            for value_set in sets:
                if len(value_set) != len(choices):
                    return False
        return True

    def set_value(self, current_node: Hex, new_value: int, row_index: int, diag1_index: int, diag2_index: int):
        """Sets the value of the current_node to new_value.

        Returns whether the value was set successfully (returns False if
        the number has already been used in the current row/diagonal).
        """
        if new_value != 0:
            if new_value in self.rows[row_index] or new_value in self.diags1[diag1_index] or new_value in \
                    self.diags2[diag2_index]:
                return False
            self.rows[row_index].add(new_value)
            self.diags1[diag1_index].add(new_value)
            self.diags2[diag2_index].add(new_value)
        self._map[current_node] = new_value
        return True

    def reset_value(self, current_node: Hex, row_index: int, diag1_index: int, diag2_index: int):
        """Resets a node to its initial state."""
        current_value = self._map[current_node]
        self._map[current_node] = 0
        if current_value != 0:
            self.rows[row_index].remove(current_value)
            self.diags1[diag1_index].remove(current_value)
            self.diags2[diag2_index].remove(current_value)

    def is_invalid_row_or_diag(self, direction: int, choices: List[int], row_index: int,
                               diag1_index: int, diag2_index: int):
        """Checks if the recently finished row or diagonal is valid."""
        invalid = False
        if direction % 3 == 0:
            # We just finished a row, check the rows
            if len(choices) != len(self.rows[row_index]):
                invalid = True
        elif direction % 3 == 1:
            # We just finished top right - bottom left diag
            if len(choices) != len(self.diags2[diag2_index]):
                invalid = True
        elif direction % 3 == 2:
            # We just finished top left - bottom right diag
            if len(choices) != len(self.diags1[diag1_index]):
                invalid = True
        return invalid

    def _walk(self, current_node: Hex, direction: int, remaining_steps: int, level: int,
              choices: List[int], choices_index: int):
        row_index = current_node.r + self.radius
        diag1_index = current_node.s + self.radius
        diag2_index = current_node.q + self.radius
        # Base case for recursion
        if current_node == Hex(0, 0, 0):
            for new_value in (0, choices[choices_index]):
                if not self.set_value(current_node, new_value, row_index, diag1_index, diag2_index):
                    continue
                if self.check_condition(choices):
                    self.print()
                self.reset_value(current_node, row_index, diag1_index, diag2_index)
            return

        # We can either leave the current cell empty (0) or fill it with the next number
        for new_value in (0, choices[choices_index]):
            new_choices_index = choices_index
            new_level = level
            new_direction = direction
            new_remaining_steps = remaining_steps
            next_node = current_node

            if new_value != 0:
                new_choices_index = (choices_index + 1) % len(choices)
            if not self.set_value(current_node, new_value, row_index, diag1_index, diag2_index):
                continue
            if remaining_steps == 0:
                # One direction finished, lets try to cut down the search tree
                if self.is_invalid_row_or_diag(direction, choices, row_index, diag1_index, diag2_index):
                    self.reset_value(current_node, row_index, diag1_index, diag2_index)
                    continue

                # Change direction
                new_direction = (direction + 1) % 6
                new_remaining_steps = self.radius - level - (1 if new_direction == 5 else 0)
                # Last element before center, there is no steps to go to in top right direction, just skip it.
                if new_direction == 5 and new_remaining_steps == 0:
                    new_direction = 0
                    new_remaining_steps = 1
                if new_direction == 0:
                    new_level += 1
            if new_remaining_steps != 0:
                next_node = current_node.neighbour(new_direction)
                new_remaining_steps -= 1
            self._walk(next_node, new_direction, new_remaining_steps, new_level, choices, new_choices_index)
            self.reset_value(current_node, row_index, diag1_index, diag2_index)

    def solve_problem(self, solve_for: int):
        """Solves the hexagon problem trying to fit `solve_for` numbers into the hexagon."""
        current_node = Hex(0, -self.radius, self.radius)
        self._walk(current_node, 0, self.radius, 0, [x + 1 for x in range(solve_for)], 0)
