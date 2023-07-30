from discord import *
from experience import XP
import luna_assets
import math

red = 0xff0000
amber = 0xffdd00
green = 0x00ff55

def user_server_type_error() -> Embed :
    return Embed(title="Invalid `type` argument", description="Please enter [user/server]", color=red)

def permission_error() -> Embed :
    return Embed(title="Sorry!", description="You must be an Admin to use this command", color=red)

def no_interactions(type : str) -> Embed :
    return Embed(title="No Interactions", description=f'{type.title()} has no custom interactions', color=amber)

def not_in_server() -> Embed :
    return Embed(title="Sorry!", description="You must be in a server to run this command", color=red)


def create_leaderboard(data : dict[Member], server_name : str = "this server") -> Embed :
    embed = Embed(title="Leaderboard", description=f'Richest players on **{server_name}**', color=green)

    count = 5
    for i, member in enumerate(data):
        if i == count :
            break
        embed.add_field(name=f'{i+1}. {member.name}', value=f'{data[member]} {luna_assets.coin_symbol}', inline=False)
    
    return embed

def experience_info(ctx : interactions.Interaction, user_file_name : str) -> Embed :
    user_xp = XP(user_file_name)
    total = user_xp.total()
    xp = user_xp.xp()
    level = user_xp.level()
    target = user_xp.target()
    unit_count = 10
    filled_unit_count = math.floor((xp/target)*unit_count)
    embed = Embed(title=f'{ctx.user.name}\'s Charisma', description=f'{luna_assets.bar_unit_filled*filled_unit_count}{luna_assets.bar_unit_empty*(unit_count-filled_unit_count)}', color=green)
    embed.add_field(name="XP", value=f'{xp}/{target}')
    embed.add_field(name="Level", value=level)
    embed.add_field(name="Total", value=total)

    return embed

def experience_change(ctx : interactions.Interaction, user_file_name : str, change : int, message : str = None) -> Embed :
    user_xp = XP(user_file_name)
    xp = user_xp.total()
    if change > 0 :
        if not message : message = "Luna likes you just a little bit more"
        embed = Embed(title=f'{ctx.user.name} Gained Charisma!', description=message, color=green)
        embed.add_field(name=xp, value=f'+{change}')
    else :
        if not message : message = "Luna seems upset"
        embed = Embed(title=f'{ctx.user.name} Lost Charisma!', description="Luna seems upset", color=red)
        embed.add_field(name=xp, value=f'{change}')
    
    return embed