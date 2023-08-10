from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

from responses import Responses
from storage import *
import actions
import luna_assets
from experience import XP

import os
import time
from io import BytesIO
from random import *
import math
import embeds
import uuid
import asyncio

from profanity_filter import ProfanityFilter
    
storage = Storage()
p_filter = ProfanityFilter(languages=['en'])

custom_interactions_user_path = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_user")}'
custom_interactions_server_path = f'{storage.get("primary_directory")}{storage.get("custom_interactions_directory")}{storage.get("custom_interactions_server")}'
user_data_path = f'{storage.get("primary_directory")}{storage.get("user_data_directory")}'
item_data_path = f'{storage.get("primary_directory")}{storage.get("items_directory")}'
config_file_name = f'{storage.get("primary_directory")}{storage.get("config_file")}'

config_file = Storage_File(config_file_name)

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
    whisper_timestamp = {}
    
    
    def interaction_key(self) -> dict[str, Interaction] :

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
        user_file_name = f'{custom_interactions_user_path}{user_id}.txt'
        server_file_name = f'{custom_interactions_server_path}{server_id}.txt'
        if os.path.isfile(user_file_name) :
            user_file = Storage_File(user_file_name)
            user_response = user_file.find_content(message)
            if user_response : return choice(user_response.split("|")).strip()

            response_dict = user_file.as_dict()
            for item in response_dict :
                if "\contains\\" in item and item.replace("\contains\\", "") in message : return choice(response_dict[item].split("|")).strip()

        if os.path.isfile(server_file_name) :
            server_file = Storage_File(server_file_name)
            server_response = server_file.find_content(message)
            if server_response : return choice(server_response.split("|")).strip()
            response_dict = server_file.as_dict()
            for item in response_dict :
                if "\contains\\" in item and item.replace("\contains\\", "") in message : return choice(response_dict[item].split("|")).strip()
        
        return None
    
    def get_guild_id(self, message_object : discord.Message | discord.interactions.Interaction) -> str | None :
        try :
            return message_object.guild.id
        except :
            return None
    
    def edit_balance(self, user_id : int, amount : int) -> None :
        user_file_name = f'{user_data_path}{user_id}.txt'
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
        user_file_name = f'{user_data_path}{user_id}.txt'
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
        charisma_embed = None

        positive = randint(1,negative_chance) != 1
        if positive :
            response = action.get_positive()
            reward = action.get_positive_score()
            if randint(0,1) == 0 : charisma_embed = self.edit_charisma(ctx, randint(20,100))
        else :
            response = action.get_negative()
            reward = action.get_negative_score()
            if randint(0,2) == 0 : charisma_embed = self.edit_charisma(ctx, randint(-30,-10))
        
        embed = discord.Embed(title=title, color=embeds.green)
        embed.add_field(name=description, value=response, inline=False)
        embed.add_field(name="Result", value=f'{reward} {luna_assets.coin_symbol}')
        
        await ctx.response.send_message(embed=embed)
        if charisma_embed : await ctx.channel.send(embed=charisma_embed)

        return reward

    def edit_charisma(self, ctx : discord.interactions.Interaction, value : int, message = None) -> discord.Embed :
        file_name = f'{user_data_path}{ctx.user.id}.txt'
        user_xp = XP(file_name)
        user_xp.edit(value)
        change_embed = embeds.experience_change(ctx, file_name, value, message)
        return change_embed

intents = discord.Intents.all()
intents.message_content = True


client = LunaBot(command_prefix='/', intents=intents)

