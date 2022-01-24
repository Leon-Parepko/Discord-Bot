# Discord-Bot

This is a personal Discord bot. Only for "Inaccessible Royal Guild" Server.

INSTALLATION REQUIREMENTS:
* Python 3.7 (or lower)
* FFmpeg driver (latest)
* discord
* discord.py
* asyncio
* requests
* youtube_dl

The bot is consist of several modules which might be used by the prefix (it could be also configured by administrators). Administrative commands could be used only by users with administrative server roles or bot superusers (configured by administrative commands). Also, all inner commands are split by the space " " symbol.
The list of commands structure you could see below:


    The module command list:   
*      ADMINISTRATIVE:
            prefix_config ARG
        
               ban @USER TIME REASON
            
                superuser_config 
                 ┣───── add USER_ID
                 ┗───── set USER_ID
            
                available_channels_config
                 ┣───── add CHANNEL_ID
                 ┗───── set CHANNEL_ID
            
                show
                 ┣───── version
                 ┣───── prefix
                 ┣───── super_users
                 ┗───── token
            
                bot_status
                 ┣───── ping
                 ┣───── music
                 ┗───── 
        
*     FUN:
            roulette
             ┣───── help
             ┣───── start BONUS_CODE
             ┣───── roll
             ┣───── megaroll
             ┣───── profile
             ┣───── items ITEM_NAME
             ┣───── trophies TROPHY NAME
             ┣───── shop ITEM_NAME
             ┣───── level
                ┗───── up
             ┣───── daily
             ┗───── top
            
            anecdote
        
            music
             ┣───── play REFFERENCE
             ┣───── pause
             ┣───── resume
             ┣───── skip
             ┣───── loop
             ┣───── queue
             ┗───── quit



