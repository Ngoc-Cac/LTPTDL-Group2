from math import inf

from typing import Union, Optional, Iterable

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


class Cell:
    __slots__ = 'position', 'parent', 'dirty_cells', 'moves', 'cost', 'heuristic_cost'
    def __init__(self, position: Position, dirty_cells: Iterable[Position],
                 moves: int = 0, parent: Optional['Cell'] = None) -> None:
        """
        Initialize a Cell instance.
        
        Note: Optional parameters are not meant to be passed when initializing a start state.

        ## Parameters:
        position (Position): the current position of the robot

        dirty_cells (Iterable[Position]): a collection of dirty cells' positions

        moves (int): the number of moves robot has made.
        This is 0 by default and should not be passed in for start state.
        
        parent (Cell): the previous state.
        This is `None` by default and should not be passed in for start state. 


        Parameters:
        position (Position): the current position of the robot
        dirty_cells (Iterable[Position]): a collection of dirty cells' positions
        moves (int): the number of moves robot has made. This is 0 by default and\
        should not be passed in for start state.
        parent (Cell): the previous state. This is None by default and\
        should not be passed in for start state. 
        """
        if not isinstance(position, Position):
            raise TypeError("position must be of type Position")
        elif (position.x < 1) or (position.y < 1):
            raise ValueError("position of cell must be larger than (1, 1)")
        if not isinstance(parent, Optional[Cell]):
            raise TypeError("parent must be of type Cell or None")
        if not isinstance(moves, int):
            raise TypeError("moves must be a positive integer")

        self.position = position
        self.parent = parent
        self.moves = moves

        self.dirty_cells = set()
        for cell_pos in dirty_cells:
            if not isinstance(cell_pos, Position):
                raise TypeError("Items in dirty_cells must be of type Position.")
            self.dirty_cells.add(cell_pos)

        self.calc_cost()

    def expand_cell(self) -> list['Cell']:
        """
        Find neighbouring 'cell'.
        
        Here neighbouring cell does not imply cells with positions next to
        the current position. Neighbouring cells here mean the next dirty cell
        that the robot can go to and clean.
        
        For example, with dirty cells {(1, 1), (1, 2)}. Function returns two Cell
        instances, one with position at (1, 1) and one with position at (1, 2)
        """
        neighbours = []

        for new_pos in self.dirty_cells:
            neighbours.append(Cell(new_pos, parent=self,
                                   dirty_cells=self.dirty_cells - {new_pos},
                                   moves=self.moves + distance(self.position, new_pos, p=inf)))
        return neighbours
    

    def calc_cost(self) -> None:
        """
        Update cost and heuristic cost of current cell
        """
        self._cost()
        self._heu_cost()
    
    def _cost(self) -> None:
        """
        Calculate the cost at the current cell
        """
        if self.parent is None: self.cost = 0
        else:
            # previous cost +
            # cost to go from previous state to this state +
            # cost to clean the cell after n movements
            self.cost = self.parent.cost +\
                        distance(self.parent.position, self.position, p=inf) +\
                        self.moves + 1
    
    def _heu_cost(self) -> None:
        """
        Calculate the heuristic cost. Heuristic cost is the total cost to clean\
        every other dirty cells, assuming that the cleaning cost is constant\
        and the distance to the dirty cells is equal to the chebyshev distance\
        between current position and the dirty cells' position. 
        """
        self.heuristic_cost = 0
        for cell_pos in self.dirty_cells:
            self.heuristic_cost += distance(self.position, cell_pos, p=inf) + self.moves + 1
        

    def __eq__(self, other: 'Cell') -> bool:
        if not isinstance(other, Cell):
            return False
        return (self.position == other.position) and\
               (self.dirty_cells == other.dirty_cells)
    
    def __hash__(self) -> int:
        return hash(self.position)
    
    def __lt__(self, other: 'Cell') -> bool:
        if not isinstance(other, Cell):
            raise TypeError(f"'<' not supported between instances of Cell and {type(other)}")
        return (self.cost + self.heuristic_cost) < (other.cost + other.heuristic_cost)