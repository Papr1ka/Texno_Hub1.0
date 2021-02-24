import discord
from discord.ext import commands
from database import Database
from bot import send_message, hex_to_rgb
import Errors
from inspect import Parameter

items = ["myrole", "doblerole", "rolecolor", "rolename", "suprole"]

prices = {
    0 : 10000,
    1 : 15000,
    2 : 1000,
    3 : 1000,
    4 : "?",
}

shop_json = [
    {
        'name' : 'Личная роль на сервере ',
        'value' : '`buy myrole "[название]" [цвет в hex]`'
    },
    {
        'name' : 'Парная роль на сервере ',
        'value' : '`buy doblerole "[название]" [цвет в hex] [@партнёр]`'
    },
    {
        'name' : 'Изменить цвет роли ',
        'value' : '`buy rolecolor [@роль] [цвет в hex]`'
    },
    {
        'name' : 'Изменить название роли ',
        'value' : '`buy rolename [@роль] "[название]"`'
    },
    {
        'name' : 'Купить роль из доступных ',
        'value' : '`shop roles`'
    },
]

cool_roles = [
    {
        'role' : 813046011269218364,
        'cost' : 100000
    },
    {
        'role' : 813047141437800489,
        'cost' : 50000
    },
    {
        'role' : 813048088746131476,
        'cost' : 20000
    }
]

