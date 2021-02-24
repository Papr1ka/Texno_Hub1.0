import discord
from discord.ext import commands
from discord.utils import get
import asyncio
from bot import send_message

class Administration(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot
    
    @commands.command(aliases = ["c", "с"])
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, amount = 6):
        try:
            await ctx.channel.purge(limit = amount + 1)
            print(f"произошла очистка чата")
        except Exception:
            print(Exception)
    
    @commands.command(aliases = ["mut"])
    async def mute(self, ctx, member : discord.Member, time : str):

        def parse(time):
            def rewrite(timeout : str):
                try:
                    timeout = int(timeout)
                    return timeout
                except:
                    return None
                    
            timeout = ""
            for i in time:
                if i == "m":
                    t = rewrite(timeout)
                    return t * 60 if t != None else None
                elif i == "h":
                    t = rewrite(timeout)
                    return t * 60 * 60 if t != None else None
                elif i == "d":
                    t = rewrite(timeout)
                    return t * 60 * 60 * 24 if t != None else None
                else:
                    timeout += i
            return None
        
        timer = parse(time)
        if not timer is None:
            role = get(ctx.guild.roles, id = 627794803446382592)
            await member.add_roles(role)
            await send_message(ctx.channel, f"{member.name} был дан мут на {timer} секунд")
            while timer > 0:
                timer -= 1
                await asyncio.sleep(1)
            
            await member.remove_roles(role)
            

def setup(Bot):
    Bot.add_cog(Administration(Bot))