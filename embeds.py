from discord import *
import luna_assets

red = 0xff0000
amber = 0xffdd00
green = 0x00ff55
cyan = 0x00ffff
purple = 0xe312d9

def user_server_type_error() -> Embed :
    return Embed(title="Invalid `type` argument", description="Please enter [user/server]", color=red)

def permission_error() -> Embed :
    return Embed(title="Sorry!", description="You do not have permission to use this command", color=red)

def profound_error() -> Embed :
    return Embed(title="Luna can't say that", description="The content contains banned terms", color=red)

def no_interactions(type : str) -> Embed :
    return Embed(title="No Interactions", description=f'{type.title()} has no custom interactions', color=amber)

def not_in_server() -> Embed :
    return Embed(title="Sorry!", description="You must be in a server to run this command", color=red)

def no_items() -> Embed :
    return Embed(title="No Items", description="Your inventory is empty\nUse `/shop` to buy items", color=amber)

def window_closed() -> Embed :
    return Embed(title="Window Closed", description="You can no longer interact with this window", color=amber)

def create_leaderboard(data : dict[Member], server_name : str = "this server") -> Embed :
    embed = Embed(title="Leaderboard", description=f'Richest players on **{server_name}**', color=green)

    count = 5
    for i, member in enumerate(data):
        if i == count :
            break
        embed.add_field(name=f'{i+1}. {member.name}', value=f'{data[member]} {luna_assets.coin_symbol}', inline=False)
    
    return embed

def menu_navigator(ctx : interactions.Interaction) -> Embed :
    return Embed(title="Menu Navigator", description=f'{luna_assets.menu_next} : Next\n{luna_assets.menu_prev} : Prev\n{luna_assets.menu_close} : Close\n{luna_assets.menu_refresh} : Refresh')

def gained_item(ctx : interactions.Interaction) -> Embed :
    return Embed(title=f'{ctx.user.name} Got An Item', description="The item will be added to their inventory", color=cyan)

def item_not_owned() -> Embed :
    return Embed(title="Item not owned", description="The interaction failed because the item is not part of your inventory", color=red)

def insufficient_funds() -> Embed :
    return Embed(title="Insufficient Funds!", description="You do not have enough coins", color=red)

def insufficient_level() -> Embed :
    return Embed(title="Insufficient Level!", description="You do meet the XP requirement", color=red)

def place_holder() -> Embed :
    return Embed(title="Placeholder", description="This is a placeholder response. If you are seeing this message regularly, please contact the support team.", color=amber)

def table(dict : dict[str, str], title : str = "Table", description : str = "No description") -> Embed :
    embed = Embed(title=title, description=description, color=cyan)
    for key in dict :
        embed.add_field(name=key, value=dict[key], inline=False)
    return embed

def error() -> Embed :
    return Embed(title="Uh Oh!", description="Something went wrong with this command", color=red)

def cooldown_error(cooldown_message : str) -> Embed :
    return Embed(title="Command on cooldown", description=f'Come back in {cooldown_message}', color=red)