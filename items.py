import discord

import math
import time
import uuid
import asyncio
from random import choice, randint

import luna_assets
from luna import *
import embeds
import experience
from data_root import Data
from economy import Balance

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

        self.last_used = 0
    
    def sell_value(self) -> int :
        value = self.base_sell_value * ((self.max_uses - self.uses) / self.max_uses)
        return math.ceil(value)
    
    async def use(self, ctx : discord.interactions.Interaction) -> bool :
        # Get user inventory
        inventory_file = Inventory("data/data.json", ctx.user.id)

        # Catch not in inventory
        if not inventory_file.user_owns(self) :
            await ctx.response.send_message(embed=embeds.item_not_owned(), ephemeral=True)
            return False
        
        # Catch not usable
        if not self.usable or self.uses == self.max_uses : return False

        # Catch cooldown
        target_epoch = self.last_used + self.cooldown
        epoch = int(time.time())
        if epoch < target_epoch :
            embed = discord.Embed(title="Item on Cooldown", description="", color=embeds.red)
            embed.add_field(name="Come Back In", value=f'{math.ceil((target_epoch - epoch)/60)} minute(s)')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return False
        
        # Try function
        success = await self.on_use_func(self=self, ctx=ctx)

        # Add 1 to uses if successful
        if success :
            self.uses += 1
            self.last_used = int(time.time())

        # Update or delete item
        if self.uses == self.max_uses :
            inventory_file.delete_item(self)
        else :
            inventory_file.set_item(self)
        return success
    
    async def sell(self, ctx : discord.interactions.Interaction) -> None :
        # Get user inventory
        inventory_file = Inventory("data/data.json", ctx.user.id)

        # Catch not in inventory
        if not inventory_file.user_owns(self) :
            await ctx.response.send_message(embed=embeds.item_not_owned(), ephemeral=True)
            return False
        
        inventory_file.delete_item(self)
        
        embed = discord.Embed(title="Sold Item", description=f'Sold **{self.icon} {self.name}** for {self.sell_value()} {luna_assets.coin_symbol}', color=embeds.green)
        balance_file = Balance("data/data.json", ctx.user.id)
        balance_file.edit(self.sell_value())
        await ctx.response.send_message(embed=embed, ephemeral=True)
    
    async def purchase(self, ctx : discord.interactions.Interaction) -> None :
        user_xp = experience.Experience("data/data.json", ctx.user.id)
        if user_xp.level() < self.required_level :
            await ctx.response.send_message(embed=embeds.insufficient_level(), ephemeral=True)
            return None
        
        balance_file = Balance("data/data.json", ctx.user.id)

        if balance_file.get() < self.cost :
            await ctx.response.send_message(embed=embeds.insufficient_funds(), ephemeral=True)
            return None
        balance_file.edit(-self.cost)
        
        purchase_embed = discord.Embed(title="Purchased Item", description=f'Bought **{self.icon} {self.name}** for {self.cost} {luna_assets.coin_symbol}', color=embeds.green)
        inventory_file = Inventory("data/data.json", ctx.user.id)
        inventory_file.create_item(self)
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

class Inventory(Data) :
    def __init__(self, directory: str, id : int) -> None :
        self.id = str(id)
        super().__init__(directory)

        # Add the item if it doesn't exist
        if not self.item_exists("user", self.id) :
            self.add_item("user", self.id)
        
        if not "inventory" in self.data()["user"][self.id] :
            data = self.data()
            data["user"][self.id]["inventory"] = {}
            self.write(data)

    def __len__(self) -> int :
        return len(self.get())
    
    def get(self) -> dict[str, dict]:
        return self.data()["user"][self.id]["inventory"]
    
    def create_item(self, item : Item) -> None :
        item.uuid = uuid.uuid4()
        self.set_item(item)
    
    def set_item(self, item : Item) -> None :
        data = self.data()
        data["user"][self.id]["inventory"][str(item.uuid)] = {
            "type" : item.type,
            "uses" : item.uses,
            "last_used" : item.last_used
        }
        self.write(data)

    def delete_item(self, item : Item) -> None :
        data = self.data()
        data["user"][self.id]["inventory"].pop(str(item.uuid))
        self.write(data)


    def get_item(self, uuid : uuid.UUID) -> Item :
        item_info = self.get()[uuid]
        item = find_item(item_info["type"])
        item.uuid = uuid
        item.uses = item_info["uses"]
        item.last_used = item_info["last_used"]
        
        return item
    
    def user_owns(self, item : Item) -> bool :
        return str(item.uuid) in self.get()

