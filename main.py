import discord
from discord import app_commands
from discord.ext import commands

from responses import Responses
from storage import Storage

import os
import time
from io import BytesIO
from random import *
    
storage = Storage()

# Configure

config_file_location = "{}{}".format(storage.get("primary_directory"), storage.get("config_file"))

TOKEN = storage.find_content(config_file_location, "token")

enable_interactions = storage.find_content(config_file_location, "enable_interactions") == "True"
enable_slash_commands = storage.find_content(config_file_location, "enable_slash_commands") == "True"


class Interaction :
    def __init__(self, response_function : str, description : str = "No Description") :
        self.function = response_function
        self.description = description
    
    def get_reply_content(self) : return self.function()
    def get_description(self) : return self.description
        

class LunaBot(commands.Bot, Responses) :
    last_wished_date = None
    
    
    def interaction_key(self) :

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

    def intercept(self, message) :
        if self.interaction_key().setdefault(message) :
            reply = self.interaction_key().setdefault(message).get_reply_content()
            return reply
        else : return None
    

    def filter_emoji(self, text) :
        # Used for tables
        substitution_table = {
            "✨" : "sparkle_emoji "
        }
        for key in substitution_table :
            text = text.replace(key, substitution_table[key])
        return text
    
    def unprompted_message(self) :
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

    def substitutions(self) :
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
    
    def cleanse_input(self, message) :
        message = message.replace(" ", "")
        message = message.lower()

        substitutions = self.substitutions()

        for key in substitutions :
            if message == key :
                message = substitutions[key]
                break
        
        return message
    
    def custom_interaction(self, message, user_id, server_id) :
        user_file_name = "{}{}{}{}.txt".format(storage.get("primary_directory"),storage.get("custom_interactions_directory"), storage.get("custom_interactions_user"), user_id)
        server_file_name = "{}{}{}{}.txt".format(storage.get("primary_directory"),storage.get("custom_interactions_directory"), storage.get("custom_interactions_server"), server_id)
        file_name = None
        if os.path.isfile(user_file_name) :
            user_response = storage.find_content(user_file_name, message)
            if user_response : return choice(user_response.split("|")).strip()

        if os.path.isfile(server_file_name) :
            server_response = storage.find_content(server_file_name, message)
            if server_response : return choice(server_response.split("|")).strip()
        
        return None
    
    def get_guild_id(self, message_object) -> str | None :
        try :
            return message_object.guild.id
        except :
            return None


intents = discord.Intents.default()
intents.message_content = True


client = LunaBot(command_prefix='/', intents=intents)




@client.event
async def on_ready():
    # When the bot logs on
    print('Luna is ready')
    try :
        print("Syncing Commands...")
        synced = await client.tree.sync()
        print("Synced {} command(s)".format(str(len(synced))))
    except Exception as e :
        print(e)
        
    
@client.event
async def on_message(message):

    if message.author == client.user : return # Do nothing if the message author is ourselves

    channel = message.channel # Get the channel of the message

    filtered_input = client.cleanse_input(message.content) # Remove spaces and capitals; Preform substitutions

    # Interactions
    if enable_interactions :
        # Intercepts any non-command msgs
        intercept = client.intercept(filtered_input)
        if intercept :
            print("Received \'{}\'\tFiltered To \'{}\'\tReturning \'{}\'".format(message.content, filtered_input, intercept))
            await channel.send(intercept)
    
    # Unprompted messages
    if True :
        unprompted_message = client.unprompted_message()
        if not unprompted_message == None :
            print("Sending Unprompted \'{}\'".format(unprompted_message))
            await channel.send(unprompted_message)
    
    # Custom interactions
    if True :
        custom_interaction = client.custom_interaction(filtered_input, message.author.id, client.get_guild_id(message))
        if custom_interaction :
            print("Received \'{}\'\tFiltered To \'{}\'\tReturning \'{}\'".format(message.content, filtered_input, custom_interaction))
            await channel.send(custom_interaction)



    
    if enable_slash_commands : await client.process_commands(message) # Process commands after any messages



# Slash Commands

