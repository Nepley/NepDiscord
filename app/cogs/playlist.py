import os
import json
from discord.ext import commands
import discord
from pytube import Playlist as pytubePlaylist

playlist_file = "playlist.json"

f = open("config.json", "r")
config = json.load(f)
f.close()

class Playlist(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	def checkIfExist(self, id_guild):
		"""
		Function that check if the playlist file of a server exist
		"""
		exist = False
		if(os.path.exists("guilds/"+id_guild+"/"+playlist_file)):
			exist = True
		
		return exist
		
	def getInfos(self, id_guild):
		"""
		Function that retrieve the data from the playlist file
		"""
		exist = self.checkIfExist(id_guild)
		content = {}
		if(exist):
			f = open("guilds/"+id_guild+"/"+playlist_file, "r")
			content = json.load(f)
			f.close()

		return content

	def saveData(self, id_guild, data):
		"""
		Function to save new data to the playlist file
		"""
		exist = self.checkIfExist(id_guild)
		if(exist):
			f = open("guilds/"+id_guild+"/"+playlist_file, "w")
			json.dump(data, f)
			f.close()
		return exist

	@commands.hybrid_command(name="playlist-setup", aliases=["PSetup"])
	async def PlaylistSetup(self, ctx: commands.Context):
		"""
		Setup an playlist collection for the server
		"""
		msg = "Unkown Error"
		# Check if it already exist
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(not exist):
			# If the server doesn"t have a folder, we create it
			if(not os.path.exists("guilds/"+str(ctx.message.guild.id)+"/")):
				os.makedirs("guilds/"+str(ctx.message.guild.id)+"/", exist_ok=True)

			# We set the default data
			data = {}
			data['channel'] = str(ctx.channel.id)
			data['playlists'] = []

			# We store them in a json file
			f = open("guilds/"+str(ctx.message.guild.id)+"/"+playlist_file, "w")
			json.dump(data, f)
			f.close()

			# We create the folder
			os.makedirs("guilds/"+str(ctx.message.guild.id)+"/playlists", exist_ok=True)

			msg = "Playlist are ready for this server"
		else:
			msg = "This server is already setup"

		await ctx.send(msg)

	@commands.hybrid_command(name="playlist-list", aliases=["PList", "PlaylistList"])
	async def getListPlaylists(self, ctx: commands.Context):
		"""
		Get a list of the playlists for this server
		"""
		msg = "Unkown Error"
		errorMessage = True
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			msg_header = "List Playlists"

			msg_content = ""
			for playlist in data['playlists']:
				msg_content += f"[{playlist['name']}]({playlist['url']})\n"

			embed = discord.Embed(color=discord.Color.blurple())
			embed.title = msg_header
			embed.description = msg_content

			msg = embed
			errorMessage = False
		else:
			msg = "This server is not ready to manage playlists"

		if(errorMessage):
			await ctx.send(msg)
		else:
			await ctx.send(embed=msg)

	@commands.hybrid_command(name="playlsit-add", aliases=["PAdd", "PlaylistAdd"])
	async def AddPlaylist(self, ctx: commands.Context, name: str, url: str):
		"""
		Add a playlist
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			# We check that the name does not already exist
			exist = False
			for playlist in data['playlists']:
				if playlist['name'] == name:
					exist = True

			if not exist:

				# We send the message now so the user doesn't wait for just the confirmation
				msg = f"Playlist {name} added"
				await ctx.send(msg)

				# We generate the file file with all the video (id and title)
				newPlaylist = pytubePlaylist(url)

				playlistData = []
				for video in newPlaylist.videos:
					playlistData.append({'id': video.video_id, 'title': video.title})

				with open("guilds/"+str(ctx.message.guild.id)+f"/playlists/{name}", "w", encoding="utf8") as file:
					listVideo = json.dump(playlistData, file)

				# Adding the playlist
				data['playlists'].append({"name": name, "url": url})

				# We save the modification
				self.saveData(str(ctx.message.guild.id), data)

				# We return now so we don't send another message
				return
			else:
				msg = "The name already exist"
		else:
			msg = "This server is not ready to manage playlists"

		await ctx.send(msg)

	@commands.hybrid_command(name="playlist-set-channel", aliases=["PSetC", "PSetChannel"])
	async def PlaylistSetChannel(self, ctx: commands.Context):
		"""
		Set the channel where the playlist will be notified
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			# We add the new sentence
			data["channel"] = str(ctx.channel.id)

			# We save the modification
			self.saveData(str(ctx.message.guild.id), data)

			msg = "Channel set"
		else:
			msg = "This server is not ready to manage playlist"

		await ctx.send(msg)
	
	@commands.hybrid_command(name="playlist-delete", aliases=["PDelete", "PlaylistDelete"])
	async def deletePlaylist(self, ctx: commands.Context, name: str):
		"""
		Delete a playlist
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			# We check that the name exist
			nameExist = False
			for playlist in data['playlists']:
				if playlist['name'] == name:
					nameExist = True
			
			if(nameExist):
				# We search the playlist and delete it
				for i in range(0, len(data['playlists'])):
					if name == data['playlists'][i]['name']:
						data['playlists'].pop(i)

				# We save the modification
				self.saveData(str(ctx.message.guild.id), data)

				msg = "Playlist deleted"
			else:
				msg = "This playlist does not exist"
		else:
			msg = "This server is not ready to manage playlist"
		
		await ctx.send(msg)

async def setup(bot):
	await bot.add_cog(Playlist(bot))