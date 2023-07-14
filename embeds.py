from discord import Embed

red = 0xff0000
amber = 0xffdd00
green = 0x00ff55

def user_server_type_error() -> Embed :
    return Embed(title="Invalid `type` argument", description="Please enter [user/server]", color=red)

def permission_error() -> Embed :
    return Embed(title="Sorry!", description="You must be an Admin to use this command", color=red)

def no_interactions(type : str) -> Embed :
    return Embed(title="No Interactions", description=f'{type.title()} has no custom interactions', color=amber)