# Info Commands

@client.tree.command(name="interactions", description="Lists all default interactions")
async def interactions(ctx) :
    # Turn the interactions dictionary into a ascii table and send to the channel
    interaction_key = client.interaction_key()
    table = "`\n┌──────────────────────────────┬─────────────────────────────────────────────┐\n├──────────────────────────────┼─────────────────────────────────────────────┤\n"
    for key in interaction_key :
        table += "│{:30s}│{:45s}│\n".format(" \'{}\'".format(key), " {}".format(interaction_key[key].get_description()))
        table += "├──────────────────────────────┼─────────────────────────────────────────────┤\n"
    table += "└──────────────────────────────┴─────────────────────────────────────────────┘`"

    try :
        await ctx.response.send_message("**List of interactions :**{}".format(table), ephemeral=True)
    except :
        await ctx.response.send_message("**List of interactions :**", file=discord.File(BytesIO(str.encode(table)), "members.txt"), ephemeral=True)

@client.tree.command(name="substitutions", description="Lists all default substitutions")
async def substitutions(ctx) :
    # Turn the interactions dictionary into a ascii table and send to the channel
    substitution_key = client.substitutions()
    table = "`\n┌─────────────────────────────────────────────┬───────────────┐\n├─────────────────────────────────────────────┼───────────────┤\n"
    for key in substitution_key :
        table += "│{:45s}│{:15s}│\n".format(" {}".format(client.filter_emoji(key)), " {}".format(substitution_key[key]))
        table += "├─────────────────────────────────────────────┼───────────────┤\n"
    table += "└─────────────────────────────────────────────┴───────────────┘`"

    try :
        await ctx.response.send_message("**List of substitutions :**\n(The following keywords are equivalent){}".format(table), ephemeral=True)
    except :
        await ctx.response.send_message("**List of substitutions :**\n(The following keywords are equivalent)", file=discord.File(BytesIO(str.encode(table)), "members.txt"), ephemeral=True)

