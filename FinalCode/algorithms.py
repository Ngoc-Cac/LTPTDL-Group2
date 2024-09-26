from math import inf
from pandas import DataFrame, Series

from FinalCode.PriorityQueue import PriorityQueue
from FinalCode.Node import Node


from typing import Iterable, Optional


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

def astar(nodes: Iterable[Node], adjacency_matrix: DataFrame,
          source: Node, target: Node) -> Series:
    my_queue: PriorityQueue[Node] = PriorityQueue()
    previous: Series[Optional[Node]] = Series([None] * len(nodes), [node.id for node in nodes])

    for node in nodes: node.h_distance = inf
    
    source.distance = 0
    my_queue.push(source)
    while my_queue:
        cur = my_queue.pop()

        if cur.id == target.id: return previous
        
        for neighbour in cur.neighbours:
            neighbour_dist = cur.distance + adjacency_matrix[neighbour.id][cur.id]
            neighbour_h_dist = cur.heuristic(neighbour)
            if neighbour_dist + neighbour_h_dist < neighbour.distance + neighbour.h_distance:
                neighbour.distance = neighbour_dist
                neighbour.h_distance = neighbour_h_dist
                previous[neighbour.id] = cur
                my_queue.push(neighbour)

    return previous