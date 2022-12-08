import discord
import asyncio
import datetime
import random
import json
import os
import sys
import getopt
import users
import messagefield as mf
import botcommands as botcoms
import sendmessages as sm
import quotes as q
import generatelogs as logs
import pagerequest as pr
import getinfo as gi
from bs4 import BeautifulSoup
from datetime import date
from dotenv import load_dotenv
from deletemods import deleteMods, undoDeletion as dm

# Globally create an empty string for Xur's location on the weekend.
XURLOCATION = ""

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

        await botcoms.handleMessage(client, message.author.name, message.author.id, message, log, USERS)

# Check the mods for the day to see if they are in the missing mod list
async def checkIfNew(user, weaponmods, good_weapons, armormods, lostsector):
    # Set what the names of the fields will be
    weapon_field = mf.MessageField("Banshee-44 Mods", "")
    good_weapon_field = mf.MessageField("Banshee-44 S-Tier Weapons", "")
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
        if len(good_weapons) == 0:
            return [weapon_field, armor_field, lostsector_field]
        else:
            for weapon in good_weapons:
                good_weapon_field.value += weapon + "\n"

            return [weapon_field, good_weapon_field, armor_field, lostsector_field]

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
    if len(good_weapons) == 0:
        return [weapon_field, armor_field, lostsector_field]
    else:
        for weapon in good_weapons:
            good_weapon_field.value += weapon + "\n"

        return [weapon_field, good_weapon_field, armor_field, lostsector_field]

# Check if it is a weekend so we know to look for info on Xur
async def checkIsWeekend(log):
    # If day is currently between 4 (Friday) and 6 (Sunday)
    # ToDo: Add support for Monday until reset as well
    if datetime.datetime.today().weekday() >= 4 and datetime.datetime.today().weekday() <= 6:
        # Additional check on Fridays, Xur will not be around until the reset
        # We need to check if it is after the reset or not when run on Friday
        if datetime.datetime.today().weekday() == 4:
            if await isTimeBetween(datetime.time(18,00), datetime.time(23,59), datetime.datetime.now().time()):
                log.AddLine("It's the weekend!")
                return True
            else:
                return False
        else:
            log.AddLine("It's the weekend!")
            return True
    else:
        log.AddLine("Another day in the office...")
        return False

# Used to check if the current time is after daily reset time
# Useful for running the bot on a Friday when Xur is not around
async def isTimeBetween (startTime, endTime, nowTime):
    if startTime < endTime:
	    return nowTime >= startTime and nowTime <= endTime
    else:
	    return nowTime >= startTime or nowTime <= endTime


