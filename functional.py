import random


# card_arr = []
# item_arr = []
# for i in range(0, 24):
#     item_arr.append(i)
# print(item_arr)
# for i in range(1, 8):
#     print((i*8-8) - (i*9 - i))
#     print(item_arr[i*8-8:i*9 - i + 1])
#     # card_arr.append(item_arr[i*8-9:i*8])
#     print(card_arr)


def roll_buff():
    events = ['double_pos', 'double_neg']
    weights = [0.1, 0.1]
    weights = map(lambda x: x + random.uniform(-0.05, 0.05), weights)

    result = random.choices(events, weights=weights)[0]

    return result


def roll(event):
    items = [0, 5, 10, 25, 50, 100, 'roll_buff', 200, 'item', 500, 'megacoins', 'ban_1', 1000, 'ban_5', 2000, 'double_balance', 'ban_60', 'trophy']
    megaroll_items = (100, 200, 'item', 'trophy')
    weights = [0.1, 0.1, 0.1, 0.1, 0.1, 1.1, 0.1, 0.1, 2.1, 0.1, 0.1, 1000.1, 0.1, 0.1, 0.1, 0.1, 0.1, 3.1]

    if event == "double_pos":
        weights[0] = weights[0] * 2        #JUST AN EXAMPLE
        pass

    elif event == "double_neg":
        weights[1] = weights[1] * 2        # JUST AN EXAMPLE
        pass

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





# print(roll("none"))