import discord
from discord import app_commands
from discord.ext import commands

from responses import Responses
from storage import *
import actions
import luna_assets

import os
import time
from io import BytesIO
from random import *
import math
import embeds
    
storage = Storage()

# Configure

config_file_location = f'{storage.get("primary_directory")}{storage.get("config_file")}'

config_file = Storage_File(config_file_location)

TOKEN = config_file.find_content("token")

enable_interactions = config_file.find_content("enable_interactions") == "True"
enable_slash_commands = config_file.find_content("enable_slash_commands") == "True"


class Interaction :
    def __init__(self, response_function : str, description : str = "No Description") -> None :
        self.function = response_function
        self.description = description
    
    def get_reply_content(self) -> str : return self.function()
    def get_description(self) -> str : return self.description
        

class LunaBot(commands.Bot, Responses) :

    last_wished_date = None
    daily_food_timestamp = {}
    play_timestamp = {}
    
    
    def interaction_key(self) -> str :

        # Interactions
        caught_attention = Interaction(self.caught_attention, "Gets Luna's Attention")
        devil_spotted = Interaction(self.demon_spotted, "Luna senses demonic activity")
        reaction = Interaction(self.reaction, "Luna reacts with something cute")
        emoticon_reaction = Interaction(self.emoticon_reaction, "Luna reacts with a cute face")
        grant_sleep = Interaction(self.grant_sleep, "Luna wishes you a good night")
        shiny_spotted = Interaction(self.shiny_spotted, "Luna spots something shiny")
        not_kitten = Interaction(self.not_kitten, "Luna claims she is not that young")
        meow = Interaction(self.meow, "Luna meows")

        intercept = {
                "ps" : caught_attention,
                "luna" : caught_attention,

                "food" : emoticon_reaction,
                "treats" : emoticon_reaction,

                "wozzy" : reaction,
                "lovely" : reaction,
                "omgo" : reaction,

                "hehe" : devil_spotted,

                "night" : grant_sleep,

                "kitten" : not_kitten,

                "meow" : meow,

                ":sparkles:" : shiny_spotted
        }

        return intercept

    def intercept(self, message : str) -> str | None :
        if self.interaction_key().setdefault(message) :
            reply = self.interaction_key().setdefault(message).get_reply_content()
            return reply
        else : return None
    

    def filter_emoji(self, text : str) -> str :
        # Used for tables
        substitution_table = {
            "✨" : "sparkle_emoji "
        }
        for key in substitution_table :
            text = text.replace(key, substitution_table[key])
        return text
    
    def unprompted_message(self) -> str | None :
        system_time = time.localtime()
        if system_time.tm_hour == 0 and not system_time.tm_yday == self.last_wished_date :
            self.last_wished_date = system_time.tm_yday
            return choice([
                "Omgo happy tommorow! I almost forgot ^..^",
                "Happy tmmorw ^_^", 
                "Oh happy tommorrow :)", 
                "hapss tommrwww ~(っ◕‿◕)っ"
                ])
        return None

    def substitutions(self) -> dict[str, str]:
        substitution_table = {
            "✨" : ":sparkles:",
            "✨✨" : ":sparkles:",
            "✨✨✨" : ":sparkles:", 

            "psps" : "ps",
            "pspsps" : "ps",
            "pspspsps" : "ps",

            "lunaa" : "luna",
            "lunaaa" : "luna",

            "hehehe" : "hehe",
            "hehehehe" : "hehe",

            "nightnight" : "night",
            "noight" : "night",
            "noightnoight" : "night",

            "kiten" : "kitten",
            "kitty" : "kitten",
            "kity" : "kitten",

            "meoww" : "meow",
            "meowww" : "meow",
            "mew" : "meow",
            "meww" : "meow",
            "mewww" : "meow"
        }
        return substitution_table
    
    def cleanse_input(self, message : str) -> str :
        message = message.replace(" ", "")
        message = message.lower()

        substitutions = self.substitutions()

        for key in substitutions :
            if message == key :
                message = substitutions[key]
                break
        
        return message
    
    def custom_interaction(self, message : str, user_id : int, server_id : int) -> str | None :
        user_file_name = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_user")}{user_id}.txt'
        server_file_name = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_server")}{server_id}.txt'
        file_name = None
        if os.path.isfile(user_file_name) :
            user_file = Storage_File(user_file_name)
            user_response = user_file.find_content(message)
            if user_response : return choice(user_response.split("|")).strip()

        if os.path.isfile(server_file_name) :
            server_file = Storage_File(server_file_name)
            server_response = server_file.find_content(message)
            if server_response : return choice(server_response.split("|")).strip()
        
        return None
    
    def get_guild_id(self, message_object : discord.Message | discord.interactions.Interaction) -> str | None :
        try :
            return message_object.guild.id
        except :
            return None
    
    def edit_balance(self, user_id : int, amount : int) -> None :
        user_file_name = f'{storage.get("primary_directory")}{storage.get("user_data_directory")}{user_id}.txt'
        user_file = Storage_File(user_file_name)
        if os.path.isfile(user_file_name) and user_file.header_exists("balance") :
            balance = int(user_file.find_content("balance"))
            balance += amount
            if balance < 0 : balance = 0
            user_file.edit_content("balance", str(balance))
        else :
            if amount < 0 : amount = 0
            user_file.add_item("balance", str(amount))
    
    def get_balance(self, user_id : int) -> int :
        user_file_name = f'{storage.get("primary_directory")}{storage.get("user_data_directory")}{user_id}.txt'
        user_file = Storage_File(user_file_name)
        if os.path.isfile(user_file_name) and user_file.header_exists("balance") :
            balance = int(user_file.find_content("balance"))
            return balance
        else :
            return 0
        
    
    async def enact(self, ctx : discord.interactions.Interaction, title : str, action : actions.Action, negative_chance : int) -> int :
        description = action.get_description(ctx.user.name)
        response = None
        reward = None

        positive = randint(1,negative_chance) != 1
        if positive :
            response = action.get_positive()
            reward = action.get_positive_score()
        else :
            response = action.get_negative()
            reward = action.get_negative_score()
        
        embed = discord.Embed(title=title, color=embeds.green)
        embed.add_field(name=description, value=response, inline=False)
        embed.add_field(name="Result", value=f'{reward} {luna_assets.coin_symbol}')
        
        await ctx.response.send_message(embed=embed)

        return reward


