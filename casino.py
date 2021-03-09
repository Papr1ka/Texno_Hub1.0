import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
from database import Database
import random
import asyncio
import Errors
from bot import send_message, min_bet, max_bet

slots = [1, 2, 3, 4, 5] #0.5, 0.75, 1, 1.25, 1.5 modifier
emoji = ["","🍗", "🍌", "🥥", "🍎", "🍺"]
mod = {
    slots[0] : 0.5,
    slots[1] : 0.75,
    slots[2] : 1,
    slots[3] : 1.25,
    slots[4] : 1.5
}

combo = {
    1 : 1, #vertival lines
    2 : 1, #bevels
    3 : 2, #big lines
    4 : 1.5, #medi lines
    5 : 1 #small lines
}

emomoji = {
    1 : 811696894149394443,
    2 : 811697988878598144,
    3 : 811698002217271316,
    4 : 811698013696688138,
    5 : 811698023666942034,
    6 : 811698034026479666  
}

class Slots(discord.Embed):
    def __init__(self):
        super().__init__(color = discord.Colour.dark_theme())
        self.size = (3, 5) #x, y 
    
    def randomize(self):
        self.roll = [random.choice(slots) for i in range(self.size[0] * self.size[1])]
        for i in range(self.size[0]):
            print([emoji[i] for i in (self.roll[self.size[1] * i : self.size[1] * i + 5])])
    
    def checkwin(self):
        r = self.roll
        """
        x 0 0
        x 0 0
        x 0 0
        """
        def check_vertical(r):
            win = 0
            up = combo[1]
            if r[0] == r[5] == r[10]:
                win += mod[r[0]] * up
            if r[1] == r[6] == r[11]:
                win += mod[r[1]] * up
            if r[2] == r[7] == r[12]:
                win += mod[r[2]] * up
            if r[3] == r[8] == r[13]:
                win += mod[r[3]] * up
            if r[4] == r[9] == r[14]:
                win += mod[r[4]] * up
            return win

        
        """
        x 0 0
        0 x 0
        0 0 x
        """

        def check_bevel(r):
            win = 0
            up = combo[2]
            if r[0] == r[6] == r[12]:
                win += mod[r[0]] * up
            if r[1] == r[7] == r[13]:
                win += mod[r[1]] * up
            if r[2] == r[8] == r[14]:
                win += mod[r[2]] * up
            return win

        
        """
        0 0 x
        0 x 0
        x 0 0
        """
        
        def check_ubevel(r):
            win = 0
            up = combo[2]
            if r[2] == r[6] == r[10]:
                win += mod[r[2]] * up
            if r[3] == r[7] == r[11]:
                win += mod[r[3]] * up
            if r[4] == r[8] == r[12]:
                win += mod[r[4]] * up
            return win
        
        """
        x x x x x
        0 0 0 0 0
        0 0 0 0 0
        """

        def check_big_line(r):
            win = 0
            up1 = combo[3]
            up2 = combo[4]
            up3 = combo[5]
            if r[0] == r[1] == r[2] == r[3] == r[4]:
                win += up1 * mod[r[0]]
            elif r[0] == r[1] == r[2] == r[3]:
                win += up2 * mod[r[0]]
            elif r[1] == r[2] == r[3] == r[4]:
                win += up2 * mod[r[1]]
            elif r[0] == r[1] == r[2]:
                win += up3 * mod[r[0]]
            elif r[1] == r[2] == r[3]:
                win += up3 * mod[r[1]]
            elif r[2] == r[3] == r[4]:
                win += up3 * mod[r[2]]

            if r[5] == r[6] == r[7] == r[8] == r[9]:
                win += up1 * mod[r[5]]
            elif r[5] == r[6] == r[7] == r[8]:
                win += up2 * mod[r[5]]
            elif r[6] == r[7] == r[8] == r[9]:
                win += up2 * mod[r[6]]
            elif r[5] == r[6] == r[7]:
                win += up3 * mod[r[5]]
            elif r[6] == r[7] == r[8]:
                win += up3 * mod[r[6]]
            elif r[7] == r[8] == r[9]:
                win += up3 * mod[r[7]]

            if r[10] == r[11] == r[12] == r[13] == r[14]:
                win += up1 * mod[r[10]]
            elif r[10] == r[11] == r[12] == r[13]:
                win += up2 * mod[r[10]]
            elif r[11] == r[12] == r[13] == r[14]:
                win += up2 * mod[r[11]]
            elif r[10] == r[11] == r[12]:
                win += up3 * mod[r[10]]
            elif r[11] == r[12] == r[13]:
                win += up3 * mod[r[11]]
            elif r[12] == r[13] == r[14]:
                win += up3 * mod[r[12]]
            return win
        
        win = check_vertical(r) + check_bevel(r) + check_ubevel(r) + check_big_line(r)
        return win

    def spin(self, bet):
        game = self.randomize()
        win = self.checkwin()
        return bet * win, self.roll

