import discord
from discord.ext import commands

import time
from random import choice

import default_interactions
import substitutions as default_substitutions
from config import Config
from log import Logs

class LunaBot(commands.Bot) :

    def intercept(self, message : str) -> str | None :
        response = interactions.get_response(message)
        if response : return str(response)
        return None

    def filter_emoji(self, text : str) -> str :
        # Used for tables
        substitution_table = {
            "✨" : "sparkle_emoji "
        }
        for key in substitution_table :
            text = text.replace(key, substitution_table[key])
        return text
    
    def unprompted_message(self) -> str | None :
        # Needs reworking
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
    
    def cleanse_input(self, message : str) -> str :
        message = message.replace(" ", "")
        message = message.lower()
        message = substitutions.substitute(message)
        
        return message
    
    def get_guild_id(self, message_object : discord.Message | discord.interactions.Interaction) -> str | None :
        try :
            return message_object.guild.id
        except :
            return None
    
    def check_permission(self, user : discord.Member) -> bool :
        # Untested
        config_file = Config("data/default/config.json")
        whitelist = config_file.whitelist()
        if user.name in whitelist :
            return True
        if user.guild_permissions.administrator : return True
        return False

from profanity_filter import ProfanityFilter
p_filter = ProfanityFilter(languages=['en'])

interactions = default_interactions.Interactions("data/default/responses.json")
substitutions = default_substitutions.Substitutions("data/default/substitutions.json")
config = Config("data/default/config.json")
console = Logs("logs/")

intents = discord.Intents.all()
intents.message_content = True


client = LunaBot(command_prefix='/', intents=intents)