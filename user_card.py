import discord
from discord.ext import commands
import asyncio
from database import Database, User
from datetime import datetime, timedelta
from PIL import Image, ImageFont, ImageDraw, ImageOps
from requests import get
from io import BytesIO
from bot import send_message
import os

level_cost = 1000

def calculate_level(exp : int):
    level = exp // level_cost
    exp_on_level = exp - level * level_cost
    return level, exp_on_level, level_cost

class Card():
    def __init__(self, user_data, mode = False):
        #mode - if false : minimal mode else full info mode
        self.mode = mode
        if mode is False:
            size = (760, 200)
        else:
            size = (760, 290)
        self.data = user_data
        self.img = Image.new('RGB', size, "#0F0F0F")
        self.draw = ImageDraw.Draw(self.img)
        self.mainfont = ImageFont.truetype('Montserrat.ttf', 24)
        self.second_font = ImageFont.truetype('Montserrat.ttf', 40)
        self.filename = str(self.data['user_id']) + ".png"
        self.color = self.data['role_color']

    def get_random_background(self):
        pass
    
    def render_avatar(self):
        padding = (20, 20)
        size = (158, 158)
        linear_size = 1

        resp = get(self.data['avatar'], stream = True)
        resp = Image.open(BytesIO(resp.content))
        resp = resp.convert('RGB')
        ava = resp.resize(size, Image.ANTIALIAS)

        back = Image.new('RGB', (size[0] + linear_size * 2, size[1] + linear_size * 2), "#646464")
        back.paste(ava, (linear_size, linear_size))

        self.img.paste(back, (padding[0], padding[1], size[0] + linear_size * 2 + padding[0], size[1] + linear_size * 2 + padding[1]))
    
    def render_info(self):
        name = self.data['username'][:16]
        discriminator = " #" + self.data['discriminator']
        self.draw.text((240, 100), name + discriminator, font = self.mainfont, fill = (246, 246, 246))
        level, exp, cost = calculate_level(int(self.data['exp']))
        exp_text = f"{exp} / {cost} XP"
        self.draw.text((590, 100), exp_text, font = self.mainfont, fill = (200, 200, 200))
        self.draw.text((590, 20), "LeveL", font = self.mainfont, fill = (13, 175, 181))
        self.draw.text((680, 6), str(level), font = self.second_font, fill = (13, 175, 181))
        top_role = "@" + self.data['role']
        self.draw.text((240, 20), top_role, font = self.mainfont, fill = self.color)
        custom = self.data['custom_text']
        if custom != "":
            custom = "#" + custom
        else:
            custom = "#" + "Texno_Hub community"
        self.draw.text((240, 50), custom, font = self.mainfont, fill = (120, 120, 120))
        if self.mode:
            messages = str(self.data['messages'])
            self.draw.text((20, 200), "Messages", font = self.mainfont, fill = (246, 246, 246))
            self.draw.text((20, 240), messages, font = self.mainfont, fill = (200, 200, 200))
            voice = str(self.data['voice'])
            self.draw.text((220, 200), "Voice online", font = self.mainfont, fill = (246, 246, 246))
            self.draw.text((220, 240), voice, font = self.mainfont, fill = (200, 200, 200))
            self.draw.text((322, 240), "min", font = self.mainfont, fill = (200, 200, 200))
            on_server = self.data["time_on_server"]
            time = f"{on_server[0]} days {on_server[1]} hours"
            self.draw.text((500, 200), "On server", font = self.mainfont, fill = (246, 246, 246))
            self.draw.text((500, 240), time, font = self.mainfont, fill = (200, 200, 200))
    
    def render_progress(self):
        percents = self.data['exp']
        data = calculate_level(percents)
        exp = data[1]
        percents = int(exp / level_cost * 100)
        progressbar = self.get_progress(percents)
        self.img.paste(progressbar, (230, 150))


    def get_progress(self, percents : int):
        #percents : % of 100
        size = (480, 32)
        im = Image.open('progress.png').convert('RGB').resize((500, 32))
        draw = ImageDraw.Draw(im)
        color=(98, 211, 245)
        x, y, diam = int(size[0] / 100 * percents), 5, 21
        if x == 0:
            pass
        else:
            half = diam // 2
            if x < half + 11:
                x = half
            elif x >= half + 11:
                x -= half
            draw.ellipse([x,y,x + diam,y+diam], fill = color)
            ImageDraw.floodfill(im, xy=(11, 18), value = color, thresh=40)
        return im




    
    def get(self):
        self.render_avatar()
        self.render_info()
        self.render_progress()
        self.img.save(self.filename)
        return self.filename

