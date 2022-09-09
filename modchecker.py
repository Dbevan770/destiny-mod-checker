import requests
import discord
import datetime
import asyncio
from bs4 import BeautifulSoup
from discord.ext import tasks

class User:
    def __init__(self, _id, _modfile, _missingWeaponMods, _missingArmorMods, _hasMissingMods):
        self.id = _id
        self.modfile = _modfile
        self.missingWeaponMods = _missingWeaponMods
        self.missingArmorMods = _missingArmorMods
        self.hasMissingMods = _hasMissingMods

me = User(144421854629593088, "missingmods.txt", [], [], False)
jones = User(311998237034938368, "jones_missingmods.txt", [], [], False)

USERS = [me]

prev_weapon_mods = []
prev_armor_mods = []

URL = "https://www.light.gg/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

# set up Discord bot client
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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

    user.missingWeaponMods = []
    user.missingArmorMods = []

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if isinstance(message.channel,discord.DMChannel):
        if message.content.lower() == "run":
            asyncio.create_task(main())

        for user in USERS:
            if message.author.id == user.id and user.hasMissingMods:
                print(user.id, user.hasMissingMods)
                if message.content.lower() in ["yes", "y"]:
                    await send_msg(user.id, "Alrighty, I will remove those mods from your list!")
                    deleteMods(user)
                elif message.content.lower() in ["no", "n"]:
                    await send_msg(user.id, "Okay, I will not remove those mods from your list.")

# async function to send the message to each user
async def send_msg(id, message):
    target = await client.fetch_user(id)
    print("Messaging User: ", end='')
    print(target)
    print("\n")
    channel = await client.create_dm(target)

    await channel.send(message)

    print("Message sent!\n")

def checkIfNew(user, weaponmods, armormods):
    message = ""
    with open(user.modfile, "r") as f:
        for line in f:
            line = line.strip()
            if line in weaponmods:
                user.missingWeaponMods.append(line)
            elif line in armormods:
                user.missingArmorMods.append(line)


            
        f.close()

    if len(user.missingWeaponMods) == 0 and len(user.missingArmorMods) == 0:
        message = "No new Mods today!"
        user.hasMissingMods = False
        return message

    if len(user.missingWeaponMods) >= 1:
        index = 0
        message += "Banshee-44 has the following Mod(s) you are missing!:\n"
        for mod in weaponmods:
            if mod in user.missingWeaponMods:
                if index != len(user.missingWeaponMods) - 1:
                    message += mod + "\n"
                else:
                    message += mod

    message += "\n"

    if len(user.missingArmorMods) >= 1:
        index = 0
        message += "Ada-1 has the following Mod(s) you are missing!:\n"
        for mod in armormods:
            if mod in user.missingArmorMods:
                if index != len(user.missingArmorMods) - 1:
                    message += mod + "\n"
                else:
                    message += mod

    user.hasMissingMods = True
    return message



async def getWeaponMods():
    weapon_mods = []
    
    print("Getting Weapon Mods List from light.gg...\n")
    while weapon_mods == prev_weapon_mods:
        weapon_mods = []
        for weapon in soup.find_all('div', class_="weapon-mods"):
            img = weapon.find_all('img', alt=True)
            for i in range(0,4):
                weapon_mods.append(img[i]['alt'])
        if weapon_mods == prev_weapon_mods:
            print("Light.gg has not updated... Waiting 60 secs and trying again...\n")
            asyncio.sleep(60)
    
    prev_weapon_mods = weapon_mods
    return weapon_mods

async def getArmorMods():
    armor_mods = []
    
    print("Getting Armor Mods List from light.gg...\n")
    while armor_mods == prev_armor_mods:
        armor_mods = []
        for armor in soup.find_all('div', class_="armor-mods"):
            img = armor.find_all('img', alt=True)
            for i in range(0,4):
                armor_mods.append(img[i]['alt'])
        if armor_mods == prev_armor_mods:
            print("Light.gg has not updated... Waiting 60 secs and trying again...\n")
            asyncio.sleep(60)

    prev_armor_mods = armor_mods
    return armor_mods

async def main():
    while True:
        await asyncio.sleep(seconds_until(19,45))
        print("Running script...\n")
        WEAPON_MODS = await getWeaponMods()
        ARMOR_MODS = await getArmorMods()

        print("Successfully got latest mods from light.gg...\n")
        print(WEAPON_MODS, ARMOR_MODS)
        print("\n")

        for user in USERS:
            print("Emptying Mod list for User: " + str(user.id) + "...")
            user.missingWeaponMods = []
            user.missingArmorMods = []

            message = checkIfNew(user, WEAPON_MODS, ARMOR_MODS)

            print("Sending message!\n")

            print(message)

            await send_msg(user.id, message)

            if message != "No new Mods today!":
                await send_msg(user.id, "Did you buy these missing mods? (Yes/No)")
        await asyncio.sleep(60)

def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time) # days always >= 0

    return (future_exec - now).total_seconds()
        
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    await main()
    

if __name__ == "__main__":
    client.run('MTAxNjEwNTg2MTAzMjE5MDA3NA.GubahS.o4DXPRBpxsV3zNjC8mb_lvqI7xijksG2wFdDV0')
