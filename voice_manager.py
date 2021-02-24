import discord
from discord.ext import commands
from discord.utils import get
from database import Database
import random
import asyncio
from threading import Thread
import time
import Errors
from bot import send_message

channelNames = ("⛵-Тихая Мэри-⛵", "⛵-Чёрная жемчужина-⛵", "⛵-Летучий Голандец-⛵", "⛵-Тихая Мэри-⛵","⛵-Перехватчик-⛵","⛵-Разящий-⛵","⛵-Стремительный-⛵","⛵-Провидэнс-⛵","⛵-Эдинбургский торговый корабль-⛵","⛵-Турецкое рыболовецкое судно-⛵","⛵-Летающий дракон-⛵","⛵-Императрица-⛵", "⛵-Сантьяго-⛵")
root = [805342393808453633, 805342463086166036, 805342797476659270, 805342875721662474, 805342914770501653]
channelParams = {
    "user_limit" : 20,
}

privateChannelParams = {
    "user_limit" : 4,
}


voice_permissions = {
    "connect" : True,
    "speak" : True,
    "move_members" : True,
    "mute_members" : True,
    "deafen_members" : True,
    "stream" : True,
    "priority_speaker" : True,
    "use_voice_activation" : True,
    "create_instant_invite" : True,
    "manage_channels" : True,
    #"manage_permissions" : True
}

