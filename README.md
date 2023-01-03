# Destiny Mod Checker -- The Ultimate Discord Bot for Destiny 2
## What is it?
In the game Destiny 2, armor and weapon mods are required to make new builds for your character classes. The system to acquire mods is to purchase them
from two vendors. One of them sells weapon mods the other sells armor mods. It seems simple enough however there are only 4 available per day from each
and which ones they are depend entirely on RNG.

*NOTE*
Mods can also be earned through random world drops as well and chests.

To check if a mod you still need is available you would need to login into the game and run to the vendor yourself or manually check one of the fan-made
websites that pull data from the API. I wanted a simpler solution and so developed this Bot.

![Banshee-44 shop](https://github.com/Dbevan770/destiny-mod-checker/tree/main/assets/Banshee-44.jpg "Merchant Banshee-44's Store")
*The merchant Banshee-44 who sells weapon mods for players*

![Ada-1 shop](https://github.com/Dbevan770/destiny-mod-checker/tree/main/assets/Ada-1.jpg "Merchant Ada-1's Store")
*The merchant Ada-1 who sells armor mods for players*


## What Does it Do?
The first step in the functionallity of the Bot is the tool *dimscraper.py*. This tool uses Selenium to open a Chrome browser and log the user into
Destiny Item Manager (DIM) a tool for managing your characters inventory. On this page the tool finds the list of all of the in-game mods and compiles
the list of those you are missing into a text file.

The second step is the Discord Bot itself. The Bot uses a .json (Soon to be an SQL database instead) of users to read their modfiles. Every day when the game has it's daily reset of vendors the Bot goes to another fan-made site *light.gg* and pulls that days vendor data. This data is compared to the user's list
of missing mods and if the vendor is selling one of them, a message is sent via Discord alerting the user they have new mods they can buy.

![Bot Message Example](https://github.com/Dbevan770/destiny-mod-checker/tree/main/assets/Bot-Message-Example.png "Bot Message Example")
*An example of the BOT sending an embedded message to a User on Discord through their direct messages(DMs).*

## How Many People Use it?
*Currently Serving: 3 Users*

Initially this was made only for me. Once my friends wanted to join it was re-written to support many more users. All that is required is that they use the dimscraper script and provide their Discord ID number to be added to the .json and the bot takes care of the rest.

# Technology Used
+ Selenium
+ CloudScraper
+ Discord.py
+ Asyncio
+ BeautifulSoup4
+ Python3
+ JSON

# Features
## Commands
+ !help (!h) - Get a list of the commands the Bot supports
+ !deletemods (!dm) - Inform the Bot you have purchased the mods that it alerted you about. These mods will be removed from your missing mods list
+ !undo (!u) - Undo previous deletion (Limited to up until the next daily reset)
+ !lostsector (!ls) - Get additional info about today's legendary lost sector -- *Currently in testing*
+ !xur (!x) - Get information about Xur - Agent of the Nine on the weekends
+ !admin (!a) - Check if you have admin priviliges -- *Admin commands coming soon!*

## WiP Commands
+ !change <context> - Allow admins to change aspects of the Bot without having to make code changes
+ !sendmsg <message> - Allow admins to send messages to users on behalf of the Bot
+ !delete <modName> - Allow user to manually delete a Mod (Or mods potentially) by specifying their name(s) to the Bot

## Additional Features -- Recently Added
+ Support for Xbox users in dimscraper.py has been added
+ Update message allows a message field detailing new features to be sent to users
+ !xur command will now send the user a message containing all armor stats currently being sold by him.
