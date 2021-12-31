import random

from discord.ext.commands import has_permissions
from discord.ext import commands
from discord.ext import tasks
import discord
import sys
import logging
import sqlite3
import functional
import text_art




# inserts = [(345241474214002690, 0, 0)]
# with sqlite3.connect('database.db') as db:
#     cursor = db.cursor()
#     # task1 = """ CREATE TABLE IF NOT EXISTS roulette (user_id INTEGER, coins INTEGER, roll_counter INTEGER) """
#     # cursor.execute(task1)
#
#
#     query = """ INSERT INTO roulette (user_id, coins, roll_counter) VALUES(?, ?, ?) """
#     cursor.executemany(query, inserts)






#--------------------------VARIABLES & CLASSES INIT----------------------------------
config_file_path = "C:\\Users\\Leon\\Desktop\\Discord-Bot\\config.txt"
win_words_file_path = "C:\\Users\\Leon\\Desktop\\Discord-Bot\\win_words.txt"
prefixes_available = "!@#$%^&*+_-~`=:;?/.<>,|"
logging.basicConfig(filename='logging.log', level=logging.INFO, filemode='w', format='%(levelname)s   -   %(asctime)s   -   %(message)s')
roulette_bonus_key = "TestBonusTestBonusTestBonus"
daily_bonus = 200
roll_price = 20


class Config:
    def __init__(self, token, prefix, available_channels, super_users, version):
        self.token = token
        self.prefix = prefix
        self.available_channels = available_channels
        self.super_users = super_users
        self.version = version







#--------------------------SUBSIDIARY_FUNCTIONS----------------------------------
def parse_file(config_file_path):
    content = []
    f = open(config_file_path, "r")
    content_raw = f.read().split("\n")
    f.close()
    for line in content_raw:
        if (line != ''):
            try:
                content.append(line.split(" = ")[1])
            except:
                content.append(line)
    return content


def db_get(exe):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        data = cursor.execute("""{}""".format(str(exe)))
        arr = []
        for i in data:
            arr.append(i)
        return arr


def db_set(exe):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("""{}""".format(str(exe)))


def change_file_var(var, arg):
    file_reader = open(config_file_path, "r")
    lines_list = file_reader.readlines()
    file_reader.close()
    lines_list[var] = str(arg)
    file_writer = open(config_file_path, "w")
    file_writer.writelines(lines_list)
    file_writer.close()


def reconfig(file_content):
    config.token = file_content[0]
    config.prefix = file_content[1]
    config.available_channels = str(file_content[2]).split(" ")
    config.super_users = str(file_content[3]).split(" ")


def prefix_check(prefix):
    if prefix in prefixes_available:
        return True
    else:
        return False


def valid_user_check(user_id, ctx):
    if user_id.isdigit():
        if int(user_id) in map(lambda x: x.id, ctx.guild.members) and str(user_id) not in config.super_users:
            return True
        else:
            return False
    else:
        return False


def valid_channel_check(channel_name, ctx):
    if str(channel_name) in map(str, ctx.guild.channels) and str(channel_name) not in config.available_channels:
        return True
    else:
        return False


def superuser_check(ctx):
    if str(ctx.message.author.id) in config.super_users:
        return True
    else:
        return False


def add_user_roulette(ctx, bonus):
    start_coins = 500
    if bonus:
        start_coins *= 4

    users = db_get(" SELECT user_id FROM roulette ")

    for i in users:
        if i[0] == int(ctx.message.author.id):
            return False
    db_set("INSERT INTO roulette (user_id, coins, roll_counter) VALUES({}, {}, 0)".format(int(ctx.message.author.id), start_coins))
    return True


def check_valid_user_roulette(ctx):
    users = db_get(" SELECT user_id FROM roulette ")

    for i in users:
        if i[0] == int(ctx.message.author.id):
            return True
    return False


def add_user_item(ctx, item):
    user_items = db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
    db_set("UPDATE roulette SET items = '{}' WHERE user_id = {}".format(str(user_items).__add__(" " + str(item)),int(ctx.message.author.id)))


def add_sub_user_coins(ctx, sum):
    user_coins = db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
    db_set("UPDATE roulette SET coins = '{}' WHERE user_id = {}".format(int(user_coins) + int(sum), int(ctx.message.author.id)))




#-----------------CUSTOM ERRORS------------------
class Error(Exception):
    pass

class CustomError(Error):
    pass






#------------------------------MAIN-----------------------------
try:

#Config initialization
    content = parse_file(config_file_path)
    config = Config(content[0], content[1], str(content[2]).split(" "), str(content[3]).split(" "), content[4])


#Bot initialization
    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix=config.prefix, intents=intents)



    @bot.event
    async def on_ready():
        logging.info("Logged on as {0}".format(bot.user))



