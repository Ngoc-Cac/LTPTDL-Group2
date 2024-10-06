from math import inf
from pandas import DataFrame, Series

from FinalCode.PriorityQueue import PriorityQueue
from FinalCode.Node import Node


from typing import Callable, Iterable, Optional


def dijkstra(nodes: Iterable[Node], adjacency_matrix: DataFrame,
             source: Node, target: Node, *,
             do_UCS: bool = False) -> Series:
    my_queue: PriorityQueue[Node] = PriorityQueue()
    previous: Series[Optional[Node]] = Series([None] * len(nodes), [node.id for node in nodes])

    if do_UCS:
        source.distance = 0
        my_queue.push(source)
    else:
        for node in nodes:
            if node == source: source.distance = 0
            else: node.distance = inf
            my_queue.push(node)

    while my_queue:
        cur = my_queue.pop()

        if cur.id == target.id: return previous

        for neighbour in cur.neighbours:
            other_dist = cur.distance + adjacency_matrix[neighbour.id][cur.id]
            if other_dist < neighbour.distance:
                neighbour.distance = other_dist
                previous[neighbour.id] = cur
                my_queue.push(neighbour)

    return previous


def manhattan(node1: Node, node2: Node) -> float:
    x1, y1 = node1.other_attributes.get('x', 0), node1.other_attributes.get('y', 0)
    x2, y2 = node2.other_attributes.get('x', 0), node2.other_attributes.get('y', 0)
    return abs(x1 - x2) + abs(y1 - y2)


def euclidean(node1: Node, node2: Node) -> float:
    x1, y1 = node1.other_attributes.get('x', 0), node1.other_attributes.get('y', 0)
    x2, y2 = node2.other_attributes.get('x', 0), node2.other_attributes.get('y', 0)
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def chebyshev(node1: Node, node2: Node) -> float:
    x1, y1 = node1.other_attributes.get('x', 0), node1.other_attributes.get('y', 0)
    x2, y2 = node2.other_attributes.get('x', 0), node2.other_attributes.get('y', 0)
    return max(abs(x1 - x2), abs(y1 - y2))

def octile(node1: Node, node2: Node) -> float:
    x1, y1 = node1.other_attributes.get('x', 0), node1.other_attributes.get('y', 0)
    x2, y2 = node2.other_attributes.get('x', 0), node2.other_attributes.get('y', 0)
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return (dx + dy) + (2**0.5 - 2) * min(dx, dy)

def hamming(node1: Node, node2: Node) -> float:
    return sum(el1 != el2 for el1, el2 in zip(node1.id, node2.id))



def astar(nodes: Iterable[Node], adjacency_matrix: DataFrame, 
          source: Node, target: Node, heuristic_func: Callable[[Node, Node], float]) -> Series:
    """
    A* algorithm implementation where the heuristic is passed externally as a function.
    """
    my_queue: PriorityQueue[Node] = PriorityQueue()
    previous: Series[Optional[Node]] = Series([None] * len(nodes), [node.id for node in nodes])

    for node in nodes:
        node.distance = inf
        node.h_distance = inf
    
    source.distance = 0 
    source.h_distance = heuristic_func(source, target)  
    my_queue.push(source)
    
    while my_queue:
        cur = my_queue.pop()


        if cur.id == target.id:
            return previous
        
        for neighbour in cur.neighbours:
            neighbour_dist = cur.distance + adjacency_matrix[neighbour.id][cur.id]
            if neighbour_dist < neighbour.distance:
                neighbour.distance = neighbour_dist
                neighbour.h_distance = heuristic_func(neighbour, target)
                previous[neighbour.id] = cur
                my_queue.push(neighbour)

    return previous


