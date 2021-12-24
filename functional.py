import random

def roll(event):
    items = ['item_1', 'item_2', 'item_3', 'item_4', 'item_5', 'item_6']
    weights = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    weights = map(lambda x: x + random.uniform(-0.05, 0.05), weights)



    if event == "Double_Pos":
        weights[0] += weights[0] * 2        #JUST AN EXAMPLE

    elif event == "Double_neg":
        weights[0] += weights[0] * 2  # JUST AN EXAMPLE




    return random.choices(items, weights=weights)[0]