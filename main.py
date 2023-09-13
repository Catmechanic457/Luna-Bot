import discord
from discord import app_commands

from luna import *

from cooldown import Cooldown

from aspects import *

from user_settings import User_Settings

from random import *
import embeds

@client.event
async def on_ready() -> None :
    # When the bot logs on
    print('Luna is ready')
    try :
        print("Syncing Commands...")
        synced = await client.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e :
        print(e)
        
    
@client.event
async def on_message(message : discord.Message) -> None :

    if message.author == client.user : return # Do nothing if the message author is ourselves

    channel = message.channel # Get the channel of the message

    filtered_input = client.cleanse_input(message.content) # Remove spaces and capitals; Preform substitutions

    # Interactions
    # Intercepts any non-command msgs
    intercept = client.intercept(filtered_input)
    if intercept :
        cooldown = Cooldown("data/cooldown.json", message.author.id, "interaction_reward")
        if cooldown.able() :
            cooldown.mark(60)
            experience_file = Experience("data/data.json", message.author.id)
            experience_file.edit(randint(5,45))
        print(f'Received \'{message.content}\'\tFiltered To \'{filtered_input}\'\tReturning \'{intercept}\'')
        await channel.send(intercept)
    
    # Unprompted messages
    if True :
        unprompted_message = client.unprompted_message()
        if not unprompted_message == None :
            print(f'Sending Unprompted \'{unprompted_message}\'')
            await channel.send(unprompted_message)
    
    # Custom interactions
    if True :
        custom_interactions_file = Custom_Interactions_Group("data/data.json", client.get_guild_id(message), message.author.id)
        response = custom_interactions_file.get_response(filtered_input)
        if response :
            print(f'Received \'{message.content}\'\tFiltered To \'{filtered_input}\'\tReturning \'{response}\'')
            await channel.send(response)


    await client.process_commands(message) # Process commands after any messages



# Slash Commands

# Say Commands

@client.tree.command(name="sparkle", description="Adds sparkles (✨) around a message")
@app_commands.describe(message = "Message to sparkle")
async def sparkle(ctx : discord.interactions.Interaction, message : str) -> None :
    # Catch profound messages
    if not p_filter.is_clean(message) :
        await ctx.response.send_message(embed=embeds.profound_error() , ephemeral=True)
        return
    await ctx.response.send_message(f':sparkles: {message} :sparkles:')

@client.tree.command(name="makequirky", description="Types a message out in aLtErNaTiNg CaPs")
@app_commands.describe(message = "Message to make quirky")
async def make_quirky(ctx : discord.interactions.Interaction, message : str) -> None :
    # Catch profound messages
    if not p_filter.is_clean(message) :
        await ctx.response.send_message(embed=embeds.profound_error() , ephemeral=True)
        return
    output_message = ""
    caps = False
    for char in message :
        if caps :
            caps = False
            output_message += char.upper()
        else :
            caps = True
            output_message += char.lower()

    await ctx.response.send_message(output_message)


@client.tree.command(name="say", description = "Sends a message as Luna")
@app_commands.describe(message = "Message to say as Luna Bot")
async def say(ctx : discord.interactions.Interaction, message : str) -> None :
    # Catch profound messages
    if not p_filter.is_clean(message) :
        await ctx.response.send_message(embed=embeds.profound_error() , ephemeral=True)
        return
    await ctx.response.send_message(message)

# Utility Commands

@client.tree.command(name="whisper", description="Send a DM to another member")
@app_commands.describe(user = "user", message = "Message to send", anonymous = "Show the recipient your identity")
async def whisper(ctx : discord.interactions.Interaction, user : discord.User, message : str, anonymous : bool = False) -> None :
    # Catch profound messages
    if not p_filter.is_clean(message) :
        await ctx.response.send_message(embed=embeds.profound_error() , ephemeral=True)
        return
    cooldown = Cooldown("data/cooldown.json", ctx.user.id, "whisper_command")
    if cooldown.able() :
        user_settings_file = User_Settings("data/data.json", user.id) 
        try :
            if ctx.user.id in user_settings_file.get_setting("blocked_users") or not user_settings_file.get_setting("accept_whisper") :
                await ctx.response.send_message(embed=discord.Embed(title="User not accepting DMs", description="You cannot send whispers to this user", color=embeds.red), ephemeral=True)
                return
            cooldown.mark(in_seconds(minutes=5,seconds=30))
            sender = "Anonymous" if anonymous else ctx.user.name
            embed = discord.Embed(title="Whisper", description="The following message was sent by another user", color=embeds.green)
            embed.add_field(name="Sender", value=sender)
            embed.add_field(name="Message", value=message, inline=False)
            view = discord.ui.View()
            block_button = discord.ui.Button(label="Block User", style=discord.ButtonStyle.red)
            opt_out_button = discord.ui.Button(label="Block All", style=discord.ButtonStyle.red)
            sender_id = ctx.user.id
            async def block(ctx : discord.interactions.Interaction) -> None :
                user_settings_file.block(sender_id)
                await ctx.response.send_message(embed=discord.Embed(title="Blocked user", description="This user can no longer send you whispers", color=embeds.red), ephemeral=True)
            async def opt_out(ctx : discord.interactions.Interaction) -> None :
                user_settings_file.edit_setting("accept_whisper", False)
                await ctx.response.send_message(embed=discord.Embed(title="Blocked all whispers", description="Users can no longer send you whispers", color=embeds.red), ephemeral=True)

            block_button.callback = block
            opt_out_button.callback = opt_out
            view.add_item(block_button)
            view.add_item(opt_out_button)
            await user.send(embed=embed, view=view)
        except :
            await ctx.response.send_message(embed=embeds.error(), ephemeral=True)
            return
    
    else :
        await ctx.response.send_message(embed=embeds.cooldown_error(cooldown.formatted_delta()), ephemeral=True)
        return

    embed = discord.Embed(title="Message sent", description=f'"{message}"', color=embeds.green)
    await ctx.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="block", description="Block a user from sending whispers")
@app_commands.describe(user = "user")
async def unblock(ctx : discord.interactions.Interaction, user : discord.User) -> None :
    user_settings_file = User_Settings("data/data.json", ctx.user.id) 
    user_settings_file.block(user.id)
    await ctx.response.send_message(embed=discord.Embed(title=f'Blocked {user.name}', description="They can no longer send you whispers", color=embeds.red), ephemeral=True)

@client.tree.command(name="unblock", description="Unblock user")
@app_commands.describe(user = "user")
async def unblock(ctx : discord.interactions.Interaction, user : discord.User) -> None :
    user_settings_file = User_Settings("data/data.json", ctx.user.id) 
    user_settings_file.unblock(user.id)
    await ctx.response.send_message(embed=discord.Embed(title=f'Unblocked {user.name}', description="They can now send you whispers", color=embeds.green), ephemeral=True)

@client.tree.command(name="acceptwhispers", description="Choose wether to accept whispers from users")
@app_commands.describe(enable = "[True/False]")
async def unblock(ctx : discord.interactions.Interaction, enable : bool) -> None :
    user_settings_file = User_Settings("data/data.json", ctx.user.id) 
    user_settings_file.edit_setting("accept_whisper", enable)
    await ctx.response.send_message(embed=discord.Embed(title=f'Accept Whispers : {enable}', description="", color=embeds.green if enable else embeds.red), ephemeral=True)

client.run(config.get_token())