import requests
import discord
import datetime
import asyncio
from bs4 import BeautifulSoup
from discord.ext import tasks
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

# Create User objects, in the future this could be pulled from a JSON
# and made to be done from a "server" rather than my RPi locally
me = User(144421854629593088, "missingmods.txt", [], [], False, False, False)
jones = User(311998237034938368, "jones_missingmods.txt", [], [], False, False, False)
sully = User(843589494338617354, "", [], [], False, False, False)

deletemods = MessageField("!deletemods", "Use this to tell Destiny Bot that you bought your missing mods and have it remove them from your list")
undo = MessageField("!undo", "Use this command to undo a mod deletion. (Can only be used once)")
comingsoon = MessageField("Coming Soon!", "More commands are coming soon! Keep an eye out for more QoL changes...")

COMMANDS = [deletemods, undo, comingsoon]

# Define what users to run the script with
USERS = [me, jones]

# Globally declare lists to store the previous days Mods
# Due to Light.gg ocassionally not updating right away
# This allows me to verify that it has updated before
# sending Discord messages
prev_mods = []

mod_desc = "I went to the vendors today to check if they have any of your missing Mods. Please see below for my comprehensive list!"

runOnce = True

# Define what page we are accessing and define the webscraper
URL = "https://www.light.gg/"

# set up Discord bot client
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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
        print(f"Received a message from a user with missing mods: {message.author}...\n")
        print(message.content)

        if message.content.lower() in ["!help", "!h"]:
            await send_embed_msg(message.author.id, "Available Commands", "A list of all Destiny Bot's available commands", 0x5eb5ff, COMMANDS)

        # When a DM is received check which user it came from
        for user in USERS:
            # Once matched check if the User even has missing mods
            if message.author.id == user.id and user.hasMissingMods:
                # If the user replies with yes delete the new mods from the list
                # Otherwise just reply no
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
    print(f"Messaging User: {target}")
    channel = await client.create_dm(target)

    await channel.send(message)

    print("Message sent!\n")

# Send an embeded message to the user
async def send_embed_msg(id, title, desc, color, fields):
    # Get todays date
    today = date.today()
    # Get the user data from their id
    target = await client.fetch_user(id)
    print(f"Sending Embeded Message to user: {target}...\n")
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
    embedMsg.set_footer(text="All data is taken from light.gg\nTo see a list of all my commands say '!help'")

    await channel.send(embed=embedMsg)

# Check the mods for the day to see if they are in the missing mod list
def checkIfNew(user, weaponmods, armormods):
    weapon_field = MessageField("Banshee-44 Mods", "")
    armor_field = MessageField("Ada-1 Mods", "")
    with open(user.modfile, "r") as f:
        for line in f:
            line = line.strip()
            if line in weaponmods:
                user.missingWeaponMods.append(line)
            elif line in armormods:
                user.missingArmorMods.append(line)


            
        f.close()

    if len(user.missingWeaponMods) == 0 and len(user.missingArmorMods) == 0:
        weapon_field.value = "No New Mods Today!"
        armor_field.value = "No New Mods Today!"
        user.hasMissingMods = False
        return [weapon_field, armor_field]

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
    return [weapon_field, armor_field]

# Go to Light.gg and scrape the website for Mods from Banshee-44 and Ada-1
async def getMods():
    weapon_mods = []
    armor_mods = []

    page = await requestPage()
    if page.status_code != 200:
        return [weapon_mods, armor_mods]

    soup = BeautifulSoup(page.content, "html.parser")

    print("Getting available Mods from light.gg...\n")
    for weapon in soup.find_all('div', class_="weapon-mods"):
        img = weapon.find_all('img', alt=True)
        for i in range(0,4):
            weapon_mods.append(img[i]['alt'])
    
    for armor in soup.find_all('div', class_="armor-mods"):
        img = armor.find_all('img', alt=True)
        for i in range(0,4):
            armor_mods.append(img[i]['alt'])

    return [weapon_mods, armor_mods]

