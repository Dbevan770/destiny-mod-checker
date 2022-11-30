from datetime import date
import discord
import quotes as q

# async function to send the message to each user
async def send_msg(client, id, message, log):
    target = await client.fetch_user(id)
    log.AddLine(f"Messaging User: {target} with '{message}'...")
    channel = await client.create_dm(target)

    await channel.send(message)

    log.AddLine("Message sent!")

# Send an embeded message to the user
async def send_embed_msg(client, id, title, desc, color, fields, log):
    # Get todays date
    today = date.today()
    # Get the user data from their id
    target = await client.fetch_user(id)
    #print(f"Sending Embeded Message to user: {target}...\n")
    log.AddLine(f"Sending Embeded Message to user: {target}...")
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
    embedMsg.set_footer(text=f"{q.getQuote()}\n\nAll data is taken from light.gg\nTo see a list of all my commands say '!help'")

    await channel.send(embed=embedMsg)