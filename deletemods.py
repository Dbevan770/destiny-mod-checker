# Function to delete the Mods of the day from the Users
# Missing Mods list.
def deleteMods(user):
    with open("./modfiles/" + user.modfile, "r") as f:
        lines = f.readlines()
    with open("./modfiles/" + user.modfile, "w") as f:
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
    with open("./modfiles/" + user.modfile, "a") as f:
        for mod in user.missingWeaponMods:
            f.write("\n")
            f.write(mod)
        for mod in user.missingArmorMods:
            f.write("\n")
            f.write(mod)