@client.tree.command(name="custom_interactions", description="Lists all custom server or user interactions")
@app_commands.describe(type = "[user/server]")
async def custom_interactions(ctx, type : str) :
    type = type.lower()
    server_id = str(client.get_guild_id(ctx))
    user_id = str(ctx.user.id)
    storage_file_name = None

    # Turn the custom interactions text file into a ascii table and send to the channel

    if type == "server" and not server_id == "None" :
        storage_file_name = "{}{}{}{}.txt".format(storage.get("primary_directory"),storage.get("custom_interactions_directory"), storage.get("custom_interactions_server"), server_id)

    elif type == "user" :
        storage_file_name = "{}{}{}{}.txt".format(storage.get("primary_directory"),storage.get("custom_interactions_directory"), storage.get("custom_interactions_user"), user_id)
    
    else : 
        await ctx.response.send_message("Invalid `type` argument. Please enter [user/server]", ephemeral=True)
        return

    if not os.path.isfile(storage_file_name) :
        await ctx.response.send_message("{} does not have any custom interactions :(".format(type), ephemeral=True)
        return


    file = open(storage_file_name, "r", encoding="utf-8")
    raw = file.readlines()
    file.close()

    table = "`\n┌──────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────┐\n├──────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤\n"
    for i in range(len(raw)//2) :
        trigger = client.filter_emoji(raw[2*i].replace("\n", "")[1:-1])
        response = client.filter_emoji(raw[2*i+1].replace("\n", ""))
        table += "│{:30s}│{:90s}│\n".format(" \'{}\'".format(trigger), " {}".format(response))
        table += "├──────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤\n"
    table += "└──────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────┘`"

    try :
        await ctx.response.send_message("**List of {} interactions :**{}".format(type, table), ephemeral=True)
    except :
        await ctx.response.send_message("**List of {} interactions :**".format(type), file=discord.File(BytesIO(str.encode(table)), "members.txt"), ephemeral=True)

# Say Commands

@client.tree.command(name="hello", description = "Checks Luna is alive and kicking")
async def hello(ctx):
    await ctx.response.send_message(f'Meow. I\'m here {ctx.user.mention}', ephemeral=True)

@client.tree.command(name="sparkle", description="Adds sparkles (✨) around a message")
@app_commands.describe(message = "Message to sparkle")
async def sparkle(ctx, message : str) :
    await ctx.response.send_message(":sparkles: {} :sparkles:".format(message))


@client.tree.command(name="make_quirky", description="Types a message out in aLtErNaTiNg CaPs")
@app_commands.describe(message = "Message to make quirky")
async def sparkle(ctx, message : str) :
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
async def say(ctx, message : str) :
    await ctx.response.send_message(message)

# Utility Commands

@client.tree.command(name="add_interaction", description="Adds a custom server or user interaction")
@app_commands.describe(type = "[user/server]", trigger = "The phrase Luna looks for", response = "Luna's response")
async def add_interaction(ctx, type : str, trigger : str, response : str) :
    type = type.lower()
    trigger = client.cleanse_input(trigger)
    server_id = str(client.get_guild_id(ctx))
    user_id = str(ctx.user.id)
    storage_file_name = None
    if type == "server" and not server_id == "None" :
        if ctx.user.guild_permissions.administrator :
            storage_file_name = "{}{}{}{}.txt".format(storage.get("primary_directory"),storage.get("custom_interactions_directory"), storage.get("custom_interactions_server"), server_id)
        else :
            await ctx.response.send_message("You must be an Admin to make server-wide interactions", ephemeral=True)

    elif type == "user" :
        storage_file_name = "{}{}{}{}.txt".format(storage.get("primary_directory"),storage.get("custom_interactions_directory"), storage.get("custom_interactions_user"), user_id)
        
    else : 
        await ctx.response.send_message("Invalid `type` argument. Please enter [user/server]" , ephemeral=True)
        return
    
    file = open(storage_file_name, "a", encoding="utf-8")
    
    try :
        file.writelines("<{}>\n{}\n".format(trigger,response))

    except :
        await ctx.response.send_message("Adding the interaction failed!\n\nPlease check that all characters are in utf-8 format (Most standard characters)" , ephemeral=True)
        file.close()
        return
    

    await ctx.response.send_message("Added {} interaction:\n **{}** --> **{}**".format(type, trigger, response), ephemeral=(type=="user"))

@client.tree.command(name="delete_interaction", description="Deletes a custom server or user interaction")
@app_commands.describe(type = "[user/server]", trigger = "The phrase to delete")
async def delete_interaction(ctx, type : str, trigger : str) :
    type = type.lower()
    trigger = client.cleanse_input(trigger)
    server_id = str(client.get_guild_id(ctx))
    user_id = str(ctx.user.id)
    storage_file_name = None
    if type == "server" and not server_id == "None" :
        if ctx.user.guild_permissions.administrator :
            storage_file_name = "{}{}{}{}.txt".format(storage.get("primary_directory"),storage.get("custom_interactions_directory"), storage.get("custom_interactions_server"), server_id)
        else :
            await ctx.response.send_message("You must be an Admin to delete server-wide interactions", ephemeral=True)

    elif type == "user" :
        storage_file_name = "{}{}{}{}.txt".format(storage.get("primary_directory"),storage.get("custom_interactions_directory"), storage.get("custom_interactions_user"), user_id)
        
    else : 
        await ctx.response.send_message("Invalid `type` argument. Please enter [user/server]", ephemeral=True)
        return
    
    file = open(storage_file_name, "r", encoding="utf-8")
    raw = file.readlines()
    file.close()

    file = open(storage_file_name, "w", encoding="utf-8")
    exists = False
    found = False
    for line in raw :
        if line.replace("\n", "") == "<{}>".format(trigger) :
            exists = True
            found = True

        elif found :
            found = False

        else : file.writelines(line)

    file.close()

    if exists :
        await ctx.response.send_message("Deleted {} interaction: **{}**".format(type, trigger), ephemeral=(type=="user"))
    else :
        await ctx.response.send_message("{} interaction: **{}** does not exist.".format(type, trigger), ephemeral=True)
    
client.run(TOKEN)