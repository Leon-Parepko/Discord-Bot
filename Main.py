from discord.ext.commands import has_permissions
from discord.ext import commands
from discord.ext import tasks
import discord
import asyncio
import requests
import random
import sys
import logging
import sqlite3
import youtube_dl
import functional



#--------------------------VARIABLES & CLASSES INIT----------------------------------
config_file_path = "C:\\Users\\Leon\\Desktop\\Discord-Bot\\config.txt"
win_words_file_path = "C:\\Users\\Leon\\Desktop\\Discord-Bot\\win_words.txt"
loose_words_file_path = "C:\\Users\\Leon\\Desktop\\Discord-Bot\\loose_words.txt"
roulette_db_name = 'roulette.db'
anecdote_db_name = 'anecdote.db'

ytdl_options = {
    'format': "bestaudio",
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
global voice_activity_counter
global queue
voice_activity_counter = [0]
queue = []
Auto_Disconnect_Timeout = 5     # minutes

prefixes_available = "!@#$%^&*+_-~`=:;?/.<>,|"
logging.basicConfig(filename='logging.log', level=logging.INFO, filemode='w', format='%(levelname)s   -   %(asctime)s   -   %(message)s')

roulette_bonus_key = "TestBonusTestBonusTestBonus"
Start_Coins = 500
daily_bonus = 200
roll_price = 35


class Config:
    def __init__(self, token, prefix, available_channels, super_users, version):
        self.token = token
        self.prefix = prefix
        self.available_channels = available_channels
        self.super_users = super_users
        self.version = version


class Item:
    def __init__(self, id, name, type, rank, sell_price, buy_price, stat, description, art):
        self.id = int(id)
        self.name = str(name)
        self.type = str(type)
        self.rank = int(rank)
        self.sell_price = int(sell_price)
        self.buy_price = int(buy_price)
        self.stat = stat
        self.description = str(description)
        self.art = art

    def info_window(self):
        text = ""
        # rank_stars = ''
        #
        # for i in range(0, self.rank):
        #     rank_stars += '*'

        if self.type == "item":
            text = '``` -------========%%%% {} %%%%========-------\n\nType: {}\nRank: {}\n\nDescription: {}\n\n{}```'.format(self.name.upper(), self.type, self.rank, self.description, self.art)

        elif self.type == "trophy":
            text = '``` -------========#### {} ####========-------\n\nType: {}\nRank: {}\n\nDescription: {}\n\n{}```'.format(self.name.upper(), self.type, self.rank, self.description, self.art)

        text = text.replace("\\n", "\n")
        return text


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
    with sqlite3.connect(roulette_db_name) as db:
        cursor = db.cursor()
        data = cursor.execute("""{}""".format(str(exe)))
        arr = []
        for i in data:
            arr.append(i)
        return arr


def db_set(exe):
    with sqlite3.connect(roulette_db_name) as db:
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


def check_valid_user_roulette(ctx):
    users = db_get(" SELECT user_id FROM roulette ")

    for i in users:
        if i[0] == int(ctx.message.author.id):
            return True
    return False


def check_item_sets(ctx, item_arr):

    user_trophies = db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")

    new_trophy = ""

    if ("neko_girlfriend" and "neko_sister" and "neko_wife" in item_arr) and ("neko_paradise" not in user_trophies):
        add_user_trophy(ctx, "neko_paradise")
        new_trophy = "neko_paradise"

    elif ("admins_keyboard" and "admins_mouse" and "admins_computer" and "admins_coffee" in item_arr) and ("binary_tambourine" not in user_trophies):
        add_user_trophy(ctx, "binary_tambourine")
        new_trophy = "binary_tambourine"

    elif ("♂three_hundred_bucks♂" and "♂sticky_finger♂" and "♂deep_dark_fantasy♂" and "**mega_♂CUM♂" in item_arr) and ("♂fucking_slave♂" not in user_trophies):
        add_user_trophy(ctx, "♂fucking_slave♂")
        new_trophy = "♂fucking_slave♂"


    if new_trophy != "":
        return new_trophy
    else:
        return None


def add_user_item(ctx, item):
    user_items = db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
    db_set("UPDATE roulette SET items = '{}' WHERE user_id = {}".format(str(user_items).__add__(" " + str(item)),int(ctx.message.author.id)))

    user_items = db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")

    result = check_item_sets(ctx, user_items)

    if result is not None:
        return result
    else:
        return None


def add_user_trophy(ctx, trophy):
    user_trophies = db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
    db_set("UPDATE roulette SET trophies = '{}' WHERE user_id = {}".format(str(user_trophies).__add__(" " + str(trophy)),int(ctx.message.author.id)))


def add_sub_user_coins(ctx, sum):
    user_coins = db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
    db_set("UPDATE roulette SET coins = '{}' WHERE user_id = {}".format(int(user_coins) + int(sum), int(ctx.message.author.id)))


def add_sub_user_megacoins(ctx, sum):
    user_megacoins = db_get("SELECT megacoins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
    db_set("UPDATE roulette SET megacoins = '{}' WHERE user_id = {}".format(int(user_megacoins) + int(sum), int(ctx.message.author.id)))


def count_user_mult(ctx):
    user_items = db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")
    roll_mult = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    for item in user_items:
        item__ = get_item(name=str(item))
        if item__ is not None:
            counter = 0
            for num in item__.stat:
                roll_mult[counter] = num * roll_mult[counter]
                counter += 1
    return roll_mult

# Just for admins
def get_all_items_in_system():

    all_items = []

    items1 = db_get("SELECT item, megaitem FROM roulette_roll_items")
    items2 = db_get("SELECT item FROM roulette_shop")
    items3 = db_get("SELECT trophy, megatrophy FROM roulette_roll_trophies")

    items1 = items1.__add__(items2).__add__(items3)

    # Yeh, it looks like a bullshit!!!
    for i in items1:
        if i is not None:
            for j in i:
                if j is not None:
                    all_items.append(j)
    return all_items


def get_item(name=None, id=None):
    try:
        if name is not None:
            db_raw_data = db_get("SELECT id, name, type, rank, sell_price, buy_price, stat, description, art FROM roulette_all_items WHERE name = '{}'".format(str(name)))[0]
        elif id is not None:
            db_raw_data = db_get("SELECT id, name, type, rank, sell_price, buy_price, stat, description, art FROM roulette_all_items WHERE id = {}".format(int(id)))[0]

        stat_raw = map(float, str(db_raw_data[6]).split(" "))

        stat = []
        for i in stat_raw:
            stat.append(i)

        item_ = Item(db_raw_data[0], db_raw_data[1], db_raw_data[2], db_raw_data[3], db_raw_data[4], db_raw_data[5], stat, db_raw_data[7], db_raw_data[8])
        return item_

    except:
        return None


def check_valid_url(url):
    if str(url).startswith("https://www.youtube.com/watch?v="):
        request = requests.get(str(url))
        if "Video unavailable" in request.text:
            return False
        else:
            return True
    else:
        return False


class phrases:
    def win(self):
        return str(random.choice(parse_file(win_words_file_path)))

    def loose(self):
        return str(random.choice(parse_file(loose_words_file_path)))



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


#Youtube_dl initialization
    ytdl = youtube_dl.YoutubeDL(ytdl_options)


#Phrases initialization
    Phrases = phrases()



    @bot.event
    async def on_ready():
        logging.info("Logged on as {}".format(bot.user))


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



    @bot.command(pass_context=True)
    @has_permissions(administrator=True)
    async def ban(ctx, user: discord.Member, ban_time, reason, *bot_use):
        if str(ctx.message.channel) in config.available_channels:
            if (superuser_check(ctx) and not ctx.message.author.bot) or bot_use[0] == True:
                # if not(int(ctx.message.author.id) == int(user.id)):
                    if not user.guild_permissions.administrator:
                        member = ctx.message.author
                        ban_role = discord.utils.get(member.guild.roles, name="prisoner")
                        user_roles = []
                        for role in user.roles[1:]:
                            user_roles.append(str(role))
                            await user.remove_roles(discord.utils.get(member.guild.roles, name=str(role)))
                        await user.add_roles(ban_role)
                        await ctx.message.channel.send("**{}** has been banned on {} min.\nReason: **{}**".format(str(user), ban_time, str(reason)))
                        print(" BAN   -   User: {},  Roles: {},  Time: {} (min),  Reason: {},  By: {}".format(str(user), str(user_roles), str(ban_time), str(reason), str(ctx.message.author)))
                        logging.info(" BAN   -   User: {},  Roles: {},  Time: {} (min),  Reason: {},  By: {}".format(str(user), str(user_roles), str(ban_time), str(reason), str(ctx.message.author)))

                        await asyncio.sleep(int(ban_time) * 60)

                        await user.remove_roles(ban_role)
                        for role in user_roles:
                            await user.add_roles(discord.utils.get(member.guild.roles, name=str(role)))
                        await ctx.message.channel.send("**{}** has been unbanned!".format(str(user)))
                    else:
                        await ctx.message.channel.send("Hay! You cant just ban an administrator.")
                # else:
                #     await ctx.message.channel.send("Just tell me why?")
            else:
                await ctx.message.channel.send("You dont have permissions to use this commands!")



#++++++++++++++++++++INFO_COMMANDS++++++++++++++++++++++
    @bot.command()
    async def show(ctx, *operation):
        if str(ctx.message.channel) in config.available_channels:
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
        if str(ctx.message.channel) in config.available_channels:
            try:
                if operation[0] == "ping":
                    await ctx.message.channel.send("```Ping - {} ms.```".format(str(round(bot.latency * 1000))) )

            except IndexError:
                await ctx.message.channel.send("```Ping - {} ms.```".format(str(round(bot.latency * 1000))) )

# ----- TEST -----
    @bot.command()
    async def ban_timer(ctx):
        pass

#++++++++++++++++++++FUN_COMMANDS++++++++++++++++++++++
    @bot.command()
    async def roulette(ctx, *operation):
        if str(ctx.message.channel) in config.available_channels:
            if ctx.message.author.bot:
                await ctx.message.channel.send('Hay! It is illegal to use bots! :(')
            else:

                try:
                    if operation[0] == "help":
                        await ctx.message.channel.send('```  ______   ______   __  __   __       ______  ______  ______  ______    \n /\  == \ /\  __ \ /\ \/\ \ /\ \     /\  ___\/\__  _\/\__  _\/\  ___\   \n \ \  __< \ \ \/\  \ \ \_\  \ \ \____\ \  __ \/_/\ \/\/_/\ \/\ \  __\   \n  \ \_\ \_ \ \_____ \ \_____ \ \_____ \ \_____\ \ \_\   \ \_\ \ \_____\ \n   \/_/ /_/ \/_____/ \/_____/ \/_____/ \/_____/  \/_/    \/_/  \/_____/ \n\n\n________-----======= THIS IS A ROULETTE GAME! =======-----________\n\n\nYou could use this commands to play:\n{0}roulette start - \n{0}roulette top - \n{0}roulette roll - \n{0}roulette megaroll - \n{0}roulette shop - \n{0}roulette profile - \n{0}roulette trophies - \n{0}roulette items - ```'.format(config.prefix))


                    elif operation[0] == "start":
                        start_coins = Start_Coins
                        try:
                            if str(operation[1]) == roulette_bonus_key:
                                start_coins = Start_Coins * 4
                        except IndexError:
                            pass

                        if check_valid_user_roulette(ctx) == False:
                            db_set("INSERT INTO roulette (user_id, coins, megacoins, items, trophies, roll_counter, daily, level) VALUES({}, {}, 0, 'default_item', 'default_trophy', 0, 0, 1)".format(int(ctx.message.author.id), start_coins))
                            await ctx.message.channel.send("New user have been added successfully!")
                        else:
                            await ctx.message.channel.send("You are already registered!")


                    elif operation[0] == "roll":
                        if check_valid_user_roulette(ctx):
                            user_coins = int(db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0])
                            if user_coins >= roll_price:
                                user_coins -= roll_price
                                user_roll_buff = db_get("SELECT roll_buff FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
                                user_roll_mult = count_user_mult(ctx)

                                roll_result = functional.roll(user_mult=user_roll_mult, event=str(user_roll_buff))

                                add_sub_user_coins(ctx, -roll_price)
                                db_set("UPDATE roulette SET roll_buff = NULL WHERE user_id = {}".format(int(ctx.message.author.id)))
                                print(roll_result, user_roll_buff)

                                if type(roll_result) == int:
                                    add_sub_user_coins(ctx, roll_result)
                                    await ctx.message.channel.send("{}\nYou have won {} © !\nTotal balance is: {} ©".format(Phrases.win(), roll_result, user_coins + roll_result))


                                elif "ban" in roll_result:
                                    ban_time = roll_result.split("_")[1]
                                    await ctx.message.channel.send("{}\nYou have won BAN on {} minutes!".format(Phrases.loose(), ban_time))
                                    await ban(ctx, ctx.message.author, ban_time, "Roulette", True)


                                elif roll_result == "item":
                                    user_items = str(db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]).split(" ")
                                    roll_items = db_get("SELECT item FROM roulette_roll_items")
                                    roll_items_reduce = db_get("SELECT item FROM roulette_roll_items")
                                    roll_items_reduce_weights = []

                                    for item in roll_items:
                                        if item[0] in user_items:
                                            roll_items_reduce.remove(item)

                                    if roll_items_reduce == []:
                                        await ctx.message.channel.send("PLEASE **STOP PLAYING THIS SHIT!**\nYou already have all the items.")

                                    else:
                                        for item in roll_items_reduce:
                                            roll_items_reduce_weights.append(int(db_get("SELECT rank FROM roulette_all_items WHERE name = '{}'".format(str(item[0])))[0][0]) ** -1.7)

                                        rand_item = functional.roll_items(roll_items_reduce, roll_items_reduce_weights)[0]
                                        have_item_set = add_user_item(ctx, rand_item)
                                        await ctx.message.channel.send("{}\nYou have won new item: {} !".format(Phrases.win(), str(rand_item).upper()))
                                        if have_item_set is not None:
                                            await ctx.message.channel.send("Also you have completed new item set, and got **{}** trophy!".format(have_item_set))

                                elif roll_result == "trophy":
                                    user_trophies = str(db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]).split(" ")
                                    roll_trophies = db_get("SELECT trophy FROM roulette_roll_trophies")
                                    roll_trophies_reduce = db_get("SELECT trophy FROM roulette_roll_trophies")
                                    roll_trophies_reduce_weights = []

                                    for trophy in roll_trophies:
                                        if trophy[0] in user_trophies:
                                            roll_trophies_reduce.remove(trophy)

                                    if roll_trophies_reduce == []:
                                        await ctx.message.channel.send("YOU'R MAD! PLEASE **STOP THIS!**\nYou already have all the trophies.")

                                    else:
                                        for trophy in roll_trophies_reduce:
                                            roll_trophies_reduce_weights.append(int(db_get("SELECT rank FROM roulette_all_items WHERE name = '{}'".format(str(trophy[0])))[0][0]) ** -1.7)

                                        rand_trophy = functional.roll_items(roll_trophies, roll_trophies_reduce_weights)[0]
                                        add_user_trophy(ctx, rand_trophy)
                                        await ctx.message.channel.send("{}\nYou have won new trophy: {} !".format(Phrases.win(), str(rand_trophy).upper()))


                                elif roll_result == "roll_buff":
                                    buff = functional.roll_buff()
                                    db_set("UPDATE roulette SET roll_buff = '{}' WHERE user_id = {}".format(str(buff), int(ctx.message.author.id)))
                                    await ctx.message.channel.send("{}\nYou have won roll buff: {}.\nIt will be automatically used in your next roll.".format(Phrases.win(), buff))


                                elif roll_result == "double_balance":
                                    add_sub_user_coins(ctx, int(user_coins))
                                    await ctx.message.channel.send("{}\nYour **balance is doubled**, now it is: {} © !".format(Phrases.win(), int(user_coins) * 2))


                                elif roll_result == "half_balance":
                                    add_sub_user_coins(ctx, -(int(user_coins) // 2))
                                    await ctx.message.channel.send("{}\nYour balance reduced in twice, now it is: {} © !".format(Phrases.loose(), int(user_coins) // 2))


                                elif roll_result == "megacoins":
                                    add_sub_user_megacoins(ctx, 1)
                                    user_megacoins = int(db_get("SELECT megacoins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0])
                                    await ctx.message.channel.send("{}\nYou have won 1 megacoin!\nTotal balance is: {} ▽".format(Phrases.win(), user_megacoins))


                                user_rolls = int(db_get("SELECT roll_counter FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0])
                                db_set("UPDATE roulette SET roll_counter = {} WHERE user_id = {}".format(int(user_rolls + 1), int(ctx.message.author.id)))


                            else:
                                await ctx.message.channel.send('You dont have enough money to roll! \n Check your status in profile or wait for the daily bonus.'.format(config.prefix))
                        else:
                            await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                    elif operation[0] == "megaroll":
                        if check_valid_user_roulette(ctx):
                            user_coins = int(db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0])
                            user_megacoins = int(db_get("SELECT megacoins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0])
                            if user_megacoins >= 1:
                                db_set("UPDATE roulette SET megacoins = {} WHERE user_id = {}".format(int(user_megacoins - 1), int(ctx.message.author.id)))
                                megaroll_result = functional.roll(event="megaroll")

                                print(megaroll_result)

                                if type(megaroll_result) == int:
                                    add_sub_user_coins(ctx, megaroll_result)
                                    await ctx.message.channel.send("{}\nYou have won {} © !\nTotal balance is: {} ©".format(Phrases.win(), megaroll_result, user_coins + megaroll_result))

                                elif megaroll_result == "item":
                                    user_items = str(db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]).split(" ")
                                    roll_items = db_get("SELECT item, megaitem FROM roulette_roll_items")
                                    roll_items_without_none = []
                                    roll_items_reduce = []

                            # THIS SHOULD BE CHANGED!!!!
                                    for i in roll_items:
                                        for j in i:
                                            if j is not None:
                                                roll_items_without_none.append(j)
                                                roll_items_reduce.append(j)

                                    for item in roll_items_without_none:
                                        if item in user_items:
                                            roll_items_reduce.remove(item)

                                    if roll_items_reduce == []:
                                        await ctx.message.channel.send("PLEASE **STOP PLAYING THIS SHIT!**\nYou already have all the items.")

                                    else:
                                        roll_items_reduce_weights = []
                                        for item in roll_items_reduce:
                                            roll_items_reduce_weights.append(int(db_get("SELECT rank FROM roulette_all_items WHERE name = '{}'".format(str(item)))[0][0]) ** -1.7)

                                        rand_item = functional.roll_items(roll_items_reduce, roll_items_reduce_weights)
                                        await ctx.message.channel.send("{}\nYou have won new item: {} !".format(Phrases.win(), str(rand_item).upper()))


                                elif megaroll_result == "trophy":
                                    user_trophies = str(db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]).split(" ")
                                    roll_trophies = db_get("SELECT trophy, megatrophy FROM roulette_roll_trophies")
                                    roll_trophies_without_none = []
                                    roll_trophies_reduce = []

                            # THIS SHOULD BE CHANGED!!!!
                                    for i in roll_trophies:
                                        for j in i:
                                            if j is not None:
                                                roll_trophies_without_none.append(j)
                                                roll_trophies_reduce.append(j)

                                    for trophy in roll_trophies_without_none:
                                        if trophy in user_trophies:
                                            roll_trophies_reduce.remove(trophy)

                                    if roll_trophies_reduce == []:
                                        await ctx.message.channel.send("YOU'R MAD! PLEASE **STOP THIS!**\nYou already have all the trophies.")

                                    else:
                                        roll_trophies_reduce_weights = []
                                        for trophy in roll_trophies_reduce:
                                            roll_trophies_reduce_weights.append(int(db_get("SELECT rank FROM roulette_all_items WHERE name = '{}'".format(str(trophy)))[0][0]) ** -1.7)

                                        rand_trophy = functional.roll_items(roll_trophies_reduce, roll_trophies_reduce_weights)
                                        add_user_trophy(ctx, rand_trophy)
                                        await ctx.message.channel.send("{}\nYou have won new trophy: {} !".format(Phrases.win(), str(rand_trophy).upper()))

                        else:
                            await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                    elif operation[0] == "profile":
                        if check_valid_user_roulette(ctx):

                            user_data_raw = db_get("SELECT coins, megacoins, roll_counter, items, level FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0]

                            user = str(ctx.message.author).split("#")[0]
                            coins = user_data_raw[0]
                            megacoins = user_data_raw[1]
                            rolls = user_data_raw[2]
                            items_arr = user_data_raw[3].split(" ")
                            level = user_data_raw[4]
                            if len(items_arr) >= 8:
                                items_arr = items_arr[0:8]
                                items_arr.append("...")
                            items = ''.join(map(lambda x: x + "  ", map(str, items_arr)))

                            trophies_arr = db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")
                            if len(trophies_arr) >= 8:
                                trophies_arr = trophies_arr[0:8]
                                trophies_arr.append("...")
                            trophies = ''.join(map(lambda x: x + "  ", map(str, trophies_arr)))

                            await ctx.message.channel.send('```\n --------------====PROFILE====-------------- \n\n UserName:     {}\n Level:        {}\n Coins:        {} ©\n Megacoins:    {} ▽\n Rolls Total:  {}\n Trophies:     {}\n Items:        {}```'.format(user, level, coins, megacoins, rolls, trophies, items))

                        else:
                            await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                    elif operation[0] == "trophies":
                        if check_valid_user_roulette(ctx):
                            try:
                                user_str = str(operation[1])
                                user_trophy_arr = db_get("SELECT trophies FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0].split(" ")
                                for i in user_trophy_arr:
                                    if user_str == str(i):
                                        user_trophy = get_item(name=user_str)
                                        if user_trophy is not None:
                                            await ctx.message.channel.send(get_item(name=user_str).info_window())
                                        else:
                                            await ctx.message.channel.send("You don't have such trophy!")

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
                                        user_item = get_item(name=user_str)
                                        if user_item is not None:
                                            await ctx.message.channel.send(get_item(name=user_str).info_window())
                                        else:
                                            await ctx.message.channel.send("You don't have such item!")

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

                                flag = True

                                for item in shop_item_arr:
                                    if user_str.upper() == str(item[0]).upper():
                                        if user_coins >= item[1]:

                                            if "*buff_" in str(item[0]):
                                                db_set("UPDATE roulette SET roll_buff = '{}' WHERE user_id = {}".format(item[0].split("*buff_")[0], int(ctx.message.author.id)))
                                                await ctx.message.channel.send('You have successfully bought {}! (buffs are NOT STACKED)\nIt will be automatically used in your next roll.')
                                                flag = False
                                                break

                                            else:
                                                user_items = db_get("SELECT items FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
                                                if str(item[0]) not in str(user_items):
                                                    if "**mega_" in str(item[0]):
                                                        have_item_set = add_user_item(ctx, item[0])
                                                        add_sub_user_megacoins(ctx, -int(item[1]))
                                                        user_megacoins = int(db_get("SELECT megacoins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0])
                                                        await ctx.message.channel.send('You have successfully bought {}!\nNow you have {} ▽'.format(str(item[0]).upper(), int(user_megacoins)))

                                                        if have_item_set is not None:
                                                            await ctx.message.channel.send("Also you have completed new item set, and got **{}** trophy!".format(have_item_set))

                                                    else:
                                                        have_item_set = add_user_item(ctx, item[0])
                                                        add_sub_user_coins(ctx, -int(item[1]))
                                                        await ctx.message.channel.send('You have successfully bought {}!\nNow you have {} ©'.format(str(item[0]).upper(), int(user_coins) - int(item[1])))

                                                        if have_item_set is not None:
                                                            await ctx.message.channel.send("Also you have completed new item set, and got **{}** trophy!".format(have_item_set))

                                                    flag = False
                                                    break
                                                else:
                                                    await ctx.message.channel.send('You already have this item.')
                                                    flag = False
                                                    break
                                        else:
                                            await ctx.message.channel.send('You dont have enough money to buy this item!')
                                            flag = False
                                            break
                                if flag:
                                    await ctx.message.channel.send('There is no such item.\nTry this commands: ```{}roulette shop item\n{}roulette shop **mega_item\n{}roulette shop *buff_item```'.format(config.prefix, config.prefix, config.prefix))


                            except IndexError:
                                out_shop_item_arr = []
                                out_shop_megaitem_arr = []
                                out_shop_buff_arr = []
                                for item in shop_item_arr:
                                    if '*buff_' in str(item):
                                        out_shop_buff_arr.append(str(item[0]).upper() + '  -  ' + str(item[1]) + ' ©\n')
                                    elif '**mega_' in str(item):
                                        out_shop_megaitem_arr.append(str(item[0]).upper() + '  -  ' + str(item[1]) + ' ▽\n')
                                    else:
                                        out_shop_item_arr.append(str(item[0]).upper() + '  -  ' + str(item[1]) + ' ©\n')
                                out_shop_item_str = ''.join(out_shop_item_arr).replace('_', ' ')
                                out_shop_buff_str = ''.join(out_shop_buff_arr).replace('_', ' ')
                                out_shop_megaitem_str = ''.join(out_shop_megaitem_arr).replace('_', ' ')
                                await ctx.message.channel.send('```\n ---------=======####$$$$$ SHOP $$$$$####=======--------- \n\n ITEMS:\n{}\n\n MEGA_ITEMS:\n{}\n\n ROLL BUFFS:\n{}```'.format(out_shop_item_str, out_shop_megaitem_str, out_shop_buff_str))

                        else:
                            await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                    elif operation[0] == "level":
                        if check_valid_user_roulette(ctx):
                            try:
                                if operation[1] == "up":
                                    user_data = db_get("SELECT coins, megacoins, roll_counter, level FROM roulette WHERE user_id = {}".format(ctx.message.author.id))[0]
                                    print(user_data)
                                    user_level = int(user_data[3])
                                    if user_level != 100:
                                        user_coins = int(user_data[0])
                                        user_megacoins = int(user_data[1])
                                        user_roll_counter = int(user_data[2])
                                        if user_roll_counter >= user_level ** 3 and user_coins >= round((user_level * 4) ** 2.7) and user_megacoins >= user_level ** 2:
                                            db_set("UPDATE roulette SET level = '{}' WHERE user_id = {}".format(user_level + 1, int(ctx.message.author.id)))
                                            add_sub_user_coins(ctx, -round((user_level * 4) ** 2.7))
                                            add_sub_user_megacoins(ctx, -user_level ** 2)
                                            await ctx.message.channel.send('**CONGRATULATIONS!**\nYou have successfully upgraded your level to {}.'.format(user_level + 1))
                                        else:
                                            await ctx.message.channel.send('Some requirements are not satisfied!\nFor next level you need:```\n1) {} rolls\n2) {} ©\n3) {} ▽```'.format(user_level ** 3, round((user_level * 4) ** 2.7), user_level ** 2))
                                    else:
                                        await ctx.message.channel.send('**SERIOUSLY?**\n I thought it was impossible to reach this level.')
                            except IndexError:
                                    await ctx.message.channel.send('```\n -------=====####:::: LEVEL_SYSTEM ::::####=====------- \n\nThe higher level you have, the better items you could buy.\nTo increase level you need to satisfy some requirements:\n\n Totall Rolls:  your_level ^ 3\n Coins:  (your_level * 4) ** 2.7\n Megacoins:  your_level ** 2\n\n\nRank       Rank       Rank       Rank       Rank       Rank       Rank\n  1          2          3          4          5          6          7\n  |          |          |          |          |          |          |\n  *----------*----------*----------*----------*----------*----------#\n  1          5          10         20         40         60         80```')
                        else:
                            await ctx.message.channel.send('You are not registered yet! Please register with:```{}roulette start```'.format(config.prefix))


                    elif operation[0] == "daily":
                        if check_valid_user_roulette(ctx):
                            user_daily = db_get("SELECT daily FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
                            if user_daily == 0:
                                coins = db_get("SELECT coins FROM roulette WHERE user_id = {}".format(int(ctx.message.author.id)))[0][0]
                                add_sub_user_coins(ctx, int(daily_bonus))
                                db_set("UPDATE roulette SET daily = 1 WHERE user_id = {}".format(int(ctx.message.author.id)))
                                await ctx.message.channel.send("Daily bonus {} ©\nYour balance is: {} ©".format(daily_bonus, coins + daily_bonus))
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


    @bot.command()
    async def anecdote(ctx):
        if str(ctx.message.channel) in config.available_channels:
            with sqlite3.connect(anecdote_db_name) as anec_db:
                cursor = anec_db.cursor()
                cursor.execute("""SELECT * FROM anecdote_table""")
                rows = cursor.fetchall()
                rand_id = random.randint(1, len(rows))

                anecdote_text = cursor.execute("""SELECT anecdote_text FROM anecdote_table WHERE id = {}""".format(rand_id))

                for text in anecdote_text:
                    await ctx.message.channel.send("**ВНИМАНИЕ АНЕКДОТ:** {}".format(str(text[0])))

# ----- TEST -----
    @bot.command()
    async def music(ctx, *operation):
        if str(ctx.message.channel) in config.available_channels:
            try:
                global queue

                if operation[0] == "queue":
                    queue_text = "------------**SONG QUEUE**------------\n"
                    counter = 1

                    if not queue:
                        queue_text += "                         **Empty**"


                    elif len(queue) <= 7:
                        for url in queue:
                            with youtube_dl.YoutubeDL(ytdl_options) as ydl:
                                info = ydl.extract_info(url, download=False)
                                queue_text += "{}) **{}**\n".format(counter, info['title'])

                                counter += 1

                    else:
                        for url in queue[:6]:
                            with youtube_dl.YoutubeDL(ytdl_options) as ydl:
                                info = ydl.extract_info(url, download=False)
                                queue_text += "{}) **{}**\n".format(counter, info['title'])

                                counter += 1
                        queue_text += "{} more song in the list...".format(len(queue) - 7)

                    await ctx.message.channel.send(queue_text)


                elif operation[0] == "play" or "pause" or "skip" or "quit" or "resume":

                    if ctx.author.voice is not None:
                        channel = ctx.author.voice.channel

                        if operation[0] == "play":
                            if check_valid_url(operation[1]):
                                queue.append(operation[1])

                                if ctx.guild.voice_client not in bot.voice_clients:
                                    await channel.connect()

                                server = ctx.message.guild
                                voice_channel = server.voice_client

                                while queue:
                                    try:

                                        while voice_channel.is_playing() or voice_channel.is_paused():
                                            await asyncio.sleep(0.5)
                                            pass

                                    except AttributeError:
                                        pass

                                    try:
                                        with youtube_dl.YoutubeDL(ytdl_options) as ydl:
                                            info = ydl.extract_info(queue[0], download=False)
                                            url2 = info['formats'][0]['url']
                                            source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
                                            voice_channel.play(source)


                                        queue.pop(0)

                                        await ctx.send('**Now playing:** {}'.format(info['title']))

                                    except:
                                        break




                            else:
                                await ctx.message.channel.send("The link is invalid or this youtube video is unavailable!")

                        # elif operation[0] == "status":
                        #     server = ctx.message.guild
                        #     voice_channel = server.voice_client
                        #     print(voice_channel.is_playing())
                        #     print(voice_channel.is_paused())

                        elif operation[0] == "pause":
                            server = ctx.message.guild
                            voice_channel = server.voice_client
                            voice_channel.pause()
                            await ctx.message.channel.send("Paused")

                        elif operation[0] == "resume":
                            server = ctx.message.guild
                            voice_channel = server.voice_client
                            voice_channel.resume()
                            await ctx.message.channel.send("Resumed")

                        elif operation[0] == "skip":
                            try:
                                server = ctx.message.guild
                                voice_channel = server.voice_client
                                voice_channel.stop()
                                await ctx.message.channel.send("Skipped")

                            except:
                                pass

                        elif operation[0] == "quit":
                            queue.clear()
                            await ctx.message.guild.voice_client.disconnect()

                    else:
                        await ctx.message.channel.send("You are not in voice channel to use this command!")


            except IndexError:
                await ctx.message.channel.send("```Music Commands\n {0}play \n {0}stop \n {0}queue \n {0}skip```".format(config.prefix))



#++++++++++++++++++++SCHEDULE_COMMANDS++++++++++++++++++++++
    @tasks.loop(hours=24)
    async def daily():
        db_set("UPDATE roulette SET daily = 0")

# Auto Disconnect
    @tasks.loop(seconds=10)
    async def every_minute():

        index_counter = 0

        for guild in bot.guilds:

            print(guild, voice_activity_counter)

            try:
                voice_channel = guild.voice_client
                if not voice_channel.is_playing() and not voice_channel.is_paused():

                    if index_counter <= len(voice_activity_counter) - 1:
                        voice_activity_counter[index_counter] += 1
                    else:
                        index_counter.append(1)


                    if voice_activity_counter[index_counter] == 6 * Auto_Disconnect_Timeout:
                        try:
                            await guild.voice_client.disconnect()
                            voice_activity_counter[index_counter] = 0

                        except:
                            pass

                else:
                    voice_activity_counter[index_counter] = 0

            except:
                voice_activity_counter[index_counter] = 0

            index_counter += 1

    every_minute.start()
    daily.start()
    bot.run(config.token)


#-----------------ERROR_CATCHER------------------
except Exception as e:
    logging.error(e)
    bot.close()
    sys.exit()

else:
    bot.close()
    sys.exit()