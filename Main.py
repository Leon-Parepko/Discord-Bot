from discord.ext.commands import has_permissions

from discord import *
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
    def __init__(self, token, prefix, available_channels, super_user):
        self.token = token
        self.prefix = prefix
        self.available_channels = available_channels
        self.super_user = super_user






#--------------------------SUBSIDIARY_FUNCTIONS----------------------------------
def parse_file(file_path):
    content = []
    f = open(file_path, "r")
    content_raw = f.read().split("\n")
    f.close()
    for i in content_raw:
        content.append(i.split(" = ")[1])
    return content

def reconfig(file_content):
    config.token = file_content[0]
    config.prefix = file_content[1]
    config.available_channels = str(file_content[2]).split(" ")
    config.super_user = str(file_content[3]).split(" ")

def prefix_check(prefix):
    if prefix in prefixes_available:
        return True
    else:
        return False

# def bot_upd_config():

def valid_user_check(user):
    pass



#-----------------CUSTOM ERRORS------------------
class Error(Exception):
    pass

class CustomError(Error):
    pass




#------------------------------MAIN-----------------------------





try:
#Config initialization
    content = parse_file(file_path)
    config = Config(content[0],
                    content[1],
                    str(content[2]).split(" "),
                    str(content[3]).split(" "))



    bot = commands.Bot(command_prefix=config.prefix)



    @bot.event
    async def on_ready():
        logging.info("Logged on as {0}".format(bot.user))




    @bot.command()
    @has_permissions(administrator=True)
    async def prefix_config(ctx, arg):
        if prefix_check(str(arg)):
            file_reader = open(file_path, "r")
            lines_list = file_reader.readlines()
            file_reader.close()
            lines_list[1] = "PREFIX = " + str(arg) + "\n"
            file_writer = open(file_path, "w")
            file_writer.writelines(lines_list)
            file_writer.close()
            reconfig(parse_file(file_path))
            bot.command_prefix = str(arg)
            await ctx.message.channel.send("Prefix has been changed successfully.")
        else:
            await ctx.message.channel.send("This prefix is invalid! Please, try one of this - ```" + prefixes_available + "```\nExample: " + config.prefix + "prefix_config PREFIX")


    # @bot.command()
    # @has_permissions(administrator=True)
    # async def superuser_config(ctx, operation, arg):
    #
    #
    #     if valid_user_check(ctx.user) == True:
    #         if operation == "add":
    #             pass
    #         elif operation == "set":
    #             pass
    #         else:
    #             await ctx.message.channel.send("This operation is invalid! Please, try one of this - set, add \nExample: " + config.prefix + "superuser_config set USER")
    #
    #         if prefix_check(str(arg)):
    #             file_reader = open(file_path, "r")
    #             lines_list = file_reader.readlines()
    #             file_reader.close()
    #             lines_list[1] = "PREFIX = " + str(arg) + "\n"
    #             file_writer = open(file_path, "w")
    #             file_writer.writelines(lines_list)
    #             file_writer.close()
    #             reconfig(parse_file(file_path))
    #             await ctx.message.channel.send("Prefix changed successfully.")
    #         else:
    #             await ctx.message.channel.send("This prefix is invalid! Please, try one of this - " + prefixes_available + "\nExample: " + config.prefix + "prefix_config PREFIX")
    #     else:
    #         await ctx.message.channel.send("This user is invalid! Please, try other one\nExample: " + config.prefix + "superuser_config set USER")
    #
    #




    bot.run(config.token)

#-----------------ERROR CATCHER------------------
except FileNotFoundError as e:
    logging.error(e)
    client.close()
    sys.exit()

except DiscordException as e:
    logging.error(e)
    client.close()
    sys.exit()

except IndexError as e:
    logging.error(e)
    client.close()
    sys.exit()

else:
    client.close()
    sys.exit()