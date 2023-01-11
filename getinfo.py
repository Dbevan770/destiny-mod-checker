import pagerequest as pr
import timekeeper as tk
import messagefield as mf
import datetime
from bs4 import BeautifulSoup
from datetime import date
import re

lost_sector_rota = ['K1 Logistics (Moon)', 'K1 Crew Quarters (Moon)', 'K1 Revelation (Moon)', 'K1 Communion (Moon)', 'Bunker E15 (Europa)', 'Concealed Void (Europa)', 'Perdition (Europa)', 'Sepulcher (Throne World)', 'Extraction (Throne World)', 'Chamber of Starlight (Dreaming City)', "Aphelion's Rest (Dreaming City)"]
rewards_rota = ['Chest', 'Head', 'Legs', 'Arms']

async def getBansheeMods(soup, log):
    weapon_mods = []

    # Get a list of the divs containing weapon mods from the page
    for weapon in soup.find_all('div', class_="weapon-mods"):
        # The names for the mods are stored in the alt tags for the imgs
        imgs = weapon.find_all('img', alt=True, src=True)
        # Iterate through all 4 imgs
        for img in imgs:
            weapon_mods.append(img['alt'])

    return weapon_mods

# Gets a list of S-Tier weapons that Banshee-44 is selling today
async def getSTierBansheeWeapons(soup, log):
    # Create empty array
    good_weps = []

    # Find the weapon div that contains all the weapons he is selling
    for weapon in soup.find_all('div', class_="weapons"):
        # Find the spans that have class names reward-<number>
        # This is all of the weapons themselves
        spans = weapon.find_all('span', attrs={'class' : re.compile('^rewards-*')})
        # Inside these spans get the imgs
        for span in spans:
            imgs = span.find_all('img', alt=True, src=True)
            # Create empty array to store the pair of
            # <Weapon Name> : <Popularity>
            img_pair = []
            for img in imgs:
                if not img['alt'] == "":
                    img_pair.append(img['alt'])
            
            # If the weapon has a popularity check if it is S
            # If it is, store it in the good weapons array
            if len(img_pair) == 2:
                if img_pair[1] == "Very Popular (S)":
                    good_weps.append(img_pair[0])
            else:
                continue

    return good_weps


# Go to Light.gg and scrape the website for Mods from Banshee-44 and Ada-1
# Also now looks for today's Legendary Lost Sector
async def getInfo(isWeekend, log):
    # Define scope of variables
    XURLOCATION = ""
    armor_mods = []
    lost_sector = []

    # Request the page content from light.gg
    page = await pr.requestPage(log)

    # If the page is returned with anything but a 200 code we didn't
    # get anything back. Return the same data so the page request runs
    # again
    if page[0] != 200:
        return [weapon_mods, armor_mods, lost_sector]

    # Get the lost sector info from the page
    log.AddLine("Getting Lost Sector Name from light.gg...")
    lost_sector = await getLostSectorLocal(log)

    # If it is the weekend get the Xur info from the page
    if isWeekend:
        log.AddLine("Getting Xur location info...")
        XURLOCATION = await getXurInfo(page[1], log)

    # Define the beautiful soup html parser for the page
    soup = BeautifulSoup(page[1], "html.parser")

    log.AddLine("Getting available Mods from light.gg...")

    weapon_mods = await getBansheeMods(soup, log)

    good_weapons = await getSTierBansheeWeapons(soup, log)

    # Get a list of the divs containing armor mods from the page
    for armor in soup.find_all('div', class_="armor-mods"):
        # The names for the mods are stored in the alt tags for the imgs
        img = armor.find_all('img', alt=True, src=True)
        # Iterate through all 4 imgs
        for i in range(0,4):
            armor_mods.append(img[i]['alt'])

    # If its the weekend, we have Xur information, return it with the rest
    if isWeekend:
        return [weapon_mods, good_weapons, armor_mods, lost_sector, XURLOCATION]

    # If it isn't the weekend just return the info on mods and lost sector
    return [weapon_mods, good_weapons, armor_mods, lost_sector]

