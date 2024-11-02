from math import inf

from typing import Union, Optional, Literal, Iterable

numeric = Union[int, float]


STATUS = {'clean', 'dirty'}
ACTION = {'move', 'suck'}

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
    __slots__ = 'position', 'status', 'action', 'parent', 'grid_dim', 'dirty_cells', 'moves', 'cost', 'heuristic_cost'
    def __init__(self, position: Position, action: Literal['move', 'suck'],
                 status: Literal['clean', 'dirty'], grid_dim: tuple[int, int],
                 dirty_cells: Iterable[Position],
                 moves: int = 0, parent: Optional['Cell'] = None,) -> None:
        if not isinstance(position, Position):
            raise TypeError("position must be of type Position")
        if not isinstance(action, str):
            raise TypeError("action must be one of string literal: 'move', 'suck'")
        elif not action in ACTION:
            raise ValueError("action must be one of string literal: 'move', 'suck'")
        if not isinstance(status, str):
            raise TypeError("status must be one of string literal: 'clean', 'dirty'")
        elif not status in STATUS:
            raise ValueError("status must be one of string literal: 'clean', 'dirty'")
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
        self.status = status
        self.parent = parent
        self.action = action
        self.grid_dim = grid_dim
        self.moves = moves

        self.dirty_cells = set()
        for cell_pos in dirty_cells:
            if not isinstance(cell_pos, Position):
                raise TypeError("Items in dirty_cells must be of type Position.")
            self.dirty_cells.add(cell_pos)

    def expand_cell(self) -> list['Cell']:
        expansion = []
        positions = []

        # suck
        if self.action == 'move' and self.status == 'dirty':
            expansion.append(Cell(self.position, action='suck', status='clean',
                                  parent=self, grid_dim=self.grid_dim,
                                  dirty_cells=self.dirty_cells - {self.position}, moves=self.moves))
            
        # up
        if self.position.y + 1 <= self.grid_dim[0]:
            positions.append(Position(self.position.x, self.position.y + 1))
        #down
        if self.position.y - 1 > 0:
            positions.append(Position(self.position.x, self.position.y - 1))
        #right
        if self.position.x + 1 <= self.grid_dim[1]:
            positions.append(Position(self.position.x + 1, self.position.y))
        #left
        if self.position.x - 1 > 0:
            positions.append(Position(self.position.x - 1, self.position.y))
            
        #top right
        if (self.position.x + 1 <= self.grid_dim[1]) and (self.position.y + 1 <= self.grid_dim[0]):
            positions.append(Position(self.position.x + 1, self.position.y + 1))
        #top left
        if (self.position.x - 1 > 0) and (self.position.y + 1 <= self.grid_dim[0]):
            positions.append(Position(self.position.x - 1, self.position.y + 1))
        #bot right
        if (self.position.x + 1 <= self.grid_dim[1]) and (self.position.y - 1 > 0):
            positions.append(Position(self.position.x + 1, self.position.y - 1))
        #bot left
        if (self.position.x - 1 > 0) and (self.position.y - 1 > 0):
            positions.append(Position(self.position.x - 1, self.position.y - 1))
            
        for new_pos in positions:
            new_status = 'dirty' if new_pos in self.dirty_cells else 'clean'
            expansion.append(Cell(new_pos, action='move', status=new_status,
                                  parent=self, grid_dim=self.grid_dim,
                                  dirty_cells=self.dirty_cells, moves=self.moves + 1))
        return expansion
    
    def calc_cost(self) -> None:
        self._cost()
        self._heu_cost()
    
    def _cost(self) -> None:
        if self.parent is None: self.cost = 0
        else: self.cost = self.parent.cost + 1 + (0 if self.action == 'move' else self.moves)
    
    def _heu_cost(self) -> None:
        self.heuristic_cost = 0
        for cell_pos in self.dirty_cells:
            self.heuristic_cost += distance(self.position, cell_pos, p=inf)
        
    def __eq__(self, other: 'Cell') -> bool:
        return (self.position == other.position) and\
               (self.status == other.status) and\
               (self.action == other.action) and\
               (self.dirty_cells == other.dirty_cells)
    def __hash__(self) -> int:
        self_id = str(self.position[0]) + str(self.position[1]) + self.status + self.action
        return hash(self_id)
    def __lt__(self, other: 'Cell') -> bool:
        return (self.cost + self.heuristic_cost) < (other.cost + other.heuristic_cost)