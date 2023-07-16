from discord import *
import luna_assets

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