#about 39%

class Rulet():
	def __init__(self):
		self.generate()

	def roll(self):
		return self.spin()
	
	def generate(self):
		self.params = {
			#color | % 2 | group
			1 : ("red", "odd", 1),
			2 : ('black', 'even', 2),
			3 : ('red', 'odd', 3),
			4 : ('black', 'even', 1),
			5 : ('red', 'odd', 2),
			6 : ('black', 'even', 3),
			7 : ('red', 'odd', 1),
			8 : ('black', 'even', 2),
			9 : ('red', 'odd', 3),
			10 : ('black', 'even', 1),
			11 : ('black', 'odd', 2),
			12 : ('red', 'even', 3),
			13 : ('black', 'odd', 1),
			14 : ('red', 'even', 2),
			15 : ('black', 'odd', 3),
			16 : ('red', 'even', 1),
			17 : ('black', 'odd', 2),
			18 : ('red', 'even', 3),
			19 : ('red', 'odd', 1),
			20 : ('black', 'even', 2),
			21 : ('red', 'odd', 3),
			22 : ('black', 'even', 1),
			23 : ('red', 'odd', 2),
			24 : ('black', 'even', 3),
			25 : ('red', 'odd', 1),
			26 : ('black', 'even', 2),
			27 : ('red', 'odd', 3),
			28 : ('black', 'even', 1),
			29 : ('black', 'odd', 2),
			30 : ('red', 'even', 3),
			31 : ('black', 'odd', 1),
			32 : ('red', 'even', 2),
			33 : ('black', 'odd', 3),
			34 : ('red', 'even', 1),
			35 : ('black', 'odd', 2),
			36 : ('red', 'even', 3),
			0 : (None, None, None)
		}
		self.field = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

	def spin(self):
		start_pos = random.choice(self.field)
		start_index = self.field.index(start_pos, 0, 37)
		rolls = 5
		abstract_field = self.field
		abstract_field.extend(abstract_field)
		abstract_field.extend(abstract_field)
		positions = []
		for i in range(rolls):
			positions.append(abstract_field[start_index : start_index + 9])
			start_index += 9
		return positions, self.params

nums = {
    1 : "1️⃣",
    2 : "2️⃣",
    3 : "3️⃣",
    4 : "4️⃣",
    5 : "5️⃣",
    6 : "6️⃣",
    7 : "7️⃣",
    8 : "8️⃣",
    9 : "9️⃣",
    0 : "0️⃣",
} 

