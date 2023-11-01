import discord

import embeds
from data import Data_File
from luna import *

class Help_Info :
    def __init__(self, help_info : dict) -> None:
        self.data = help_info
    
    def title(self) -> str :
        return self.data["title"]

    def description(self) -> str :
        return self.data["description"]
    
    def color(self) -> int :
        return self.data["color"]
    
    def commands(self) -> str :
        return self.data["commands"]
    
    def embed(self) -> discord.Embed :
        embed = discord.Embed(title=self.title(), description=self.description(), color=self.color())
        commands = self.commands()
        for command in commands :
            command_description = commands[command]["description"]
            parameters = commands[command]["parameters"]
            for parameter in parameters :
                command_description = f'{command_description}\n**{parameter}:** {parameters[parameter]}'
            embed.add_field(name=f'`/{command}`', value=command_description, inline=False)
        
        return embed



class Help(Data_File) :
    def help_info(self) -> dict :
        help_info_dict = {}
        for key in self.data() : help_info_dict[key] = Help_Info(self.data()[key]).embed()
        return help_info_dict

async def all_commands(ctx : discord.interactions.Interaction) -> None :
    help_info = Help("data/default/help.json").help_info()
    await ctx.response.send_message(embeds=tuple(help_info.values()), ephemeral=True)


async def interactions_commands(ctx : discord.interactions.Interaction) -> None :
    help_info = Help("data/default/help.json").help_info()
    await ctx.response.send_message(embed=help_info["default_interactions"], ephemeral=True)

async def custom_interactions_commands(ctx : discord.interactions.Interaction) -> None :
    help_info = Help("data/default/help.json").help_info()
    await ctx.response.send_message(embed=help_info["custom_interactions"], ephemeral=True)

async def economy_commands(ctx : discord.interactions.Interaction) -> None :
    help_info = Help("data/default/help.json").help_info()
    await ctx.response.send_message(embed=help_info["economy"], ephemeral=True)

async def items_commands(ctx : discord.interactions.Interaction) -> None :
    help_info = Help("data/default/help.json").help_info()
    await ctx.response.send_message(embed=help_info["items"], ephemeral=True)

async def experience_commands(ctx : discord.interactions.Interaction) -> None :
    help_info = Help("data/default/help.json").help_info()
    await ctx.response.send_message(embed=help_info["experience"], ephemeral=True)

async def whisper_commands(ctx : discord.interactions.Interaction) -> None :
    help_info = Help("data/default/help.json").help_info()
    await ctx.response.send_message(embed=help_info["whisper"], ephemeral=True)

async def fun_commands(ctx : discord.interactions.Interaction) -> None :
    help_info = Help("data/default/help.json").help_info()
    await ctx.response.send_message(embed=help_info["fun"], ephemeral=True)

@client.tree.command(name="help", description="Provides useful info for using Luna Bot")
async def help(ctx : discord.interactions.Interaction) -> None :
    embed = discord.Embed(title="Luna Bot",description="Luna Bot is designed to be a fun addition to any text channel, reacting to certain phrases is a cute way.\nLuna also has an economy, charisma and item system. Earn coins by playing with Luna, and use those coins to purchase items in the shop. Interacting with Luna will increase your charisma, allowing you to unlock new items.\n\nLuna bot was created as a passion project during school holidays.", color=embeds.green)
    embed.add_field(name="Discord Server", value="https://discord.gg/Jkbuz8SwBY")

    view = discord.ui.View()

    commands_button = discord.ui.Button(label="All Commands", style=discord.ButtonStyle.green, row=4)
    commands_button.callback = all_commands
    view.add_item(commands_button)

    interactions_button = discord.ui.Button(label="Interactions", style=discord.ButtonStyle.grey, emoji="📕")
    interactions_button.callback = interactions_commands
    view.add_item(interactions_button)

    custom_interactions_button = discord.ui.Button(label="Custom Interactions", style=discord.ButtonStyle.grey, emoji="📗")
    custom_interactions_button.callback = custom_interactions_commands
    view.add_item(custom_interactions_button)

    economy_button = discord.ui.Button(label="Economy", style=discord.ButtonStyle.grey, emoji="🪙")
    economy_button.callback = economy_commands
    view.add_item(economy_button)

    items_button = discord.ui.Button(label="Items", style=discord.ButtonStyle.grey, emoji="🎁")
    items_button.callback = items_commands
    view.add_item(items_button)

    experience_button = discord.ui.Button(label="Experience", style=discord.ButtonStyle.grey, emoji="💎")
    experience_button.callback = experience_commands
    view.add_item(experience_button)

    whisper_button = discord.ui.Button(label="Whisper", style=discord.ButtonStyle.grey, emoji="💬")
    whisper_button.callback = whisper_commands
    view.add_item(whisper_button)

    fun_button = discord.ui.Button(label="Fun", style=discord.ButtonStyle.grey, emoji="✨")
    fun_button.callback = fun_commands
    view.add_item(fun_button)

    await ctx.response.send_message(embed=embed, view=view, ephemeral=True)