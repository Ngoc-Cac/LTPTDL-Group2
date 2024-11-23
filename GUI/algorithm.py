from PriorityQueue import PriorityQueue
from Cell import Position, Cell

from typing import Iterable, Optional

def chebyshev_move(start: Position, end: Position) -> tuple[list[int], list[int]]:
    cur_x, cur_y = start
    xs = [cur_x]
    ys = [cur_y]

    while (cur_x != end.x) or (cur_y != end.y):
        dx = end.x - cur_x
        dy = end.y-cur_y
        if abs(dx) == abs(dy):
            # cur_x > end.x -> decrease x
            if dx < 0: cur_x -= 1
            else: cur_x += 1

            #cur_y > end.y -> decrease y
            if dy < 0: cur_y -= 1
            else: cur_y += 1
        elif abs(dx) < abs(dy):
            if dy < 0: cur_y -= 1
            elif dy > 0: cur_y += 1
        else:
            if dx < 0: cur_x -= 1
            elif dx > 0: cur_x += 1
        xs.append(cur_x)
        ys.append(cur_y)
    return xs, ys
def chebyshev_move(start: Position, end: Position) -> list[Position]:
    cur_x, cur_y = start
    positions = [start]

    while (cur_x != end.x) or (cur_y != end.y):
        dx = end.x - cur_x
        dy = end.y - cur_y
        if abs(dx) >= abs(dy):
            # cur_x > end.x => dx < 0  => decrease cur_x
            if dx < 0: cur_x -= 1
            elif dx > 0: cur_x += 1
        if abs(dx) <= abs(dy):
            #cur_y > end.y => dy < 0 => decrease cur_y
            if dy < 0: cur_y -= 1
            elif dy > 0: cur_y += 1
        positions.append(Position(cur_x, cur_y))
    return positions

def path_traceback(start_state: Cell, goal_state: Cell) -> list[Cell]:
    path = []
    while goal_state != start_state:
        path.append(goal_state)
        goal_state = goal_state.parent
    path.append(start_state)
    return list(reversed(path))

def astar_vacuum(dirty_cells: Iterable[Position],
                 start: Position, *,
                 max_iter: int = 100000,
                 do_traceback: bool = False)\
                -> tuple[Cell, Optional[list[Cell]]]:
    my_queue: PriorityQueue[Cell] = PriorityQueue()

    start_node = Cell(position=start, dirty_cells=dirty_cells)
    start_node.calc_cost()
    my_queue.push(start_node)
    i = -1
    while my_queue and (i := i + 1) < max_iter:
        cur = my_queue.pop()

        if len(cur.dirty_cells) == 0: break
        
        for neighbour in cur.expand_cell():
            if my_queue.get_attr(neighbour, 'cost', default_value=neighbour.cost + 1) > neighbour.cost:
                my_queue.push(neighbour)

    traceback = path_traceback(start_node, cur) if do_traceback else None
    if len(cur.dirty_cells) != 0: cur = None
    return cur, traceback