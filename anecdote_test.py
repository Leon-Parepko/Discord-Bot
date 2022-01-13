import random
import time

import requests, bs4
import sqlite3
import re



# with sqlite3.connect('anekdot.db') as db:
#     cursor = db.cursor()
#     item_arr = []
#     data = cursor.execute("""SELECT anekdot_text FROM anekdot_table""")
#     counter = 0
#
#     for i in data:
#         item_arr.append(i[0])
#         print("processing...")
#
#     for item in item_arr:
#         print("formating:" + str(counter))
#         counter += 1
#         cursor.execute("""UPDATE anekdot_table SET id = {}, anekdot_text = '{}' WHERE anekdot_text = '{}'""".format(counter, str(item).strip(), item))
        # print(counter, item[0].strip())
        # print(item)
        # print(cursor.execute("""SELECT id FROM anekdot_table WHERE anekdot_text = '{}'""".format(item[0])))
        # cursor.execute("""INSERT INTO test (id, anekdot) VALUES ({}, '{}')""".format(int(counter), str(item[0]).strip()))




with sqlite3.connect('anecdote_v2.db') as db:
    cursor = db.cursor()
    item_arr = []

    counter = 0
    z = 0
    for _ in range(4000):
        time.sleep(0.5)
        s = requests.get('http://anekdotme.ru/random') # запрос к сайту с анекдотами
        b = bs4.BeautifulSoup(s.text, "html.parser") # получаем html код
        p = b.select('.anekdot_text') # ищем блок с текстом анекдота
        for x in p:     # в цикле заносим анекдот в базу
            s = (x.getText().strip())
            reg = re.compile('[^a-zA-Zа-яА-я .,!?:1234567890]')
            s = reg.sub('', s)
            z += 1
            cursor.execute("""INSERT INTO anecdote_table (id, anecdote_text) VALUES ({}, '{}')""".format(int(z), str(s)))
        print("parsing: " + str(z))

    cursor.execute("""DELETE FROM anecdote_table WHERE id NOT IN (SELECT MIN(id) id FROM anecdote_table GROUP BY anecdote_text)""")

    data = cursor.execute("""SELECT anecdote_text FROM anecdote_table""")

    for i in data:
        item_arr.append(i[0])
        print("processing...")

    for item in item_arr:
        print("formating: " + str(counter))
        counter += 1
        cursor.execute("""UPDATE anecdote_table SET id = {}, anecdote_text = '{}' WHERE anecdote_text = '{}'""".format(counter, str(item).strip(), item))

    print("Finished!")