import discord

from random import randint, choice

from luna import *
from data import Data_File
import embeds
import luna_assets
import experience
from cooldown import Cooldown, in_seconds
from economy import Balance

class Action(Data_File) :
    def __init__(self, directory: str, action_id : str, type : str) -> None:
        self.id = action_id
        self.type = type
        super().__init__(directory)

    def get_title(self, user_name : str) -> str :
        return choice(self.data()[self.id]["title_pool"]).format(user_name)
    
    def get_response(self) -> str :
        return choice(self.data()[self.id][self.type]["responses"])
    
    def get_reward(self, reward_type : str) -> int :
        range = self.data()[self.id][self.type]["rewards"][reward_type]
        return randint(range["min"], range["max"])


common_actions = ["pet", "tease", "balloon"]
daily_food_actions = ["give_food"]

async def enact(ctx : discord.interactions.Interaction, title : str, action : Action) -> None :

    balance_reward = action.get_reward("currency")
    experience_reward = action.get_reward("experience")

    embed = discord.Embed(title=title, color=embeds.green)
    embed.add_field(name=action.get_title(ctx.user.name), value=action.get_response(), inline=False)
    embed.add_field(name="Result", value=f'{balance_reward} {luna_assets.coin_symbol}')

    balance_file = Balance("data/data.json", ctx.user.id)
    balance_file.edit(balance_reward)

    await ctx.response.send_message(embed=embed)
    if randint(0,1) == 0 : await ctx.channel.send(embed=experience.edit_charisma(ctx, experience_reward))

@client.tree.command(name="play", description="Play with Luna to receive rewards")
async def play(ctx : discord.interactions.Interaction) -> None :
    cooldown = Cooldown("data/cooldown.json", ctx.user.id, "play_command")
    if cooldown.able() :
        cooldown.mark(in_seconds(minutes=15, seconds=30))
        negative_chance = 3
        type = "positive" if randint(1,negative_chance) != 1 else "negative"
        action = Action("data/default/actions.json", choice(common_actions), type)
        await enact(ctx, "Play with Luna", action)
        return

    else :
        embed = discord.Embed(title="Luna's tired", description="Luna needs a break from playing", color=embeds.red)
        embed.add_field(name="Come Back In", value=cooldown.formatted_delta())
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return

@client.tree.command(name="daily", description="Give Luna her daily bowl of food receive rewards")
async def play(ctx : discord.interactions.Interaction) -> None :
    cooldown = Cooldown("data/cooldown.json", ctx.user.id, "daily_command")
    if cooldown.able() :
        cooldown.mark(in_seconds(hours=18, minutes=30))
        negative_chance = 5
        type = "positive" if randint(1,negative_chance) != 1 else "negative"
        action = Action("data/default/actions.json", choice(daily_food_actions), type)
        await enact(ctx, "Feed Luna", action)
        return

    else :
        embed = discord.Embed(title="Luna's already been fed", description="Wait until tomorrow to feed Luna again", color=embeds.red)
        embed.add_field(name="Come Back In", value=cooldown.formatted_delta())
        await ctx.response.send_message(embed=embed, ephemeral=True)
        return