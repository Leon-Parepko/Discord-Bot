import random




def roll_buff():
    events = ['double_pos', 'double_neg']
    weights = [0.1, 0.1]
    weights = map(lambda x: x + random.uniform(-0.05, 0.05), weights)

    result = random.choices(events, weights=weights)[0]

    return result


def roll(event):
    # 19 elements total
    items =     [0,     5,      10,     25,     50,     100,    'roll_buff', 200,    'item', 500,    'megacoins', 'ban_1', 1000, 'ban_5', 2000, 'double_balance', 'ban_60', 'trophy', 'half_balance']
    weights =   [1.45,   1.4,    1.3,    1.1,   0.6,    0.65,    0.6,        0.45,    0.15,  0.35,    0.1,         0.08,   0.08,  0.04,   0.04,  0.02,             0.007,     0.01,     0.007]
    megaroll_items = (100, 200, 'item', 'trophy')


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
                items_new.append(str(item))
                counter +=1
            else:
                weights.pop(counter)
        items = items_new
        # print(items, "\n", weights)


    # NEED CHANCE CORRECTION


    weights = map(lambda x: x + random.uniform(-0.05, 0.05), weights)

    result = random.choices(items, weights=weights)[0]

    if type(result) == int:
        result += random.randint(-(round(result / 10)), round(result / 10))


    return result


roll("none")

# for i in range(0, 100):
#     print(roll("double_neg"))