import discord
from discord.ext import commands
from discord.utils import get
from PIL import Image, ImageFont, ImageDraw
import math
import emoji
import regex
import asyncio
import random
import time
import datetime
from random import randint
import Errors
import os

Token = str(os.environ.get("TOKEN"))
prefixes = ('?', '+', '=')
min_bet = 100
max_bet = 5000

Bot = commands.Bot(command_prefix = ['?', '+', '='], intents = discord.Intents.all())
new_year_url = "https://images-ext-2.discordapp.net/external/DUJiSi_F0zD4qC7KQ_fhitA-71QafMEy5yr9AlmqOuM/%3Fsize%3D604x453%26quality%3D96%26sign%3D3516dad15b573bc76e756800404d003a%26type%3Dalbum/https/sun9-52.userapi.com/impf/ujA6AEanaoSdjFoESy4N8lwYHSHAv6iFzXtOIw/VXmJolIY4lE.jpg"
Bot.remove_command("help")

@Bot.event
async def on_ready():
	print(f"{Bot.user.name} авторизован")
	game = discord.Game('prefixes: ' + str(' '.join(prefixes)), activity = discord.ActivityType.custom)
	await Bot.change_presence(status=discord.Status.online, activity=game)

def get_channel_text(channel_id):
	for channel in Bot.get_all_channels():
		if channel.id == channel_id and channel.type == discord.ChannelType.text:
			return channel

async def send_message(channel, message, delete = None, coud = False):
	"""
	channel : obj , channel
	message : str , text
	delete : int , delete_after
	coud : boot, delete last bot message
	"""
	if coud:
		msgs = 0
		async for i in channel.history(limit = 2):
			if i.author.bot == True:
				msgs += 1
		if msgs > 1:
			await channel.purge(limit = 1)
	embed = discord.Embed(
		color = discord.Colour.from_rgb(randint(0, 255),randint(0, 255),randint(0, 255)),
		title = message)
	message = await channel.send(embed = embed, delete_after = delete)
	return message

async def hex_to_rgb(hex):
	hex = hex.lstrip('#')
	return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))



@Bot.command()
@commands.has_permissions(administrator=True)
async def hello(ctx, arg):
	await ctx.send(arg)
	print(arg)


@Bot.command(pass_context = True, aliases = ['hel', 'h'])
async def help(ctx, category = None):
	embed = discord.Embed(
						color = discord.Colour.blurple(),
						title = "Команды сервера Texno_hub || префиксы: = , + , ? ")
	if category is None:
		embed.add_field(name = "Казино и деньги", value = "`help casino`", inline = False)
		embed.add_field(name = "Приватные каналы", value = "`help private`", inline = False)
		embed.add_field(name = "Пользовательское", value = "`help user`", inline = False)
		embed.add_field(name = "Другое", value = "`help other`", inline = False)
	elif category == "casino":
		embed.description = " '[ ]' - не ставить, '~' - не обязательно"
		embed.add_field(name = "Крутить рулетку",
						value = "`roll [сумма денег] [ставка]`",
						inline = False)
		embed.add_field(name = "Крутить слоты",
						value = "`spin [сумма денег]`",
						inline = False)
		embed.add_field(name = "Сыграть в кости",
						value = "`dice [сумма денег] ~[@user]`",
						inline = False)
		embed.add_field(name = "Коэффициенты спинов",
						value = "`kf spin`",
						inline = False)
		embed.add_field(name = "Коэффициенты и ставки рулетки",
						value = "`kf roll`",
						inline = False)
		embed.add_field(name = "Правила и выйгрыш костей",
						value = "`kf dice`",
						inline = False)
		embed.add_field(name = "Передать деньги",
						value = "`give [сумма денег] [@user]`",
						inline = False)
	elif category == "private":
		embed.add_field(name = "Пригласить в приватный канал",
						value = "`private invite [@user], сокращения: private - p, invite - i`",
						inline = False)
		embed.add_field(name = "Кикнуть из приватного канала",
						value = "`private kick [@user], сокращения: private - p, kick - k`",
						inline = False)
	elif category == "other":
		embed.add_field(name = "Опрос",
						value = "`opros [тема опроса]/[вариант ответа]/.../[вариант ответа]`",
						inline = False)
		embed.add_field(name = "Новогодняя тема",
						value = "`theme`",
						inline = False)
		embed.add_field(name = "Погода",
						value = "`weather [город], weather[id из результата поиска]`",
						inline = False)
		embed.add_field(name = "Музыкальные боты",
						value = "`bots, сокращения: bots - b`",
						inline = False)
		embed.add_field(name = "Шар предсказаний",
						value = "`ball [ваш вопрос]`",
						inline = False)
		embed.add_field(name = "Поддержать сервер",
						value = "`donate`",
						inline = False)
	elif category == "user":
		embed.add_field(name = "Статус",
						value = "`status`",
						inline = False)
		embed.add_field(name = "изменить статус",
						value = "`custom [статус]`",
						inline = False)
		embed.add_field(name = "Статистика",
						value = "`stats`",
						inline = False)
		embed.add_field(name = "Инвентарь",
						value = "`inventory`",
						inline = False)
		embed.add_field(name = "Взять предмет из инвентаря",
						value = "`inventory take [id предмета]`",
						inline = False)
		embed.add_field(name = "Взять все предметы из инвентаря",
						value = "`inventory take all`",
						inline = False)
		embed.add_field(name = "Положить предмет в инвентарь",
						value = "`inventory keep [@role]`",
						inline = False)
		embed.add_field(name = "Магазин",
						value = "`shop`",
						inline = False)
	else:
		await send_message(ctx.channel, "категория не найдена")
		return
		
	embed.set_thumbnail(url = new_year_url)
	await ctx.send(embed = embed)