class Item :
    def __init__(
              self,
              name : str,
              icon : str,
              type : str,
              description : str = luna_assets.msg_no_description,
              purchasable : bool = False,
              required_level : int = 0,
              cost : int = 0,
              sell_value : int = 0,
              usable : bool = False,
              uses : int = 1,
              cooldown_seconds : int = 0,
              on_use_func = None
              ) -> None:
        
        self.name = name
        self.icon = icon
        self.type = type
        self.description = description
        self.purchasable = purchasable
        self.required_level = required_level
        self.cost = cost
        self.base_sell_value = sell_value
        self.usable = usable
        self.max_uses = uses
        self.cooldown = cooldown_seconds
        self.on_use_func = on_use_func

        self.uses = 0
        self.uuid = None

        self.item_path = item_data_path
        self.user_path = user_data_path
        self.last_used = 0
    
    def exists(self) -> bool :
        if self.uuid and os.path.isfile(f'{self.item_path}{self.uuid}.txt') :
            return True
        return False
    
    def sell_value(self) -> int :
        value = self.base_sell_value * ((self.max_uses - self.uses) / self.max_uses)
        return math.ceil(value)
    
    async def use(self, ctx : discord.interactions.Interaction) -> bool :
        if not self.exists() :
            await ctx.response.send_message(embed=embeds.item_not_exist(), ephemeral=True)
            return False
        if not user_owns_item(ctx.user.id, user_data_path, self) :
            await ctx.response.send_message(embed=embeds.item_not_owned(), ephemeral=True)
            return False
        if not self.usable or self.uses == self.max_uses : return None

        target_epoch = self.last_used + self.cooldown
        epoch = int(time.time())
        if epoch < target_epoch :
            embed = discord.Embed(title="Item on Cooldown", description="", color=embeds.red)
            embed.add_field(name="Come Back In", value=f'{math.ceil((target_epoch - epoch)/60)} minute(s)')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return False
        success = await self.on_use_func(self=self, ctx=ctx)
        if success :
            self.uses += 1
            self.last_used = int(time.time())
        if self.uses == self.max_uses :
            delete_item(item_data_path, f'{user_data_path}{ctx.user.id}.txt', self)
        else :
            update_item(item_data_path, self)
        return success
    
    async def sell(self, ctx : discord.interactions.Interaction) -> None :
        if not self.exists() :
            await ctx.response.send_message(embed=embeds.item_not_exist(), ephemeral=True)
            return None
        if not user_owns_item(ctx.user.id, user_data_path, self) :
            await ctx.response.send_message(embed=embeds.item_not_owned(), ephemeral=True)
            return None
        embed = discord.Embed(title="Sold Item", description=f'Sold **{self.icon} {self.name}** for {self.sell_value()} {luna_assets.coin_symbol}', color=embeds.green)
        client.edit_balance(ctx.user.id, self.sell_value())
        delete_item(item_data_path, f'{user_data_path}{ctx.user.id}.txt', self)
        await ctx.response.send_message(embed=embed, ephemeral=True)
    
    async def purchase(self, ctx : discord.interactions.Interaction) -> None :
        if client.get_balance(ctx.user.id) < self.cost :
            await ctx.response.send_message(embed=embeds.insufficient_funds(), ephemeral=True)
            return None
        user_xp = XP(f'{user_data_path}{ctx.user.id}.txt')
        if user_xp.level() < self.required_level :
            await ctx.response.send_message(embed=embeds.insufficient_level(), ephemeral=True)
            return None
        purchase_embed = discord.Embed(title="Purchased Item", description=f'Bought **{self.icon} {self.name}** for {self.cost} {luna_assets.coin_symbol}', color=embeds.green)
        client.edit_balance(ctx.user.id, -self.cost)
        grant_user_item(item_data_path, user_data_path, ctx.user.id, self)
        await ctx.response.send_message(embeds=(purchase_embed, self.inventory_item_info()), view=self.inventory_item_options(), ephemeral=True)
    
    def inventory_item_info(self) :
        info_embed = discord.Embed(title=f'{self.icon} {self.name}', description=f'{self.description}\n{luna_assets.invisible_char*70}', color=embeds.cyan)
        if self.usable :
            info_embed.add_field(name="Uses", value=f'{self.max_uses-self.uses}/{self.max_uses}')
        else :
            info_embed.add_field(name="Uses", value="None")
        info_embed.add_field(name="Sell Value", value=f'{self.sell_value()} {luna_assets.coin_symbol}')
        return info_embed
    
    def inventory_item_options(self) -> discord.ui.View :
        view = discord.ui.View()
        if self.usable :
            use_button = discord.ui.Button(label="Use", style=discord.ButtonStyle.blurple)
            use_button.callback = self.use
            view.add_item(use_button)
        sell_button = discord.ui.Button(label=f'{self.sell_value()} Sell', style=discord.ButtonStyle.green, emoji=luna_assets.coin_symbol)
        sell_button.callback = self.sell
        view.add_item(sell_button)

        return view
    
    def shop_item_info(self) -> discord.Embed :
        info_embed = discord.Embed(title=f'{self.icon} {self.name}', description=f'{self.description}\n{luna_assets.invisible_char*70}', color=embeds.cyan)
        info_embed.add_field(name="Cost", value=f'{self.cost} {luna_assets.coin_symbol}')
        if self.usable :
            info_embed.add_field(name="Uses", value=f'{self.max_uses}')
        else :
            info_embed.add_field(name="Uses", value="None")
        info_embed.add_field(name="Req. Level", value=f'{self.required_level}', inline=False)
        return info_embed
    
    def shop_item_options(self) -> discord.ui.View :
        purchase_button = discord.ui.Button(label=f'{self.cost} Buy', style=discord.ButtonStyle.green, emoji=luna_assets.coin_symbol)
        purchase_button.callback = self.purchase
        view = discord.ui.View()
        view.add_item(purchase_button)

        return view
    
    def all_item_info(self) -> discord.Embed :
        info_embed = discord.Embed(title=f'{self.icon} {self.name}', description=f'{self.description}\n{luna_assets.invisible_char*70}', color=embeds.cyan)
        info_embed.add_field(name="Purchasable", value=f'{self.purchasable}')
        info_embed.add_field(name="Req. Level", value=f'{self.required_level}')
        info_embed.add_field(name="Cost", value=f'{self.cost} {luna_assets.coin_symbol}', inline=False)
        info_embed.add_field(name="Sell Value", value=f'{self.sell_value()} {luna_assets.coin_symbol}', inline=False)
        if self.usable :
            info_embed.add_field(name="Uses", value=f'{self.max_uses-self.uses}/{self.max_uses}', inline=False)
        else :
            info_embed.add_field(name="Uses", value="None", inline=False)
        return info_embed

    def debug_item_info(self) -> discord.Embed :
        info_embed = discord.Embed(title=f'{self.icon} {self.name}', description=f'{self.description}\n{luna_assets.invisible_char*70}', color=embeds.cyan)
        info_embed.add_field(name="Type", value=f'{self.type}')
        info_embed.add_field(name="Purchasable", value=f'{self.purchasable}')
        info_embed.add_field(name="Req. Level", value=f'{self.required_level}')
        info_embed.add_field(name="Cost", value=f'{self.cost} {luna_assets.coin_symbol}')
        info_embed.add_field(name="Base Sell Value", value=f'{self.base_sell_value} {luna_assets.coin_symbol}', inline=False)
        info_embed.add_field(name="Sell Value", value=f'{self.sell_value()} {luna_assets.coin_symbol}')
        info_embed.add_field(name="Usable", value=f'{self.usable}')
        info_embed.add_field(name="Max. Uses", value=f'{self.max_uses}')
        info_embed.add_field(name="Uses", value=f'{self.uses}')
        info_embed.add_field(name="Use Func.", value=f'{self.on_use_func}', inline=False)
        return info_embed

