import json

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

def checkIfAdmin(userId):
    with open('admins.json') as admin_file:
        data = json.load(admin_file)

    for admin in data:
        if userId == admin['id']:
            return True
        else:
            continue

    return False

# Sets users to default state
async def clearUserData(user):
    user.missingWeaponMods = []
    user.missingArmorMods = []
    user.hasMissingMods = False
    user.hasDeleted = False
    user.canUndo = False