@Bot.command(pass_context = True)
async def theme(ctx):
	file = discord.File("./BandagedBD.exe")
	file2 = discord.File("./Texho_Hub.theme.css")
	description = "Инструкция:\nЧтобы установить тему, необходимо:\n1. - Скачать BandagedBD\n2. - Agree\n3. - Install BandagedBD\n4. - Install to stable\n5. - Install\n6. - Открыть discord, зайти в настройки, выбрать themes\n7. - Open Theme Folder\n8. - Скачать Texno-Hub theme\n9. - Закинуть тему в папку (пункт 7)\n10. - Активировать тему в дискорде - готово!\n\nЕсли возникли проблемы:\n1. - выполнить пункты 1-3\n2. - Repair BandagedBD\n3. - Repair On Stable\n 4. - Поставить все галочки\n5. - Repair"
	embed = discord.Embed(
						color = discord.Colour.blurple(),
						title = "Texno_hub theme version 1.0",
						description = description)
	await ctx.send(embed=embed, files = [file, file2])


@Bot.command(pass_context = True, aliases = ["предсказание", "bal","шарик","bol","boll"])
async def ball(ctx, text=None):
		asks = {
    		1 : "Бесспорно",
    		2 : "Предрешено",
    		3 : "Никаких сомнений",
    		4 : "Определённо да",
    		5 : "Можешь быть уверен в этом",
    		6 : 'Мне кажется - "да"',
    		7 : "Вероятнее всего",
    		8 : "Хорошие перспективы",
    		9 : 'Знаки говорят - "да"',
    		10 : "Да",
    		11: "Пока не ясно, попробуй снова",
    		12 : "Спроси позже",
    		13 : "Лучше не рассказывать",
    		14 : "Сейчас нельзя предсказать",
    		15 : "Сконцентрируйся и спроси опять",
    		16 : "Даже не думай",
    		17 : 'Мой ответ - "нет"',
    		18 : 'По моим данным - "нет"',
    		19 : "Перспективы не очень хорошие",
    		20 : "Весьма сомнительно",
    	}
		ask = random.randint(1,20)
		ask = asks[ask]
		
		embed = discord.Embed(
    		color = discord.Color.dark_teal(),
    		title = ask)
		await ctx.send(embed = embed)


