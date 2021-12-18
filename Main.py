import sys
import logging
import discord




#-----------------VARIABLES & CLASSES------------------
logging.basicConfig(filename='logging.log', filemode='w', format='%(levelname)s   -   %(asctime)s   -   %(message)s')

# client = discord.Client()

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





#-----------------ERROR CATCHER------------------
except FileNotFoundError as e:
    logging.error(e)
    sys.exit()

except IndexError as e:
    logging.error(e)
    sys.exit()

else:
    sys.exit()
