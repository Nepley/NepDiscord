from discord.ext import commands
import discord
import requests
import os
import json
import asyncio
from fastapi import FastAPI
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache

f = open("config.json", "r")
config = json.load(f)
f.close()

intents = discord.Intents.default()  # Allow the use of custom intents
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='Nep', help_command=None, intents=intents)
token = config["token"]

# Server in order to make Webservice
app = FastAPI()

## Emoji
UniHappy = "<:UniHappy:674721951058624560>"
UniCry = "<:UniCry:679016707343515672>"
###

urlAPI = config["urlAPI"]
youtubeApiKey = config["youtubeApiKey"]

### Events

@bot.event
async def on_ready():
	# Trying to contact the main API
	try:
		result = requests.get(urlAPI)
	except Exception as e:
		print("Error while trying to contact the main API.")
		os._exit(0)

	# Creating guilds folder if it doesn't exist
	if(not os.path.exists("guilds/")):
		os.makedirs("guilds/", exist_ok=True)

	# Loadings cogs
	await bot.load_extension('cogs.citations')
	await bot.load_extension('cogs.echo')
	await bot.load_extension('cogs.anniversary')
	await bot.load_extension('cogs.misc')
	await bot.load_extension('cogs.playlist')
	await bot.load_extension('cogs.randomPicker')

	# We sync the application command
	await bot.tree.sync()

	print("Main API called. All Cogs loaded. Discord Bot started.")

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	channel = message.channel

	# Good/Bad bot reaction
	lower_msg = message.content.lower()
	if bot.user.mentioned_in(message):
		if("good bot" in lower_msg):
			await channel.send(UniHappy)

		if("bad bot" in lower_msg):
			await channel.send(UniCry)

	await bot.process_commands(message)

@bot.hybrid_command(name="nep", aliases=["Nep"])
async def Nep(ctx: commands.Context):
	"""Say Nep"""
	await ctx.send('Nep!')

#WS checking anniversaries
@app.get("/")
async def checkAnniversary():
	# We list all of the guild that have the anniversaries setup
	guilds = os.listdir("guilds/")
	for guild in guilds:
		if(os.path.exists("guilds/"+guild+"/anniversary.json")):
			f = open("guilds/"+guild+"/"+"/anniversary.json", "r")
			content = json.load(f)
			f.close()
			# We request the creation of a collection for the guild
			result = None
			try:
				result = requests.get(urlAPI+"anniversary", params={"id": content["id"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result.text != "[]"):
				# Getting the start of the sentence
				if "sentence" in content:
					sentence = content["sentence"]
				else:
					sentence = "Today is the anniversary of "

				anniversaries = json.loads(result.text)

				for anniversary in anniversaries:
					# Forming message to send
					msg = sentence+anniversary["name"]
					if(anniversary["image"] != {} and anniversary["image"]["found"]):
						msg += "\n"+anniversary["image"]["url"]

					# Sending the message to the channel
					if(content["channel"]):
						channel = bot.get_channel(int(content["channel"]))
						await channel.send(msg)

	return {"status": "OK"}

#WS Checking if a playlist has been modified
@app.get("/check-playlist")
async def checkPlaylist():
	guilds = os.listdir("guilds/")
	for guild in guilds:
		if(os.path.exists("guilds/"+guild+"/playlist.json")):
			with open("guilds/"+guild+"/playlist.json", "r") as file:
				data = json.load(file)

			for playlist in data['playlists']:
				listVideoPlaylist = []
				listNewVideo = []
				listDeletedVideo = []
				playlistNotCreated = False

				# We check if we have a file for this playlist
				if(os.path.exists("guilds/"+guild+f"/playlists/{playlist['name']}")):
					# We retrieve the video list
					with open("guilds/"+guild+f"/playlists/{playlist['name']}", "r", encoding="utf8") as file:
						listVideo = json.load(file)

					listVideoId = []

					for video in listVideo:
						listVideoId.append(video['id'])

					idPlaylist = playlist['url'].split('=')[1]
					listVideoPlaylist = getListVideoFromPlaylist(idPlaylist)

					listVideoIdPlaylist = []
					for video in listVideoPlaylist:
						videoId = video["id"]
						videoTitle = video["snippet"]["title"]

						# We add the video to the list id
						listVideoIdPlaylist.append(videoId)

						# We check if the video does not exist
						if videoId not in listVideoId:
							listNewVideo.append({'id': videoId, 'title': videoTitle})

					# We check if a video does not exist anymore
					for video in listVideo:
						if video['id'] not in listVideoIdPlaylist:
							listDeletedVideo.append(video)

				# If we don't have the file, there is a problem, so we ignore it
				else:
					playlistNotCreated = True

				# We add the new video to the file
				listVideoWithDeleted = listVideo + listNewVideo
				listVideo = []

				# We delete the video that has been deleted
				if listDeletedVideo:
					# We take the id list
					listDeletedVideoId = []
					for video in listDeletedVideo:
						listDeletedVideoId.append(video['id'])

					for video in listVideoWithDeleted:
						if(video['id'] not in listDeletedVideoId):
							listVideo.append(video)
				else:
					listVideo = listVideoWithDeleted

				# We save the playlist in a file
				with open("guilds/"+guild+f"/playlists/{playlist['name']}", "w", encoding="utf8") as file:
					json.dump(listVideo, file)

				if(not playlistNotCreated and (listNewVideo or listDeletedVideo)):
					channel = bot.get_channel(int(data["channel"]))
					# If we have new video
					if listNewVideo:
						msg_header = f"Video(s) have been added to {playlist['name']}"

						msg_content = ""
						for video in listNewVideo:
							msg_content += f"[{video['title']}](https://www.youtube.com/watch?v={video['id']})\n"

						embed = discord.Embed(color=discord.Color.green())
						embed.title = msg_header
						embed.description = msg_content
						
						await channel.send(embed=embed)

					# If we have deleted video
					if listDeletedVideo:
						msg_header = f"Video(s) have been deleted from {playlist['name']}"

						msg_content = ""
						for video in listDeletedVideo:
							msg_content += f"[{video['title']}](https://www.youtube.com/watch?v={video['id']})\n"

						embed = discord.Embed(color=discord.Color.red())
						embed.title = msg_header
						embed.description = msg_content

						await channel.send(embed=embed)

	return {"status": "OK"}

async def run():
	try:
		await bot.start(token)
	except KeyboardInterrupt:
		await bot.logout()

## Helper Functions

class MemoryCache(Cache):
	_CACHE = {}

	def get(self, url):
		return MemoryCache._CACHE.get(url)

	def set(self, url, content):
		MemoryCache._CACHE[url] = content

def getListVideoFromPlaylist(id):
	youtube = build('youtube', 'v3', developerKey=youtubeApiKey, cache=MemoryCache())

	finished = False
	listVideo = []
	pageToken = ""
	maxAttempt = 10
	attempt = 0
	while not finished and attempt < maxAttempt:
		if(pageToken != ""):
			request = youtube.playlistItems().list(
				part="snippet,contentDetails",
				maxResults=50,
				playlistId=id,
				pageToken = response["nextPageToken"]
			)
		else:
			request = youtube.playlistItems().list(
				part="snippet,contentDetails",
				maxResults=50,
				playlistId=id
			)

		response = request.execute()

		# We list every video of this page
		listVideo = listVideo + response["items"]

		# If there is no other page, we end the loop
		if(not "nextPageToken" in response):
			finished = True
		else:
			pageToken = response["nextPageToken"]
			attempt += 1

	return listVideo

asyncio.create_task(run())