#++++++++++++++++++++SUPERUSER_COMMANDS++++++++++++++++++++++
    @bot.command()
    @has_permissions(administrator=True)
    async def prefix_config(ctx, arg):
        if superuser_check(ctx) and not ctx.message.author.bot:
            if prefix_check(str(arg)):
                change_file_var(1, "PREFIX = " + str(arg) + "\n")
                reconfig(parse_file(config_file_path))
                bot.command_prefix = str(arg)
                await ctx.message.channel.send("Prefix has been changed successfully.")
            else:
                await ctx.message.channel.send("This prefix is invalid! Please, try one of this: ```" + prefixes_available + "```\nExample:```" + config.prefix + "prefix_config PREFIX```")
        else:
            await ctx.message.channel.send("You dont have permissions to use this commands!")


    @bot.command()
    @has_permissions(administrator=True)
    async def superuser_config(ctx, operation, arg):
        if superuser_check(ctx) and not ctx.message.author.bot:
            if operation != "add" and operation != "set":
                await ctx.message.channel.send("This operation is invalid! Please, try one of this - set, add \nExample:```" + config.prefix + "superuser_config set USER_ID```")

            elif valid_user_check(arg, ctx):
                if operation == "add":
                    change_file_var(3, open(config_file_path, "r").readlines()[3].split("\n")[0] + " " + arg + "\n")
                    reconfig(parse_file(config_file_path))
                    await ctx.message.channel.send("New SuperUser: " + str(bot.get_user(int(arg))) + " has been set successfully.")

                elif operation == "set":
                    change_file_var(3, "SUPERUSERS = " + arg + "\n")
                    reconfig(parse_file(config_file_path))
                    await ctx.message.channel.send("New SuperUser: " + str(bot.get_user(int(arg))) + " has been set successfully.")

            else:
                await ctx.message.channel.send("This user is invalid or already in the list! Please, try other one\nExample:```" + config.prefix + "superuser_config set USER_ID```")
        else:
            await ctx.message.channel.send("You dont have permissions to use this commands!")



    @bot.command()
    @has_permissions(administrator=True)
    async def available_channels_config(ctx, operation, arg):
        if superuser_check(ctx) and not ctx.message.author.bot:
            if operation != "add" and operation != "set":
                await ctx.message.channel.send("This operation is invalid! Please, try one of this - set, add \nExample:```" + config.prefix + "available_channels_config set CHANNEL_NAME```")

            elif valid_channel_check(arg, ctx) == True:
                if operation == "add":
                    change_file_var(2, open(config_file_path, "r").readlines()[2].split("\n")[0] + " " + arg + "\n")
                    reconfig(parse_file(config_file_path))
                    await ctx.message.channel.send("New channel has been added successfully.")

                elif operation == "set":
                    change_file_var(2, "CHANNELS = " + arg + "\n")
                    reconfig(parse_file(config_file_path))
                    await ctx.message.channel.send("New channel has been set successfully.")

            else:
                await ctx.message.channel.send("This channel is invalid or already in the list! Please, try other one\nExample:```" + config.prefix + "available_channels_config set CHANNEL_NAME```")
        else:
            await ctx.message.channel.send("You dont have permissions to use this commands!")


#++++++++++++++++++++INFO_COMMANDS++++++++++++++++++++++
    @bot.command()
    async def show(ctx, *operation):
        try:
            if operation[0] == "version":
                await ctx.message.channel.send("```Version = " + config.version + "```")

            elif operation[0] == "prefix":
                await ctx.message.channel.send("```Prefix = " + config.prefix + "```")

            elif operation[0] == "available_channels":
                await ctx.message.channel.send("```Available Channels = " + str(config.available_channels) + "```")

            elif operation[0] == "super_users":
                await ctx.message.channel.send("```Super Users = " + str(config.super_users) + "```")

            elif operation[0] == "token":
                await ctx.message.channel.send("Are you serious?")

        except IndexError:
            await ctx.message.channel.send("```Version = {}\nPrefix = {}\nAvailable Channels = {}\nSuper Users = {}```".format(config.version, config.prefix, config.available_channels, config.super_users))

    @bot.command()
    async def bot_status(ctx, *operation):
        try:
            if operation[0] == "ping":
                await ctx.message.channel.send("```Ping - {} ms.```".format(str(round(bot.latency * 1000))) )

        except IndexError:
            await ctx.message.channel.send("```Ping - {} ms.```".format(str(round(bot.latency * 1000))) )


