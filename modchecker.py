import cloudscraper
import discord
import asyncio
import random
import datetime
import json
import os
from bs4 import BeautifulSoup
from datetime import date
import sys

# Define the User constructor, allows the program to be more expandable
# I can add more attributes or even methods down the line if necessary
class User:
    def __init__(self, _id, _modfile, _missingWeaponMods, _missingArmorMods, _hasMissingMods, _hasDeleted, _canUndo):
        self.id = _id
        self.modfile = _modfile
        self.missingWeaponMods = _missingWeaponMods
        self.missingArmorMods = _missingArmorMods
        self.hasMissingMods = _hasMissingMods
        self.hasDeleted = _hasDeleted
        self.canUndo = _canUndo

class MessageField:
    def __init__(self, _name, _value):
        self.name = _name
        self.value = _value

class LogFile:
    data = []
    def __init__(self, _name):
        self.name = _name

    @classmethod
    def AddLine(cls, line):
        print(f'{line}\n')
        LogFile.data.append([datetime.datetime.now(), line])

deletemods = MessageField("!deletemods", "Use this to tell Destiny Bot that you bought your missing mods and have it remove them from your list")
undo = MessageField("!undo", "Use this command to undo a mod deletion. (Can only be used once)")
lost_sector = MessageField("!lostsector", "Use this command to get more details about today's Legendary Lost Sector!")
xur = MessageField("!xur", "Use this command to see where Xûr is this weekend!")
comingsoon = MessageField("Coming Soon!", "More commands are coming soon! Keep an eye out for more QoL changes...")

COMMANDS = [deletemods, undo, lost_sector, xur, comingsoon]
QUOTES = []

# Globally declare lists to store the previous days Mods
# Due to Light.gg ocassionally not updating right away
# This allows me to verify that it has updated before
# sending Discord messages
prev_info = []
log = None

mod_desc = "It is another new day in Destiny 2! I have gone to the vendors to see if they have any of your missing Mods. Please see below for a list if there are any. I have also gone spelunking and found what today's Legendary Lost Sector is! Feel free to solo it for some awesome loot!"

runOnce = True

# Define what page we are accessing and define the webscraper
URL = "https://www.light.gg/"

# set up Discord bot client
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def getQuote(quotes):
    random_num = random.randint(0, 23)

    quote = quotes[random_num][0]
    author = quotes[random_num][1]

    return f"“{quote}” - {author}"

# Create users from JSON file rather than store their details in plaintext
def createUsers():
    users = []
    with open('users.json') as data_file:
        data = json.load(data_file)

    for user in data:
        temp_usr = User(user['id'], user['modfile'], user['missingWeaponMods'], user['missingArmorMods'], user['hasMissingMods'], user['hasDeleted'], user['canUndo'])
        users.append(temp_usr)

    data_file.close()
    return users

# Store all created users for later
USERS = createUsers()

# Generates the log file at the end of each day
async def generateLogfile(name, data):
    # Stores the filepath to where logs will be kept
    filepath = os.path.join('./logs/', name)

    # Create the new log file and begin writing data to it
    with open(filepath, "w") as f:
        index = 0
        for line in data:
            if index != len(data) - 1:
                f.write(f'[{line[0].strftime("%Y-%m-%d %H:%M:%S")}] {line[1]}')
                f.write("\n")
                index = index + 1
            else:
                f.write(f'[{line[0].strftime("%Y-%m-%d %H:%M:%S")}] {line[1]}')
    
    f.close()

# Function to delete the Mods of the day from the Users
# Missing Mods list.
def deleteMods(user):
    with open(user.modfile, "r") as f:
        lines = f.readlines()
    with open(user.modfile, "w") as f:
        for line in lines:
            if line.strip("\n") in user.missingWeaponMods:
                continue
            elif line.strip("\n") in user.missingArmorMods:
                continue
            else:
                f.write(line)
    f.close()

# If the User mistakingly replied Yes and deleted Mods from their
# list they can Undo once
def undoDeletion(user):
    with open(user.modfile, "a") as f:
        for mod in user.missingWeaponMods:
            f.write("\n")
            f.write(mod)
        for mod in user.missingArmorMods:
            f.write("\n")
            f.write(mod)

