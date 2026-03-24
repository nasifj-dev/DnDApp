import pickle

with open("charactersPickle", "rb") as fin:
    try:
        char = pickle.load(fin)
        for key, val in char.items():
            print(key, val)
    except EOFError:
        pass