import cloudscraper
import discord
import asyncio
import datetime
import json
import os
import sys
import users
import messagefield as mf
import botcommands as botcoms
import sendmessages as sm
import quotes as q
import generatelogs as logs
from bs4 import BeautifulSoup
from datetime import date
from dotenv import load_dotenv
from deletemods import deleteMods, undoDeletion as dm

# Globally create an empty string for Xur's location on the weekend.
XURLOCATION = ""

# Store the bots commands to be used for the !help command
COMMANDS = [botcoms.deletemods, botcoms.undo, botcoms.lost_sector, botcoms.xur, botcoms.comingsoon, botcoms.admin]

# Store Admin commands for the Bot
ADMIN_COMMANDS = []

# Globally declare lists to store the previous days Mods
# Due to Light.gg ocassionally not updating right away
# This allows me to verify that it has updated before
# sending Discord messages
prev_info = []

# Set log file variable to None
log = None

# This is the main tagline for the embeded message. Stored in a variable up here to make changing it easier
mod_desc = "It is another new day in Destiny 2! I have gone to the vendors to see if they have any of your missing Mods. Please see below for a list if there are any. I have also gone spelunking and found what today's Legendary Lost Sector is! Feel free to solo it for some awesome loot!"

# Global boolean to determine if the modchecker should run immediately one time during prod execution
runOnce = True

# Define what page we are accessing.
URL = "https://www.light.gg/"

# set up Discord bot client
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Store all created users for later
USERS = users.createUsers()

# Event for when a message is received
@client.event
async def on_message(message):

    # If the message is from the Bot just ignore it
    if message.author == client.user:
        return
    
    # If it is sent in a DM do stuff
    if isinstance(message.channel,discord.DMChannel):
        # Let me know a user sent a message and print the content
        log.AddLine(f"Received a message from a user: {message.author.name}...")
        log.AddLine(f"{message.content}")

        # If the user runs the help command send the embeded message with the
        # list of all available commands at the moment
        if message.content.lower() in ["!help", "!h"]:
            await sm.send_embed_msg(client, message.author.id, "Available Commands", "A list of all Destiny Bot's available commands", 0x5eb5ff, COMMANDS, log)

        if message.content.lower() in ["!lostsector", "!ls"]:
            await sm.send_embed_msg(client, message.author.id, "Legendary Lost Sector", "This command is only in testing. It doesn't do anything at the moment.", 0xffd700, [], log)

        if message.content.lower() in ["!xur", "!x"]:
            await sm.send_embed_msg(client, message.author.id, "Xûr", "Find out where Xûr is this weekend.", 0xffd700, [mf.MessageField("Location", f"Xûr is located at the {XURLOCATION}."), mf.MessageField("Items Available", "This is currently in testing. Please stay tuned!")], log)

        if message.content.lower() in ["!admin", "!a"]:
            log.AddLine(f"Checking if User: {message.author.name} ID: {message.author.id} is an Admin...")
            if users.checkIfAdmin(message.author.id):
                log.AddLine(f"IDs Match! User: {message.author.name} ID: {message.author.id} is an Admin!")
                await sm.send_msg(client, message.author.id, "You are an Admin! Don't do anything too crazy my friend!", log)
            elif not users.checkIfAdmin(message.author.id):
                log.AddLine(f"IDs Don't Match! User: {message.author.name} ID: {message.author.id} is not an Admin!")
                await sm.send_msg(client, message.author.id, "You are not an Admin.", log)
            else:
                log.AddLine(f"Error fetching Admin status for User: {message.author.name} ID: {message.author.id}")
                await sm.send_msg(client, message.author.id, "Failed to fetch Admin status. If this error persists please contact my creator.", log)

        # When a DM is received check which user it came from
        for user in USERS:
            # Once matched check if the User even has missing mods
            if message.author.id == user.id and user.hasMissingMods:
                # If the user has missing mods, wait for the delete command
                # and remove the mods from the users list
                if message.content.lower() in ["!deletemods", "!dm"] and not user.hasDeleted:
                    await sm.send_msg(client, user.id, "Okay, I will remove those mods from your list!", log)
                    dm.deleteMods(user)
                    user.hasDeleted = True
                    await sm.send_msg(client, user.id, "Successfully removed your Mods, if this was a mistake, say '!undo'.", log)
                    user.canUndo = True

                # The user can request 1 undo
                if message.content.lower() in ["!undo", "!u"] and user.canUndo:
                    await sm.send_msg(client, user.id, "Okay, I will undo the previous deletion!", log)
                    dm.undoDeletion(user)
                    user.canUndo = False