@Bot.command(aliases = ["b", "bot"])
async def bots(ctx, channel : discord.TextChannel = None):
	if not channel is None:
		guild = channel.guild
	else:
		guild = ctx.guild
	b1 = get(guild.members, id = 235088799074484224)
	b2 = get(guild.members, id = 252128902418268161)
	b3 = get(guild.members, id = 415062217596076033)
	embed = discord.Embed(color = discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
						title = "Музыкальные боты	:white_check_mark: - свободен,   :x: - занят")
	embed.add_field(name = f"@Rythm#3722 {':x:' if b1.voice else ':white_check_mark:'}",
					value = f"префикс `!`",
					inline = False)
	embed.add_field(name = f"@Rythm 2#2000 {':x:' if b2.voice else ':white_check_mark:'}",
					value = f"префикс `-`",
					inline = False)
	embed.add_field(name = f"@Rythm Canary#8406 {':x:' if b3.voice else ':white_check_mark:'}",
					value = f"префикс `*`",
					inline = False)
	if not channel is None:
		await channel.send(embed = embed)
	else:
		await ctx.send(embed = embed)



@Bot.event
async def on_command_error(ctx, error):
	channel = ctx.channel
	timeout = 10

	if isinstance(error, Errors.InvalidItemError):
		await send_message(channel, "позиция не найдена", timeout)
	elif isinstance(error, Errors.InvalidNameError):
		await send_message(channel, "название недоступно", timeout)
	elif isinstance(error, Errors.InvalidRoleError):
		await send_message(channel, "такая роль уже существует или недоступна", timeout)
	elif isinstance(error, Errors.InvalidColorError):
		await send_message(channel, "неизвестный цвет, введите в hex", timeout)
	elif isinstance(error, Errors.NotEnoughMoneyError):
		await send_message(channel, "недостаточно средств", timeout)
	elif isinstance(error, Errors.HasNoRequiredRole):
		await send_message(channel, "у вас нет такой роли, или эта роль недоступна для махинаций", timeout)
	elif isinstance(error, Errors.InvalidFriendError):
		await send_message(channel, "пользователь указан неверно", timeout)
	elif isinstance(error, Errors.InvalidBetError):
		await send_message(channel, f"невозможная ставка, минимально {min_bet}, максимум {max_bet}", timeout)
	elif isinstance(error, Errors.InvalidMoneyError):
		await send_message(channel, "невозможное количество денег", timeout)
	elif isinstance(error, Errors.InvalidSimpleBetError):
		await send_message(channel, "невозможная ставка", timeout)
	elif isinstance(error, Errors.NotConnectedError):
		await send_message(channel, "отсутствует подключение к голосовому каналу", timeout)
	elif isinstance(error, Errors.NotPrivateChannelError):
		await send_message(channel, "вы находитесь не в приватном канале", timeout)
	elif isinstance(error, Errors.NotChannelAdminError):
		await send_message(channel, "вы не являетесь администратором канала", timeout)
	elif isinstance(error, commands.MissingRequiredArgument):
		await send_message(channel, "недостаточно аргументов", timeout)
	elif isinstance(error, commands.CommandNotFound):
		await send_message(channel, "команды не существует", timeout)
	elif isinstance(error, commands.MissingRole):
		await send_message(channel, "недостаточно прав", timeout)
	elif isinstance(error, commands.ArgumentParsingError):
		await send_message(channel, "ошибка", timeout)
	elif isinstance(error, commands.TooManyArguments):
		await send_message(channel, "слишком много агрументов", timeout)
	elif isinstance(error, commands.UserInputError):
		await send_message(channel, "Что-то было указано неверно", timeout)
	elif isinstance(error, commands.CommandOnCooldown):
		await send_message(channel, "подождите, или используйте другой канал", timeout)
	else:
		print(error)

Bot.load_extension("casino")
Bot.load_extension("voice_manager")
Bot.load_extension("members")
Bot.load_extension("administration")
Bot.load_extension("fun")
Bot.load_extension("user_card")
Bot.load_extension("leveling")
Bot.load_extension("shop")
Bot.load_extension("donate")
Bot.load_extension("giveaway")

Bot.run(Token)
