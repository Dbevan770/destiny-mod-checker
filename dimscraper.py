from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from getpass import getpass
import time

# Opens a chrome browser window and navigates to DIM login page
def launchBrowser():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://app.destinyitemmanager.com/login')

    return driver

# Writes the list of all missing mods to a file
def writeMissingModList(missing_mods):
    # Index to track when it is the last element in the list
    index = 0
    # Prompt the user for what they would like to name the file
    FILE = input("What would you like to name the file?(include extension): ")
    with open(FILE, 'w') as f:
        for mod in missing_mods:
            f.write(mod)

            if index != len(missing_mods) - 1:
                f.write('\n')
            else:
                continue

            index += 1

        f.close()
    
    print("Success!")

# Main function for finding the missing mods
def getModList():
    print("Attempting to get a list of missing mods...")
    missing_mods = []

    time.sleep(10)
    # Stores all Navbar items at the top of the page
    navBarItems = driver.find_elements(By.CSS_SELECTOR, '._1edz_9G')
    time.sleep(1)

    # Selects the records tab by index
    navBarItems[4].click()

    time.sleep(2)

    # Selects the Collections section on the page
    col_section = driver.find_element(By.ID, 'p_3790247699')

    # Within the collections section makes a list of
    # all mod sections
    mods_sections = col_section.find_elements(By.XPATH, ".//div[@class='presentation-node']")

    # Within the list grabs the Mods Section by index
    mods = mods_sections[4]

    # Opens the Mods section dropdown, divs are not
    # exposed otherwise
    mods.click()
    time.sleep(1)
    
    # Gets a list of each of the sub sections under Mods
    mod_cats = mods.find_elements(By.XPATH, ".//div[@class='presentation-node']")

    # Within each Mod sub-type finds each mod that is missing
    for mod in mod_cats:
        mod.click()
        time.sleep(1)
        missingMods = mod.find_elements(By.XPATH, ".//div[@class='fV3okWbl KerNRXuo']/div")

        # Gets the name of the mod from the title of the div
        # these titles contain a newline and additional info
        # we cut the data off at the newline thus only getting
        # the name of the mod
        for mm in missingMods:
            missing_mods.append(mm.get_attribute("title").split('\n')[0])

    writeMissingModList(missing_mods)

# If user has 2FA prompt for code and enter it into the text field
def twoFactorLogin(twoFactorEntry, authType):
    twoFA = input("Enter 2FA Code: ")

    # Send enter key press as is more reliable than
    # click function in this instance
    twoFactorEntry.send_keys(twoFA, Keys.RETURN)
    time.sleep(3)

    if authType.lower() == "email":
        driver.find_element(By.ID, "success_continue_btn").click()
        time.sleep(3)

    multiLog = input("Did you play Destiny 1?: ")

    if multiLog.lower() in ["yes", "y"]:
        driver.find_element(By.CLASS_NAME, "A9Xa62lt").click()
        time.sleep(3)

    getModList()

def loginXbox():

    # Finds the login button and activates it
    driver.find_element(By.CSS_SELECTOR, ".fjefWfiB.dim-button").click()
    time.sleep(1)

    # Gets an array of all platform login buttons and clicks Steam
    # None of these have their name in their classes so instead
    # it is accessed via the index
    btns = driver.find_elements(By.CLASS_NAME, "provider-selector-btn")
    btns[0].click()
    time.sleep(1)

    # Find the e-mail entry field; input username; click Next
    driver.find_element(By.ID, "i0116").send_keys(USER_NAME)
    driver.find_element(By.ID, "idSIButton9").click()
    time.sleep(1)

    # Find the password entry field; input password; click Sign in
    driver.find_element(By.ID, "i0118").send_keys(PASS)
    driver.find_element(By.ID, "idSIButton9").click()
    time.sleep(1)

    # Find the authorize button and press yes
    driver.find_element(By.ID, "idBtn_Accept").click()
    time.sleep(1)

def loginSteam():

    # Finds the login button and activates it
    driver.find_element(By.CSS_SELECTOR, ".fjefWfiB.dim-button").click()
    time.sleep(1)

    # Gets an array of all platform login buttons and clicks Steam
    # None of these have their name in their classes so instead
    # it is accessed via the index
    btns = driver.find_elements(By.CLASS_NAME, "provider-selector-btn")
    btns[2].click()
    time.sleep(1)

    # Finds the username and password text fields then clicks Login
    driver.find_element(By.NAME, "username").send_keys(USER_NAME)
    time.sleep(1)
    driver.find_element(By.NAME, "password").send_keys(PASS)
    time.sleep(1)
    driver.find_element(By.ID, 'imageLogin').click()
    time.sleep(1)

    authType = input("What is your 2FA Type? (email/ phone/ none): ")

    if authType.lower() == "email":
        twoFactorLogin(driver.find_element(By.ID, 'authcode'), authType)
    elif authType.lower() == "phone":
        twoFactorLogin(driver.find_element(By.ID, 'twofactorcode_entry'), authType)
    elif authType.lower() == "none":
        getModList()

def getUserPlatform():
    userPlatform = input("Enter what platform you play on((S)team/ (X)box/ (P)laystaion): ")

    return userPlatform.lower()

# Ask user for Steam user/ pass for login
USER_PLATFORM = getUserPlatform()
plat_index = 0
if USER_PLATFORM in ['s', 'steam']:
    USER_NAME = input("Enter your Steam username: ")
    PASS = getpass("Enter your Steam password: ")
    plat_index = 0
elif USER_PLATFORM in ['x', 'xbox']:
    USER_NAME = input("Enter your Xbox username: ")
    PASS = getpass("Enter your Xbox password: ")
    plat_index = 1
elif USER_PLATFORM in ['p', 'playstation']:
    USER_NAME = input("Enter your Playstation username: ")
    PASS = getpass("Enter your Playstation password: ")
    plat_index = 2
else:
    print("Invalid platform selected...")

# Store reference to the web browser instance
driver = launchBrowser()

time.sleep(3)

# If login is necessary begin login process otherwise skip to finding mods
if driver.find_element(By.CSS_SELECTOR, ".fjefWfiB.dim-button"):
    if plat_index == 0:
        loginSteam()
    elif plat_index == 1:
        loginXbox()
    elif plat_index == 2:
        loginPlaystation()
else:
    getModList()