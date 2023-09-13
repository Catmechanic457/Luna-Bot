import discord
from discord import app_commands

import embeds
import luna_assets

from luna import *
from data_root import Data, Manage

class Balance(Data) :
    def __init__(self, data_directory : str, id : int) -> None :
        self.id = str(id)
        super().__init__(data_directory)

        # Add the item if it doesn't exist
        if not self.item_exists("user", self.id) :
            self.add_item("user", self.id)
        
        if not "balance" in self.data()["user"][self.id] :
            data = self.data()
            data["user"][self.id]["balance"] = 0
            self.write(data)
    
    def get(self) -> int :
        return self.data()["user"][self.id]["balance"]
    
    def set(self, value : int) -> None :
        data = self.data()
        data["user"][self.id]["balance"] = value
        self.write(data)
    
    def edit(self, amount : int) -> None :
        data = self.data()
        data["user"][self.id]["balance"] += amount
        if data["user"][self.id]["balance"] < 0 : data["user"][self.id]["balance"] = 0
        self.write(data)

@client.tree.command(name="balance", description="Tells you how many coins are in a user's wallet")
@app_commands.describe(user = "user")
async def balance(ctx : discord.interactions.Interaction, user : discord.User = None) -> None :
    if user == None :
        user_id = str(ctx.user.id)
        user = ctx.user
    else :
        user_id = user.id

    balance_file = Balance("data/data.json", user_id)
    balance = balance_file.get()
    embed = discord.Embed(title=f'{user.name}\'s Wallet', description="Wallet Details", color=embeds.green)
    embed.add_field(name="Balance", value=f'{str(balance)} {luna_assets.coin_symbol}', inline=False)
    await ctx.response.send_message(embed=embed, ephemeral=True)

leaderboard_group = app_commands.Group(name="leaderboard", description="...")

@leaderboard_group.command(name="server", description="Lists the richest players on the server")
async def leaderboard(ctx : discord.interactions.Interaction) -> None :

    if ctx.guild == None :
        await ctx.response.send_message(embed=embeds.not_in_server())
        return


    members = ctx.guild.members
    leaderboard = {}
    manage = Manage("data/data.json")
    for member in members :
        if manage.user_exists(member.id) :
            leaderboard[member] = Balance("data/data.json", member.id).get()
    
    leaderboard = dict(sorted(leaderboard.items(), key=lambda x:x[1], reverse=True))
    
    await ctx.response.send_message(embed=embeds.create_leaderboard(leaderboard, ctx.guild.name), ephemeral=True)

@leaderboard_group.command(name="global", description="Lists the richest players globally")
async def leaderboard_global(ctx : discord.interactions.Interaction) -> None :

    leaderboard = {}
    manage = Manage("data/data.json")
    for user_id in manage.users() :
        user_id = int(user_id)
        leaderboard[client.get_user(user_id)] = Balance("data/data.json", user_id).get()
    
    leaderboard = dict(sorted(leaderboard.items(), key=lambda x:x[1], reverse=True))
    
    await ctx.response.send_message(embed=embeds.create_leaderboard(leaderboard, "Discord"), ephemeral=True)

client.tree.add_command(leaderboard_group)