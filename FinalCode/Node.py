from math import inf
from copy import deepcopy

from typing import Optional


class Node:
    __slots__ = 'id', 'other_attributes','distance', 'h_distance', 'neighbours'
    def __init__(self, id: str, *, neighbours: Optional[list['Node']] = None,
                 **other_attrs) -> None:
        if not neighbours: neighbours = []

        self.id = id
        self.other_attributes = other_attrs
        self.distance = inf
        self.h_distance = None
        self.neighbours: list[Node] = deepcopy(neighbours)


    def heuristic(self, other: 'Node') -> float:
        raise NotImplementedError("Heuristic function not implemeneted.")
    
    
    def __hash__(self) -> int:
        return hash(self.id)

    def __lt__(self, other: 'Node') -> bool:
        if self.h_distance != None:
            return (self.distance + self.h_distance) < (other.distance + other.h_distance)
        else: return self.distance < other.distance