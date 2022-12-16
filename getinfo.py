import pagerequest as pr
from bs4 import BeautifulSoup
import re

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
    global XURLOCATION
    armor_mods = []
    lost_sector = ""

    # Request the page content from light.gg
    page = await pr.requestPage(log)

    # If the page is returned with anything but a 200 code we didn't
    # get anything back. Return the same data so the page request runs
    # again
    if page[0] != 200:
        return [weapon_mods, armor_mods, lost_sector]

    # Get the lost sector info from the page
    log.AddLine("Getting Lost Sector Name from light.gg...")
    lost_sector = await getLostSector(page[1], log)

    # If it is the weekend get the Xur info from the page
    if isWeekend:
        log.AddLine("Getting Xur location info...")
        XURLOCATION = await getXurInfo(page[1], log)

    # The lost sector sometimes returns blank. If this is the case
    # reattempt the request by returning the information
    if lost_sector == "":
        return [weapon_mods, armor_mods, lost_sector]

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
    return xur[1].strip()

# Extract current legendary lost sector information
async def getLostSector(page, log):
    # Define html parser
    soup = BeautifulSoup(page, "html.parser")

    # Get all the divs with the class legend-rewards, this is where lost sector info is stored
    div = soup.find("div", {'class':'legend-rewards'})

    # If the parser finds no data, there was an issue with the request, return blank string so it will run again
    if div == None:
        return ""
    else:
        # Otherwise grab the h3 which contains the lost sector name
        h3 = div.findChild("h3")
        ls = h3.findAll(text=True)
        return ls[0]
