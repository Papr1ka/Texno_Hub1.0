import discord
from discord.ext import commands

class Donate(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.command()
    async def donate(self, ctx):
        embed = discord.Embed(
            color = discord.Colour.teal(),
            title = "Поддержать Сервер")
        embed.url = "https://www.tinkoff.ru/sl/3LSEAlOHPj5"
        embed.description = "```markdown\n* курс 1 руб к 100 $\n* время обработки до 12ч\n* переходите по ссылке и пишите свой в поле 'сообщение...'\nник discord в формате name#discriminator\n* ждите прибавления)```"
        await ctx.send(embed = embed)

def setup(Bot):
    Bot.add_cog(Donate(Bot))