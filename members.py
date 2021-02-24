import discord
from discord.ext import commands
from discord.utils import get
from PIL import Image, ImageFont, ImageDraw
import asyncio
import math
import emoji
import regex
from bot import get_channel_text
from database import Database

class Members(Database, commands.Cog):

    def __init__(self, Bot):
        super().__init__('main')
        self.Bot = Bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = get(member.guild.roles, id = 770224340738244668)
        await member.add_roles(role) #Матрос

        role = get(member.guild.roles, id = 696087348945092678)
        await member.add_roles(role) #DJ
        channel = get_channel_text(596065067116789772)
        def split_count(text):
            emoji_counter = 0
            data = regex.findall(r'\X', text)
            for word in data:
                if any(char in emoji.UNICODE_EMOJI for char in word):
                    emoji_counter += 1
                    # Remove from the given text the emojis
                    text = text.replace(word, '') 
            return emoji_counter

        img = Image.open("base.png")
        text = member.name + "#" + member.discriminator
        text_font = math.floor( (310 - 39) / len(text) * 1.58 ) 
        text_font2 = round( text_font * 0.719 )

        print(text_font)
        print(text_font2)

        while text_font2 > 60:
            text_font -= 1
            text_font2 = math.floor( text_font * 0.719 )
            print(text_font)

        font = math.floor((text_font*250 + text_font2 * 60) / 310)

        print(font)


        if split_count(text) == 0 and text.isascii() == True:
            f1 = "Cousine-BoldItalic.ttf"
        else:
            f1 = "Symbola.ttf"

        headline = ImageFont.truetype(f1, size = text_font )
        idraw = ImageDraw.Draw(img)
        idraw.text( ( round((39 + 310) / 2) - ( len(text) * (text_font) * 0.615 ) / 2, round((208 + 269) / 2) - (text_font) / 2) , text , font = headline)

        idraw.text( (70, 300), "присоединился" , font = ImageFont.truetype("Cousine-BoldItalic.ttf", size = 26 ))
        img.save('random.jpg', 'png')
        Imagination = discord.File("./random.jpg")
        await channel.send(file = Imagination)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = get_channel_text(596065067116789772)
        def split_count(text):
            emoji_counter = 0
            data = regex.findall(r'\X', text)
            for word in data:
                if any(char in emoji.UNICODE_EMOJI for char in word):
                    emoji_counter += 1
                    # Remove from the given text the emojis
                    text = text.replace(word, '') 
            return emoji_counter

        img = Image.open("base.png")
        text = member.name + "#" + member.discriminator
        text_font = math.floor( (310 - 39) / len(text) * 1.58 ) 
        text_font2 = round( text_font * 0.719 )

        print(text_font)
        print(text_font2)

        while text_font2 > 60:
            text_font -= 1
            text_font2 = math.floor( text_font * 0.719 )
            print(text_font)

        font = math.floor((text_font*250 + text_font2 * 60) / 310)

        print(font)


        if split_count(text) == 0 and text.isascii() == True:
            f1 = "Cousine-BoldItalic.ttf"
        else:
            f1 = "Symbola.ttf"

        headline = ImageFont.truetype(f1, size = text_font )
        idraw = ImageDraw.Draw(img)
        idraw.text( ( round((39 + 310) / 2) - ( len(text) * (text_font) * 0.615 ) / 2, round((208 + 269) / 2) - (text_font) / 2) , text , font = headline)

        idraw.text( (80,300), "покинул нас" , font = ImageFont.truetype("Cousine-BoldItalic.ttf", size = 26 ))
        img.save('random.jpg', 'png')
        Imagination = discord.File("./random.jpg")
        await channel.send(file=Imagination)
        self.remove_user(member.id)

    

def setup(Bot):
    Bot.add_cog(Members(Bot))