class VoiceManager(Database, commands.Cog):
    def __init__(self, Bot):
        super().__init__('root')
        self.Bot = Bot
        self.online_channels = [] #channel.id
        self.to_clean = [] #channel.id
        self.private_channels = [] #(channel.id, role.id, admin.id, support.id)
    
    async def start(self):
        channels = self.get_all_channels()
        for i in channels:
            channel = self.guild.get_channel(int(i['channel_id']))
            thr = Thread(target = self.manage_channel, args = (channel, ))
            thr.start()
            self.online_channels.append(channel.id)
            if not i['role_id'] is None:
                self.private_channels.append((int(i['channel_id']), int(i['role_id']), int(i['admin']), int(i['support_id'])))

    async def get_name(self):
        return random.choice(channelNames)
    
    async def on_member_channel(self):
        await self.Bot.wait_until_ready()
        chn = self.channel
        while not self.Bot.is_closed():
            if len(chn.members) > 0:
                await self.create_channel(chn.members[0])
            await asyncio.sleep(1)
    
    async def on_member_private_channel(self):
        await self.Bot.wait_until_ready()
        chn = self.private_channel
        while not self.Bot.is_closed():
            if len(chn.members) > 0:
                await self.create_private_channel(chn.members[0])
            await asyncio.sleep(1)
    
    def manage_channel(self, channel):
        while True:
            if len(channel.members) == 0:
                data = self.get_channel(channel.id)
                self.to_clean.append(channel.id)
                self.remove_channel(channel.id)
                self.online_channels.remove(channel.id)
                if not data['role_id'] is None:
                    self.to_clean.append(int(data['role_id']))
                    self.to_clean.append(int(data['support_id']))
                    self.private_channels.remove((int(data['channel_id']), int(data['role_id']), int(data['admin']), int(data['support_id'])))
                return
            time.sleep(1)
    
    async def create_channel(self, member):
        name = await self.get_name()
        overwrites = {
            get(self.guild.roles, id = 691745971725664276) : discord.PermissionOverwrite(view_channel = False),
            get(self.guild.roles, id = 627794803446382592) : discord.PermissionOverwrite(view_channel = False, speak = False)
        }
        channel = await self.category.create_voice_channel(name = name,  **channelParams, overwrites = overwrites, reason = f"{member.name} создал канал")
        await member.move_to(channel)
        self.add_channel(channel.id)
        self.online_channels.append(channel.id)
        thr = Thread(target = self.manage_channel, args = (channel, ))
        thr.start()
    
    async def create_private_channel(self, member):
        name = await self.get_name() ############################here!!!
        role = await self.guild.create_role(name = name, colour = discord.Colour.teal())
        overwrites = {
            self.guild.get_role(691745971725664276) : discord.PermissionOverwrite(view_channel = False),
            self.guild.get_role(self.guild.id) : discord.PermissionOverwrite(connect = False, speak = False, move_members = False, mute_members = False, deafen_members = False),
            role : discord.PermissionOverwrite(connect = True, speak = True),
            member : discord.PermissionOverwrite(**voice_permissions)
        }
        channel = await self.category.create_voice_channel(name = name,  **privateChannelParams, overwrites = overwrites, reason = f"{member.name} создал канал")
        await member.move_to(channel)
        await member.add_roles(role)
        overwrites = {
            self.guild.get_role(691745971725664276) : discord.PermissionOverwrite(view_channel = False),
            self.guild.get_role(self.guild.id) : discord.PermissionOverwrite(view_channel = False),
            role : discord.PermissionOverwrite(view_channel = True)
        }
        support = await self.category.create_text_channel(name = name, overwrites = overwrites, reason = f"{member.name} создал канал")
        self.add_channel(channel.id, role.id, member.id, support.id)
        self.online_channels.append(channel.id)
        self.private_channels.append((channel.id, role.id, member.id, support.id))
        thr = Thread(target = self.manage_channel, args = (channel, ))
        thr.start()
        embed = discord.Embed(title = "Ваш приватный канал", color = discord.Colour.teal())
        description = f"**Добро пожаловать в управление вашим голосовым каналом**\n\n**пригласить в приватный канал**\n`p i [@user]`\n\n**кикнуть из приватного канала**\n`p k [@user]`\n\nВы наделены абсолютной властью внутри своего голосового канала!!!"
        embed.description = description
        embed.set_footer(text = "используйте этот чат как посчитаете нужным)")
        await support.send(embed = embed)
    
    async def cleaner(self):
        await self.Bot.wait_until_ready()
        while not self.Bot.is_closed():
            for channel in self.to_clean:
                test = self.guild.get_channel(channel)
                channel = test if not test is None else self.guild.get_role(channel)
                await channel.delete()
                self.to_clean.remove(channel.id)
            await asyncio.sleep(1)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.Bot.get_guild(453565320708489226)
        self.channel = self.guild.get_channel(805342914770501653)
        self.private_channel = self.guild.get_channel(813705729164312596)
        self.category = self.channel.category
        await self.start()
        self.Bot.loop.create_task(self.on_member_channel())
        self.Bot.loop.create_task(self.on_member_private_channel())
        self.Bot.loop.create_task(self.cleaner())
    
    @commands.command(aliases = ['p'])
    async def private(self, ctx, arg = None, member : discord.Member = None):
        user = ctx.author
        if not arg in ('invite', 'i', 'kick', 'k'):
            raise commands.UserInputError
        if arg in ('invite', 'i'):
            if not user.voice:
                raise Errors.NotConnectedError
            voice = user.voice.channel
            channel = self.get_channel(voice.id)
            if channel is None:
                raise Errors.NotPrivateChannelError
            else:
                if user.id != int(channel['admin']):
                    raise Errors.NotChannelAdminError
                if member is None:
                    raise Errors.InvalidFriendError
                await member.add_roles(self.guild.get_role(int(channel['role_id'])))
                await send_message(ctx.channel, "пользователь был успешно добавлен")
        elif arg in ('kick', 'k'):
            if not user.voice:
                raise Errors.NotConnectedError
            voice = user.voice.channel
            channel = self.get_channel(voice.id)
            if channel is None:
                raise Errors.NotPrivateChannelError
            else:
                if user.id != int(channel['admin']):
                    raise Errors.NotChannelAdminError
                if member is None:
                    raise Errors.InvalidFriendError
                await member.remove_roles(self.guild.get_role(int(channel['role_id'])))
                if member.voice:
                    if member.voice.channel.id == voice.id:
                        await member.move_to(self.guild.get_channel(453568968305672209))
                await send_message(ctx.channel, "пользователь был успешно кикнут")


def setup(Bot):
    Bot.add_cog(VoiceManager(Bot))