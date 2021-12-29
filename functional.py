import random

def roll(event):
    items = (0, 5, 10, 25, 50, 100, 'roll_buff', 200, 'item', 500, 'megaroll', 'ban_1', 1000, 'ban_5', 2000, 'double_balance', 'ban_60', 'trophy')
    weights = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    weights = map(lambda x: x + random.uniform(-0.05, 0.05), weights)



    if event == "Double_Pos":
        weights[0] += weights[0] * 2        #JUST AN EXAMPLE

    elif event == "Double_neg":
        weights[0] += weights[0] * 2        # JUST AN EXAMPLE

    result = random.choices(items, weights=weights)[0]


    # NEED CHANCE CORRECTION


    if type(result) == int:
        result += random.randint(-(round(result / 10)), round(result / 10))


    return result