class Shop(Database, commands.Cog):

    def __init__(self, Bot):
        super(Shop, self).__init__('main')
        self.Bot = Bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.Bot.get_guild(453565320708489226)

    @commands.command(aliases = ['sho', 'store'])
    async def shop(self, ctx, arg = None):
        member = self.get_user(ctx.author.id)
        member_roles = len(member['inventory']) + len(member['custom_roles'])
        modifier = (2 * member_roles) if member_roles != 0 else 1
        embed = discord.Embed(
            color = discord.Colour.dark_theme()
            )
        embed.set_author(name = 'Texno_hub shop!', icon_url = 'http://s1.iconbird.com/ico/2014/1/606/w512h5121390848250shop512.png')
        if arg is None:
            for param in shop_json:
                embed.add_field(name = param['name'] + f"`{str(prices[shop_json.index(param, 0, 6)] * modifier if prices[shop_json.index(param, 0, 6)] != 1000 else 1000) + '$' if shop_json.index(param, 0, 6) != 4 else '?'}`", value = param['value'], inline = False)
            await ctx.send(embed = embed)
        elif arg == "roles":
            roles = cool_roles
            i = 1
            for role in roles:
                embed.add_field(name = f"{i}. {self.guild.get_role(role['role']).name} Цена - `{role['cost']}$`", value = f"`buy suprole {i}`", inline = False)
                i += 1
            await ctx.send(embed = embed)
        else:
            raise Errors.InvalidItemError
    
    async def check_wallet(self, member_id, value):
        user = self.get_user(member_id)
        return True if int(user['money']) / value >= 1 else value - int(user['money'])
    
    async def pay(self, member_id, value):
        can_pay = await self.check_wallet(member_id, value)
        if can_pay is True:
            result = self.update_user(member_id, 'inc', money = -value)
            return result
        else:
            raise Errors.NotEnoughMoneyError(can_pay)
    
    async def check_name(self, name : str):
        if name is None:
            raise Errors.InvalidNameError
        elif not 3 < len(name) < 17 or not discord.utils.get(self.guild.roles, name = name) is None:
            raise Errors.InvalidNameError
        return name
    
    async def check_color(self, color : str):
        try:
            color = await hex_to_rgb(color)
        except:
            raise Errors.InvalidColorError
        else:
            return color

    async def getRoleFromMention(self, mention):
        try:
            id_ = int(mention[3:-1])
        except:
            raise Errors.HasNoRequiredRole
        return discord.utils.get(self.guild.roles, id = id_)

    async def isCustomRole(self, member_id, role_id):
        if role_id in self.get_user(member_id)['custom_roles']:
            return True
        return False

    async def parse_param(self, param):
        if param == "all":
            return param
        try:
            param = int(param)
        except:
            raise Errors.InvalidItemError
        else:
            return int(param)
    
    @commands.command(aliases = ['bay'])
    async def buy(self, ctx, item = None, param1 = None, param2 = None, member2 : discord.Member = None):
        member = ctx.author
        user = self.get_user(ctx.author.id)
        user_roles = len(user['inventory']) + len(user['custom_roles'])
        modifier = (2 * user_roles) if user_roles != 0 else 1
        if not item in items:
            raise Errors.InvalidItemError
        elif item in (items[:2]):
            cash = 10000 * modifier
            name = await self.check_name(param1)
            color = await self.check_color(param2)
            role = await self.guild.create_role(name = name, colour = discord.Colour.from_rgb(color[0], color[1], color[2]), mentionable = True, reason = f"The {member.name} has bought the role")
            if item == "doblerole":
                cash = 15000 * modifier
                if not member2:
                    await role.delete()
                    raise Errors.InvalidFriendError
                self.update_user(member2.id, mode = 'push', inventory = role.id)
            try:
                await self.pay(member.id, cash)
            except Errors.NotEnoughMoneyError:
                await role.delete()
            else:
                await member.add_roles(role)
                self.update_user(member.id, 'push', custom_roles = role.id)
                await send_message(ctx.channel, f"вы купили роль {role.name}!")
                if not member2 is None:
                    await send_message(ctx.channel, f"Чтобы получить роль, {member2.name} должен написать `inventory take [id предмета]` или `inventory take all`")
            
        elif item in(items[2:4]):
            role = await self.getRoleFromMention(param1)
            if role in member.roles and await self.isCustomRole(member.id, role.id):
                cash = 1000
                if item == "rolecolor":
                    color = await self.check_color(param2)
                    await self.pay(member.id, cash)
                    try:
                        await role.edit(colour = discord.Colour.from_rgb(color[0], color[1], color[2]))
                    except:
                        self.update_user(member.id, 'inc', money = cash)
                        await send_message(ctx.channel, "Невозможно обновить роль")
                        return
                    message = "цвет"
                elif item == "rolename":
                    name = await self.check_name(param2)
                    await self.pay(member.id, cash)
                    try:
                        await role.edit(name = name)
                    except:
                        self.update_user(member.id, 'inc', money = cash)
                        await send_message(ctx.channel, "Невозможно обновить роль")
                        return
                    message = "имя"
                await send_message(ctx.channel, f"Вы успешно обновили {message} роли")
            else:
                raise Errors.HasNoRequiredRole
        elif item in items[4:]:
            if not param1 is None:
                try:
                    param1 = int(param1)
                except:
                    raise Errors.InvalidItemError
                else:
                    if param1 in range(1, len(cool_roles) + 1):
                        param1 -= 1
                        srole = cool_roles[param1]
                        role = self.guild.get_role(srole['role'])
                        if role in member.roles:
                            raise Errors.InvalidRoleError
                        await self.pay(member.id, srole['cost'])
                        await member.add_roles(role, reason = f'{member.name} купил роль!')
                        self.update_user(member.id, 'push', custom_roles = role.id)
                    else:
                        raise Errors.InvalidItemError
                    await send_message(ctx.channel, f"Вы купили роль {role.name}!")
            else:
                raise Errors.InvalidItemError
                    

    @commands.command()
    async def inventory(self, ctx, action = None, param = None):
        member = ctx.author
        items = list(self.get_user(member.id)['inventory'])
        if action is None:
            embed = discord.Embed(color = discord.Colour.teal())
            embed.set_author(name = f"{member.name} inventory", icon_url = member.avatar_url)
            for i in range(len(items)):
                role = self.guild.get_role(int(items[i]))
                embed.add_field(name = str(i + 1), value = role.name)
            if len(items) == 0:
                embed.title = "У вас нет предметов :("
            embed.set_thumbnail(url = "https://cdn1.iconfinder.com/data/icons/video-game-lineal/32/inventory-item-chest-512.png")
            await ctx.send(embed = embed)
        elif action == "take":
            if param is None:
                raise Errors.InvalidItemError
            else:
                param = await self.parse_param(param)
                if param == "all":
                    for item in items:
                        self.update_user(member.id, 'pull', inventory = int(item))
                        self.update_user(member.id, 'push', custom_roles = int(item))
                        await member.add_roles(self.guild.get_role(int(item)))
                    await send_message(ctx.channel, "все предметы были применены")
                elif param - 1 in range(len(items)):
                    role_id = int(items[param - 1])
                    self.update_user(member.id, 'pull', inventory = int(role_id))
                    self.update_user(member.id, 'push', custom_roles = int(role_id))
                    await member.add_roles(self.guild.get_role(role_id))
                    await send_message(ctx.channel, f"предмет {self.guild.get_role(role_id).name} был применен")
                else:
                    raise Errors.InvalidItemError
        elif action == "keep":
            if param is None:
                raise Errors.InvalidItemError
            else:
                role = await self.getRoleFromMention(param)
                if role in member.roles and await self.isCustomRole(member.id, role.id):
                    self.update_user(member.id, 'push', inventory = int(role.id))
                    self.update_user(member.id, 'pull', custom_roles = int(role.id))
                    await member.remove_roles(role)
                    await send_message(ctx.channel, f"предмет {role.name} был перенесён в инвентарь")
                else:
                    raise Errors.HasNoRequiredRole

        else:
            raise Errors.InvalidItemError



def setup(Bot):
    Bot.add_cog(Shop(Bot))