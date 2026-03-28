class Item():
    """A class to represent D&D items."""

    def __init__(self, name: str, count: int, weight: float):
        """Builds the item out of the inputted name, count, and weight."""
        self._name = name
        self._count = count
        self._weight = weight

    def __str__(self):
        """Return a string representation of the item with its name and count."""
        return f"{self._name} ({self._count})"