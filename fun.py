import discord
from discord.ext import commands
from random import randint
import requests
from bs4 import BeautifulSoup
import datetime
from bot import send_message
import asyncio

class fun(commands.Cog):

	pages = {}

	def get_html(self, url, city=None):
			if city == None:
				r = requests.get(url, headers=self.HEADERS)
			else:
				r = requests.get(url+city, headers=self.HEADERS)
			return r

	def parse_sun(self, sun):
			op = []
			for elem in sun:
				elem = elem.split("—")
				if len(elem) > 1:
					op.append(elem[1])
				else:
					op.append(elem[0])
			return op

	def spl(self, sb):
			for i in range(len(sb)):
				if "(" in sb[i]:
					sb = sb[:i]
					return sb
			return sb

	def parse_wind(self, winds):
			winds2 = []
			for i in winds:
				if "-" in i:
					i = i.split("-")
					i = int((int(i[0])+int(i[1]))/2)
					winds2.append(i)
				else:
					winds2.append(int(i))
			return winds2

	def get_content(self, html):
			global pages
			soup = BeautifulSoup(html, "html.parser")
			sections = soup.find_all("section", class_="catalog_block")
			if len(sections)!= 0:
				if len(sections) > 1:
					section = sections[1]
				else:
					section = sections[0]
				results = section.find_all("div", class_="catalog_item")
				if len(results) >= 5:
					op = 5
				else:
					op = len(results)
				for i in range(op):
					result = results[i]
					names = result.find_all('a', class_="catalog_link")
					sb = names[1].get_text()
					sb = self.spl(sb.split())
					spp = ""
					for o in sb:
						spp += str(o) +" "
					if names[0].get_text() not in names[1].get_text():
						name = names[0].get_text()+" - "+str(spp)+" - "+names[-1].get_text()
					else:
						name = names[0].get_text()+" - "+names[-1].get_text()
					print(f"{i+1}. {name}")
					self.pages[name] = self.DOMEN+names[0].get("href")
				return True
			else:
				print("поиск не дал результатов")
				return False

	def parse_results(self):
			html = self.get_html(self.URL, city=self.city)
			if html.status_code == 200:
				po = self.get_content(html.text)
				if po == False:
					return False
				else:
					return True

	def parse(self):
			times = {
			0 : 0,
			3 : 1,
			6 : 2,
			9 : 3,
			12 : 4,
			15 : 5,
			18 : 6,
			21 : 7,
			}
			time = datetime.datetime.now().strftime("%H")
			time = int(time)
			if time%3 == 0:
				pass
			elif time + 1 == 24:
				time = 21
			elif (time - 1)%3 == 0:
				time = time-1
			elif (time + 1)%3 == 0:
				time = time + 1
			else:
				pass

			global city_weather
			for i in self.pages:
				href = self.pages[i]
				page = self.get_html(href)
				soup = BeautifulSoup(page.text, "html.parser")
				today = soup.find('a', class_="tab tablink tooltip")
				temp = today.find('div', class_="tab-weather")
				temp_now = temp.find('span', class_="unit unit_temperature_c").get_text(strip=True)
				self.city_weather['temp_now'] = temp_now
				temp_now_feel = temp.find('span', class_="tab-weather__feel-value").find('span', class_="unit unit_temperature_c").get_text(strip=True)
				self.city_weather['temp_now_feel'] = temp_now_feel

				wind = soup.find('div',class_="widget__row widget__row_table widget__row_wind-or-gust")
				wind = wind.find_all('div', class_="w_wind")
				winds = []
				for w in wind:
					winds.append(w.find('span', class_="unit unit_wind_m_s").get_text(strip=True))
				winds = self.parse_wind(winds)
				self.city_weather['wind'] = winds[times[time]]
				pressure = soup.find('div', class_="chart chart__pressure")
				pressure = pressure.find_all('span', class_="unit unit_pressure_mm_hg_atm")
				pressures = []
				for press in pressure:
					pressures.append(int(press.get_text(strip=True)))
				self.city_weather['pressure'] = pressures[times[time]]
				humidity = soup.find('div', class_="widget__row widget__row_table widget__row_humidity")
				humidity = humidity.find_all('div', class_="w-humidity")
				humidities = []
				for hum in humidity:
					humidities.append(int(hum.get_text(strip=True)))
				self.city_weather['humidity'] = humidities[times[time]]
				astronomy = soup.find('div', class_="astronomy_blocks clearfix")
				sun = astronomy.find_all('div', class_="id_item")
				elements = []
				for s in sun:
					elements.append(s.get_text(strip=True))
				sun = self.parse_sun(elements)
				sun_on = sun[1]
				sun_off = sun[2]
				moon = sun[3]
				self.city_weather['sun'] = (sun_on,sun_off,moon)
				weather = soup.find('a', class_="tab tablink tooltip").get("data-text")
				self.city_weather['weather'] = weather
				visible = soup.find('div', class_="widget__row widget__row_table widget__row_visibility")
				visible = visible.find_all('span', class_="unit unit_visibility_m")
				visibles = []
				for vis in visible:
					visibles.append((vis.get_text(strip=True)).split('км')[0])
				self.city_weather['visible'] = visibles[times[time]]
			self.pages.clear()

	def choose_result(self, result):
		res = self.pages[result]
		self.pages.clear()
		self.pages[result] = res

	def __init__(self, Bot):
		self.Bot = Bot


	@commands.command(aliases=['wether'])
	async def weather(self, ctx, city=None, arg = None):
		try:
			arg = int(city)
		except:
			pass

		if len(self.pages) == 0:
			self.URL = "https://www.gismeteo.ru/search/"
			self.DOMEN = "https://www.gismeteo.ru"
			self.HEADERS = {
			"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
			"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
			}

			self.city = str(city)
			self.city_weather = {
				'temp_now' : 0,
				'temp_now_feel' : 0,
				'wind' : 0,
				'pressure' : 0,
				'humidity' : 0,
				'weather' : 0,
				'sun' : 0,
				'visible' : 0,
			}


			op = self.parse_results()
			if not op:
				embed = discord.Embed(
				color = discord.Color.green(),
				title = f"Поиск не дал результатов")
				await ctx.send(embed=embed)
				return

			description = ""
			i = 1
			for p in self.pages.keys():
				description = description + f"{i}. {str(p)}\n" 
				i += 1

			embed = discord.Embed(
				color = discord.Color.green(),
				title = "Результаты поиска:",
				description = "```swift\n"+description+"```")
			await ctx.send(embed=embed)
		else:
			keys = {}
			i = 1
			for key in self.pages.keys():
				keys[i] = key
				i += 1 
			self.choose_result(keys[int(arg)])
			self.parse()
			description = ""
			params = self.city_weather
			temp = params['temp_now']
			temp_feel = params['temp_now_feel']
			wind = params['wind']
			pressure = params['pressure']
			humidity = params['humidity']
			weather = params['weather']
			sun = params['sun']
			sun_on = sun[0]
			sun_off = sun[1]
			moon = sun[2]
			visible = params['visible']

			embed = discord.Embed(
				color = discord.Color.green(),
				title = f"Погода в {keys[int(arg)]}")
			embed.add_field(name="Температура", value=f"{temp} °C")
			embed.add_field(name="По ощущению", value=f"{temp_feel} °C")
			embed.add_field(name="Ветер", value=f"{wind} м/с")
			embed.add_field(name="Давление", value=f"{pressure} мм рт. ст.")
			embed.add_field(name="Влажность", value=f"{humidity} %")
			embed.add_field(name="Видимость", value=f"{visible} км")
			embed.add_field(name="Погода", value=weather)
			embed.add_field(name="Восход", value=f"🌄 {sun_on}")
			embed.add_field(name="Заход", value=f"🌇 {sun_off}")
			embed.add_field(name="Луна", value=f"🌚 {moon}")
			await ctx.send(embed=embed)

	@commands.command(aliases=['opr', 'opro', 'oproc', 'opsos', 'опрос', 'опр'])
	async def opros(self, ctx, *args):
		await ctx.message.delete()
		emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
		close_emoji = "❌"
		if ctx.channel.id != 785751352147574814:
			await send_message(ctx.channel, "пожалуйста используйте канал ║-📄-опросы")
		else:
			message = []
			op = " ".join(args)
			op = op.split("/")
			for i in op:
				if i != "":
					message.append(i)
			
			count = len(message)

			if 11 > count > 2:
				#всё хорошо
				title = message[0]
				args = []
				for i in message[1:]:
					if i != "":
						args.append(i)

				description = "\n"
				for i in range(len(args)):
					print(emoji[i])
					print(args[i])
					description += emoji[i] + " :snowflake: " + args[i] + "\n\n"
				color = (randint(0, 255), randint(0, 255), randint(0, 255))
				print(color)
				embed = discord.Embed(
					color = discord.Colour.from_rgb(color[0], color[1], color[2]),
					title = title,
					description = description
				)
				embed.set_author(name = (ctx.author.name + "#" + ctx.author.discriminator), icon_url = ctx.author.avatar_url)
				msg = await ctx.send(embed = embed)
				timer = 30
				embed = discord.Embed(
					color = discord.Colour.from_rgb(color[0], color[1], color[2]),
					title = f'нажмите ❌, чтобы удалить',
				)
				msg_id = msg.id

				op = await ctx.send(embed = embed, delete_after = 30)

				for i in range(len(args)):
					await msg.add_reaction(emoji[i])
				await msg.add_reaction(close_emoji)
				while timer > 0:
					msg = await msg.channel.fetch_message(msg_id)
					for reaction in msg.reactions:
						if reaction.emoji == "❌":
							users = await reaction.users().flatten()
							for user in users:
								if user.id == ctx.author.id:
									await msg.delete()
									await op.delete()
									timer = 0
									break

					await asyncio.sleep(2)
					timer -= 2

				try:
					await msg.channel.fetch_message(msg_id)
					await msg.clear_reaction(close_emoji)
					await op.delete()
				except:
					pass

			elif count <= 2:
				#мало
				await send_message(ctx.channel, "слишком мало вариантов ответа", 10)
			else:
				#много
				await send_message(ctx.channel, "слишком много вариантов ответа", 10)

def setup(Bot):
	Bot.add_cog(fun(Bot))