def items() -> dict[str, Item] :
        async def basic_fish(self : Item, ctx : discord.interactions.Interaction) -> bool :
            action_embed = discord.Embed(title=f'{ctx.user.name} is fishing', description="They cast their line into the water", color=embeds.gold)
            common = ["fish"]
            uncommon = ["shrimp", "tropical_fish", "crab", "puffer_fish"]
            frequency = [common, common, uncommon]
            catch = choice(choice(frequency))
            item = find_item(catch)
            grant_user_item(item_data_path, user_data_path, ctx.user.id, item)
            await ctx.response.send_message(embeds=(action_embed, embeds.gained_item(ctx), item.inventory_item_info(), client.edit_charisma(ctx, randint(10,30))))
            return True
        
        async def advanced_fish(self : Item, ctx : discord.interactions.Interaction) -> bool :
            action_embed = discord.Embed(title=f'{ctx.user.name} is fishing', description="They cast their line into the water", color=embeds.gold)
            common = ["fish"]
            uncommon = ["shrimp", "tropical_fish", "crab", "puffer_fish"]
            rare = ["squid", "lobster", "octopus"]
            frequency = [common, common, common, uncommon, uncommon, rare]
            catch = choice(choice(frequency))
            item = find_item(catch)
            grant_user_item(item_data_path, user_data_path, ctx.user.id, item)
            await ctx.response.send_message(embeds=(action_embed, embeds.gained_item(ctx), item.inventory_item_info(), client.edit_charisma(ctx, randint(10,30))))
            return True

        async def feed_luna_fish(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} feeds Luna a delicious fish', description="She happily eats it", color=embeds.gold)
            await ctx.response.send_message(embeds=(embed, client.edit_charisma(ctx, randint(20,60))))
            return True
        async def scratch(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} gives Luna something to scratch', description="She digs in her claws", color=embeds.gold)
            await ctx.response.send_message(embeds=(embed, client.edit_charisma(ctx, randint(10,30))))
            return True
        
        async def treats(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} gives Luna a treat', description="She gobbles it up", color=embeds.gold)
            await ctx.response.send_message(embeds=(embed, client.edit_charisma(ctx, randint(40,90))))
            return True

        async def yarn(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} gives Luna a ball of blue yarn', description="She bats it around the room", color=embeds.gold)
            await ctx.response.send_message(embeds=(embed, client.edit_charisma(ctx, randint(20,40))))
            return True
        
        async def mouse(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} gives Luna a toy mouse', description="She bats it around the room", color=embeds.gold)
            await ctx.response.send_message(embeds=(embed, client.edit_charisma(ctx, randint(20,40))))
            return True
        
        async def laser(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} points a laser near Luna', description="She chases it", color=embeds.gold)
            await ctx.response.send_message(embeds=(embed, client.edit_charisma(ctx, randint(30,80))))
            return True
                
        items = [
            Item("Basic Fishing Rod", luna_assets.fishing_rod, "basic_fishing_rod", description="Used to catch fish. Cannot catch large fish", purchasable=True, cost=200, sell_value=75, usable=True, uses=3, cooldown_seconds=300, on_use_func=basic_fish),
            Item("Advanced Fishing Rod", luna_assets.advanced_fishing_rod, "advanced_fishing_rod", description="Used to catch fish. Can catch larger fish", purchasable=True, required_level=6, cost=500, sell_value=250, usable=True, uses=10, cooldown_seconds=240, on_use_func=advanced_fish),
            Item("Fish", luna_assets.fish, "fish", description="A fish to feed to Luna", usable=True, sell_value=15, uses=1, on_use_func=feed_luna_fish),
            Item("Shrimp", luna_assets.shrimp, "shrimp", description="A small shrimp", sell_value=60),
            Item("Tropical Fish", luna_assets.tropical_fish, "tropical_fish", description="A rare tropical fish", sell_value=100),
            Item("Crab", luna_assets.crab, "crab", description="A chill crab", sell_value=100),
            Item("Puffer Fish", luna_assets.puffer, "puffer_fish", description="A spiky puffer fish", sell_value=120),
            Item("Squid", luna_assets.squid, "squid", description="A small squid", sell_value=350),
            Item("Lobster", luna_assets.lobster, "lobster", description="A large lobster", sell_value=500),
            Item("Octopus", luna_assets.octopus, "octopus", description="A large octopus", sell_value=650),
            Item("Cardboard Scratch Box", luna_assets.cardboard_box, "scratch_box", description="Some cardboard for Luna to scratch", purchasable=True, cost=150, sell_value=60, usable=True, uses=2, cooldown_seconds=180, on_use_func=scratch),
            Item("Scratch Post", luna_assets.wooden_frame, "scratch_post", description="A wooden post for Luna to scratch", purchasable=True, required_level=3, cost=250, sell_value=100, usable=True, uses=8, cooldown_seconds=120, on_use_func=scratch),
            Item("Treats", luna_assets.treats_can, "treats_can", description="A small tin of treats to feed Luna", purchasable=True, required_level=4, cost=300, sell_value=120, usable=True, uses=5, cooldown_seconds=600, on_use_func=treats),
            Item("Jar of Treats", luna_assets.treats_jar, "treats_jar", description="A jar of treats to feed Luna", purchasable=True, required_level=7, cost=550, sell_value=225, usable=True, uses=15,cooldown_seconds=600, on_use_func=treats),
            Item("Yarn", luna_assets.yarn, "yarn", description="A ball of yarn", purchasable=True, cost=75, sell_value=25, usable=True, uses=1, on_use_func=yarn),
            Item("Toy Mouse", luna_assets.mouse, "mouse", description="A toy mouse made from yarn", purchasable=True, required_level=2, cost=150, sell_value=80, usable=True, uses=4, cooldown_seconds=120, on_use_func=mouse),
            Item("Laser Pointer", luna_assets.laser_pointer, "laser_pointer", description="A laser pointer Luna loves to chase", purchasable=True, required_level=8, cost=750, sell_value=400, usable=True, uses=15, cooldown_seconds=120, on_use_func=laser)
        ]

        items_table = {}
        for item in items :
            items_table[item.type] = item

        return items_table

