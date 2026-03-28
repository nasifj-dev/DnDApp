class Spell():
    def __init__(self, level: int, name: str, save_atk: str, action: str, 
                 range:int, shape: str, comp: list[str], duration: str, ref: str):
        self._level = level
        self._name = name
        self._save_atk = save_atk
        self._action = action
        self._range = range
        self._shape = shape
        self._comp = comp
        self._duration = duration
        self._ref = ref

    def __str__(self):
        return f"{self._name} ({self._level})"