# Event for when a message is received
@client.event
async def on_message(message):

    # If the message is from the Bot just ignore it
    if message.author == client.user:
        return
    
    # If it is sent in a DM do stuff
    if isinstance(message.channel,discord.DMChannel):
        # Let me know a user sent a message and print the content
        log.AddLine(f"Received a message from a user: {message.author}...")
        log.AddLine(f"{message.content}")

        # If the user runs the help command send the embeded message with the
        # list of all available commands at the moment
        if message.content.lower() in ["!help", "!h"]:
            await send_embed_msg(message.author.id, "Available Commands", "A list of all Destiny Bot's available commands", 0x5eb5ff, COMMANDS)

        if message.content.lower() in ["!lostsector", "!ls"]:
            await send_embed_msg(message.author.id, "Legendary Lost Sector", "This command is only in testing. It doesn't do anything at the moment.", 0xffd700, [])

        if message.content.lower() in ["!xur", "!x"]:
            await send_embed_msg(message.author.id, "Xûr", "Find out where Xûr is this weekend.", 0xffd700, [MessageField("Location", "Xûr is located on Uranus nerd. Get fucked."), MessageField("Items Available", "This is currently in testing, do not be offended by the above message.")])

        # When a DM is received check which user it came from
        for user in USERS:
            # Once matched check if the User even has missing mods
            if message.author.id == user.id and user.hasMissingMods:
                # If the user has missing mods, wait for the delete command
                # and remove the mods from the users list
                if message.content.lower() in ["!deletemods", "!dm"] and not user.hasDeleted:
                    await send_msg(user.id, "Okay, I will remove those mods from your list!")
                    deleteMods(user)
                    user.hasDeleted = True
                    await send_msg(user.id, "Successfully removed your Mods, if this was a mistake, say '!undo'.")
                    user.canUndo = True

                # The user can request 1 undo
                if message.content.lower() in ["!undo", "!u"] and user.canUndo:
                    await send_msg(user.id, "Okay, I will undo the previous deletion!")
                    undoDeletion(user)
                    user.canUndo = False

# async function to send the message to each user
async def send_msg(id, message):
    target = await client.fetch_user(id)
    log.AddLine(f"Messaging User: {target} with '{message}'...")
    channel = await client.create_dm(target)

    await channel.send(message)

    log.AddLine("Message sent!")

# Send an embeded message to the user
async def send_embed_msg(id, title, desc, color, fields):
    # Get todays date
    today = date.today()
    # Get the user data from their id
    target = await client.fetch_user(id)
    #print(f"Sending Embeded Message to user: {target}...\n")
    log.AddLine(f"Sending Embeded Message to user: {target}...")
    # Stores the DM channel for the user to send a DM
    channel = await client.create_dm(target)

    # Create embeded Message template
    embedMsg = discord.Embed(title=title, description=desc, color=color)
    embedMsg.set_author(name=today.strftime("%B %d %Y"))

    # Create all necessary fields and input their values
    if len(fields) > 0:
        for field in fields:
            embedMsg.add_field(name=field.name, value=field.value, inline=False)
    
    # Add footer to each embeded message
    embedMsg.set_footer(text=f"{getQuote(QUOTES)}\n\nAll data is taken from light.gg\nTo see a list of all my commands say '!help'")

    await channel.send(embed=embedMsg)

async def clearUserData(user):
    user.missingWeaponMods = []
    user.missingArmorMods = []
    user.hasMissingMods = False
    user.hasDeleted = False
    user.canUndo = False

# Check the mods for the day to see if they are in the missing mod list
async def checkIfNew(user, weaponmods, armormods, lostsector):
    # Set what the names of the fields will be
    weapon_field = MessageField("Banshee-44 Mods", "")
    armor_field = MessageField("Ada-1 Mods", "")
    lostsector_field = MessageField("Legendary Lost Sector", lostsector)
    with open(user.modfile, "r") as f:
        for line in f:
            line = line.strip()
            if line in weaponmods:
                user.missingWeaponMods.append(line)
            elif line in armormods:
                user.missingArmorMods.append(line)
           
    f.close()

    if len(user.missingWeaponMods) == 0 and len(user.missingArmorMods) == 0:
        if random.randint(0,9) == 0:
            weapon_field.value = "Ain't got shit!"
            armor_field.value = "Bitch better have my mods tomorrow!"
        else:
            weapon_field.value = "No New Mods Today!"
            armor_field.value = "No New Mods Today!"
        user.hasMissingMods = False
        return [weapon_field, armor_field, lostsector_field]

    if len(user.missingWeaponMods) >= 1:
        index = 0
        for mod in weaponmods:
            if mod in user.missingWeaponMods:
                if index != len(user.missingWeaponMods) - 1:
                    weapon_field.value += mod + "\n"
                else:
                    weapon_field.value += mod
    elif len(user.missingWeaponMods) == 0:
        weapon_field.value = "No New Mods Today!"

    if len(user.missingArmorMods) >= 1:
        index = 0
        for mod in armormods:
            if mod in user.missingArmorMods:
                if index != len(user.missingArmorMods) - 1:
                    armor_field.value += mod + "\n"
                else:
                    armor_field.value += mod
    elif len(user.missingArmorMods) == 0:
        armor_field.value = "No New Mods Today!"

    user.hasMissingMods = True
    return [weapon_field, armor_field, lostsector_field]