#++++++++++++++++++++FUN_COMMANDS++++++++++++++++++++++
    @bot.command()
    async def roulette(ctx, *operation):

        if ctx.message.author.bot:
            await ctx.message.channel.send('Hay! It is illegal to use bots! :(')
        else:

            try:
                if operation[0] == "help":
                    await ctx.message.channel.send('```  ______   ______   __  __   __       ______  ______  ______  ______    \n /\  == \ /\  __ \ /\ \/\ \ /\ \     /\  ___\/\__  _\/\__  _\/\  ___\   \n \ \  __< \ \ \/\  \ \ \_\  \ \ \____\ \  __ \/_/\ \/\/_/\ \/\ \  __\   \n  \ \_\ \_ \ \_____ \ \_____ \ \_____ \ \_____\ \ \_\   \ \_\ \ \_____\ \n   \/_/ /_/ \/_____/ \/_____/ \/_____/ \/_____/  \/_/    \/_/  \/_____/ \n\n\n________-----======= THIS IS A ROULETTE GAME! =======-----________\n\n\nYou could use this commands to play:\n{}roulette start - \n{}roulette top - \n{}roulette roll - \n{}roulette megaroll - \n{}roulette shop - \n{}roulette profile - \n{}roulette trophies - \n{}roulette items - ```'.format(config.prefix, config.prefix, config.prefix, config.prefix, config.prefix, config.prefix, config.prefix, config.prefix))


                elif operation[0] == "start":
                    start_coins = 500
                    try:
                        if str(operation[1]) == roulette_bonus_key:
                            start_coins *= 4
                    except IndexError:
                        pass

                    if check_valid_user_roulette(ctx) == False:
                        db_set("INSERT INTO roulette (user_id, coins, megarolls, items, trophies, roll_counter, daily) VALUES({}, {}, 0, 'default_item', 'default_trophy', 0, 0)".format(int(ctx.message.author.id), start_coins))
                        await ctx.message.channel.send("New user have been added successfully!")
                    else:
                        await ctx.message.channel.send("You are already registered!")


#               NOT WORK
                elif operation[0] == "roll":
                    if check_valid_user_roulette(ctx):
                        user_coins = int(db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0])
                        if user_coins >= roll_price:
                            user_coins -= roll_price
                            roll_result = functional.roll("None")
                            win_phrase = random.choice(parse_file(win_words_file_path))
                            print(roll_result)

                            add_sub_user_coins(ctx, -roll_price)

                            if type(roll_result) == int:
                                add_sub_user_coins(ctx, roll_result)
                                await ctx.message.channel.send("{}\nYou have won {} © !\nTotal balance is: {} ©".format(win_phrase, roll_result, user_coins + roll_result))


                            elif "ban" in roll_result:
                                ban_time = roll_result.split("_")[1]
                                await ctx.message.channel.send("{}\nYou have won BAN on {} minutes!".format(win_phrase, ban_time))


                            elif roll_result == "item":
                                user_items = str(db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]).split(" ")
                                roll_items = db_get("SELECT item FROM roulette_roll_items")
                                roll_items_reduce = db_get("SELECT item FROM roulette_roll_items")

                                for item in roll_items:
                                    if item[0] in user_items:
                                        roll_items_reduce.remove(item)

                                if roll_items_reduce == []:
                                    await ctx.message.channel.send("PLEASE **STOP PLAYING THIS SHIT!**\nYou already have all the items.")

                                else:
                                    rand_item = random.choice(roll_items_reduce)[0]
                                    add_user_item(ctx, rand_item)
                                    await ctx.message.channel.send("{}\nYou have won new item: {} !".format(win_phrase, str(rand_item).upper()))



                            elif roll_result == "item_4":
                                pass
                            elif roll_result == "item_5":
                                pass


                        else:
                            await ctx.message.channel.send('You dont have enough money to roll! \n Check your status in profile or wait for the daily bonus.'.format(config.prefix))
                    else:
                        await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


