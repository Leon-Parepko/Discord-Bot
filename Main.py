from discord import *
import discord
import sys
import logging





#-----------------VARIABLES & CLASSES INIT------------------
logging.basicConfig(filename='logging.log', filemode='w', format='%(levelname)s   -   %(asctime)s   -   %(message)s')

client = discord.Client()

@client.event
async def on_ready():
    logging.error("Logged on as {0}".format(client.user)) # Some problems with this (it is not errors!)



class Config:
    def __init__(self, token, prefix, test_1):
        self.token = token
        self.prefix = prefix
        self.test_1 = test_1






#-----------------CUSTOM ERRORS------------------
class Error(Exception):
    pass

class CustomError(Error):
    pass




#-----------------MAIN------------------
try:

    f = open("C:\\Users\\Leon\\Desktop\\Discord-Bot\\config.txt", "r")
    content = f.read().split("\n")

    config = Config(content[0], content[1], content[2])



    @client.event
    async def on_message(message):
        if message.content.startswith("#Test"):
            await message.channel.send(message.content.split(" ")[1])







    client.run(config.token)



#-----------------ERROR CATCHER------------------
except FileNotFoundError as e:
    logging.error(e)
    sys.exit()

except IndexError as e:
    logging.error(e)
    sys.exit()

else:
    sys.exit()