# Go to Light.gg and scrape the website for Mods from Banshee-44 and Ada-1
# Also now looks for today's Legendary Lost Sector
async def getInfo():
    weapon_mods = []
    armor_mods = []
    lost_sector = ""

    page = await requestPage()
    if page[0] != 200:
        return [weapon_mods, armor_mods, lost_sector]

    lost_sector = await getLostSector(page[1])

    if lost_sector == "":
        return [weapon_mods, armor_mods, lost_sector]

    soup = BeautifulSoup(page[1], "html.parser")

    log.AddLine("Getting available Mods from light.gg...")
    for weapon in soup.find_all('div', class_="weapon-mods"):
        img = weapon.find_all('img', alt=True, src=True)
        for i in range(0,4):
            weapon_mods.append(img[i]['alt'])
    
    for armor in soup.find_all('div', class_="armor-mods"):
        img = armor.find_all('img', alt=True, src=True)
        for i in range(0,4):
            armor_mods.append(img[i]['alt'])

    return [weapon_mods, armor_mods, lost_sector]

async def getLostSector(page):

    log.AddLine("Getting Lost Sector Name from light.gg...")
    soup = BeautifulSoup(page, "html.parser")

    div = soup.find("div", {'class':'legend-rewards'})
    if div == None:
        return ""
    else:
        h3 = div.findChild("h3")
        ls = h3.findAll(text=True)
        return ls[0]


async def requestPage():
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )
    page = scraper.get(URL)
    page_content = page.text
    log.AddLine(f"Response from light.gg: {page.status_code}")
    if page.status_code != 200:
        return [page.status_code, "Failed to fetch page."]
    else:
        return [page.status_code, page_content]