intents = discord.Intents.all()
intents.message_content = True


client = LunaBot(command_prefix='/', intents=intents)




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
    if enable_interactions :
        # Intercepts any non-command msgs
        intercept = client.intercept(filtered_input)
        if intercept :
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
        custom_interaction = client.custom_interaction(filtered_input, message.author.id, client.get_guild_id(message))
        if custom_interaction :
            print(f'Received \'{message.content}\'\tFiltered To \'{filtered_input}\'\tReturning \'{custom_interaction}\'')
            await channel.send(custom_interaction)



    
    if enable_slash_commands : await client.process_commands(message) # Process commands after any messages



# Slash Commands

# Info Commands

@client.tree.command(name="interactions", description="Lists all default interactions")
async def interactions(ctx : discord.interactions.Interaction) -> None :
    # Turn the interactions dictionary into a ascii table and send to the channel
    interaction_key = client.interaction_key()
    table = "`\n┌──────────────────────────────┬─────────────────────────────────────────────┐\n├──────────────────────────────┼─────────────────────────────────────────────┤\n"
    for key in interaction_key :
        table += "│{:30s}│{:45s}│\n".format(f' \'{key}\'', f' {interaction_key[key].get_description()}')
        table += "├──────────────────────────────┼─────────────────────────────────────────────┤\n"
    table += "└──────────────────────────────┴─────────────────────────────────────────────┘`"

    try :
        await ctx.response.send_message("**List of interactions :**{}".format(table), ephemeral=True)
    except :
        await ctx.response.send_message("**List of interactions :**", file=discord.File(BytesIO(str.encode(table)), "members.txt"), ephemeral=True)

@client.tree.command(name="substitutions", description="Lists all default substitutions")
async def substitutions(ctx : discord.interactions.Interaction) -> None :
    # Turn the interactions dictionary into a ascii table and send to the channel
    substitution_key = client.substitutions()
    table = "`\n┌─────────────────────────────────────────────┬───────────────┐\n├─────────────────────────────────────────────┼───────────────┤\n"
    for key in substitution_key :
        table += "│{:45s}│{:15s}│\n".format(f' {client.filter_emoji(key)}', f' {substitution_key[key]}')
        table += "├─────────────────────────────────────────────┼───────────────┤\n"
    table += "└─────────────────────────────────────────────┴───────────────┘`"

    try :
        await ctx.response.send_message(f'**List of substitutions :**\n(The following keywords are equivalent){table}', ephemeral=True)
    except :
        await ctx.response.send_message("**List of substitutions :**\n(The following keywords are equivalent)", file=discord.File(BytesIO(str.encode(table)), "members.txt"), ephemeral=True)

