from database import Database
import discord
from discord.ext import commands
import asyncio
import random
import Errors

class Giveaway(Database, commands.Cog):
    def __init__(self, Bot):
        self.connect('main')
        self.Bot = Bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.Bot.get_guild(453565320708489226)
        self.emoji = await self.guild.fetch_emoji(777656743211302913)
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def giveaway(self, ctx, money : int, time : int = 5):
        await ctx.send("@here")
        embed = discord.Embed(
            title = f"Контрабанда! {money} $",
            description = f"Чтобы побороться за товар, нажмите на реакцию\nИтоги через {time} минут!",
            color = discord.Colour.teal()
        )
        embed.set_thumbnail(url = "https://investor100.ru/wp-content/uploads/2019/05/6_sluchayno_naydennyh_ogromnyh_kladov.jpg")
        await ctx.message.delete()
        giveaway = await ctx.send(embed = embed)
        await giveaway.add_reaction(str(self.emoji))
        await asyncio.sleep(time * 60)
        msg = await giveaway.channel.fetch_message(giveaway.id)
        users = await msg.reactions[0].users().flatten()
        users.pop(users.index(self.Bot.user))
        if len(users) > 0:
            winner = random.choice(users)
            self.update_user(winner.id, 'inc', money = money)
            await ctx.send(f"{winner.mention} забрал контрабанду!")
        else:
            text = "Увы, контрабанду перехватили("
        
            embed.set_footer(text = text)
            await giveaway.edit(embed = embed)

def setup(Bot):
    Bot.add_cog(Giveaway(Bot))