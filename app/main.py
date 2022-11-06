from nextcord.ext import commands
import nextcord
import requests
import os
import json
import asyncio
from fastapi import FastAPI
from pytube import Playlist, YouTube

f = open("config.json", "r")
config = json.load(f)
f.close()

intents = nextcord.Intents.default()  # Allow the use of custom intents
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
	bot.load_extension('cogs.citations')
	bot.load_extension('cogs.echo')
	bot.load_extension('cogs.anniversary')
	bot.load_extension('cogs.misc')
	bot.load_extension('cogs.playlist')
	bot.load_extension('cogs.randomPicker')

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

@bot.command()
async def Nep(ctx):
	await ctx.reply('Nep!')

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

					playlistToCheck = Playlist(playlist['url'])
					
					for video in playlistToCheck.videos:
						listVideoPlaylist.append(video.video_id)

					for video in listVideoPlaylist:
						# We check if the video does not exist
						if video not in listVideoId:
							listNewVideo.append({'id': video, 'title': YouTube(f"https://www.youtube.com/watch?v={video}").title})

					# We check if a video does not exist anymore
					for video in listVideo:
						if video['id'] not in listVideoPlaylist:
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

						embed = nextcord.Embed(color=nextcord.Color.green())
						embed.title = msg_header
						embed.description = msg_content
						
						await channel.send(embed=embed)

					# If we have deleted video
					if listDeletedVideo:
						msg_header = f"Video(s) have been deleted from {playlist['name']}"

						msg_content = ""
						for video in listDeletedVideo:
							msg_content += f"[{video['title']}](https://www.youtube.com/watch?v={video['id']})\n"

						embed = nextcord.Embed(color=nextcord.Color.red())
						embed.title = msg_header
						embed.description = msg_content

						await channel.send(embed=embed)

	return {"status": "OK"}

async def run():
	try:
		await bot.start(token)
	except KeyboardInterrupt:
		await bot.logout()

asyncio.create_task(run())