@client.tree.command(name="custom_interactions", description="Lists all custom server or user interactions")
@app_commands.describe(type = "[user/server]")
async def custom_interactions(ctx : discord.interactions.Interaction, type : str) -> None :
    type = type.lower()
    server_id = str(client.get_guild_id(ctx))
    user_id = str(ctx.user.id)
    storage_file_name = None

    # Turn the custom interactions text file into a ascii table and send to the channel

    if type == "server" and not server_id == "None" :
        storage_file_name = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_server")}{server_id}.txt'

    elif type == "user" :
        storage_file_name = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_user")}{user_id}.txt'
    
    else : 
        await ctx.response.send_message(embed=embeds.user_server_type_error() , ephemeral=True)
        return

    if not os.path.isfile(storage_file_name) :
        await ctx.response.send_message(embed=embeds.no_interactions(type), ephemeral=True)
        return


    file = open(storage_file_name, "r", encoding="utf-8")
    raw = file.readlines()
    file.close()

    table = "`\n┌──────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────┐\n├──────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤\n"
    for i in range(len(raw)//2) :
        trigger = client.filter_emoji(raw[2*i].replace("\n", "")[1:-1])
        response = client.filter_emoji(raw[2*i+1].replace("\n", ""))
        table += "│{:30s}│{:90s}│\n".format(f' \'{trigger}\'', f' {response}')
        table += "├──────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤\n"
    table += "└──────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────┘`"

    try :
        await ctx.response.send_message(f'**List of {type} interactions :**{table}', ephemeral=True)
    except :
        await ctx.response.send_message(f'**List of {type} interactions :**', file=discord.File(BytesIO(str.encode(table)), "members.txt"), ephemeral=True)

# Say Commands

@client.tree.command(name="hello", description = "Checks Luna is alive and kicking")
async def hello(ctx : discord.interactions.Interaction) -> None :
    await ctx.response.send_message(f'Meow. I\'m here {ctx.user.mention}', ephemeral=True)

@client.tree.command(name="sparkle", description="Adds sparkles (✨) around a message")
@app_commands.describe(message = "Message to sparkle")
async def sparkle(ctx : discord.interactions.Interaction, message : str) -> None :
    await ctx.response.send_message(f':sparkles: {message} :sparkles:')


@client.tree.command(name="make_quirky", description="Types a message out in aLtErNaTiNg CaPs")
@app_commands.describe(message = "Message to make quirky")
async def make_quirky(ctx : discord.interactions.Interaction, message : str) -> None :
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
    await ctx.response.send_message(message)

# Utility Commands

@client.tree.command(name="add_interaction", description="Adds a custom server or user interaction")
@app_commands.describe(type = "[user/server]", trigger = "The phrase Luna looks for", response = "Luna's response")
async def add_interaction(ctx : discord.interactions.Interaction, type : str, trigger : str, response : str) -> None :
    type = type.lower()
    trigger = client.cleanse_input(trigger)
    server_id = str(client.get_guild_id(ctx))
    user_id = str(ctx.user.id)
    storage_file_name = None
    if type == "server" and not server_id == "None" :
        if ctx.user.guild_permissions.administrator :
            storage_file_name = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_server")}{server_id}.txt'
        else :
            await ctx.response.send_message(embed=embeds.permission_error(), ephemeral=True)

    elif type == "user" :
        storage_file_name = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_user")}{user_id}.txt'
        
    else : 
        await ctx.response.send_message(embed=embeds.user_server_type_error() , ephemeral=True)
        return
    
    storage_file = Storage_File(storage_file_name)
    
    if os.path.isfile(storage_file_name) and storage_file.header_exists(trigger) :
        existing_response = storage_file.find_content(trigger)
        storage_file.edit_content(trigger, f'{existing_response} | {response}')
    
    else :
    
        try :
            storage_file.add_item(trigger, response)

        except :
            embed = discord.Embed(title="Uh oh", description="Adding the interaction failed!\n\nPlease check that all characters are in utf-8 format (Most standard characters)", color=embeds.red)
            await ctx.response.send_message(embed=embed , ephemeral=True)
            return
    
    embed = discord.Embed(title=f'Added {type} interaction', description=f'**{trigger}**  :arrow_right:  {response}', color=embeds.green)
    await ctx.response.send_message(embed=embed, ephemeral=(type=="user"))

@client.tree.command(name="delete_interaction", description="Deletes a custom server or user interaction")
@app_commands.describe(type = "[user/server]", trigger = "The phrase to delete")
async def delete_interaction(ctx : discord.interactions.Interaction, type : str, trigger : str) -> None :
    type = type.lower()
    trigger = client.cleanse_input(trigger)
    server_id = str(client.get_guild_id(ctx))
    user_id = str(ctx.user.id)
    storage_file_name = None
    if type == "server" and not server_id == "None" :
        if ctx.user.guild_permissions.administrator :
            storage_file_name = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_server")}{server_id}.txt'
        else :
            await ctx.response.send_message(embed=embeds.permission_error(), ephemeral=True)

    elif type == "user" :
        storage_file_name = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_user")}{user_id}.txt'
        
    else : 
        await ctx.response.send_message(embed=embeds.user_server_type_error() , ephemeral=True)
        return
    
    if not os.path.isfile(storage_file_name) :
        await ctx.response.send_message(embed=embeds.no_interactions(type), ephemeral=True)
        return

    
    storage_file = Storage_File(storage_file_name)

    if storage_file.header_exists(trigger) :
        storage_file.delete_item(trigger)
        embed = discord.Embed(title=f'Deleted interaction', description=f'{type.title()} interaction **{trigger}** has been deleted',color=embeds.red)
        await ctx.response.send_message(embed=embed, ephemeral=(type=="user"))
    else :
        embed = discord.Embed(title="Interaction not found", description=f'{type.title()} interaction **{trigger}** does not exist', color=embeds.amber)
        await ctx.response.send_message(embed=embed, ephemeral=True)

# Economy Commands

@client.tree.command(name="daily_food", description="Gives Luna her daily bowl of food. Hopefully she likes it")
async def daily_food(ctx : discord.interactions.Interaction) -> None :
    user_id = str(ctx.user.id)
    day = time.localtime().tm_yday
    if user_id in client.daily_food_timestamp and client.daily_food_timestamp[user_id] == day :
        embed = discord.Embed(title="Luna's already been fed", description="Wait until tomorrow to feed Luna again", color=embeds.red)
        await ctx.response.send_message(embed=embed, ephemeral=True)
    else :
        client.daily_food_timestamp[user_id] = day
        reward = await client.enact(ctx, "Feed Luna", actions.give_food, 4)
        client.edit_balance(user_id, reward)


@client.tree.command(name="play", description="Play with luna to increase or decrease your Purr Points")
async def play(ctx : discord.interactions.Interaction) -> None :
    user_id = str(ctx.user.id)
    epoch = time.time()
    break_min = 15
    if user_id in client.play_timestamp :
        target_epoch = client.play_timestamp[user_id] + (break_min * 60)
        if epoch < target_epoch :
            embed = discord.Embed(title="Luna's tired", description="Luna needs a break from playing", color=embeds.red)
            embed.add_field(name="Come Back In", value=f'{math.ceil((target_epoch - epoch)/60)} minute(s)')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
    client.play_timestamp[user_id] = epoch
    action_pool = [actions.pet, actions.tease, actions.balloon]
    reward = await client.enact(ctx, "Play with Luna", choice(action_pool), 2)
    client.edit_balance(user_id, reward)

@client.tree.command(name="balance", description="Tells you how many Purr Points is in your wallet")
@app_commands.describe(user = "user")
async def balance(ctx : discord.interactions.Interaction, user : discord.User = None) -> None :
    if user == None :
        user_id = str(ctx.user.id)
        user = ctx.user
    else :
        user_id = user.id

    balance = client.get_balance(user_id)
    embed = discord.Embed(title=f'{user.name}\'s Wallet', description="Wallet Details", color=embeds.green)
    embed.add_field(name="Balance", value=f'{str(balance)} {luna_assets.coin_symbol}', inline=False)
    await ctx.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="leaderboard", description="Lists the richest players on the server")