async def requestPage():
    page = []
    page = requests.get(URL)

    return page

# Main loop of the program, executed on a timer every 24 hours
async def main():
    # Ensure proper scope of this variable
    global prev_mods
    global mod_desc
    increment = 0

    match sys.argv[1]:
        case "req-test":
            page = await requestPage()
            soup = BeautifulSoup(page.content, "html.parser")

            for armor in soup.find_all('div', class_="armor-mods"):
                img = armor.find_all('img', alt=True)
                for i in range(0,4):
                    print(img[i]['alt'])
        case "embed-test":
            await send_embed_msg(USERS[0].id)
        case "dev":
            # Store yesterday's Mods
            prev_mods = [[],[]]

            print(prev_mods)

            print("Running script...\n")

            MODS = await getMods()
            print(f"Weapon Mods: {MODS[0]}\n")
            print(f"Armor Mods: {MODS[1]}\n")

            while not MODS or MODS == prev_mods:
                print("light.gg has not updated yet... Waiting 60s before trying again...\n")
                await asyncio.sleep(60)
                MODS = await getMods()
                print(MODS, prev_mods)

            print("Successfully obtained available mods!\n")

            for user in USERS:
                print(f"Emptying Mod list for User: {str(user.id)}...")
                user.missingWeaponMods = []
                user.missingArmorMods = []

                fields = checkIfNew(user, MODS[0], MODS[1])

                await send_embed_msg(user.id, "Hello Guardian!",  mod_desc, 0xafff5e, fields)
        case "prod":
            if len(sys.argv) == 3:
                if sys.argv[2] == "-r":
                    runOnce = True
            else:
                runOnce = False

            while True:
                # Can now run immediately at reset, due to the program waiting
                # 60 seconds if light.gg has not updated

                # Store yesterday's Mods
                if not runOnce:
                    prev_mods = await getMods()
                    print(f"Previous Weapon Mods: {prev_mods[0]}\n")
                    print(f"Previous Armor Mods: {prev_mods[1]}\n")
                    print("Waiting until next Daily Reset...")
                    await asyncio.sleep(seconds_until(19,5))
                else:
                    prev_mods = [[],[]]

                print("Running script...\n")

                MODS = await getMods()
                print(f"Weapon Mods: {MODS[0]}\n")
                print(f"Armor Mods: {MODS[1]}\n")

                while not MODS or MODS == prev_mods:
                    if increment == 10:
                        for user in USERS:
                            await send_msg(user.id, "Looks like light.gg hasn't updated for at least 10 minutes... I'm still trying and I'll let you know when it is working!")

                    print("light.gg has not updated yet... Waiting 60s before trying again...\n")
                    await asyncio.sleep(60)
                    MODS = await getMods()
                    print(MODS, prev_mods)
                    increment = increment + 1

                print("Successfully obtained available mods!\n")

                for user in USERS:
                    print(f"Emptying Mod list for User: {str(user.id)}...")
                    user.missingWeaponMods = []
                    user.missingArmorMods = []

                    fields = checkIfNew(user, MODS[0], MODS[1])

                    await send_embed_msg(user.id, "Hello Guardian!",  mod_desc, 0xafff5e, fields)

                runOnce = False
        case "annoy":
            print(f"Annoying Sully with message...\n")
            await send_embed_msg(sully.id, "Hello Guardian!", "I noticed you still haven't gotten on to play Destiny 2. I am here to remind you that you should come check it out!", 0xa83232, [])
        case _:
            print("You input the wrong argument. Please try again.")

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
    print(f'We have logged in as {client.user}\n')

    await main()
    
# Run the client and connect it to Discord
if __name__ == "__main__":
    client.run('MTAxNjEwNTg2MTAzMjE5MDA3NA.GubahS.o4DXPRBpxsV3zNjC8mb_lvqI7xijksG2wFdDV0')