#               NOT WORK
                elif operation[0] == "megaroll":
                    if check_valid_user_roulette(ctx):
                        pass
                    else:
                        await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                elif operation[0] == "profile":
                    if check_valid_user_roulette(ctx):
                        user =      str(ctx.message.author).split("#")[0]

                        coins =     db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]

                        megerols =  db_get("SELECT megarolls FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]

                        rolls =     db_get("SELECT roll_counter FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]

                        items_arr = db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")
                        if len(items_arr) >= 8:
                            items_arr = items_arr[0:8]
                            items_arr.append("...")
                        items = ''.join(map(lambda x: x + "  ", map(str, items_arr)))

                        trophies_arr = db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")
                        if len(trophies_arr) >= 8:
                            trophies_arr = trophies_arr[0:8]
                            trophies_arr.append("...")
                        trophies = ''.join(map(lambda x: x + "  ", map(str, trophies_arr)))

                        await ctx.message.channel.send('```\n --------------====PROFILE====-------------- \n\n UserName:     {}\n Coins:        {} ©\n Megarolls:    {}\n Rolls Total:  {}\n Trophies:     {}\n Items:        {}```'.format(user, coins, megerols, rolls, trophies, items))

                    else:
                        await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                elif operation[0] == "trophies":
                    if check_valid_user_roulette(ctx):
                        try:
                            user_str = str(operation[1])
                            user_trophy_arr = db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")
                            for i in user_trophy_arr:
                                if user_str == str(i):
                                    await ctx.message.channel.send('``` -------========#### {} ####========-------\n\n {}```'.format(user_str.upper(), text_art.arts.trophy_select(user_str)))

                        except IndexError:
                                await ctx.message.channel.send('```\n -------====++++#### TROPHY_HALL ####++++====------- \n\n {}```'.format(db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]))
                    else:
                        await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                elif operation[0] == "items":
                    if check_valid_user_roulette(ctx):
                        try:
                            user_str = str(operation[1])
                            user_item_arr = db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")
                            for i in user_item_arr:
                                if user_str == str(i):
                                    await ctx.message.channel.send('``` -------========%%%% {} %%%%========-------\n\n {}```'.format(user_str.upper(), text_art.arts.item_select(user_str)))

                        except IndexError:
                                await ctx.message.channel.send('```\n -------=====****%%%% ITEMS %%%%****=====------- \n\n {}```'.format(db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]))
                    else:
                        await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                elif operation[0] == "shop":
                    if check_valid_user_roulette(ctx):

                        shop_item_arr = db_get("SELECT item, price FROM roulette_shop")

                        try:
                            user_str = str(operation[1])
                            user_coins = db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
                            for item in shop_item_arr:
                                if user_str.upper() == str(item[0]).upper():
                                    if user_coins >= item[1]:
                                        user_items = db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
                                        if str(item[0]) not in str(user_items):
                                            add_user_item(ctx, item[0])
                                            add_sub_user_coins(ctx, -int(item[1]))
                                            await ctx.message.channel.send('You have successfully bought {}!\nNow you have {} ©'.format(str(item[0]).upper(), int(user_coins) - int(item[1])))
                                            break
                                        else:
                                            await ctx.message.channel.send('You already have this item.')
                                    else:
                                        await ctx.message.channel.send('You dont have enough money to buy this item!')



                        except IndexError:
                            out_shop_item_arr = []
                            out_shop_buff_arr = []
                            for item in shop_item_arr:
                                if 'buff' in str(item):
                                    out_shop_buff_arr.append(str(item[0]).upper() + '  -  ' + str(item[1]) + ' ©\n')
                                else:
                                    out_shop_item_arr.append(str(item[0]).upper() + '  -  ' + str(item[1]) + ' ©\n')
                            out_shop_item_str = ''.join(out_shop_item_arr).replace('_', ' ')
                            out_shop_buff_str = ''.join(out_shop_buff_arr).replace('_', ' ')
                            await ctx.message.channel.send('```\n ---------=======####$$$$$ SHOP $$$$$####=======--------- \n\n ITEMS:\n{}\n\n ROLL BUFFS:\n{}```'.format(out_shop_item_str, out_shop_buff_str))

                    else:
                        await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                elif operation[0] == "daily":
                    if check_valid_user_roulette(ctx):
                        user_daily = db_get("SELECT daily FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
                        if user_daily == 0:
                            coins = db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
                            add_sub_user_coins(ctx, int(daily_bonus))
                            db_set("UPDATE roulette SET daily = 1 WHERE user_id = {}".format(int(ctx.message.author.id)))
                            await ctx.message.channel.send("Your balance is: {} ©".format(coins + daily_bonus))
                        else:
                            await ctx.message.channel.send("You have already used daily bonus. Try next day.")
                    else:
                        await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                elif operation[0] == "top":
                    if check_valid_user_roulette(ctx):
                        top_arr = db_get("SELECT user_id, coins FROM roulette ORDER BY coins DESC")

                        top_arr = top_arr[0:10]

                        counter = 1
                        top = ''
                        for user in top_arr:
                            top += ''.__add__(str(counter) + '. - ' + str(bot.get_user(int(user[0]))).split("#")[0] + " " + str(user[1]) + " ©\n")
                            counter += 1
                        await ctx.message.channel.send('```--------------====TOP LEADERS====--------------\n\n{}```'.format(top))
                    else:
                        await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


            except IndexError:
                await ctx.message.channel.send("Try this commands to play 'THE ROULETTE GAME': ```{}roulette help\n{}roulette start```".format(config.prefix, config.prefix))





#++++++++++++++++++++SCHEDULE_COMMANDS++++++++++++++++++++++
    @tasks.loop(hours=24)
    async def daily():
        db_set("UPDATE roulette SET daily = 0")


    daily.start()
    bot.run(config.token)


#-----------------ERROR CATCHER------------------
except Exception as e:
    logging.error(e)
    bot.close()
    sys.exit()

else:
    bot.close()
    sys.exit()