async def leaderboard(ctx : discord.interactions.Interaction) -> None :

    if ctx.guild == None :
        await ctx.response.send_message(embed=embeds.not_in_server())
        return


    members = ctx.guild.members
    leaderboard = {}
    for member in members:
        user_id = member.id
        user_file_name = f'{storage.get("primary_directory")}{storage.get("user_data_directory")}{user_id}.txt'
        user_file = Storage_File(user_file_name)
        if os.path.isfile(user_file_name) and user_file.header_exists("balance") :
            leaderboard[member] = int(user_file.find_content("balance"))
        
        else :
            leaderboard[member] = 0
    
    leaderboard = dict(sorted(leaderboard.items(), key=lambda x:x[1], reverse=True))
    
    await ctx.response.send_message(embed=embeds.create_leaderboard(leaderboard, ctx.guild.name), ephemeral=True)

@client.tree.command(name="leaderboard_global", description="Lists the richest players globally")
async def leaderboard_global(ctx : discord.interactions.Interaction) -> None :

    directory = f'{storage.get("primary_directory")}{storage.get("user_data_directory")}'
    leaderboard = {}
    for filename in os.listdir(directory) :
        leaderboard[client.get_user(int(filename.replace(".txt", "")))] = int(Storage_File(f'{directory}{filename}').find_content("balance"))
    
    leaderboard = dict(sorted(leaderboard.items(), key=lambda x:x[1], reverse=True))
    
    await ctx.response.send_message(embed=embeds.create_leaderboard(leaderboard, "Discord"), ephemeral=True)

client.run(TOKEN)