class Item():
    def __init__(self, name: str, count: int, weight: float):
        self._name = name
        self._count = count
        self._weight = weight

    def __str__(self):
        return f"{self._name} ({self._count})"