def find_item(type : str) -> Item :
    return items().setdefault(type)

def create_item(item_path : str, item : Item) -> uuid.UUID :
    item.uuid = uuid.uuid4()
    file_name = f'{item_path}{item.uuid}.txt'
    item_file = Storage_File(file_name)
    item_file.add_item("type", item.type)
    if item.usable :
        item_file.add_item("uses", str(item.uses))
        item_file.add_item("last_used", str(item.last_used))
    return item.uuid

def update_item(item_path : str, item : Item) :
    if not item.uuid : raise ValueError("Item has no associated UUID")
    file_name = f'{item_path}{item.uuid}.txt'
    item_file = Storage_File(file_name)
    item_file.edit_content("type", item.type)
    item_file.edit_content("uses", str(item.uses))
    item_file.edit_content("last_used", str(item.last_used))

def delete_item(item_path : str, user_file_name : str, item : Item) -> None :
    if not item.uuid : raise ValueError("Item has no associated UUID")
    item_file_name = f'{item_path}{item.uuid}.txt'
    os.remove(item_file_name)

    user_file = Storage_File(user_file_name)
    uuids = user_file.find_content("inventory").split("|")
    line = ""
    for uuid in uuids :
        uuid = uuid.strip()
        if not uuid == str(item.uuid) and not uuid == "" :
            line += f'{uuid} | '
    user_file.edit_content("inventory", line)


