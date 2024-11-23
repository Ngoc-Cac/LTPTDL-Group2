from math import inf
from copy import deepcopy
from csv import reader

from typing import Optional, Union

def from_csv(filename: str) -> tuple[dict[str, tuple[int, 'Node']], list[list[float]]]:
    """
    Construct list of nodes and adjacency matrix from csv file. Each line in file must be
    a tuple representing edges in the graph, that is v_from, v_to, weight. This function
    assumes the graph is **undirected**.

    ## Parameters:
    \tfilename: path to csv file
    ## Returns:
    \tA tuple containing the nodes and adjencency matrix. Nodes are stored as dictionary
    with key-value pair being node_id (node label) and (node_index, Node object). **Note that
    adjacency matrix must be read using node_index.**

    For example, consider the following csv file:
    ```
    0, 2, 3
    0, 1, 2
    2, 1, 1
    0, 3, 4
    ```
    then the function will return nodes and adjacency_matrix with the following result:
    ```
    nodes = {'0': (0, Node object),
             '2': (1, Node object),
             '1': (2, Node object),
             '3': (3, Node object)}
    adjcency_matrix =[[0, 3, 2, 4],
                      [3, 0, 1, 0],
                      [2, 1, 0, 0],
                      [4, 0, 0, 0]]
    ```
    The weight of the edge connecting vertices from '0' to '2' will be the value of the element
    at row 0, column 1 in the matrix.
    """
    with open(filename, newline='') as csvfile:
        lines = list(reader(csvfile, delimiter=','))

    nodes: dict[str, tuple[int, 'Node']] = {}
    node_index = 0
    for v_from, v_to, _ in lines:
        if not v_from in nodes:
            nodes[v_from] = (node_index, Node(v_from))
            node_index += 1
        if not v_to in nodes:
            nodes[v_to] = (node_index, Node(v_to))
            node_index += 1
    
    adjacency_mat = [[0] * len(nodes) for _ in range(len(nodes))]
    for v_from, v_to, weight in lines:
        index_from, node_from = nodes[v_from]
        index_to, node_to = nodes[v_to]
        node_from.neighbours.append(node_to)
        node_to.neighbours.append(node_from)
        adjacency_mat[index_from][index_to] = float(weight)
        adjacency_mat[index_to][index_from] = float(weight)
    return nodes, adjacency_mat

class Node:
    """
    Data container to represent nodes of a graph.

    # Attributes:
    id: the id, more specifically, the name of the node\
    
    neighbours: the adjacent nodes to the current node\
    
    distance: the distance from an arbitrary source node to this current node.
    By default, this is infinity as there are no path yet discovered. This attribute is
    used specifically by dijkstra's algorithm.
    """
    __slots__ = 'id', 'neighbours', 'distance'
    def __init__(self, id: str, *,
                 neighbours: Optional[list['Node']] = None) -> None:
        if not neighbours: neighbours = []

        self.id = id
        self.distance = inf
        self.neighbours = deepcopy(neighbours)
    
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, other: Union['Node', str]) -> bool:
        return self.id == other.id

    def __lt__(self, other: 'Node') -> bool:
        return self.distance < other.distance