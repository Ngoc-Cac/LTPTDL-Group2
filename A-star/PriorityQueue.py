import heapq as hq

from typing import TypeVar, Generic, Iterator,\
                   Iterable, Optional
T = TypeVar('T')


# item = [item, count, is_removed]
# count used for FIFO structuring when priority is equal

def counter() -> Iterator[int]:
    num = 0
    while (num := num + 1): yield num

class PriorityQueue(Generic[T]):
    """
    Priority Queue implemented with minimum heap. This priority queue supports\
    updating elements as well as supporting FIFO order for items with equal priority.\n
    
    In order for the queue to work, items in queue need to be:
    - Sortable: must implement a `__lt__` method.
    - Hashable: must implement a `__hash__` method.
    """
    __slots__ = "_min_heap", "_items_list", "_counter"
    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._min_heap: list[list[T, int, bool]] = []
        self._items_list: dict[T, list[T, int, bool]] = {}
        self._counter = counter()

        if items:
            for item in items: self.push(item)

    def push(self, item: T) -> None:
        """
        Insert a new item. If item already exists, update the item priority instead.\n

        ------------\n
        ## Exceptions:
        Raise TypeError if:
        - Item is not sortable (do not have a `__lt__` method).
        - Item is not hashable (do not have a `__hash__` method).
        """
        # Remove item if already exists
        if item in self._items_list:
            # Flag item as removed
            self._items_list[item][2] = True

        new_item = [item, next(self._counter), False]
        self._items_list[item] = new_item
        hq.heappush(self._min_heap, new_item)

    def pop(self) -> T:
        """
        Remove and return the item with smallest priority.\n

        ------------\n
        ## Exceptions:
        Raise IndexError is queue is empty.
        """
        while self._min_heap:
            item, _, is_removed = hq.heappop(self._min_heap)
            if not is_removed:
                del self._items_list[item]
                return item
        raise IndexError("Queue is empty")


    def seek(self) -> T:
        """
        Return the item with smallest priority without removal.
        """
        while self._min_heap:
            item, _, is_removed = self._min_heap[0]
            if not is_removed: return item
            else: hq.heappop(self._min_heap)

    def clear(self) -> None:
        """
        Clear the queue.
        """
        self._min_heap.clear()
        self._items_list.clear()
        self._counter = counter()


    def __len__(self) -> int: return len(self._items_list)

    def __bool__(self) -> bool: return bool(self._items_list)