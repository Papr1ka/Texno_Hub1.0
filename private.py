import discord
from discord.ext import commands
from discord.utils import get
import asyncio
from threading import Thread
import time
from random import choice, randint
from bot import send_message, get_channel_text

################################
######### consts ###############
channels = [] #[channel, role]
channelParams = {
    "user_limit" : 2,
}
channelNames = ("-⛵-Тихая Мэри-", "-⛵-Чёрная жемчужина-", "-⛵-Летучий Голандец-", "-⛵-Тихая Мэри-","-⛵-Перехватчик-","-⛵-Разящий-","-⛵-Стремительный-","-⛵-Провидэнс-","-⛵-Эдинбургский торговый корабль-","-⛵-Турецкое рыболовецкое судно-","-⛵-Летающий дракон-","-⛵-Императрица-", "-Сантьяго-")
prefixes = ("🎄", "🎆", "💟", "🕯️", "🎇", "☃️", "❄️")
root = [687624128479756341, 691667127056203859, 784362579036340224, 771677356150226984, 784026248086290432]
################################

class VoiceChannels(commands.Cog):

    toClean = []

    def __init__(self, Bot):
        self.Bot = Bot
    
    async def onMemberInChannel(self):
        await self.Bot.wait_until_ready()
        while not self.Bot.is_closed():
            if len(self.main_channel.members) > 0:
                await self.create_channel()
            await asyncio.sleep(1)
    
    async def getRandomName(self):
        name = choice(channelNames)
        prefix = choice(prefixes)
        return prefix + name + prefix
    
    async def create_channel(self):
        try:
            member = self.main_channel.members[0]
        except:
            return
        else:
            name = await self.getRandomName()
            overwrites = { get(self.guild.roles, id = 691745971725664276) : discord.PermissionOverwrite(view_channel = False) }
            channel = await self.category.create_voice_channel(name = name, **channelParams, overwrites = overwrites)
            await channel.edit(topic = channel.id)
            await channel.set_permissions(self.everyone, connect = False, move_members = False, mute_members = False, deafen_members = False)
            await self.command_channel.send(f"создан приватный канал {channel.name}, by {member.name + '#' + member.discriminator}")
            await member.move_to(channel)
            await self.createPanel(member, channel)
            thr = Thread(target = self.voice_thread, args = (channel, ))
            thr.start()

    async def createPanel(self, admin : discord.Member , channel):
        emoji = ["➖", "🔓", "🔒", "➕"]
        description = "invite - p invite @member\nkick - p kick @member\nchange members count - ➕ , ➖\nlock - 🔒\nunlock - 🔓"
        embed = discord.Embed(title = channel.name,
                                description = description,
                                color = discord.Colour.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255)))
        overwrites = {
            admin : discord.PermissionOverwrite(read_messages = True, send_messages = True, read_message_history = True,
            self.everyone : discord.PermissionOverwrite(read_messages = False, read_messages_history = False))
        }
        channel = await self.category.create_text_channel(channel.name, overwrites = overwrites, position = 1)
        message = await channel.send(embed = embed)
        for i in emoji:
            await message.add_reaction(i)
        
        while True:
            if channel:
                pass
            else:
                await channel.delete()
            await asyncio.sleep(1)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot == False:
            channel = get_channel_text(payload.channel_id)
            try:
                voice = get(self.Bot.get_all_channels, id = int(channel.topic))
            except:
                pass
            else:
                if str(payload.emoji) == "➖":
                    await voice.edit(user_limit = voice.user_limit - 1)
                elif str(payload.emoji) == "➕":
                    await voice.edit(user_limit = voice.user_limit + 1)
                elif str(payload.emoji) == "🔓":
                    await payload.member.voice.channel.set_permissions(self.everyone, connect = True)
                    name = payload.member.voice.channel.name[1:]
                    name = "🔓" + name
                    await channel.edit(name = name)
                elif str(payload.emoji) == "🔒":
                    await payload.member.voice.channel.set_permissions(self.everyone, connect = False)
                    name = payload.member.voice.channel.name[1:]
                    name = "🔒" + name
                    await channel.edit(name = name)
                

                
    
    def voice_thread(self, channel):
        while True:
            if len(channel.members) == 0:
                self.toClean.append(channel.id)
                print(f"удалён пустой канал : {channel.id}")
                return
            time.sleep(1)
    
    async def cleaner(self):
        while not self.Bot.is_closed():
            for i in self.toClean:
                channel = self.Bot.get_channel(i)
                await self.command_channel.send(f"удалён канал {channel.name}")
                await channel.delete()
                self.toClean.remove(i)
            await asyncio.sleep(1)


    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.Bot.get_guild(453565320708489226)
        self.category = self.guild.get_channel(805146020299407420).category
        self.main_channel = self.Bot.get_channel(805146020299407420)
        self.Bot.loop.create_task(self.onMemberInChannel())
        self.Bot.loop.create_task(self.cleaner())
        self.command_channel = self.Bot.get_channel(686361227483807754)
        self.everyone = get(self.guild.roles, id = self.guild.id)


def setup(Bot):
	Bot.add_cog(VoiceChannels(Bot))

#####################################
"""
futures:
empty
"""
#####################################