# Check the mods for the day to see if they are in the missing mod list
async def checkIfNew(user, weaponmods, armormods, lostsector):
    # Set what the names of the fields will be
    weapon_field = mf.MessageField("Banshee-44 Mods", "")
    armor_field = mf.MessageField("Ada-1 Mods", "")
    lostsector_field = mf.MessageField("Legendary Lost Sector", lostsector)
    with open("./modfiles/" + user.modfile, "r") as f:
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

async def checkIsWeekend():
    if datetime.datetime.today().weekday() >= 4 and datetime.datetime.today().weekday() <= 6:
        print("It's the weekend!")
        return True
    else:
        print("Another day in the office...")
        return False

# Go to Light.gg and scrape the website for Mods from Banshee-44 and Ada-1
# Also now looks for today's Legendary Lost Sector
async def getInfo(isWeekend):
    global XURLOCATION
    weapon_mods = []
    armor_mods = []
    lost_sector = ""

    page = await requestPage()
    if page[0] != 200:
        return [weapon_mods, armor_mods, lost_sector]

    lost_sector = await getLostSector(page[1])

    if isWeekend:
        log.AddLine("Getting Xur location info...")
        XURLOCATION = await getXurInfo(page[1])

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

    if isWeekend:
        return [weapon_mods, armor_mods, lost_sector, XURLOCATION]

    return [weapon_mods, armor_mods, lost_sector]

