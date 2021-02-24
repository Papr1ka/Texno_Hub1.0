import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import vk_api
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
from threading import Thread
from bs4 import BeautifulSoup


global posts
posts = []

class MyVkLongPoll(VkLongPoll):
		def listen(self):
			while True:
				try: 
					for event in self.check():
						yield event
				except Exception as e:
					print('error', e)

def on_message():
	vk_session = vk_api.VkApi(token=TOKEN)
	longpoll = MyVkLongPoll(vk_session)
	for event in longpoll.listen():
		if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
			posts.append(event)

def get_html(url):
	HEADERS = {
			"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
			"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
			}
	r = requests.get(url, headers=HEADERS)
	return r

def get_image_url(image : str):
	ref = ""
	for i in range(1, len(image) - 1):
			if image[i - 1] + image[i] + image[i + 1] != "url":
				pass
			else:
				for i in range(i + 3, len(image)):
					if image[i] != ")":
						ref += image[i]
					else:
						break
				break
	return ref


def handle(message : str):
	href = None

	msg = message.split()
	for item in msg:
		if 'vk.com' in item:
			href = item

	if not href is None and "wall" in href:
		try:
			page = get_html(href)
			soup = BeautifulSoup(page.text, "html.parser")
			post = soup.find('div', class_ = "_post_content")
			thumbnail = post.find('a', class_ = "post_image")
			thumbnail = thumbnail.find('img', class_ = "post_img").get("src")
			author = post.find('a', class_ = "author").get_text(strip = True)
			image = post.find('div', class_ = "page_post_sized_thumbs")
			image_images = image.find_all("a")
			images = []
			videos = []

			for img in image_images:
				images.append(get_image_url(img.get("style")))
				video = img.get("href")
				if video != None and "video" in video:
					videos.append("https://vk.com" + video)
					if len(images) > 1:
						images.remove(get_image_url(img.get("style")))


			text = post.find('div', class_ = "wall_post_text")
			if text != None:
				text = text.get_text(strip = True)

			vk_message = "access"

			params = {
				'thumbnail' : thumbnail,
				'author' : author,
				'images' : images,
				'videos' : videos,
				'text' : text,
			}

			print(params)
		except Exception as E:
			print(E)
			handle(message)

	else:
		vk_message = "error"

	if vk_message == "access":
		return params
	elif vk_message == "error":
		return None


class vk(commands.Cog):

	async def send_vk(self, message, post):
		try:
			self.vk.messages.send(
								user_id = post.user_id,
								message = message,
								random_id = post.random_id
							)
		except Exception:
			await asyncio.sleep(1)
			await self.send_vk(message, post)

	async def on_vk_msg(self):
		await self.Bot.wait_until_ready()

		msg = Thread(target = on_message)
		msg.start()

		while not self.Bot.is_closed():
			for post in posts:
				print(posts)
				data = handle(post.text)
				if not data is None:
					await self.send_vk("successfully", post)

					msg = []
					emojis = ["<:sex1:777608679808958484>", "<:sex2:777608962606366752>", "<:sex3:777608978091081808>", "<:sex4:777608990309220372>"]
					embed = discord.Embed(
						color = discord.Colour.dark_purple(),
						title = data["author"],
						description = data['text'])
					print(data['thumbnail'])
					embed.set_thumbnail(url = data['thumbnail'])
					if len(data['images']) == 1:
						embed.set_image(url = data['images'][0])
					else:
						for i in data['images']:
							msg.append(i)
					for i in data['videos']:
						msg.append(i)
					channel = get(self.Bot.get_all_channels(), id = 789978335052431391)
					message = await channel.send(embed = embed)
					for i in range(len(emojis)):
						await message.add_reaction(emojis[i])
					for i in msg:
						await channel.send(i)
					posts.remove(post)
				else:
					await self.send_vk("Error: This post type is not supported", post)
					posts.remove(post)


			await asyncio.sleep(1)
		                
	def __init__(self, Bot, vk_session):
		self.Bot = Bot
		self.vk_session = vk_session
		self.longpoll = MyVkLongPoll(self.vk_session)
		self.vk = self.vk_session.get_api()
		self.Bot.loop.create_task(self.on_vk_msg())
	



def setup(Bot):
	vk_session = vk_api.VkApi(token=TOKEN)
	Bot.add_cog(vk(Bot, vk_session))


TOKEN = "9a920143824fdf91240f8ce33d5300fd4a1e8567758d7b9718c4f0f7488683060f3d34179e5291a517265"