class UserCard(Database, commands.Cog):

    top_list = {
        "money" : [None, 0], #user : id : int, value : int
        "exp" : [None, 0],
        "messages" : [None, 0],
        "voice" : [None, 0]
    }

    def __init__(self, Bot):
        super(UserCard, self).__init__('main')
        self.Bot = Bot
    
    def get_time(self, time):
        if time % 10 == 1 and time % 100 != 11:
            return 1 #час день
        elif 1 < time % 10 < 5 and (not time % 100 in (11, 12, 13, 14)):
            return 2 #часа дня
        else:
            return 3 #часов дней
    
    @commands.command()
    async def status(self, ctx, member : discord.Member = None):
        if not member:
            member = ctx.author
        

        user_data = self.get_user(member.id)
        now = datetime.now()
        then = member.joined_at
        delta = now - then
        days = delta.days
        hours = int(delta.seconds / 60 // 60)
        user_data["time_on_server"] = (days, hours)
        user_data["avatar"] = str(member.avatar_url)[:-10] if "size" in str(member.avatar_url) else str(member.avatar_url)
        member = discord.utils.get(self.guild.members, id = int(user_data['user_id']))
        user_data["username"] = member.nick if not member.nick is None else member.name
        user_data["discriminator"] = member.discriminator
        user_data["role"] = member.top_role.name
        user_data["role_color"] = (member.top_role.colour.r, member.top_role.colour.g, member.top_role.colour.b)
        pic = Card(user_data, mode = False).get()
        picture = discord.File('./' + pic)
        await ctx.send(file = picture)
        os.remove("./" + pic)
    
    @commands.command()
    async def stats(self, ctx, member : discord.Member = None):
        if not member:
            member = ctx.author
        
        user_data = self.get_user(member.id)
        name = member.nick if not member.nick is None else member.name
        title = f"Статистика {name}#{member.discriminator}"
        color = member.top_role.color
        now = datetime.now()
        then = member.joined_at
        delta = now - then
        days = delta.days
        hours = int(delta.seconds / 60 // 60)
        days_id = self.get_time(days)
        hours_id = self.get_time(hours)
        time_on_server = f"{days} {'день' if days_id == 1 else 'дня' if days_id == 2 else 'дней'} и {hours} {'час' if hours_id == 1 else 'часа' if hours_id == 2 else 'часов'}"
        embed = discord.Embed(title = title, color = color)
        embed.set_thumbnail(url = member.avatar_url)
        embed.add_field(name = "Money", value = f"{user_data['money']} $", inline = True)
        embed.add_field(name = "Messages", value = f"{user_data['messages']}", inline = True)
        embed.add_field(name = "Voice activity", value = f"{user_data['voice']} min", inline = True)
        embed.add_field(name = "With us", value = time_on_server, inline = True)
        await ctx.send(embed = embed)
    
    async def check_users(self):
        for member in self.guild.members:
            user = self.get_user(member.id)
            if user["money"] > self.top_list["money"][1]:
                self.top_list["money"] = [member.id, int(user["money"])]
            if user["exp"] > self.top_list["exp"][1]:
                self.top_list["exp"] = [member.id, int(user["exp"])]
            if user["messages"] > self.top_list["messages"][1]:
                self.top_list["messages"] = [member.id, int(user["messages"])]
            if user["voice"] > self.top_list["voice"][1]:
                self.top_list["voice"] = [member.id, int(user["voice"])]
    
    @commands.command(aliases = ['set_castom', 'custom', 'castom', 's_c'])
    async def set_custom(self, ctx, *args):
        """
        set custom status
        """
        text = " ".join(args)
        if len(text) > 23:
            await send_message(ctx.channel, "невозможно установить значение длиннее 23 символов", None)
        else:
            self.update_user(ctx.author.id, custom_text = text)
            await send_message(ctx.channel, "ваш статус установлен", None)


    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.Bot.get_guild(453565320708489226)
        print("Checking all users")
        await self.check_users()
        print("Checking finished")

def setup(Bot):
    Bot.add_cog(UserCard(Bot))
