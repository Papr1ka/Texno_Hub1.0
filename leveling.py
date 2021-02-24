import discord
from discord.ext import commands
from bot import prefixes
from database import Database
from asyncio import sleep as asleep
from time import sleep
from threading import Thread
from bot import bots
from user_card import level_cost, calculate_level

up_table = {
    'message' : 5, #if message (not command and not in bot channel)
    'picture' : 10, #if message has picture
    'voice' : 10, #for 1 minute of beeng in a voice channel
    'homework' : 35, #for homework
}

money_for_level = {
    '1' : 500,
    '5' : 1000
}

class Leveling(Database, commands.Cog):

    @commands.Cog.listener()
    async def on_message(self, message):
        msg = message.content
        if not msg.startswith((prefixes)) and not message.author.bot and message.channel.id != self.tech_id:
            cost = up_table['message']
            if len(message.attachments) > 0:
                cost += up_table['picture']
                if message.channel.id == self.home_id:
                    cost += up_table['homework']
            
            if message.channel.category.id == 453565321194897428:
                self.up_exp(message.author.id, cost)
                print("апнул экспу")
            self.update_user(message.author.id, mode = 'inc', messages = 1)
        if "You need to be in the same voice channel as Rythm to use this command" in msg:
            await bots(message.channel)


    def update_level(self, member_id, level):
        money = money_for_level['5'] if level % 5 == 0 else money_for_level['1']
        self.update_user(member_id, 'inc', money = money)

    def up_exp(self, member_id, exp):
        start_exp = int(self.get_user(member_id)['exp'])
        start_level = calculate_level(start_exp)[0]
        end_level = calculate_level(start_exp + exp)[0]
        if end_level > start_level:
            self.update_level(member_id, end_level)
        self.update_user(member_id, 'inc', exp = exp)


    def manage_user(self, member):
        timer = 0
        while True:
            if member.voice:
                if not member.voice.mute and not member.voice.self_mute:
                    timer += 1
            else:
                self.registered_users.remove(member.id)
                print(f'{member.name} отключился')
                return
            if timer >= 60:
                #self.update_user(member.id, mode = 'inc', exp = up_table['voice'])
                self.up_exp(member.id, up_table['voice'])
                self.update_user(member.id, mode = 'inc', voice = 1)
                print(f'update {member.name}')
                timer -= 60
            sleep(1)

    async def processing_members(self):
        while True:
            channels = self.guild.voice_channels
            for channel in channels:
                if channel.id != self.guild.afk_channel.id:
                    for member in channel.members:
                        if member.voice.mute or member.voice.self_mute:
                            pass
                        else:
                            if not member.id in self.registered_users:
                                print(f'processing {member}')
                                thr = Thread(target = self.manage_user, args = (member, ))
                                thr.start()
                                print(f'created task for {member}')
                                self.registered_users.append(member.id)
            await asleep(2)

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.Bot.get_guild(453565320708489226)
        self.Bot.loop.create_task(self.processing_members())
        print("create task")
    
    def __init__(self, Bot):
        super(Leveling, self).__init__('main')
        self.Bot = Bot
        self.tech_id = 510175032786288660
        self.home_id = 777644390533431306
        self.registered_users = [] #id

def setup(Bot):
    Bot.add_cog(Leveling(Bot))
