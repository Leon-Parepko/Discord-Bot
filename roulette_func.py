import random


# EXAMPLE: 10 - ten times positive, -10 - ten times negative
global chance_corrector
chance_corrector = 0


def roll_buff():
    events = ['double_pos', 'double_neg']
    weights = [0.1, 0.1]
    weights = map(lambda x: x + random.uniform(-0.05, 0.05), weights)

    result = random.choices(events, weights=weights)[0]

    return result


def roll_items(items, weights):
    weights = map(lambda x: x + random.uniform(-0.005, 0.005), weights)
    result = random.choices(items, weights=weights)[0]
    return result


def roll(user_mult=None, event=None):
    global chance_corrector

    # 19 elements total
    items =     [0,     5,      10,     25,     50,     100,    'roll_buff', 200,    'item', 500,    'megacoins', 'ban_1', 1000, 'ban_5', 2000, 'double_balance', 'ban_60', 'trophy', 'half_balance']
    weights =   [1.65,  1.6,    1.5,    1.3,    0.65,    0.4,    0.6,        0.35,    0.15,  0.25,    0.1,         0.08,   0.1,   0.04,   0.04,  0.02,             0.007,    0.01,     0.007]
    megaroll_items = (100, 200, 500, 1000, 'item', 'trophy')
    neg_items = [0, 5, 10, 'ban_1', 'ban_5', 'ban_60', 'half_balance']

    if user_mult is not None:
        counter = 0
        for num in weights:
            weights[counter] = float(num * user_mult[counter])
            counter += 1

        if chance_corrector > 0:
            weights[0] = weights[0] + chance_corrector ** 2 / 40
            weights[1] = weights[1] + chance_corrector ** 2 / 40
            weights[2] = weights[2] + chance_corrector ** 2 / 40
            weights[11] = weights[11] + chance_corrector ** 2 / 110
            weights[13] = weights[13] + chance_corrector ** 2 / 110
            weights[16] = weights[16] + chance_corrector ** 2 / 110
            weights[18] = weights[18] + chance_corrector ** 2 / 110

        elif chance_corrector < 0:
            weights[0] = weights[0] - chance_corrector ** 2 / 90
            weights[1] = weights[1] - chance_corrector ** 2 / 90
            weights[2] = weights[2] - chance_corrector ** 2 / 90
            weights[11] = weights[11] - chance_corrector ** 2 / 170
            weights[13] = weights[13] - chance_corrector ** 2 / 170
            weights[16] = weights[16] - chance_corrector ** 2 / 170
            weights[18] = weights[18] - chance_corrector ** 2 / 170


    # print(chance_corrector, weights)


    if event == "double_pos":
        weights[0] = weights[0] / 2
        weights[1] = weights[1] / 2
        weights[2] = weights[2] / 2
        weights[11] = weights[11] / 2
        weights[13] = weights[13] / 2
        weights[16] = weights[16] / 2
        weights[18] = weights[18] / 2

    elif event == "double_neg":
        weights[0] = weights[0] * 1.3
        weights[1] = weights[1] * 1.3
        weights[2] = weights[2] * 1.3
        weights[11] = weights[11] * 10
        weights[13] = weights[13] * 10
        weights[16] = weights[16] * 10
        weights[18] = weights[18] * 10

    elif event == "megaroll":
        counter = 0
        items_new = []
        for item in items:
            if item in megaroll_items:
                items_new.append(item)
                counter += 1
            else:
                weights.pop(counter)
        items = items_new

    weights = map(lambda x: x + random.uniform(-0.05, 0.05), weights)

    result = random.choices(items, weights=weights)[0]

    # print(result)



    if result in neg_items:
        if chance_corrector > 0:
            chance_corrector = 0
        chance_corrector -= 1
    else:
        if chance_corrector < 0:
            chance_corrector = 0
        chance_corrector += 1



    if type(result) == int:
        result += random.randint(-(round(result / 10)), round(result / 10))


    return result


# for i in range(0, 100):
#     roll(user_mult=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])