def get_item(item_path : str, uuid : str) -> Item | None :
    file_name = f'{item_path}{uuid}.txt'
    item = None
    if not os.path.isfile(file_name) : return None
    
    item_file = Storage_File(file_name)
    item_type = item_file.find_content("type")
    item = items()[item_type]
    item.uuid = uuid
    if item.usable :
        item.uses = int(item_file.find_content("uses"))
        item.last_used = int(item_file.find_content("last_used"))

    return item

def grant_user_item(item_path : str, user_path : str, user_id : int, item : Item) -> None :
    uuid = create_item(item_path, item)
    user_file_name = f'{user_path}{user_id}.txt'
    user_file = Storage_File(user_file_name)
    if user_file.header_exists("inventory") :
        prev_data = user_file.find_content("inventory")
        user_file.edit_content("inventory", f'{prev_data}{uuid} | ')
    else :
        user_file.add_item("inventory", f'{uuid} | ')

def user_owns_item(user_id : int, user_path : str, item : Item) -> bool :
    user_file_name = f'{user_path}{user_id}.txt'
    user_file = Storage_File(user_file_name)
    if user_file.header_exists("inventory") :
        raw = user_file.find_content("inventory")
        for uuid in raw.split("|") :
            uuid = uuid.strip()
            if uuid == str(item.uuid) : return True
    return False



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
            if randint(0,3) == 0 :
                user_xp = XP(f'{user_data_path}{message.author.id}.txt')
                user_xp.edit(randint(10,20))
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
        storage_file_name = f'{custom_interactions_server_path}{server_id}.txt'

    elif type == "user" :
        storage_file_name = f'{custom_interactions_user_path}{user_id}.txt'
    
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
    if not p_filter.is_clean(response) :
        await ctx.response.send_message(embed=embeds.profound_error() , ephemeral=True)
        return

    type = type.lower()
    trigger = client.cleanse_input(trigger)
    server_id = str(client.get_guild_id(ctx))
    user_id = str(ctx.user.id)
    storage_file_name = None
    if type == "server" and not server_id == "None" :
        if ctx.user.guild_permissions.administrator :
            storage_file_name = f'{custom_interactions_server_path}{server_id}.txt'
        else :
            await ctx.response.send_message(embed=embeds.permission_error(), ephemeral=True)

    elif type == "user" :
        storage_file_name = f'{custom_interactions_user_path}{user_id}.txt'
        
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
            storage_file_name = f'{custom_interactions_server_path}{server_id}.txt'
        else :
            await ctx.response.send_message(embed=embeds.permission_error(), ephemeral=True)

    elif type == "user" :
        storage_file_name = f'{custom_interactions_user_path}{user_id}.txt'
        
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