def items() -> dict[str, Item] :
        async def basic_fish(self : Item, ctx : discord.interactions.Interaction) -> bool :
            action_embed = discord.Embed(title=f'{ctx.user.name} is fishing', description="They cast their line into the water", color=embeds.amber)
            common = ["fish"]
            uncommon = ["shrimp", "tropical_fish", "crab", "puffer_fish"]
            frequency = [common, common, uncommon]
            catch = choice(choice(frequency))
            item = find_item(catch)
            inventory_file = Inventory("data/data.json", ctx.user.id)
            inventory_file.create_item(item)
            await ctx.response.send_message(embeds=(action_embed, embeds.gained_item(ctx), item.inventory_item_info(), experience.edit_charisma(ctx, randint(10,30))))
            return True
        
        async def advanced_fish(self : Item, ctx : discord.interactions.Interaction) -> bool :
            action_embed = discord.Embed(title=f'{ctx.user.name} is fishing', description="They cast their line into the water", color=embeds.amber)
            common = ["fish"]
            uncommon = ["shrimp", "tropical_fish", "crab", "puffer_fish"]
            rare = ["squid", "lobster", "octopus"]
            frequency = [common, common, common, uncommon, uncommon, rare]
            catch = choice(choice(frequency))
            item = find_item(catch)
            inventory_file = Inventory("data/data.json", ctx.user.id)
            inventory_file.create_item(item)
            await ctx.response.send_message(embeds=(action_embed, embeds.gained_item(ctx), item.inventory_item_info(), experience.edit_charisma(ctx, randint(10,30))))
            return True

        async def feed_luna_fish(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} feeds Luna a delicious fish', description="She happily eats it", color=embeds.amber)
            await ctx.response.send_message(embeds=(embed, experience.edit_charisma(ctx, randint(20,60))))
            return True
        
        async def scratch(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} gives Luna something to scratch', description="She digs in her claws", color=embeds.amber)
            await ctx.response.send_message(embeds=(embed, experience.edit_charisma(ctx, randint(10,30))))
            return True
        
        async def treats(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} gives Luna a treat', description="She gobbles it up", color=embeds.amber)
            await ctx.response.send_message(embeds=(embed, experience.edit_charisma(ctx, randint(40,90))))
            return True

        async def yarn(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} gives Luna a ball of blue yarn', description="She bats it around the room", color=embeds.amber)
            await ctx.response.send_message(embeds=(embed, experience.edit_charisma(ctx, randint(20,40))))
            return True
        
        async def mouse(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} gives Luna a toy mouse', description="She bats it around the room", color=embeds.amber)
            await ctx.response.send_message(embeds=(embed, experience.edit_charisma(ctx, randint(20,40))))
            return True
        
        async def laser(self : Item, ctx : discord.interactions.Interaction) -> bool :
            embed = discord.Embed(title=f'{ctx.user.name} points a laser near Luna', description="She chases it", color=embeds.amber)
            await ctx.response.send_message(embeds=(embed, experience.edit_charisma(ctx, randint(30,80))))
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
    return items()[type]

@client.tree.command(name="inventory", description="Lists the items in your inventory and the actions you can preform")
async def inventory(ctx : discord.interactions.Interaction) -> None :
    # Catch use in DMs
    if not client.get_guild_id(ctx) :
        await ctx.response.send_message(embed=embeds.not_in_server(), ephemeral=True)
        return None

    inventory_file = Inventory("data/data.json", ctx.user.id)

    if len(inventory_file) :

        page = 0
        embed = discord.Embed(title="Please Wait", description="Generating inventory...", color=embeds.amber)
        await ctx.response.send_message(embed=embed, ephemeral=True)

        message = await ctx.channel.send(embed=embeds.menu_navigator(ctx))
        controls = ["◀️","⏹","▶️","🔄"]
        for control in controls :
            await message.add_reaction(control)

        # https://stackoverflow.com/a/67451379
        while not client.is_closed() :
            inventory_file = Inventory("data/data.json", ctx.user.id)
            inventory = inventory_file.get()

            if not len(inventory_file) :
                await ctx.edit_original_response(content="", embed=embeds.no_items(), view=None)
                await message.delete()
                return None

            item_embeds = []
            item_actions = []
            
            for uuid in inventory :
                item = inventory_file.get_item(uuid)
                item_embeds.append(item.inventory_item_info())
                item_actions.append(item.inventory_item_options())
            
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
    # Catch use in DMs
    if not client.get_guild_id(ctx) :
        await ctx.response.send_message(embed=embeds.not_in_server(), ephemeral=True)
        return None

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

        balance_file = Balance("data/data.json", ctx.user.id)
        balance_embed = discord.Embed(title="Balance",description=f'{balance_file.get()} {luna_assets.coin_symbol}')
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