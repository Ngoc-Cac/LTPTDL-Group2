from math import inf
from copy import deepcopy
from csv import reader

from typing import Optional, Union

def from_csv(filename: str) -> tuple[dict[str, tuple[int, 'Node']], list[list[float]]]:
    """
    Construct list of nodes and adjacenc matrix from csv files. Each line in file must be\
    a tuple of edges, that is (v_from, v_to, weight).\n
    ## Parameters:
    \tfilename: path to csv file
    ## Returns:
    \tA tuple containing the nodes and adjencency matrix. Nodes are stored as dictionary\
    with key-value pair being node_id (node label) and (node_index, Node object). Note that\
    adjacency matrix must be read using node_index.\n
    For example, consider the following csv file:
    ```
    0, 2, 3
    0, 1, 2
    2, 1, 1
    0, 3, 4
    ```
    then\n
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
    """
    with open(filename, newline='') as csvfile:
        lines = list(reader(csvfile, delimiter=','))

    nodes: dict[str, tuple[int, 'Node']] = {}
    node_index = 0
    for row in lines:
        if not row[0] in nodes:
            nodes[row[0]] = (node_index, Node(row[0]))
            node_index += 1
        if not row[1] in nodes:
            nodes[row[1]] = (node_index, Node(row[0]))
            node_index += 1
    
    adjacency_mat = [[0] * len(nodes) for _ in range(len(nodes))]
    for row in lines:
        index_from, node_from = nodes[row[0]]
        index_to, node_to = nodes[row[1]]
        node_from.neighbours.append(node_to.id)
        node_to.neighbours.append(node_from.id)
        adjacency_mat[index_from][index_to] = float(row[2])
        adjacency_mat[index_to][index_from] = float(row[2])
    return nodes, adjacency_mat

class Node:
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
        if isinstance(other, Node): return self.id == other.id
        elif isinstance(other, str): return self.id == other
        else: return False

    def __lt__(self, other: 'Node') -> bool:
        return self.distance < other.distance