@client.tree.command(name="whisper", description="Send an anonymous DM to another member")
@app_commands.describe(user = "user", message = "Message to send")
async def play(ctx : discord.interactions.Interaction, user : discord.User, message : str) -> None :
    user_id = ctx.user.id
    epoch = time.time()
    break_min = 120
    if user_id in client.whisper_timestamp :
        target_epoch = client.whisper_timestamp[user_id] + (break_min * 60)
        if epoch < target_epoch :
            time_in_seconds = target_epoch - epoch
            mins = math.floor((time_in_seconds/60)%60)
            hours = int(time_in_seconds//3600)
            if hours == 0 : hours = ""
            else : hours = f'{hours} hour(s)'
            embed = discord.Embed(title="Easy there", description="Let's not be sending too many secret messages", color=embeds.red)
            embed.add_field(name="Come Back In", value=f'{hours} {mins} minute(s)')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
    try :
        await user.send(message)
    except :
        embed = discord.Embed(title="Uh oh!", description="Something went wrong and the message was not sent, please try again later", color=embeds.red)
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return
    
    client.whisper_timestamp[user_id] = epoch

    embed = discord.Embed(title="Message sent", description="Lets hope they like it", color=embeds.green)
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
        user_file_name = f'{user_data_path}{user_id}.txt'
        user_file = Storage_File(user_file_name)
        if os.path.isfile(user_file_name) and user_file.header_exists("balance") :
            leaderboard[member] = int(user_file.find_content("balance"))
        
        else :
            leaderboard[member] = 0
    
    leaderboard = dict(sorted(leaderboard.items(), key=lambda x:x[1], reverse=True))
    
    await ctx.response.send_message(embed=embeds.create_leaderboard(leaderboard, ctx.guild.name), ephemeral=True)

@client.tree.command(name="leaderboard_global", description="Lists the richest players globally")
async def leaderboard_global(ctx : discord.interactions.Interaction) -> None :

    directory = user_data_path
    leaderboard = {}
    for filename in os.listdir(directory) :
        leaderboard[client.get_user(int(filename.replace(".txt", "")))] = int(Storage_File(f'{directory}{filename}').find_content("balance"))
    
    leaderboard = dict(sorted(leaderboard.items(), key=lambda x:x[1], reverse=True))
    
    await ctx.response.send_message(embed=embeds.create_leaderboard(leaderboard, "Discord"), ephemeral=True)

# XP

@client.tree.command(name="experience", description="Displays your current Charisma (XP) level")
async def experience(ctx : discord.interactions.Interaction) -> None :
    await ctx.response.send_message(embed=embeds.experience_info(ctx, f'{user_data_path}{ctx.user.id}.txt'), ephemeral=False)

# Items

@client.tree.command(name="inventory", description="Lists the items in your inventory and the actions you can preform")
async def inventory(ctx : discord.interactions.Interaction) -> None :
    if not client.get_guild_id(ctx) :
        await ctx.response.send_message(embed=embeds.not_in_server(), ephemeral=True)
        return None
    user_file_name = f'{user_data_path}{ctx.user.id}.txt'
    user_file = Storage_File(user_file_name)
    if os.path.isfile(user_file_name) and user_file.header_exists("inventory") :

        page = 0
        embed = discord.Embed(title="Please Wait", description="Generating inventory...", color=embeds.amber)
        await ctx.response.send_message(embed=embed, ephemeral=True)

        message = await ctx.channel.send(embed=embeds.menu_navigator(ctx))
        controls = ["◀️","⏹","▶️","🔄"]
        for control in controls :
            await message.add_reaction(control)

        # https://stackoverflow.com/a/67451379
        while not client.is_closed() :
            raw = user_file.find_content("inventory")
            if not raw :
                await ctx.edit_original_response(content="", embed=embeds.no_items(), view=None)
                await message.delete()
                return None
            inventory_uuids = raw.split("|")
            item_embeds = []
            item_actions = []
            for uuid in inventory_uuids :
                uuid = str(uuid).strip()
                if uuid == "" : continue
                path = item_data_path
                item = get_item(path, uuid)
                if item :
                    item_embeds.append(item.inventory_item_info())
                    item_actions.append(item.inventory_item_options())
            if len(item_embeds) == 0 :
                await ctx.edit_original_response(content="", embed=embeds.no_items(), view=None)
                await message.delete()
                return None
            
            if page >= len(item_embeds) : page = len(item_embeds) - 1

            await ctx.edit_original_response(content=f'Page {page+1} of {len(item_embeds)}', embed=item_embeds[page], view=item_actions[page])

            async def close() :
                await message.delete()
                await ctx.edit_original_response(content="", embed=embeds.window_closed(), view=None)
            try :
                react, user = await client.wait_for(
                    "reaction_add",
                    timeout = 90.0,
                    check = lambda r, u: r.emoji in controls and u.id == ctx.user.id and r.message.id == message.id
                )

                if react.emoji == controls[0] and page > 0:
                    page -= 1
                elif react.emoji == controls[1]:
                    await close()
                    break
                elif react.emoji == controls[2] and page < len(item_embeds) - 1:
                    page += 1
                
                await message.remove_reaction(react.emoji, user)

            except asyncio.TimeoutError:
                await close()
                break
            
        return None
    
    await ctx.response.send_message(embed=embeds.no_items(), ephemeral=True)

@client.tree.command(name="shop", description="Opens the item shop where you can spen your Purr Points")
async def shop(ctx : discord.interactions.Interaction) -> None :
    if not client.get_guild_id(ctx) :
        await ctx.response.send_message(embed=embeds.not_in_server(), ephemeral=True)
        return None
    user_file_name = f'{user_data_path}{ctx.user.id}.txt'
    user_file = Storage_File(user_file_name)

    page = 0
    embed = discord.Embed(title="Please Wait", description="Generating shop...", color=embeds.amber)
    await ctx.response.send_message(embed=embed, ephemeral=True)

    message = await ctx.channel.send(embed=embeds.menu_navigator(ctx))
    controls = ["◀️","⏹","▶️","🔄"]
    for control in controls :
        await message.add_reaction(control)

    # https://stackoverflow.com/a/67451379
    while not client.is_closed() :
        item_embeds = []
        item_actions = []
        for item_id in items() :
            item = find_item(item_id)
            if item.purchasable :
                item_embeds.append(item.shop_item_info())
                item_actions.append(item.shop_item_options())
        
        if page >= len(item_embeds) : page = len(item_embeds) - 1

        balance_embed = discord.Embed(title="Balance",description=f'{client.get_balance(ctx.user.id)} {luna_assets.coin_symbol}')
        await ctx.edit_original_response(content=f'Page {page+1} of {len(item_embeds)}', embeds=(balance_embed, item_embeds[page]), view=item_actions[page])

        async def close() :
                await message.delete()
                await ctx.edit_original_response(content="", embed=embeds.window_closed(), view=None)
        try :
            react, user = await client.wait_for(
                "reaction_add",
                timeout = 90.0,
                check = lambda r, u: r.emoji in controls and u.id == ctx.user.id and r.message.id == message.id
            )

            if react.emoji == controls[0] and page > 0:
                page -= 1
            elif react.emoji == controls[1]:
                await close()
                break
            elif react.emoji == controls[2] and page < len(item_embeds) - 1:
                page += 1
            
            await message.remove_reaction(react.emoji, user)

        except asyncio.TimeoutError:
            await close()
            break

client.run(TOKEN)