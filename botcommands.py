import messagefield as mf
import sendmessages as sm
import deletemods as dm
import pagerequest as pr
import getinfo as gi
import modchecker as mc
import users

deletemods = mf.MessageField("!deletemods", "Use this to tell Destiny Bot that you bought your missing mods and have it remove them from your list")
undo = mf.MessageField("!undo", "Use this command to undo a mod deletion. (Can only be used once)")
lost_sector = mf.MessageField("!lostsector", "Use this command to get more details about today's Legendary Lost Sector!")
xur = mf.MessageField("!xur", "Use this command to see where Xûr is this weekend!")
comingsoon = mf.MessageField("Coming Soon!", "More commands are coming soon! Keep an eye out for more QoL changes...")
admin = mf.MessageField("!admin", "Check if your account has admin privileges with the Bot.")

COMMANDS = [deletemods, undo, lost_sector, xur, admin, comingsoon]

async def helpCommand(client, userId, COMMANDS, log):
    await sm.send_embed_msg(client, userId, "Available Commands", "A list of all Destiny Bot's available commands", 0x5eb5ff, COMMANDS, log)

async def lostSectorCommand(client, userId, log):
    await sm.send_embed_msg(client, userId, "Legendary Lost Sector", "This command is only in testing. It doesn't do anything at the moment.", 0xffd700, [], log)

async def xurCommand(client, userId, log):
    isWeekend = await mc.checkIsWeekend(log)
    if not isWeekend:
        await sm.send_embed_msg(client, userId, "Xûr", "Find out where Xûr is this weekend.", 0x3c1361, [mf.MessageField("Location", f"Xûr is currently not around at the moment can I take a message? (If it is not the weekend, he is not around. If it is the weekend light.gg may not be working at the moment try again later)."), mf.MessageField("Items Available", "This is currently in testing. Please stay tuned!")], log)
    else:
        page = await pr.requestPage(log)
        xurLocation = await gi.getXurInfo(page[1])
        await sm.send_embed_msg(client, userId, "Xûr", "Find out where Xûr is this weekend.", 0x3c1361, [mf.MessageField("Location", f"Xûr is located at the {xurLocation}."), mf.MessageField("Items Available", "This is currently in testing. Please stay tuned!")], log)

async def adminCommand(client, userId, userName, log):
    log.AddLine(f"Checking if User: {userName} ID: {userId} is an Admin...")
    if users.checkIfAdmin(userId):
        log.AddLine(f"IDs Match! User: {userName} ID: {userId} is an Admin!")
        await sm.send_msg(client, userId, "You are an Admin! Don't do anything too crazy my friend!", log)
    elif not users.checkIfAdmin(userId):
        log.AddLine(f"IDs Don't Match! User: {userName} ID: {userId} is not an Admin!")
        await sm.send_msg(client, userId, "You are not an Admin.", log)
    else:
        log.AddLine(f"Error fetching Admin status for User: {userName} ID: {userId}")
        await sm.send_msg(client, userId, "Failed to fetch Admin status. If this error persists please contact my creator.", log)

async def deleteCommand():
    content = message.content.split("")

    dm.deleteModsManually(user, modName)

async def handleMessage(client, userName, userId, message, log, USERS):
    # If the user runs the help command send the embeded message with the
    # list of all available commands at the moment
    if message.content.lower() in ["!help", "!h"]:
        await helpCommand(client, userId, COMMANDS, log)
        
    if message.content.lower() in ["!lostsector", "!ls"]:
        await lostSectorCommand(client, userId, log)

    # If the user runs the Xur command, tell them Xurs location. In the future I want to provide detailed item data as well
    if message.content.lower() in ["!xur", "!x"]:
        await xurCommand(client, userId, log)

    # If the user runs the admin command, check if the user is an admin and respond appropriately
    if message.content.lower() in ["!admin", "!a"]:
        await adminCommand(client, userId, userName, log)

    # Currently in testing: User sends name of a mod and manually deletes it
    if message.content.lower() in ["!delete", "!d"]:
        await deleteCommand()

    # When a DM is received check which user it came from
    for user in USERS:
        # Once matched check if the User even has missing mods
        if userId == user.id and user.hasMissingMods:
            # If the user has missing mods, wait for the delete command
            # and remove the mods from the users list
            if message.content.lower() in ["!deletemods", "!dm"] and not user.hasDeleted:
                await sm.send_msg(client, userId, "Okay, I will remove those mods from your list!", log)
                dm.deleteMods(user)
                user.hasDeleted = True
                await sm.send_msg(client, userId, "Successfully removed your Mods, if this was a mistake, say '!undo'.", log)
                user.canUndo = True

            # The user can request 1 undo
            if message.content.lower() in ["!undo", "!u"] and user.canUndo:
                await sm.send_msg(client, userId, "Okay, I will undo the previous deletion!", log)
                dm.undoDeletion(user)
                user.canUndo = False