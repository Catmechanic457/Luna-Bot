import discord
from discord import app_commands

import embeds
from luna import *

help_interactions = discord.Embed(title="Default Interactions", description="Luna will respond to certain phrases that you send in any channel she's part of and had send_message permissions in.", color=embeds.red)
help_interactions.add_field(name="/interactions default list", value="Lists all of the default interactions.", inline=False)

help_custom_interactions = discord.Embed(title="Custom Interactions", description="Custom interactions work the same way as default interactions. Custom interactions can be bound by user or bound by server. Only server administrators can create server-wide custom interactions.", color=embeds.purple)
help_custom_interactions.add_field(name="/interactions custom list", value="Lists custom interactions.\n**type:** Must be either 'user' or 'server' to list all user-bound or server-bound custom interactions")
help_custom_interactions.add_field(name="/interactions custom add", value="Create a custom interaction.\n**type:** Must be either 'user' or 'server' to create user-bound or server-bound custom interactions\n**trigger:** The phrase Luna looks for. Upper-case and spaces will be ignored. Adding '\\contains\\ at the start of the trigger will make Luna respond to any message containing the phrase anywhere in it's content'\n**response:** The phrase Luna should respond with. Separate possible responses with a '|'.", inline=False)
help_custom_interactions.add_field(name="/interactions custom delete", value="Delete a custom interaction.\n**type:** Must be either 'user' or 'server' to delete a user-bound or server-bound custom interaction\n**trigger:** The phrase associated with the interaction you're trying to delete. Upper-case and spaces will be ignored.", inline=False)


help_economy = discord.Embed(title="Economy", description="Luna Bot has an economy system. Earn coins by playing with Luna. The highest net-worth accounts will be displayed on the leaderboard.", color=embeds.green)
help_economy.add_field(name="/daily", value="Feed Luna her daily portion of food to earn a reward.", inline=False)
help_economy.add_field(name="/play", value="Play with Luna to receive rewards.", inline=False)
help_economy.add_field(name="/balance", value="Display the contents of a user's wallet.", inline=False)
help_economy.add_field(name="/leaderboard server", value="Displays the richest users on the server.", inline=False)
help_economy.add_field(name="/leaderboard global", value="Displays the richest users on Discord.", inline=False)

help_items = discord.Embed(title="Items", description="Luna Bot's item system consists of items that can be bought, used and sold. Items can grant rewards, experience and more.", color=embeds.cyan)
help_items.add_field(name="/shop", value="Browse items to purchase with your coins. Use the reactions to navigate the menu.", inline=False)
help_items.add_field(name="/inventory", value="Displays the contents of your inventory and the actions that can be taken for each item. Use the reactions to navigate the menu.", inline=False)

help_experience = discord.Embed(title="Charisma", description="Luna Bot has an XP system called Charisma. Earn Charisma by interacting with Luna, using items, or playing with Luna. Increasing your lever unlocks items an rewards.", color=embeds.amber)
help_experience.add_field(name="/experience", value="Display your current level.", inline=False)

async def commands_help(ctx : discord.interactions.Interaction) -> None :
    await ctx.response.send_message(embeds=(help_interactions, help_custom_interactions, help_economy, help_items, help_experience), ephemeral=True)


@client.tree.command(name="help", description="Provides useful info for using Luna Bot")
async def help(ctx : discord.interactions.Interaction) -> None :
    embed = discord.Embed(title="Luna Bot",description="Luna Bot is designed to be a fun addition to any text channel, reacting to certain phrases is a cute way.\nLuna also has an economy, charisma and item system. Earn coins by playing with Luna, and use those coins to purchase items in the shop. Interacting with Luna will increase your charisma, allowing you to unlock new items.\n\nLuna bot was created as a passion project during school holidays and named after my girlfriend's cat.", color=embeds.green)
    embed.add_field(name="Discord Server", value="https://discord.gg/Jkbuz8SwBY")

    view = discord.ui.View()
    commands_button = discord.ui.Button(label="Commands", style=discord.ButtonStyle.green)
    commands_button.callback = commands_help
    view.add_item(commands_button)

    await ctx.response.send_message(embed=embed, view=view, ephemeral=True)