import discord

import math

from luna import *
import embeds
from data_root import Data
import luna_assets

class Experience(Data) :
    def __init__(self, data_directory : str, id : int) -> None :
        self.id = str(id)
        super().__init__(data_directory)

        # Add the item if it doesn't exist
        if not self.item_exists("user", self.id) :
            self.add_item("user", self.id)
        
        if not "experience" in self.data()["user"][self.id] :
            data = self.data()
            data["user"][self.id]["experience"] = 0
            self.write(data)
    
    def get(self) -> int :
        return self.data()["user"][self.id]["experience"]
    
    def set(self, value : int) -> None :
        data = self.data()
        data["user"][self.id]["experience"] = value
        self.write(data)
    
    def edit(self, amount : int) -> None :
        data = self.data()
        data["user"][self.id]["experience"] += amount
        if data["user"][self.id]["experience"] < 0 : data["user"][self.id]["experience"] = 0
        self.write(data)
        
    def formatted_total(self) -> tuple[int, int] :
        def req_experience(lvl : int) -> int :
            return int((((0.0001*lvl)**2) * 200000000) + 100)
            
        xp = self.get()
        lvl = 0

        while True :
            if xp - req_experience(lvl) >= 0 : 
                xp += - req_experience(lvl)
                lvl += 1
            else : return lvl, xp
    
    def level(self) -> int :
        return self.formatted_total()[0]

    def xp(self) -> int :
        return self.formatted_total()[1]
    
    def target(self) -> int :
        return int((((0.0001*self.level())**2) * 200000000) + 100)

# Embeds

def experience_info(ctx : discord.interactions.Interaction, user_xp : Experience) -> discord.Embed :
    total = user_xp.get()
    xp = user_xp.xp()
    level = user_xp.level()
    target = user_xp.target()
    unit_count = 10
    filled_unit_count = math.floor((xp/target)*unit_count)
    embed = discord.Embed(title=f'{ctx.user.name}\'s Charisma', description=f'{luna_assets.bar_unit_filled*filled_unit_count}{luna_assets.bar_unit_empty*(unit_count-filled_unit_count)}', color=embeds.green)
    embed.add_field(name="XP", value=f'{xp}/{target}')
    embed.add_field(name="Level", value=level)
    embed.add_field(name="Total", value=total)

    return embed

def experience_change(ctx : discord.interactions.Interaction, user_xp : Experience, change : int, message : str = None) -> discord.Embed :

    xp = user_xp.get()
    if change > 0 :
        if not message : message = "Luna likes you just a little bit more"
        embed = discord.Embed(title=f'{ctx.user.name} Gained Charisma!', description=message, color=embeds.green)
        embed.add_field(name=xp, value=f'+{change}')
    else :
        if not message : message = "Luna seems upset"
        embed = discord.Embed(title=f'{ctx.user.name} Lost Charisma!', description="Luna seems upset", color=embeds.red)
        embed.add_field(name=xp, value=f'{change}')
    
    return embed

def edit_charisma(ctx : discord.interactions.Interaction, value : int, message = None) -> discord.Embed :
    user_xp = Experience("data/data.json", ctx.user.id)
    user_xp.edit(value)
    change_embed = experience_change(ctx, user_xp, value, message)
    return change_embed

# Commands

@client.tree.command(name="experience", description="Displays your current Charisma (XP) level")
async def experience(ctx : discord.interactions.Interaction) -> None :
    await ctx.response.send_message(embed=experience_info(ctx, Experience("data/data.json", ctx.user.id)))