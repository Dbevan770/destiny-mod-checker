import messagefield as mf

deletemods = mf.MessageField("!deletemods", "Use this to tell Destiny Bot that you bought your missing mods and have it remove them from your list")
undo = mf.MessageField("!undo", "Use this command to undo a mod deletion. (Can only be used once)")
lost_sector = mf.MessageField("!lostsector", "Use this command to get more details about today's Legendary Lost Sector!")
xur = mf.MessageField("!xur", "Use this command to see where Xûr is this weekend!")
comingsoon = mf.MessageField("Coming Soon!", "More commands are coming soon! Keep an eye out for more QoL changes...")
admin = mf.MessageField("!admin", "Check if your account has admin priviledges with the Bot.")