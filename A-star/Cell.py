from math import inf

from typing import Union, Optional, Iterable, Literal

numeric = Union[int, float]


def distance(point1: 'Position', point2: 'Position', *, p: numeric = 2) -> float:
    """
    Find p-norm of between two Cartesian coordinates.

    --------------
    ## Parameters:
    point1 (Position): coordinates of first point\n
    point2 (Position): coordinates of second point\n
    p (int | float): the p degree in p-norm. By default, function gives Euclidian distance (p = 2)

    --------------
    ## Raises:
    TypeError if p is not int or float
    ValueError if p is not larger than or equal to 1

    Parameters:
    point1 (Position): coordinates of first point
    point2 (Position): coordinates of second point
    p (int | float): the p degree in p-norm. By default, function gives Euclidian distance (p = 2)
    """
    if not isinstance(p, numeric):
        raise TypeError("p must be a number larger than or equal to 1")
    elif p < 1:
        raise ValueError("p must be a number larger than or equal to 1")
    
    if p is inf: return max(abs(point1.x - point2.x), abs(point1.y - point2.y))
    else: return (abs(point1.x - point2.x) ** p + abs(point1.y - point2.y) ** p) ** (1 / p)


class Position(tuple):
    """
    Represent coordinates on the Cartesian plane. Note: Position is of type tuple.

    --------------
    ## Attributes:
    x (int | float): the x-coordinate of position\n
    y (int | float): the y-coordinate of position
    """
    def __new__(cls, x: numeric, y: numeric) -> 'Position':
        """
        Create a coordinate on the Cartesian plane.

        --------------
        ## Parameters:
        x (int | float): the x-coordinate of position\n
        y (int | float): the y-coordinate of position

        ----------
        ## Raises:
        TypeError if x or y is not int or float

        Parameters:
        x (int | float): the x-coordinate of position
        y (int | float): the y-coordinate of position
        """
        if not isinstance(x, numeric):
            raise TypeError(f"x-coordinates must be int or float, '{x}' was given")
        if not isinstance(y, numeric):
            raise TypeError(f"y-coordinates must be int or float, '{y}' was given")
        return super().__new__(cls, (x, y))
    
    @property
    def x(self) -> numeric:
        """The x-coordinate of position"""
        return self[0]
    @property
    def y(self) -> numeric:
        """The y-coordinate of position"""
        return self[1]

ACTIONS = {'move', 'suck'}

class Cell:
    __slots__ = 'position', 'parent', 'grid_dim', 'dirty_cells', 'moves', 'action', 'cost', 'heuristic_cost'
    def __init__(self, position: Position, grid_dim: tuple[int, int],
                 dirty_cells: Iterable[Position], moves: int = 0,
                 parent: Optional['Cell'] = None, action: Literal['move', 'suck'] = 'move') -> None:
        if not isinstance(position, Position):
            raise TypeError("position must be of type Position")
        elif (position.x < 1) or (position.y < 1):
            raise ValueError("position of cell must be larger than (1, 1)")
        if not isinstance(grid_dim, tuple):
            raise TypeError("grid_dim must be a tuple of int representing the number of rows and cols")
        elif not all(isinstance(value, int) for value in grid_dim):
            raise TypeError("non-integer type passed in grid_dim")
        elif grid_dim[0] < 1 or grid_dim[1] < 1:
            raise ValueError(f"Invalid grid dimensions {grid_dim}")
        if not isinstance(moves, int):
            raise TypeError("moves must be a positive integer")
        if not isinstance(parent, Optional[Cell]):
            raise TypeError("parent must be of type Cell or None")
        if not isinstance(action, str):
            raise TypeError("action must be a string literal of 'move' or 'suck'")
        elif not action in ACTIONS:
            raise ValueError("action msut be a string literal of 'move' or 'suck'")

        self.position = position
        self.parent = parent
        self.grid_dim = grid_dim
        self.moves = moves
        self.action = action

        self.dirty_cells = set()
        for cell_pos in dirty_cells:
            if not isinstance(cell_pos, Position):
                raise TypeError("Items in dirty_cells must be of type Position.")
            self.dirty_cells.add(cell_pos)

        self.calc_cost()

    def expand_cell(self) -> list['Cell']:
        neighbours = []

        # suck if dirty
        if self.position in self.dirty_cells:
            neighbours.append(Cell(self.position, parent=self, grid_dim=self.grid_dim,
                                   dirty_cells=self.dirty_cells - {self.position},
                                   moves = self.moves, action='suck'))
        
        neigh_pos = []
        # up, down, left, right
        if self.position.x > 1:
            neigh_pos.append((self.position.x - 1, self.position.y))
        if self.position.x < self.grid_dim[1]:
            neigh_pos.append((self.position.x + 1, self.position.y))
        if self.position.y > 1:
            neigh_pos.append((self.position.x, self.position.y - 1))
        if self.position.y < self.grid_dim[0]:
            neigh_pos.append((self.position.x, self.position.y + 1))

        # top/bot left/right
        if (self.position.x > 1) and (self.position.y > 1):
            neigh_pos.append((self.position.x - 1, self.position.y - 1))
        if (self.position.x > 1) and (self.position.y < self.grid_dim[0]):
            neigh_pos.append((self.position.x - 1, self.position.y + 1))
        if (self.position.x < self.grid_dim[1]) and (self.position.y > 1):
            neigh_pos.append((self.position.x + 1, self.position.y - 1))
        if (self.position.x < self.grid_dim[1]) and (self.position.y < self.grid_dim[0]):
            neigh_pos.append((self.position.x + 1, self.position.y + 1))

        for new_pos in neigh_pos:
            neighbours.append(Cell(Position(*new_pos), parent=self,
                                   grid_dim=self.grid_dim,
                                   dirty_cells=self.dirty_cells,
                                   moves=self.moves + 1))
        return neighbours
    

    def calc_cost(self) -> None:
        self._cost()
        self._heu_cost()
    
    def _cost(self) -> None:
        if self.parent is None: self.cost = 0
        else:
            if self.action == 'move': self.cost = self.parent.cost + 1
            else: self.cost = self.parent.cost + self.moves + 1
    
    def _heu_cost(self) -> None:
        self.heuristic_cost = 0
        for cell_pos in self.dirty_cells:
            self.heuristic_cost += distance(self.position, cell_pos, p=inf)
        if len(self.dirty_cells) != 0:
            self.heuristic_cost /= len(self.dirty_cells)
        

    def __eq__(self, other: 'Cell') -> bool:
        return (self.position == other.position) and\
               (self.dirty_cells == other.dirty_cells)
    
    def __hash__(self) -> int:
        return hash(self.position)
    
    def __lt__(self, other: 'Cell') -> bool:
        return (self.cost + self.heuristic_cost) < (other.cost + other.heuristic_cost)