# Main loop of the program, executed on a timer every 24 hours
async def main():
    # Ensure proper scope of this variable
    global prev_info
    global mod_desc
    global log
    global QUOTES
    with open("quotes.json") as quote_file:
        data = json.load(quote_file)
    QUOTES = list(data.items())
    quote_file.close()
    increment = 0
    log = None
    log = LogFile(date.today().strftime("%Y%m%d") + ".log")

    if sys.argv[1] == "req-test":
        page = await requestPage(log)
        soup = BeautifulSoup(page.content, "html.parser")

        for armor in soup.find_all('div', class_="armor-mods"):
            img = armor.find_all('img', alt=True)
            for i in range(0,4):
                print(img[i]['alt'])

    elif sys.argv[1] == "embed-test":
        await send_embed_msg(USERS[0].id, "Hello Guardian!", "This is an embeded message test!", 0x333333, [])

    elif sys.argv[1] == "dev":
        # Store yesterday's Mods
        prev_info = [[],[], ""]

        print(prev_info)

        log.AddLine("Running script...")

        INFO = await getInfo()

        log.AddLine(f"Weapon Mods: {INFO[0]}")
        log.AddLine(f"Armor Mods: {INFO[1]}")
        log.AddLine(f"Legendary Lost Sector: {INFO[2]}")

        while not INFO or INFO == prev_info:
            log.AddLine("light.gg has not updated yet... Waiting 60s before trying again...")
            await asyncio.sleep(60)
            INFO = await getInfo()
            log.AddLine(f"Retrieved Weapon Mods: {INFO[0]}\n")
            log.AddLine(f"Retrieved Armor Mods: {INFO[1]}\n")
            log.AddLine(f"Retrieved Legendary Lost Sector: {INFO[2]}")
            log.AddLine(f"Previous Weapon Mods: {prev_info[0]}\n")
            log.AddLine(f"Previous Armor Mods: {prev_info[1]}\n")
            log.AddLine(f"Previous Armor Mods: {prev_info[2]}\n")

        log.AddLine("Successfully obtained available mods!")

        log.AddLine(f"Emptying Mod list for User: {str(USERS[0].id)}...")
        await clearUserData(USERS[0])

        fields = await checkIfNew(USERS[0], INFO[0], INFO[1], INFO[2])

        if datetime.datetime.today().weekday() == 1:
                    fields.append(MessageField("Weekly Reset","Today is Tuesday which means there has been a weekly reset! Start grinding those pinacles Guardian. GM nightfalls won't get completed with your tiny light level!"))

        await send_embed_msg(USERS[0].id, "Hello Guardian!",  mod_desc, 0xafff5e, fields)

        await generateLogfile(log.name, log.data)

    elif sys.argv[1] == "prod":
        if len(sys.argv) > 3:
            if sys.argv[2] == "-r":
                runOnce = True
                prev_info = list(sys.argv[3], sys.argv[4], sys.argv[5])
        elif len(sys.argv) == 3:
            if sys.argv[2] == "-r":
                runOnce = True
        else:
            runOnce = False

        while True:
            increment = 0
            # Can now run immediately at reset, due to the program waiting
            # 60 seconds if light.gg has not updated

            # Store yesterday's Mods
            if not runOnce:
                prev_info = await getInfo()
                log.AddLine(f"Previous Weapon Mods: {prev_info[0]}")
                log.AddLine(f"Previous Armor Mods: {prev_info[1]}")
                log.AddLine(f"Previous Lost Sector: {prev_info[2]}")

                # Check if users have deleted their mods 1 hour before the reset.
                await asyncio.sleep(seconds_until(17,0))
                for user in USERS:
                    if user.hasMissingMods and not user.hasDeleted:
                        log.AddLine(f"User: {user.id} has forgotten to delete their mods... Reminding them before the reset...")
                        await send_msg(user.id, "Hello Guardian! The daily reset will happen in one hour and you haven't told me you purchased your mods yet. I'm just checking on you to make sure you haven't forgotten!")
                    else:
                        log.AddLine(f"User: {user.id} deleted their mods before reset! Huzzah!")

                log.AddLine("Waiting until next Daily Reset...")
                await asyncio.sleep(seconds_until(18,5))
            else:
                prev_info = [[],[], ""]

            log.AddLine("Running script...")

            INFO = await getInfo()
            log.AddLine(f"Weapon Mods: {INFO[0]}")
            log.AddLine(f"Armor Mods: {INFO[1]}")
            log.AddLine(f"Legendary Lost Sector: {INFO[2]}")

            while not INFO or (INFO[0] == prev_info[0] or INFO[1] == prev_info[1] or INFO[2] == prev_info[2]):
                if increment == 10:
                    for user in USERS:
                        await send_msg(user.id, "Looks like light.gg hasn't updated for at least 10 minutes... I'm still trying and I'll let you know when it is working!")

                log.AddLine("light.gg has not updated yet... Waiting 60s before trying again...")
                await asyncio.sleep(60)
                INFO = await getInfo()
                log.AddLine(f"Retrieved Weapon Mods: {INFO[0]}")
                log.AddLine(f"Retrieved Armor Mods: {INFO[1]}")
                log.AddLine(f"Retrieved Legendary Lost Sector: {INFO[2]}")
                log.AddLine(f"Previous Weapon Mods: {prev_info[0]}")
                log.AddLine(f"Previous Armor Mods: {prev_info[1]}")
                log.AddLine(f"Previous Lost Sector Mods: {prev_info[2]}")
                increment = increment + 1

            log.AddLine("Successfully obtained information from light.gg!")
            
            for user in USERS:
                log.AddLine(f"Emptying Mod list for User: {str(user.id)}...")
                await clearUserData(user)

                fields = await checkIfNew(user, INFO[0], INFO[1], INFO[2])
                if datetime.datetime.today().weekday() == 1:
                    fields.append(MessageField("Weekly Reset","Today is Tuesday which means there has been a weekly reset! Start grinding those pinacles Guardian. GM nightfalls won't get completed with your tiny light level!"))

                if datetime.datetime.today().weekday() >= 4 or datetime.datetime.today().weekday() <= 6:
                    fields.append(MessageField("Xûr has arrived to bestow upon you some more disappointing items!"))

                await send_embed_msg(user.id, "Hello Guardian!",  mod_desc, 0xafff5e, fields)

            runOnce = False
            await generateLogfile(log.name, log.data)

    elif sys.argv[1] == "annoy":
        log.AddLine(f"Annoying Sully with message...")
        await send_embed_msg(USERS[2].id, "Hello Guardian!", "I noticed you still haven't gotten on to play Destiny 2. I am here to remind you that you should come check it out!", 0xa83232, [])

    elif sys.argv[1] == "user-test":
        for user in USERS:
            print(user.id)
            print(user.modfile)

    elif sys.argv[1] == "log-test":
        log.AddLine("This is a log file test.")
        log.AddLine("If this works I should see these lines printed.")
        log.AddLine("The log file should also be created in the logs directory.")
        log.AddLine(f"Received message from user {USERS[0].id}")
        await generateLogfile(log.name, log.data)

    elif sys.argv[1] == "quote-test":
        print(getQuote(QUOTES))

    elif sys.argv[1] == "ls-test":
        page = await requestPage()
        
        print(await getLostSector(page))

    elif sys.argv[1] == "message-users":
        for user in USERS:
            await send_msg(user.id, sys.argv[2])
    
# Function that pauses execution of the main loop until a certain time day
def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time) # days always >= 0

    return (future_exec - now).total_seconds()

# What does the bot do as soon as it is ready?    
@client.event
async def on_ready():
    print(f'\nWe have logged in as {client.user}\n')

    await main()
    
# Run the client and connect it to Discord
if __name__ == "__main__":
    client.run('MTAxNjEwNTg2MTAzMjE5MDA3NA.GubahS.o4DXPRBpxsV3zNjC8mb_lvqI7xijksG2wFdDV0')