# Extract the Xur info from the light.gg pull
async def getXurInfo(page, log):
    # Define parser
    soup = BeautifulSoup(page, "html.parser")

    # Xur's location info is stored in a span with a class of map-name
    # This class applies to a lot of things
    spans = soup.find_all('span', class_="map-name")

    # Initialize an array to store the spans
    xur = []

    # Xur's section is at the 5th index on the page
    for span in spans[5]:
        # Remove whitespace and add the remaining spans
        if span.text.strip() != "":
            xur.append(span.text)
            
    # First indexed span is irrelevant, select the second instead which contains the name of the location
    try:
        xurLocation = xur[1]
        xurLocation = xurLocation.strip()
    except:
        xurLocation = "???"
        log.AddLine("Xur Location currently unknown, try again later.")
        return xurLocation

    log.AddLine("Successfully retrieved Xur's Location")
    if xur[1].strip() == "Nessus":
        return "Watcher's Grave (Nessus)"
    elif xur[1].strip() == "EDZ":
        return "Winding Cove (EDZ)"
    else:
        return xur[1].strip()

async def getXurArmorInfo(page, log):
    # Xur Message Fields
    xurHunter = mf.MessageField("Hunter", "Armor items sold for the Hunter class.")
    xurTitan = mf.MessageField("Titan", "Armor items sold for the Titan class.")
    xurWarlock = mf.MessageField("Warlock", "Armor items sold for the Warlock class")
    xurExotic = mf.ArmorMessageField("Exotic","", 0, 0, 0, 0, 0, 0)
    xurHelmet = mf.ArmorMessageField("Helmet", "", 0, 0, 0, 0, 0, 0)
    xurArms = mf.ArmorMessageField("Arms", "", 0, 0, 0, 0, 0, 0)
    xurChest = mf.ArmorMessageField("Chest", "", 0, 0, 0, 0, 0, 0)
    xurLegs = mf.ArmorMessageField("Legs", "", 0, 0, 0, 0, 0, 0)
    xurClassItem = mf.ArmorMessageField("Class Item", "", 0, 0, 0, 0, 0, 0)

    armorFields = [
        xurExotic,
        xurHelmet,
        xurArms,
        xurChest,
        xurLegs,
        xurClassItem
    ]

    xurMessage = []

    page = await pr.requestPage(log)

    soup = BeautifulSoup(page[1], "html.parser")

    xurBillboard = soup.find_all('div', id="xurv2-billboard")

    for section in xurBillboard:
        xurArmor = section.find_all('div', class_="armor-container")

    for section in xurArmor:
        armorContainer = section.find_all('div', class_="rewards-container")
        for rewards in armorContainer:
            clearfix = rewards.find_all('div', class_="clearfix")
    
    classIndex = 0
    for _class in clearfix:
        itemStats = _class.select('div.xur-stats')
        statAmounts = []
        index = 0
        for item in itemStats:
            d2Stats = item.select('div.d2-stats span span')
            d1Stats = item.select('div.d1-stats span span')
            statAmounts = d2Stats + d1Stats

            statIndex = 0
            for stat in statAmounts:
                if statIndex == 0:
                    armorFields[index].mobility = stat.text
                elif statIndex == 1:
                    armorFields[index].resilience = stat.text
                elif statIndex == 2:
                    armorFields[index].recovery = stat.text
                elif statIndex == 3:
                    armorFields[index].discipline = stat.text
                elif statIndex == 4:
                    armorFields[index].intellect = stat.text
                elif statIndex == 5:
                    armorFields[index].strength = stat.text

                armorFields[index].generateValueMessage()
                statIndex += 1

            index += 1
        if classIndex == 0:
            xurMessage.append(xurHunter)
            xurMessage.append(armorFields)
            classIndex += 1
            continue
        elif classIndex == 1:
            xurMessage.append(xurTitan)
            xurMessage.append(armorFields)
            classIndex += 1
            continue
        elif classIndex == 2:
            xurMessage.append(xurWarlock)
            xurMessage.append(armorFields)
            classIndex += 1
            continue

    return xurMessage

async def getLostSectorLocal(log):
    season_start = date(2022, 12, 6)
    todays_date = date.today()

    time_between  = todays_date - season_start
    days = time_between.days

    if await tk.isTimeBetween(datetime.time(18,00), datetime.time(00,00), datetime.datetime.now().time()):
        days = days - 1

    currentLSRota = days % 11
    currentRewardRota = days % 4

    log.AddLine(f"Current Lost Sector in Rotation: {lost_sector_rota[currentLSRota]}")
    log.AddLine(f"Current Reward: {rewards_rota[currentRewardRota]}")

    return (lost_sector_rota[currentLSRota], rewards_rota[currentRewardRota])