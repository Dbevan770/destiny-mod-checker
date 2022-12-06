import pagerequest as pr
from bs4 import BeautifulSoup

# Go to Light.gg and scrape the website for Mods from Banshee-44 and Ada-1
# Also now looks for today's Legendary Lost Sector
async def getInfo(isWeekend, log):
    # Define scope of variables
    global XURLOCATION
    weapon_mods = []
    armor_mods = []
    #lost_sector = ""

    # Request the page content from light.gg
    page = await pr.requestPage(log)

    # If the page is returned with anything but a 200 code we didn't
    # get anything back. Return the same data so the page request runs
    # again
    if page[0] != 200:
        return [weapon_mods, armor_mods] #lost_sector]

    # Get the lost sector info from the page
    #log.AddLine("Getting Lost Sector Name from light.gg...")
    #lost_sector = await getLostSector(page[1])

    # If it is the weekend get the Xur info from the page
    if isWeekend:
        log.AddLine("Getting Xur location info...")
        XURLOCATION = await getXurInfo(page[1])

    # The lost sector sometimes returns blank. If this is the case
    # reattempt the request by returning the information
    #if lost_sector == "":
        #return [weapon_mods, armor_mods, lost_sector]

    # Define the beautiful soup html parser for the page
    soup = BeautifulSoup(page[1], "html.parser")

    log.AddLine("Getting available Mods from light.gg...")

    # Get a list of the divs containing weapon mods from the page
    for weapon in soup.find_all('div', class_="weapon-mods"):
        # The names for the mods are stored in the alt tags for the imgs
        img = weapon.find_all('img', alt=True, src=True)
        # Iterate through all 4 imgs
        for i in range(0,4):
            weapon_mods.append(img[i]['alt'])

    # Get a list of the divs containing armor mods from the page
    for armor in soup.find_all('div', class_="armor-mods"):
        # The names for the mods are stored in the alt tags for the imgs
        img = armor.find_all('img', alt=True, src=True)
        # Iterate through all 4 imgs
        for i in range(0,4):
            armor_mods.append(img[i]['alt'])

    # If its the weekend, we have Xur information, return it with the rest
    if isWeekend:
        return [weapon_mods, armor_mods, XURLOCATION]

    # If it isn't the weekend just return the info on mods and lost sector
    return [weapon_mods, armor_mods]

# Extract the Xur info from the light.gg pull
async def getXurInfo(page):
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
    if xur[1].strip() == "???":
        return "Currently Unknown try again later."
    else:
        return xur[1].strip()

# Extract current legendary lost sector information
async def getLostSector(page):
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