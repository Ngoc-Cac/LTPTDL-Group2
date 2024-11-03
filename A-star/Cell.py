from math import inf

from typing import Union, Optional, Literal, Iterable

numeric = Union[int, float]


def distance(p1: 'Position', p2: 'Position', *, p: float = 2) -> float:
    if not isinstance(p, float):
        raise TypeError("p must be a positive integer")
    elif p < 1:
        raise ValueError("p must be a positive integer")
    if p is inf: return max(abs(p1.x - p2.x), abs(p1.y - p2.y))
    else: return (abs(p1.x - p2.x) ** p + abs(p1.y - p2.y) ** p) ** (1 / p)


class Position(tuple):
    def __new__(cls, x: numeric, y: numeric) -> 'Position':
        if not isinstance(x, numeric):
            raise TypeError(f"x-coordinates must be int or float, '{x}' was given")
        if not isinstance(y, numeric):
            raise TypeError(f"y-coordinates must be int or float, '{y}' was given")
        return super().__new__(cls, (x, y))
    
    @property
    def x(self) -> numeric: return self[0]
    @property
    def y(self) -> numeric: return self[1]


class Cell:
    __slots__ = 'position', 'parent', 'grid_dim', 'dirty_cells', 'moves', 'cost', 'heuristic_cost'
    def __init__(self, position: Position, grid_dim: tuple[int, int],
                 dirty_cells: Iterable[Position], moves: int = 0,
                 parent: Optional['Cell'] = None,) -> None:
        if not isinstance(position, Position):
            raise TypeError("position must be of type Position")
        elif (position.x < 1) or (position.y < 1):
            raise ValueError("position of cell must be larger than (1, 1)")
        if not isinstance(parent, Optional[Cell]):
            raise TypeError("parent must be of type Cell or None")
        if not isinstance(grid_dim, tuple):
            raise TypeError("grid_dim must be a tuple of int representing the number of rows and cols")
        elif not all(isinstance(value, int) for value in grid_dim):
            raise TypeError("non-integer type passed in grid_dim")
        elif grid_dim[0] < 1 or grid_dim[1] < 1:
            raise ValueError(f"Invalid grid dimensions {grid_dim}")
        if not isinstance(moves, int):
            raise TypeError("moves must be a positive integer")

        self.position = position
        self.parent = parent
        self.grid_dim = grid_dim
        self.moves = moves

        self.dirty_cells = set()
        for cell_pos in dirty_cells:
            if not isinstance(cell_pos, Position):
                raise TypeError("Items in dirty_cells must be of type Position.")
            self.dirty_cells.add(cell_pos)

    def expand_cell(self) -> list['Cell']:
        neighbours = []

        for new_pos in self.dirty_cells:
            neighbours.append(Cell(new_pos, parent=self, grid_dim=self.grid_dim,
                                  dirty_cells=self.dirty_cells - {new_pos},
                                  moves=self.moves + distance(self.position, new_pos, p=inf)))
        return neighbours
    
    
    def calc_cost(self) -> None:
        self._cost()
        self._heu_cost()
    
    def _cost(self) -> None:
        if self.parent is None: self.cost = 0
        else:
            # previous cost +
            # cost to go from previous state to this state +
            # cost to clean the cell after n movements
            self.cost = self.parent.cost +\
            distance(self.parent.position, self.position) +\
            self.moves + 1
    
    def _heu_cost(self) -> None:
        self.heuristic_cost = 0
        for cell_pos in self.dirty_cells:
            self.heuristic_cost += distance(self.position, cell_pos, p=inf)
        

    def __eq__(self, other: 'Cell') -> bool:
        return (self.position == other.position) and\
               (self.dirty_cells == other.dirty_cells)
    
    def __hash__(self) -> int:
        self_id = str(self.position[0]) + str(self.position[1])
        return hash(self_id)
    
    def __lt__(self, other: 'Cell') -> bool:
        return (self.cost + self.heuristic_cost) < (other.cost + other.heuristic_cost)