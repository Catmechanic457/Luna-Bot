import discord
from discord import app_commands

from custom_interactions import *
from default_interactions import Interactions
import embeds
from luna import *

interactions_group = app_commands.Group(name="interactions", description="...")
default_group = app_commands.Group(name="default", parent=interactions_group, description="...")
custom_group = app_commands.Group(name="custom", parent=interactions_group, description="...")

@default_group.command(name="list", description="Lists all default interactions")
async def list_default(ctx : discord.interactions.Interaction) -> None :
    interactions_file = Interactions("data/default/responses.json")
    interactions = interactions_file.key()
    embed = discord.Embed(title="Default Interactions", description="List of default interactions", color=embeds.cyan)
    for trigger in interactions :
        response = interactions[trigger]
        embed.add_field(name=f'\"{trigger}\"', value=response.get_description())
    await ctx.response.send_message(embed=embed, ephemeral=True)

@custom_group.command(name="list", description="Lists all custom interactions")
@app_commands.describe(type = "[user/server]")
async def custom_interactions(ctx : discord.interactions.Interaction, type : str) -> None :
    type = type.lower()
    # Get id
    # id == None if invalid
    id = {"user" : ctx.user.id, "server" : client.get_guild_id(ctx)}.setdefault(type)

    if not id : 
        # Inform user of invalid id
        await ctx.response.send_message(embed=embeds.user_server_type_error(), ephemeral=True)
        return

    interactions_file = Custom_Interactions("data/data.json", type, id)

    # Catch no interactions
    if len(interactions_file) == 0 :
        await ctx.response.send_message(embed=embeds.no_interactions(type), ephemeral=True)
        return
    
    embed = discord.Embed(title=f'Custom {type.title()} Interactions', description=f'List of custom {type} interactions', color=embeds.cyan)
    groups = ["exclusive" , "contains"]
    
    for group in groups :
        interactions = interactions_file.get()[group]
        for trigger in interactions :
            responses = interactions[trigger]
            embed.add_field(name=f'\"{trigger}\"', value=", ".join(responses), inline=False)
    await ctx.response.send_message(embed=embed, ephemeral=True)

@custom_group.command(name="add", description="Adds a custom server or user interaction")
@app_commands.describe(type = "[user/server]", trigger = "The phrase Luna looks for", response = "Luna's response")
async def add_interaction(ctx : discord.interactions.Interaction, type : str, trigger : str, response : str) -> None :
    # Catch profound responses. Triggers are not filtered
    if not p_filter.is_clean(response) :
        await ctx.response.send_message(embed=embeds.profound_error() , ephemeral=True)
        return
    
    type = type.lower()
    # Get id
    # id == None if invalid
    id = {"user" : ctx.user.id, "server" : client.get_guild_id(ctx)}.setdefault(type)


    if not id : 
        # Inform user of invalid id
        await ctx.response.send_message(embed=embeds.user_server_type_error(), ephemeral=True)
        return
    
    trigger = client.cleanse_input(trigger)

    if type == "server" :
        # Check permission level for server interaction
        if not ctx.user.guild_permissions.administrator :
            await ctx.response.send_message(embed=embeds.permission_error(), ephemeral=True)
            return

    # Classify group
    group = "contains" if "\contains\\" in trigger else "exclusive"
    trigger = trigger.replace("\contains\\","")
    
    interactions_file = Custom_Interactions("data/data.json", type, id)

    responses = response.split("|")
    for i, response in enumerate(responses) :
        responses[i] = response.strip()
    
    try :
        # Attempt to add
        interactions_file.add(trigger, responses, group)

    except :
        # Inform user of errors
        await ctx.response.send_message(embed=embeds.error() , ephemeral=True)
        return
    
    # Send a confirmation
    embed = discord.Embed(title=f'Added {type} interaction', description="", color=embeds.green)
    embed.add_field(name=f'\"{trigger}\"', value=", ".join(responses))
    await ctx.response.send_message(embed=embed, ephemeral=True if type == "user" else False)

@custom_group.command(name="delete", description="Deletes a custom server or user interaction")
@app_commands.describe(type = "[user/server]", trigger = "The phrase to delete")
async def delete_interaction(ctx : discord.interactions.Interaction, type : str, trigger : str) -> None :
    type = type.lower()
    # Get id
    # id == None if invalid
    id = {"user" : ctx.user.id, "server" : client.get_guild_id(ctx)}.setdefault(type)

    if not id : 
        # Inform user of invalid id
        await ctx.response.send_message(embed=embeds.user_server_type_error(), ephemeral=True)
        return
    
    interactions_file = Custom_Interactions("data/data.json", type, id)

    # Catch no interactions
    if len(interactions_file) == 0 :
        await ctx.response.send_message(embed=embeds.no_interactions(type), ephemeral=True)
        return
    
    trigger = client.cleanse_input(trigger)

    # Classify group
    group = "contains" if "\contains\\" in trigger else "exclusive"
    trigger = trigger.replace("\contains\\","")

    if type == "server" :
        # Check permission level for server interaction
        if not ctx.user.guild_permissions.administrator :
            await ctx.response.send_message(embed=embeds.permission_error(), ephemeral=True if type == "user" else False)
            return

    if interactions_file.interaction_exists(trigger, group) :

        # Delete
        interactions_file.delete(trigger, group)

        # Send a confirmation
        embed = discord.Embed(title=f'Deleted interaction', description=f'{type.title()} interaction **{trigger}** has been deleted',color=embeds.red)
        await ctx.response.send_message(embed=embed, ephemeral=(type=="user"))

    else :
        # Catch missing interaction
        embed = discord.Embed(title="Interaction not found", description=f'{type.title()} interaction **{trigger}** does not exist', color=embeds.amber)
        await ctx.response.send_message(embed=embed, ephemeral=True)
  
client.tree.add_command(interactions_group)