# Main loop of the program, executed on a timer every 24 hours
async def main():
    # Ensure proper scope of these variables
    global prev_info
    global mod_desc
    global log
    increment = 0
    log = None
    log = logs.LogFile(date.today().strftime("%Y%m%d") + ".log")
    mode = ""
    runOnce = False
    update = ""
    appendUpdate = False
    prev_info = []
    argv = sys.argv[1:]

    # Set up the command line switches for the program
    try:
        options, args = getopt.getopt(argv, "m:r:u:p:", ["mode =", "runOnce =", "update =", "prev ="])
    except Exception as e:
        print(e)

    # Get and store the values from all switches used
    for name, value in options:
        if name in ['-m', '--mode']:
            mode = value
        elif name in ['-r', '--runOnce']:
            runOnce = value
        elif name in ['-u', '--update']:
            update = value
            appendUpdate = True
        elif name in ['-p', '--prev']:
            prev = value
            prev_info = list(map(str, prev.strip("[]''").split(',')))

    # Testing mode for page requests
    if mode == "req-test":
        page = await pr.requestPage(log)
        soup = BeautifulSoup(page[1], "html.parser")

        weapon_mods = []
        armor_mods = []

        # Get a list of the divs containing weapon mods from the page
        for weapon in soup.find_all('div', class_="weapon-mods"):
            # The names for the mods are stored in the alt tags for the imgs
            imgs = weapon.find_all('img', alt=True, src=True)
            # Iterate through all 4 imgs
            for img in imgs:
                weapon_mods.append(img['alt'])

        # Get a list of the divs containing armor mods from the page
        for armor in soup.find_all('div', class_="armor-mods"):
            # The names for the mods are stored in the alt tags for the imgs
            imgs = armor.find_all('img', alt=True, src=True)
            # Iterate through all 4 imgs
            for img in imgs:
                armor_mods.append(img['alt'])

        print(weapon_mods, armor_mods)

    # Testing mode to test emebeded messages
    elif mode == "embed-test":
        await send_embed_msg(client, USERS[0].id, "Hello Guardian!", "This is an embeded message test!", 0x333333, [], log)

    # Bot runs in dev environment
    elif mode == "dev":
        isWeekend = False

        # Store yesterday's Mods
        isWeekend = await checkIsWeekend(log)

        if isWeekend:
            prev_info = [[],[],[],"",""]
        else:
            prev_info = [[],[],[], ""]

        print(prev_info)

        log.AddLine("Running script...")


        INFO = await gi.getInfo(isWeekend, log)

        log.AddLine(f"Weapon Mods: {INFO[0]}")
        log.AddLine(f"Good weapons: {INFO[1]}")
        log.AddLine(f"Armor Mods: {INFO[2]}")
        log.AddLine(f"Legendary Lost Sector: {INFO[3]}")
        if isWeekend:
            log.AddLine(f"Xur Location: {prev_info[4]}")

        while not INFO or INFO == prev_info:
            log.AddLine("light.gg has not updated yet... Waiting 60s before trying again...")
            await asyncio.sleep(60)
            INFO = await gi.getInfo(isWeekend, log)
            log.AddLine(f"Retrieved Weapon Mods: {INFO[0]}\n")
            log.AddLine(f"Retrieved Good Weapons: {INFO[1]}\n")
            log.AddLine(f"Retrieved Armor Mods: {INFO[2]}\n")
            log.AddLine(f"Retrieved Legendary Lost Sector: {INFO[3]}")
            log.AddLine(f"Previous Weapon Mods: {prev_info[0]}\n")
            log.AddLine(f"Previous Good Weapons: {prev_info[1]}\n")
            log.AddLine(f"Previous Armor Mods: {prev_info[2]}\n")
            log.AddLine(f"Previous Armor Mods: {prev_info[3]}\n")

        log.AddLine("Successfully obtained available mods!")

        log.AddLine(f"Emptying Mod list for User: {str(USERS[0].id)}...")
        await users.clearUserData(USERS[0])

        fields = await checkIfNew(USERS[0], INFO[0], INFO[1], INFO[2], INFO[3])

        if datetime.datetime.today().weekday() == 1:
                    fields.append(mf.MessageField("Weekly Reset","Today is Tuesday which means there has been a weekly reset! Start grinding those pinacles Guardian. GM nightfalls won't get completed with your tiny light level!"))

        if isWeekend:
            fields.append(mf.MessageField("It's the weekend Baby!", f"Xûr has arrived at the {XURLOCATION} to bestow upon you some more disappointing items!"))

        if appendUpdate:
            fields.append(mf.MessageField("What's New?", update))
            appendUpdate = False

        await sm.send_embed_msg(client, USERS[0].id, "Hello Guardian!",  mod_desc, 0xafff5e, fields, log)

        await logs.generateLogfile(log.name + "_dev", log.data)

    # Bot runs in production environment
    elif mode == "prod":
        # Default to not the weekend
        isWeekend = False

        while True:
            increment = 0
            # Can now run immediately at reset, due to the program waiting
            # 60 seconds if light.gg has not updated

            # Check if it is the weekend for Xur info
            isWeekend = await checkIsWeekend(log)

            # If the Bot has not been told to run immediately prepare to wait for next daily reset
            if not runOnce:
                prev_info = await gi.getInfo(isWeekend, log)
                log.AddLine(f"Previous Weapon Mods: {prev_info[0]}")
                log.AddLine(f"Previous Good Weapons: {prev_info[1]}")
                log.AddLine(f"Previous Armor Mods: {prev_info[2]}")
                log.AddLine(f"Previous Lost Sector: {prev_info[3]}")
                if isWeekend:
                    log.AddLine(f"Xur Location: {prev_info[4]}")

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
                if isWeekend:
                    prev_info = [[],[],[],"",""]
                else:
                    prev_info = [[],[],[], ""]

            # Beginning of the execution of the Bots main focus
            log.AddLine("Running script...")

            # Check again if it is the weekend since waiting
            isWeekend = await checkIsWeekend(log)

            # Gather the info on mods, lost sectors, and Xur if applicable
            INFO = await gi.getInfo(isWeekend, log)
            log.AddLine(f"Weapon Mods: {INFO[0]}")
            log.AddLine(f"Good Weapons: {INFO[1]}")
            log.AddLine(f"Armor Mods: {INFO[2]}")
            log.AddLine(f"Legendary Lost Sector: {INFO[3]}")
            if isWeekend:
                log.AddLine(f"Xur's Location: {INFO[4]}")

            # Check if the data pulled back is the same as yesterday's -- if it is, wait 60 seconds to see if light.gg updates
            while not INFO or (INFO[0] == prev_info[0] or INFO[2] == prev_info[2] or INFO[3] == prev_info[3]):
                if increment == 10:
                    for user in USERS:
                        await sm.send_msg(client, user.id, "Looks like light.gg hasn't updated for at least 10 minutes... I'm still trying and I'll let you know when it is working!", log)

                log.AddLine("light.gg has not updated yet... Waiting 60s before trying again...")
                await asyncio.sleep(60)
                INFO = await gi.getInfo(isWeekend, log)
                log.AddLine(f"Retrieved Weapon Mods: {INFO[0]}")
                log.AddLine(f"Retrieved Good Weapons: {INFO[1]}")
                log.AddLine(f"Retrieved Armor Mods: {INFO[2]}")
                log.AddLine(f"Retrieved Legendary Lost Sector: {INFO[3]}")
                log.AddLine(f"Previous Weapon Mods: {prev_info[0]}")
                log.AddLine(f"Previous Good Weapons: {prev_info[1]}")
                log.AddLine(f"Previous Armor Mods: {prev_info[2]}")
                log.AddLine(f"Previous Lost Sector Mods: {prev_info[3]}")
                increment = increment + 1

            log.AddLine("Successfully obtained information from light.gg!")
            
            for user in USERS:
                log.AddLine(f"Emptying Mod list for User: {str(user.id)}...")
                await users.clearUserData(user)

                fields = await checkIfNew(user, INFO[0], INFO[1], INFO[2], INFO[3])
                if datetime.datetime.today().weekday() == 1:
                    fields.append(mf.MessageField("Weekly Reset","Today is Tuesday which means there has been a weekly reset! Start grinding those pinacles Guardian. GM nightfalls won't get completed with your tiny light level!"))

                if isWeekend:
                    fields.append(mf.MessageField("It's the weekend Baby!", f"Xûr has arrived at the {XURLOCATION} to bestow upon you some more disappointing items!"))

                if appendUpdate:
                    fields.append(mf.MessageField("What's New?", update))
                    appendUpdate = False

                await sm.send_embed_msg(client, user.id, "Hello Guardian!",  mod_desc, 0xafff5e, fields, log)

            runOnce = False
            await logs.generateLogfile(log.name, log.data)
        
    elif mode == "check-admin":
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
