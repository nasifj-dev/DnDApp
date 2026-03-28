import math
from Item import Item
from Spell import Spell


class Character():
    def __init__(self, name: str, dclass: str, level: int, player: str, 
                 race:str, backgroud:str, ability_scores:dict[str:int], senses: list[str], 
                 proficiencies: list[str], h_profs: list[str], expertises: list[str], ac:int, prof_bonus: int, 
                 defences: list[str], saving_throw_notes: str, speed: int, max_hp: int, hitdice: str, actions: list[str], 
                 gold: float, encumberance: int, inventory: list[Item], spellcasting_ability: str,
                 spells: list[Spell], spell_slots: dict[int:int]):
        self._name = name
        self._dclass = dclass
        self._level = level
        self._player_name = player
        self._race = race
        self._background = backgroud
        self._ability_scores = ability_scores
        self._senses = senses
        self._proficiencies = proficiencies
        self._h_profs = h_profs
        self._expertises = expertises
        self._ac = ac
        self._prof_bonus = prof_bonus
        self._defences = defences
        self._saving_throw_notes = saving_throw_notes
        self._speed = speed
        self._max_hp = max_hp
        self._current_hp = max_hp
        self._hitdice = hitdice
        self._actions = actions
        self._gold = gold
        self._encumberance = encumberance
        self._inventory = inventory
        self._spellcasting_ability = spellcasting_ability
        self._spells = spells
        self._spell_slots = spell_slots

    def damage(self, hitpoints: int):
        if type(hitpoints) is not int:
            raise TypeError("Hitpoints must be an integer.")
        self._current_hp = max(self._current_hp - hitpoints, 0)
        return f"{self._name} took {hitpoints} damage and is now at {self._current_hp} hp."
    """Apply damage to the character and return a message with the new HP total."""
    
    def heal(self, hitpoints: int):
        if type(hitpoints) is not int:
            raise TypeError("Hitpoints must be an integer.")
        self._current_hp = min(self._current_hp + hitpoints, self._max_hp)
        return f"{self._name} healed {hitpoints} damage and is now at {self._current_hp} hp."
    """Heal the character and return a message with the new HP total."""

    def modifier(self, ability: str):
        if ability not in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            raise ValueError("Abiltity must be STR, DEX, CON, INT, WIS, or CHA.")
        return math.floor((self._ability_scores[ability]-10)/2)
    """Calculate the ability modifier for a given ability score."""
    
    def skill(self, skill: str):
        if skill not in ['Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 
                         'Deception', 'History', 'Insight', 'Intimidation', 'Investigation', 
                         'Medicine', 'Nature', 'Perception', 'Performance', 'Persuasion', 
                         'Religion','Sleight of Hand', 'Stealth', 'Survival']:
            raise ValueError("Skill must be Acrobatics, Animal Handling, Arcana, Athletics, "/
                             "Deception, History, Insight, Intimidation, Investigation, "/
                             "Medicine, Nature, Perception, Performance, Persuasion, "/
                             "Religion, Sleight of Hand, Stealth, Survival")
        elif skill == "Athletics":
            ability = "STR"
        elif skill in ["Acrobatics", "Sleight of Hand", "Stealth"]:
            ability = "DEX"
        elif skill in ["Arcana", "History", "Investigation", "Nature", "Religion"]:
            ability = "INT"
        elif skill in ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"]:
            ability = "WIS"
        elif skill in ["Deception", "Intimidation", "Performance", "Persuasion"]:
            ability = "CHA"

        if skill in self._proficiencies:
            return self.modifier(ability) + self._prof_bonus
        elif skill in self._h_profs:
            return self.modifier(ability) + math.floor(self._prof_bonus/2)
        elif skill in self._expertises:
            return self.modifier(ability) + (self._prof_bonus*2)
        return self.modifier(ability)
    """Calculate the skill modifier for a given skill, taking into account proficiency, half proficiency, and expertise."""
    
    def battle_stats(self):
        return f"HP: {self._current_hp}/{self._max_hp}, AC: {self._ac}, Speed: {self._speed} ft."
    """Return a string with the character's current HP, AC, and speed for easy reference during battle."""
    
    def passive_perception(self):
        return 10 + self.skill("Perception")
    """Calculate the passive perception score for the character."""
    
    def passive_insight(self):
        return 10 + self.skill("Insight")
    """Calculate the passive insight score for the character."""
    
    def passive_investigation(self):
        return 10 + self.skill("Investigation")
    """Calculate the passive investigation score for the character."""
    
    def initiative(self):
        return self.modifier("DEX")
    """Calculate the initiative modifier for the character."""
    
    def inventory(self):
        return [str(i) for i in self._inventory]
    """Return a list of the items in the character's inventory."""
    
    def spells(self):
        return [str(i) for i in self._spells]
    """Return a list of the character's spells."""
    
    def spell_save_dc(self):
        if self._spellcasting_ability:
            return self.spell_attack_bonus() + 8
        return None
    """Calculate the spell save DC for the character's spells."""
    
    def spell_attack_bonus(self):
        if self._spellcasting_ability:
            return self.modifier(self._spellcasting_ability) + self._prof_bonus
        return None
    """Calculate the spell attack bonus for the character's spells."""
    
    def big_desc(self):
        return f"{self._name} is a level {self._level} {self._race} {self._dclass} " \
               f"played by {self._player_name}. They have a {self._background} background, " \
               f"their ability scores are {self._ability_scores}, and have proficiencies in " \
               f"{self._proficiencies}. AC: {self._ac}, Prof. Bonus: {self._prof_bonus}, Speed: " \
               f"{self._speed}, Max HP: {self._max_hp}, Hitdice: {self._hitdice}, Defences: {self._defences}, Actions: {self._actions}, " \
               f"Gold: {self._gold}, Encumberance: {self._encumberance} lbs, Inventory: {self.inventory()}, " \
               f"Spellcasting ability: {self._spellcasting_ability}, Spells: {self.spells()}, Spell slots: {self._spell_slots}, " \
               f"Senses: {self._senses}, Saving throw notes: {self._saving_throw_notes}"
    """Return a detailed description of the character with all their stats and information."""
    
    def __str__(self):
        return f"{self._name}, level {self._level} {self._race} {self._dclass}"
    """Return a short string representation of the character with their name, level, race, and class."""