async def getXurInfo(page):
    soup = BeautifulSoup(page, "html.parser")

    spans = soup.find_all('span', class_="map-name")
    xur = []
    for span in spans[5]:
        if span.text.strip() != "":
            xur.append(span.text)

    return xur[1].strip()

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
    # Ensure proper scope of these variables
    global prev_info
    global mod_desc
    global log
    increment = 0
    log = None
    log = logs.LogFile(date.today().strftime("%Y%m%d") + ".log")

    # Testing mode for page requests
    if sys.argv[1] == "req-test":
        page = await requestPage()
        soup = BeautifulSoup(page[1], "html.parser")

        spans = soup.find_all('span', class_="map-name")
        xur = []
        for span in spans[5]:
            if span.text.strip() != "":
                xur.append(span.text.strip())

        print(xur[1])

    # Testing mode to test emebeded messages
    elif sys.argv[1] == "embed-test":
        await send_embed_msg(client, USERS[0].id, "Hello Guardian!", "This is an embeded message test!", 0x333333, [], log)

    # Bot runs in dev environment
    elif sys.argv[1] == "dev":
        isWeekend = False

        # Store yesterday's Mods
        isWeekend = await checkIsWeekend()

        if isWeekend:
            prev_info = [[],[],"",""]
        else:
            prev_info = [[],[], ""]

        print(prev_info)

        log.AddLine("Running script...")


        INFO = await getInfo(isWeekend)

        log.AddLine(f"Weapon Mods: {INFO[0]}")
        log.AddLine(f"Armor Mods: {INFO[1]}")
        log.AddLine(f"Legendary Lost Sector: {INFO[2]}")
        if isWeekend:
            log.AddLine(f"Xur Location: {prev_info[3]}")

        while not INFO or INFO == prev_info:
            log.AddLine("light.gg has not updated yet... Waiting 60s before trying again...")
            await asyncio.sleep(60)
            INFO = await getInfo(isWeekend)
            log.AddLine(f"Retrieved Weapon Mods: {INFO[0]}\n")
            log.AddLine(f"Retrieved Armor Mods: {INFO[1]}\n")
            log.AddLine(f"Retrieved Legendary Lost Sector: {INFO[2]}")
            log.AddLine(f"Previous Weapon Mods: {prev_info[0]}\n")
            log.AddLine(f"Previous Armor Mods: {prev_info[1]}\n")
            log.AddLine(f"Previous Armor Mods: {prev_info[2]}\n")

        log.AddLine("Successfully obtained available mods!")

        log.AddLine(f"Emptying Mod list for User: {str(USERS[0].id)}...")
        await users.clearUserData(USERS[0])

        fields = await checkIfNew(USERS[0], INFO[0], INFO[1], INFO[2])

        if datetime.datetime.today().weekday() == 1:
                    fields.append(mf.MessageField("Weekly Reset","Today is Tuesday which means there has been a weekly reset! Start grinding those pinacles Guardian. GM nightfalls won't get completed with your tiny light level!"))

        if isWeekend:
            fields.append(mf.MessageField("It's the weekend Baby!", f"Xûr has arrived at the {XURLOCATION} to bestow upon you some more disappointing items!"))

        await sm.send_embed_msg(client, USERS[0].id, "Hello Guardian!",  mod_desc, 0xafff5e, fields, log)

        await logs.generateLogfile(log.name + "_dev", log.data)

    # Bot runs in production environment
    elif sys.argv[1] == "prod":
        # Default to not the weekend
        isWeekend = False

        # Different switches for prod environment allows for customized arguments
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

            # Check if it is the weekend for Xur info
            isWeekend = await checkIsWeekend()

            # If the Bot has not been told to run immediately prepare to wait for next daily reset
            if not runOnce:
                prev_info = await getInfo(isWeekend)
                log.AddLine(f"Previous Weapon Mods: {prev_info[0]}")
                log.AddLine(f"Previous Armor Mods: {prev_info[1]}")
                log.AddLine(f"Previous Lost Sector: {prev_info[2]}")
                if isWeekend:
                    log.AddLine(f"Xur Location: {prev_info[3]}")

                # Check if users have deleted their mods 1 hour before the reset.
                await asyncio.sleep(seconds_until(17,0))
                for user in USERS:
                    if user.hasMissingMods and not user.hasDeleted:
                        log.AddLine(f"User: {user.id} has forgotten to delete their mods... Reminding them before the reset...")
                        await sm.send_msg(client, user.id, "Hello Guardian! The daily reset will happen in one hour and you haven't told me you purchased your mods yet. I'm just checking on you to make sure you haven't forgotten!", log)
                    else:
                        log.AddLine(f"User: {user.id} deleted their mods before reset! Huzzah!")

                log.AddLine("Waiting until next Daily Reset...")
                await asyncio.sleep(seconds_until(18,5))
            else:
                prev_info = [[],[], ""]

            # Beginning of the execution of the Bots main focus
            log.AddLine("Running script...")

            # Check again if it is the weekend since waiting
            isWeekend = await checkIsWeekend()

            # Gather the info on mods, lost sectors, and Xur if applicable
            INFO = await getInfo(isWeekend)
            log.AddLine(f"Weapon Mods: {INFO[0]}")
            log.AddLine(f"Armor Mods: {INFO[1]}")
            log.AddLine(f"Legendary Lost Sector: {INFO[2]}")
            if isWeekend:
                log.AddLine(f"Xur's Location: {INFO[3]}")

            # Check if the data pulled back is the same as yesterday's -- if it is, wait 60 seconds to see if light.gg updates
            while not INFO or (INFO[0] == prev_info[0] or INFO[1] == prev_info[1] or INFO[2] == prev_info[2]):
                if increment == 10:
                    for user in USERS:
                        await send_msg(client, user.id, "Looks like light.gg hasn't updated for at least 10 minutes... I'm still trying and I'll let you know when it is working!", log)

                log.AddLine("light.gg has not updated yet... Waiting 60s before trying again...")
                await asyncio.sleep(60)
                INFO = await getInfo(isWeekend)
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
                await users.clearUserData(user)

                fields = await checkIfNew(user, INFO[0], INFO[1], INFO[2])
                if datetime.datetime.today().weekday() == 1:
                    fields.append(mf.MessageField("Weekly Reset","Today is Tuesday which means there has been a weekly reset! Start grinding those pinacles Guardian. GM nightfalls won't get completed with your tiny light level!"))

                if isWeekend:
                    fields.append(mf.MessageField("It's the weekend Baby!", f"Xûr has arrived at the {XURLOCATION} to bestow upon you some more disappointing items!"))

                await sm.send_embed_msg(client, user.id, "Hello Guardian!",  mod_desc, 0xafff5e, fields, log)

            runOnce = False
            await logs.generateLogfile(log.name, log.data)
        
    elif sys.argv[1] == "check-admin":
        if users.checkIfAdmin(int(sys.argv[2])):
            print("User is an Admin!")
        else:
            print("User is not an Admin!")

    
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
    load_dotenv()
    client.run(os.getenv('DISCORD_TOKEN'))
