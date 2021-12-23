from discord.ext.commands import has_permissions
from discord.ext import commands
import discord.errors
import discord
# import asyncio
import sys
import logging
# import functional



#--------------------------VARIABLES & CLASSES INIT----------------------------------
file_path = "C:\\Users\\Leon\\Desktop\\Discord-Bot\\config.txt"
prefixes_available = "!@#$%^&*+_-~`=:;?/.<>,|"
logging.basicConfig(filename='logging.log', level=logging.INFO, filemode='w', format='%(levelname)s   -   %(asctime)s   -   %(message)s')

command_index = ""

class Config:
    def __init__(self, token, prefix, available_channels, super_users):
        self.token = token
        self.prefix = prefix
        self.available_channels = available_channels
        self.super_users = super_users






#--------------------------SUBSIDIARY_FUNCTIONS----------------------------------
def parse_file(file_path):
    content = []
    f = open(file_path, "r")
    content_raw = f.read().split("\n")
    f.close()
    for i in content_raw:
        if (i != ''):
            content.append(i.split(" = ")[1])
    return content


def change_file_var(var, arg):
    file_reader = open(file_path, "r")
    lines_list = file_reader.readlines()
    file_reader.close()
    lines_list[var] = str(arg)
    file_writer = open(file_path, "w")
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





#-----------------CUSTOM ERRORS------------------
class Error(Exception):
    pass

class CustomError(Error):
    pass






#------------------------------MAIN-----------------------------
try:
#Config initialization
    content = parse_file(file_path)
    config = Config(content[0], content[1], str(content[2]).split(" "), str(content[3]).split(" "))


    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix=config.prefix, intents=intents)



    @bot.event
    async def on_ready():
        logging.info("Logged on as {0}".format(bot.user))


    @bot.command()
    @has_permissions(administrator=True)
    async def prefix_config(ctx, arg):
        if prefix_check(str(arg)):
            change_file_var(1, "PREFIX = " + str(arg) + "\n")
            reconfig(parse_file(file_path))
            bot.command_prefix = str(arg)
            await ctx.message.channel.send("Prefix has been changed successfully.")
        else:
            await ctx.message.channel.send("This prefix is invalid! Please, try one of this: ```" + prefixes_available + "```\nExample:```" + config.prefix + "prefix_config PREFIX```")


    @bot.command()
    @has_permissions(administrator=True)
    async def superuser_config(ctx, operation, arg):

        if operation != "add" and operation != "set":
            await ctx.message.channel.send("This operation is invalid! Please, try one of this - set, add \nExample:```" + config.prefix + "superuser_config set USER_ID```")

        elif valid_user_check(arg, ctx):
            if operation == "add":
                change_file_var(3, open(file_path, "r").readlines()[3].split("\n")[0] + " " + arg + "\n")
                reconfig(parse_file(file_path))
                await ctx.message.channel.send("New SuperUser: " + str(bot.get_user(int(arg))) + " has been set successfully.")

            elif operation == "set":
                change_file_var(3, "SUPERUSERS = " + arg + "\n")
                reconfig(parse_file(file_path))
                await ctx.message.channel.send("New SuperUser: " + str(bot.get_user(int(arg))) + " has been set successfully.")

        else:
            await ctx.message.channel.send("This user is invalid or already in the list! Please, try other one\nExample:```" + config.prefix + "superuser_config set USER_ID```")


    @bot.command()
    @has_permissions(administrator=True)
    async def available_channels_config(ctx, operation, arg):
        if operation != "add" and operation != "set":
            await ctx.message.channel.send("This operation is invalid! Please, try one of this - set, add \nExample:```" + config.prefix + "available_channels_config set CHANNEL_NAME```")

        elif valid_channel_check(arg, ctx) == True:
            if operation == "add":
                change_file_var(2, open(file_path, "r").readlines()[2].split("\n")[0] + " " + arg + "\n")
                reconfig(parse_file(file_path))
                await ctx.message.channel.send("New channel has been added successfully.")

            elif operation == "set":
                change_file_var(2, "CHANNELS = " + arg + "\n")
                reconfig(parse_file(file_path))
                await ctx.message.channel.send("New channel has been set successfully.")

        else:
            await ctx.message.channel.send("This channel is invalid or already in the list! Please, try other one\nExample:```" + config.prefix + "available_channels_config set CHANNEL_NAME```")


    @bot.command()
    @has_permissions(administrator=True)
    async def show(ctx, *operation):
        try:
            if operation[0] == "prefix":
                await ctx.message.channel.send("```Prefix = " + config.prefix + "```")

            elif operation[0] == "available_channels":
                await ctx.message.channel.send("```Available Channels = " + str(config.available_channels) + "```")

            elif operation[0] == "super_users":
                await ctx.message.channel.send("```Super Users = " + str(config.super_users) + "```")

            elif operation[0] == "token":
                await ctx.message.channel.send("Are you serious?")

        except IndexError:
            await ctx.message.channel.send("```Prefix = " + config.prefix + "\nAvailable Channels = " + str(config.available_channels) + "\nSuper Users = " + str(config.super_users) + "```")





    bot.run(config.token)

#-----------------ERROR CATCHER------------------
except Error as e:
    logging.error(e)
    bot.close()
    sys.exit()
#
# except DiscordException as e:
#     logging.error(e)
#     bot.close()
#     sys.exit()
#
# except IndexError as e:
#     logging.error(e)
#     bot.close()
#     sys.exit()

else:
    bot.close()
    sys.exit()