from Character import Character
from Item import Item
from Spell import Spell

def pdftosheet(first, second, last):
    """Parse the text extracted from a character sheet PDF into a Character object. The function takes three lists of strings representing the text from the first, second, and last pages of the PDF, and extracts relevant information to create and return a Character object with all the character's stats and information."""
    # Level/class
    if "/" in first[59]:
        splits = first[59].split("/")
        classes = []
        lev = 0
        for cls in splits:
            c = cls.strip().split(" ")
            classes.append(c[0])
            lev += int(c[1])
        classlevel = ["/".join(classes), lev]
    else:
        classlevel = first[59].split(" ")

    # Ability scores
    abilityscores = {"STR":int(first[64]), "DEX":int(first[66]), "CON":int(first[68]), 
                     "INT":int(first[70]), "WIS":int(first[72]), "CHA":int(first[74])}
    
    # Initializes empty proficiency lists.
    proficiencies = []
    h_profs = []
    expertises = []

    # Separates indecies related to saving throw modifiers and proficiencies and adds
    # saving throw type to proficiency list if proficient.
    save_prof_count = first.count('• ')
    save_break = 82+save_prof_count
    saving_throws = first[76:save_break]
    save_offset = 0
    for i, ability in enumerate(["STR", "DEX", "CON", "INT", "WIS", "CHA"]):
        if saving_throws[i + save_offset] == '• ':
            proficiencies.append(ability.strip())
            save_offset += 1
    
    # Separates indecies related to skill modifiers and proficiencies and adds
    # skill type to proficiency list if proficient.
    skill_start = first.index("DEX ")-2
    skills_break = first.index('--')-5
    skills = first[skill_start:skills_break]
    skill_offset = 0
    for i, skill in enumerate(['Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 
                               'Deception', 'History', 'Insight', 'Intimidation', 'Investigation', 
                               'Medicine', 'Nature', 'Perception', 'Performance', 'Persuasion', 
                               'Religion','Sleight of Hand', 'Stealth', 'Survival']):
        off_check = 2*i + skill_offset
        if skill in ['Sleight of Hand', 'Stealth', 'Survival']:
            off_check -= ['Sleight of Hand', 'Stealth', 'Survival'].index(skill) + 1
        if skills[off_check] == 'P ':
            proficiencies.append(skill)
            skill_offset += 1
        elif skills[off_check] == 'H ':
            h_profs.append(skill)
            skill_offset += 1
        elif skills[off_check] == 'E ':
            expertises.append(skill)
            skill_offset += 1  
        if not i and not skill_offset:
            skill_offset += 1

    # Adds senses in a list, if any are present.
    senses = []
    for line in first[skills_break-4:]:
        if "ft." in line:
            senses.append(line)
        elif '+' in line:
            break

    # Adds defences in a list and saving throw notes in a string, if any are present.
    saving_throw_notes = ""
    defences = []
    for defence in first[save_break:skill_start]:
        if "-" in defence:
            defences.append(defence.strip())
        else:
            saving_throw_notes += defence

    # Makes listed speed into integer.
    speed = int(first[skills_break+3].split("ft.")[0])

    # Separates indecies related to proficiencies and training and adds
    # them to proficiency list.
    training = first[skills_break+7:first.index("=== ACTIONS === ")-4]
    for train in training:
        train = train.strip()
        if '=' in train: continue
        elif ',' in train:
            train = train.split(',')
            for t in train:
                if t: proficiencies.append(t.strip())
        else:
            proficiencies.append(train)
    
    # Adds listed action titles to list.
    actions = first[first.index("Interact with an Object, Study, Influence ")+1:]
    action_list = ["Standard Actions"]
    for i, line in enumerate(actions):
        if "     " in line:
            action_list.append(actions[i-1].strip())

    # Adds gold
    gold_break = 0
    for i, line in enumerate(second):
        if "lb." in line:
            gold_break = i
            break
    gold = (int(second[gold_break-5])/100 + int(second[gold_break-4])/10 + int(second[gold_break-3])/2 + 
            int(second[gold_break-2]) + int(second[gold_break-1])*10)
    
    # Adds emcumberance
    encumberance = float(second[gold_break].split(' ')[0])

    # Adds inventory
    inv_list = second[gold_break+3:-1]
    inventory = []
    for i in range(0, len(inv_list), 3):
        if inv_list[i+2].split(' ')[0] == "--":
            weight = 0
        else:
            weight = float(inv_list[i+2].split(' ')[0])
        count = int(inv_list[i+1].replace(',', ''))
        new_item = Item(inv_list[i].strip(), count, weight)
        inventory.append(new_item)

    # Add spells
    spell_break = last.index("NOTES")
    if not last[spell_break+1]:
        spellcasting_ability = None
        spells = []
        spell_slots = {}
    else:
        spellcasting_ability = last[spell_break+1].strip()
        spell_list = last[spell_break+7:]

        spells = []
        spell_slots = {}

        level = 0
        spell_offset = 0
        for i in range(0, len(spell_list), 10):
            index = i + spell_offset
            if "=" in spell_list[index]:
                level += 1
                index += 1
                spell_offset += 1
            if "Slot" in spell_list[index] or "Pact" in spell_list[index]:
                spell_slots[level] = spell_list[index].count("O")
                index += 1
                spell_offset += 1
            spell = spell_list[index: index+10]
            if spell == ['']:
                break
            range_shape = spell[5].split('/')
            ran = spell[5]
            shape = None
            if len(range_shape) > 1:
                ran = range_shape[0]
                shape = range_shape[1]
            new_spell = Spell(level, spell[1].strip(), spell[3], spell[4], range, shape, 
                              spell[6], spell[7], spell[8])
            spells.append(new_spell)

    # Builds character.
    ch = Character(first[58].strip(), classlevel[0], int(classlevel[1]), first[60].strip(), 
                   first[61].strip(), first[62].strip(), abilityscores, senses, proficiencies, h_profs, expertises,
                   int(first[skills_break+1]), int(first[skills_break+2]), defences, saving_throw_notes, speed, 
                   int(first[skills_break+4]), first[skills_break+6], action_list, gold, encumberance, inventory, 
                   spellcasting_ability, spells, spell_slots)
    
    return ch

if __name__ == "__main__":
    pass