class Casino(Database, commands.Cog):

    def __init__(self, Bot):
        super(Casino, self).__init__('main')
        self.Bot = Bot
        self.casino = self.get_user(777)
        self.last_money = int(self.casino['money'])
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.Bot.get_guild(453565320708489226)
    
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
    
    @commands.command()
    @cooldown(2, 6, BucketType.channel)
    async def spin(self, ctx, bet = None):
        if bet is None:
            raise Errors.InvalidBetError
        else:
            try:
                bet = int(bet)
                if bet < min_bet or bet > max_bet:
                    raise Errors.InvalidBetError
            except:
                raise Errors.InvalidBetError
        await self.pay(ctx.author.id, bet)
        embed = discord.Embed(title = "Слоты", color = discord.Colour.magenta())
        embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
        embed.set_thumbnail(url = "https://cdn.iconscout.com/icon/free/png-512/casino-chance-gamble-gambling-roulette-table-wheel-4-17661.png")
        lines = ["☠️☠️☠️☠️☠️", "☠️☠️☠️☠️☠️", "☠️☠️☠️☠️☠️"]
        for l in range(3):
            lines[l] = " ".join(list(lines[l]))
        embed.description = "".join([i + "\n" for i in lines])
        game = await ctx.send(embed = embed)
        roll = Slots().spin(bet)
        for i in range(5):
            await asyncio.sleep(1)
            for lin in range(3):
                lines[lin] = lines[lin][:i * 2] + str(emoji[roll[1][i + lin * 5]]) + " " + lines[lin][(i + 2) * 2:]
            description = "".join([i + "\n" for i in lines])
            embed.description = description
            await game.edit(embed = embed)
        embed.set_footer(text = ("Вы потеряли" if roll[0] - bet < 0 else "Вы выиграли") + " " + str(abs(roll[0] - bet)) + " $", icon_url = "https://image.flaticon.com/icons/png/512/8/8817.png")
        await game.edit(embed = embed)
        await self.info_casino(-(roll[0] - bet))
        self.update_user(ctx.author.id, 'inc', money = int(roll[0]))
    
    async def rollTheDice(self):
        return random.randint(1, 6), random.randint(1, 6)
    
    @commands.command()
    async def dice(self, ctx, bet = None, member : discord.Member = None):
        if bet is None:
            raise Errors.InvalidBetError
        else:
            try:
                bet = int(bet)
                if bet < min_bet or bet > max_bet:
                    raise Errors.InvalidBetError
            except:
                raise Errors.InvalidBetError
        embed = discord.Embed(color = discord.Colour.teal())
        embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
        if member is None:
            embed.title = f"{ctx.author.display_name} vs King Dice!"
            embed.set_thumbnail(url = "https://i.pinimg.com/originals/a0/39/f0/a039f043d0c0089a203fc3b974081496.png")
            await self.pay(ctx.author.id, bet)
            win = await self.rollTheDice()
            embed.title = f"{ctx.author.display_name} : {str(await self.guild.fetch_emoji(emomoji[win[0]]))} vs {str(await self.guild.fetch_emoji(emomoji[win[1]]))} : King Dice"
            dic = await ctx.send(embed = embed)
            if win[0] > win[1]:
                description = f"{ctx.author.display_name} выйграл! {bet - bet // 20}$"
                self.update_user(ctx.author.id, 'inc', money = (bet * 2) - bet // 20)
                await self.info_casino(-((bet * 2) - bet // 20))
            elif win[0] == win[1]:
                description = f"ничья"
                self.update_user(ctx.author.id, 'inc', money = bet)
            else:
                description = f"King Dice выйграл! {bet}$"
                await self.info_casino(bet)
            await asyncio.sleep(1)
            embed.set_footer(text = description)
            await dic.edit(embed = embed)
        else:
            if member.id == ctx.author.id:
                raise Errors.InvalidFriendError
            await ctx.send(f"{member.mention}, {ctx.author.display_name} приглашает вас в сыграть в кости, ставка {bet}, напишите `claim`")

            def check(m):
                return (m.content == 'claim' or m.content[1:] == 'claim') and m.channel == ctx.channel and m.author == member

            msg = await self.Bot.wait_for('message', check = check, timeout = 60)
            await self.pay(ctx.author.id, bet)
            await self.pay(msg.author.id, bet)
            embed.title = f"{ctx.author.display_name} vs {msg.author.display_name}!"
            embed.set_thumbnail(url = msg.author.avatar_url)
            win = await self.rollTheDice()
            embed.title = f"{ctx.author.display_name} : {str(await self.guild.fetch_emoji(emomoji[win[0]]))} vs {str(await self.guild.fetch_emoji(emomoji[win[1]]))} : {msg.author.name}"
            dic = await ctx.send(embed = embed)
            if win[0] > win[1]:
                description = f"{ctx.author.display_name} выйграл! {bet}$"
                self.update_user(ctx.author.id, 'inc', money = bet * 2)
            elif win[0] == win[1]:
                description = f"ничья!"
                self.update_user(ctx.author.id, 'inc', money = bet)
                self.update_user(msg.author.id, 'inc', money = bet)
            else:
                description = f"{msg.author.display_name} выйграл! {bet}$"
                self.update_user(msg.author.id, 'inc', money = bet * 2)
            await asyncio.sleep(2)
            embed.set_footer(text = description)
            await dic.edit(embed = embed)

    @commands.command(aliases = ['pay'])
    async def give(self, ctx, money = None, member : discord.Member = None):
        if money is None:
            raise Errors.InvalidMoneyError
        else:
            try:
                money = int(money)
            except:
                raise Errors.InvalidMoneyError
        if member is None or ctx.author.id == member.id:
            raise Errors.InvalidFriendError
        await self.pay(ctx.author.id, money)
        self.update_user(member.id, mode = 'inc', money = money)
        embed = discord.Embed(color = discord.Colour.teal(), title = f"{ctx.author.display_name} передал {member.nick if not member.nick is None else member.name} {money}$")
        await ctx.send(embed = embed)
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def pgive(self, ctx, money = None, member : discord.Member = None):
        if money is None:
            raise Errors.InvalidMoneyError
        else:
            try:
                money = int(money)
            except:
                raise Errors.InvalidBetError
        if member is None:
            raise Errors.InvalidFriendError
        
        self.update_user(member.id, mode = 'inc', money = money)
        embed = discord.Embed(color = discord.Colour.teal(), title = f"{ctx.author.display_name} передал {member.nick if not member.nick is None else member.name} {money}$")
        await ctx.send(embed = embed)
    
    def get_emoji(self, number, params):
        if number == 0:
            return "🟢"
        elif len(str(number)) == 1:
            if params[number][0] == "red":
                return "🔴"
            else:
                return "⚫"
        else:
            if params[number][0] == "black":
                return "⚫⚫"
            else:
                return "🔴🔴"

    def get_number(self, number):
        r = ""
        for i in str(number):
            r += nums[int(i)]
        return r
    
    @commands.command()
    @cooldown(2, 6, BucketType.channel)
    async def roll(self, ctx, money = None, bet = None, co_bet = None):
        if money is None:
            raise Errors.InvalidMoneyError
        else:
            try:
                money = int(money)
                if money < min_bet or money > max_bet:
                    raise Errors.InvalidBetError
            except:
                raise Errors.InvalidBetError
        if bet is None or not bet in (*[str(i) for i in range(37)], "red", "black", "odd", "even", "dozen", "line"):
            raise Errors.InvalidSimpleBetError
        
        if bet in ("dozen", "line"):
            if co_bet is None:
                raise Errors.InvalidBetError
            else:
                try:
                    co_bet = int(co_bet)
                    if not co_bet in range(1, 4):
                        raise Errors.InvalidBetError
                except:
                    raise Errors.InvalidBetError

        await self.pay(ctx.author.id, money)
        embed = discord.Embed(color = discord.Colour.teal(), title = "Рулетка")
        embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url)
        embed.set_thumbnail(url = "https://cdn.vox-cdn.com/thumbor/5hMUP65bqtC1-S93-7iJRR_KxFA=/0x0:1280x720/1400x1050/filters:focal(538x258:742x462):format(jpeg)/cdn.vox-cdn.com/uploads/chorus_image/image/56980799/All_Bets_are_Off_header.0.jpg")
        positions, params = Rulet().roll()
        display0 = "⬇"
        display1 = " | ".join([ self.get_emoji(i, params) for i in positions[0]])
        display2 = " | ".join([ self.get_number(i) for i in positions[0]])
        embed.description = display0 + "\n\n" + display1 + "\n" + display2
        game = await ctx.send(embed = embed)
        for x in range(1, 5):
            await asyncio.sleep(1)
            display1 = " | ".join([ self.get_emoji(i, params) for i in positions[x]])
            display2 = " | ".join([ self.get_number(i) for i in positions[x]])
            embed.description = display0 + "\n\n" + display1 + "\n" + display2
            await game.edit(embed = embed)

        win = positions[-1][0]
        bigboom = 0
        if bet in ("red", "black"):
            if bet == params[win][0]:
                bigboom = money * 2
        elif bet in ("even", "odd"):
            if bet == params[win][1]:
                bigboom = money * 2
        elif bet == "dozen":
            if win in (range(1, 37)):
                if win in range(1, 13):
                    if co_bet == 1:
                        bigboom = money * 3
                elif win in range(12, 25):
                    if co_bet == 2:
                        bigboom = money * 3
                elif win in range(24, 37):
                    if co_bet == 3:
                        bigboom = money * 3

        elif bet == "line":
            if co_bet == int(params[win][2]):
                bigboom = money * 3
        elif int(bet) in (range(37)):
            if int(bet) == win:
                bigboom = money * 36
        
        if bigboom > 0:
            text = f"Вы выйграли {bigboom - money}$ !!!"
            await self.info_casino(bigboom - money)
        else:
            text = f"Вы проиграли {money}"
            await self.info_casino(money)
        self.update_user(ctx.author.id, 'inc', money = bigboom)
        embed.set_footer(text = text)
        await game.edit(embed = embed)
    
    @commands.command()
    async def kf(self, ctx, arg):
        if arg is None or not arg in ("spin", "roll", "dice"):
            raise Errors.InvalidItemError
        else:
            embed = discord.Embed(title = f"Справка по {arg}", color = discord.Colour.teal())
            if arg == "roll":
                embed.description = "***Типы ставок и выйгрыши***"
                embed.add_field(name = "`red` или `black`", value = "ставка на цвет, выйгрыш 1 к 1")
                embed.add_field(name = "`odd` или `even`", value = "ставка на чётность, выйгрыш 1 к 1")
                embed.add_field(name = "`dozen [число](1 - 3)`", value = "ставка на дюжину, выйгрыш 2 к 1")
                embed.add_field(name = "`line [число](1 - 3)`", value = "ставка на колонку, выйгрыш 2 к 1")
                embed.add_field(name = "`[число](0 - 36)`", value = "ставка на число, выйгрыш 35 к 1")
                embed.set_image(url = "http://12bets.ru/attachments/Image/evropeyskaya-ruletka.JPG?template=generic")
            elif arg == "spin":
                embed.description = "Выйгрыши, суммируются, формируется по формуле - `тип выйгрыша` * `тип предметов`"
                embed.add_field(name = "3 в ряд или по диагонали", value = "Коэффициент - 1")
                embed.add_field(name = "4 в ряд", value = "Коэффициент - 1.5")
                embed.add_field(name = "5 в ряд", value = "Коэффициент - 2")
                embed.add_field(name = str(emoji[1]), value = "Коэффициент - 0.5")
                embed.add_field(name = str(emoji[2]), value = "Коэффициент - 0.75")
                embed.add_field(name = str(emoji[3]), value = "Коэффициент - 1")
                embed.add_field(name = str(emoji[4]), value = "Коэффициент - 1.25")
                embed.add_field(name = str(emoji[5]), value = "Коэффициент - 1.5")
            elif arg == "dice":
                embed.description = "***Правила и выйгрыш***\n\nВыигрывает тот, у кого выпадет большее значение\nВыйгрыш:\n 1 к 1 если с игроком\n1 к 1 - 2.5% от выйгрыша если с дайсом"
            await ctx.send(embed = embed)
    
    async def info_casino(self, money):
        self.update_user(777, 'inc', money = money) #cash
        self.update_user(777, 'inc', voice = money) #income
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def income(self, ctx):
        embed = discord.Embed(
            color = discord.Colour.magenta(),
            title = "Прибыль казино"
        )
        income = int(self.get_user(777)['voice'])
        cash = int(self.get_user(777)['money'])
        embed.set_thumbnail(url = 'http://pm1.narvii.com/6640/7d60e26077831a9496381d56a97160506ade7d1f_00.jpg')
        embed.add_field(name = "Доход за всё время", value = str(income))
        embed.add_field(name = "Доход за сегодня", value = str(income - self.last_money))
        embed.add_field(name = "Счёт", value = str(cash))
        await ctx.send(embed = embed)
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def cashout(self, ctx):
        money = int(self.get_user(777)['money'])
        self.update_user(777, 'inc', money = -money)
        self.update_user(ctx.author.id, 'inc', money = money)
        await send_message(ctx.channel, f"{ctx.author} Снял со счёта казино {money} $")


def setup(Bot):
    Bot.add_cog(Casino(Bot))
