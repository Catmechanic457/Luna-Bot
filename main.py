import discord
from discord import app_commands
from discord.ext import commands

import time
from random import *

class Storage :
    def __init__(self, primary_directory = "data/", settings_file = "settings.txt", config_file = "config.txt") :
        self.directory_lookup = {
            "primary_directory" : primary_directory,
            "settings_file" : settings_file,
            "config_file" : config_file
        }
    
    def get(self, item_id : str) :
        return self.directory_lookup[item_id]
    
    def find_content(self, file_location, header : str) :
        file = open(file_location, "r")
        all_content = file.readlines()
        file.close()
        found_header = False
        for item in all_content :
            if not found_header :
                if item.replace("\n", "") == "<{}>".format(header) :
                    found_header = True
            else : return item.replace("\n", "")
    
storage = Storage()

# Configure

config_file_location = "{}{}".format(storage.get("primary_directory"), storage.get("config_file"))

TOKEN = storage.find_content(config_file_location, "token")

enable_interactions = storage.find_content(config_file_location, "enable_interactions") == "True"
enable_slash_commands = storage.find_content(config_file_location, "enable_slash_commands") == "True"


class Interaction :
    def __init__(self, function : str, description : str = "No Description") :
        self.function = function
        self.description = description
    
    def get_reply_content(self) : return self.function()
    def get_description(self) : return self.description
        

class LunaBot(commands.Bot) :
    last_wished_date = None
    def caught_attention(self) -> str :
        response_pool = [
            "Huh? What?",
            "You Called?",
            "You Needed Me?",
            "What? Where?",
            "What is it?",
            "I SWEAR I JUST HEARD MY NAME",
            "WHO SAID THAT?"
        ]
        return choice(response_pool)
    
    def demon_spotted(self) -> str :
        response_pool = [
            "Stay back, Demon!",
            "That's the laugh of the devil...",
            "Ahhh! Demon!",
            "Get away ya Demon!",
            "nonono You Get back, Demon!",
            "Why does that laugh sound so demonic?",
            "\*hisses\*"
        ]
        return choice(response_pool)
    
    def shiny_spotted(self) -> str :
        response_pool = [
            "Omgo it's sparkly!",
            "^_^ Sparkly",
            "Ohh it shiny",
            ":sparkles:",
            ":sparkles: :sparkles:",
            ":sparkles: :sparkles: :sparkles:"
        ]
        return choice(response_pool)
    
    def reaction(self) -> str :
        response_pool = [
            "OMGO",
            "omgo",
            "lovley",
            "woozy",
            ":sparkles: wozzy :sparkles:",
            ":sparkles: lovely :sparkles:",
            "^_^",
            ":sparkles:",
            ":sparkles: :sparkles:",
            ":sparkles: :sparkles: :sparkles:"
        ]
        return choice(response_pool)
    
    def emoticon_reaction(self) -> str :
        response_pool = [
            "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "^_^",
            "=^..^=",
            "~(^._.)",
            "(っ◕‿◕)っ",
            "=^..^= ~(^._.) (っ◕‿◕)っ"
        ]
        return choice(response_pool)
        
    
    def grant_sleep(self) -> str :
        response_pool = [
            "Night",
            "Night Night",
            "Noight",
            "Noight Noight",
            "Ima go slep too",
            "Yes... Sleep, Child"
        ]
        return choice(response_pool)
    
    def interaction_key(self) :

        # Interactions
        caught_attention = Interaction(self.caught_attention, "Gets Luna's Attention")
        devil_spotted = Interaction(self.demon_spotted, "Luna senses demonic activity")
        reaction = Interaction(self.reaction, "Luna reacts with something cute")
        emoticon_reaction = Interaction(self.emoticon_reaction, "Luna reacts with a cute face")
        grant_sleep = Interaction(self.grant_sleep, "Luna wishes you a good night")
        shiny_spotted = Interaction(self.shiny_spotted, "Luna spots something shiny")

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
            "noightnoight" : "night"
        }
        return substitution_table
    
    def cleanse_input(self, message) :
        message = message.strip()
        message = message.lower()

        substitutions = self.substitutions()

        for key in substitutions :
            if message == key :
                message = substitutions[key]
                break
        
        return message


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
    print("Received :", message.content)

    # Interactions
    if enable_interactions :
        # Intercepts any non-command msgs
        intercept = client.intercept(client.cleanse_input(message.content))
        if intercept :
            await channel.send(intercept)
    
    # Unprompted messages
    if True :
        unprompted_message = client.unprompted_message()
        if not unprompted_message == None :
            await channel.send(unprompted_message)


    
    if enable_slash_commands : await client.process_commands(message) # Process commands after any messages

# Slash Commands

@client.tree.command(name="hello")
async def hello(ctx):
    await ctx.response.send_message(f'Meow. I\'m here {ctx.user.mention}')


@client.tree.command(name="interactions")
async def interactions(ctx) :
    # Turn the interactions dictionary into a ascii table and send to the channel
    interaction_key = client.interaction_key()
    table = "**List of interactions :**`\n┌──────────────────────────────┬─────────────────────────────────────────────┐\n├──────────────────────────────┼─────────────────────────────────────────────┤\n"
    for key in interaction_key :
        table += "│{:30s}│{:45s}│\n".format(" \'{}\'".format(key), " {}".format(interaction_key[key].get_description()))
        table += "├──────────────────────────────┼─────────────────────────────────────────────┤\n"
    table += "└──────────────────────────────┴─────────────────────────────────────────────┘`"

    await ctx.response.send_message(table)

@client.tree.command(name="substitutions")
async def substitutions(ctx) :
    # Turn the interactions dictionary into a ascii table and send to the channel
    substitution_key = client.substitutions()
    table = "**List of substitutions :**\n(The following keywords are equivalent)`\n┌─────────────────────────────────────────────┬───────────────┐\n├─────────────────────────────────────────────┼───────────────┤\n"
    for key in substitution_key :
        table += "│{:45s}│{:15s}│\n".format(" {}".format(client.filter_emoji(key)), " {}".format(substitution_key[key]))
        table += "├─────────────────────────────────────────────┼───────────────┤\n"
    table += "└─────────────────────────────────────────────┴───────────────┘`"

    await ctx.response.send_message(table)

@client.tree.command(name="sparkle")
@app_commands.describe(message = "Message to sparkle")
async def sparkle(ctx, message : str) :
    await ctx.response.send_message(":sparkles: {} :sparkles:".format(message))

@client.tree.command(name="make_quirky")
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

    
client.run(TOKEN)