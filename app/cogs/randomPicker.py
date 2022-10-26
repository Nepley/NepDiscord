import os
import json
from nextcord.ext import commands
import nextcord
import requests
import hashlib

randomPicker_file = "randomPicker.json"

f = open("config.json", "r")
config = json.load(f)
f.close()

class RandomPicker(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def checkIfExist(self, id_guild):
		"""
		Function that check if the randomPicker file of a server exist
		"""
		exist = False
		if(os.path.exists("guilds/"+id_guild+"/"+randomPicker_file)):
			exist = True

		return exist

	def getInfos(self, id_guild):
		"""
		Function that retrieve the data from the randomPicker file
		"""
		exist = self.checkIfExist(id_guild)
		content = {}
		if(exist):
			f = open("guilds/"+id_guild+"/"+randomPicker_file, "r")
			content = json.load(f)
			f.close()

		return content
	
	def saveData(self, id_guild, data):
		"""
		Function to save new data to the randomPicker file
		"""
		exist = self.checkIfExist(id_guild)
		if(exist):
			f = open("guilds/"+id_guild+"/"+randomPicker_file, "w")
			json.dump(data, f)
			f.close()
		return exist

	@commands.command(aliases=["RPSetup"])
	async def RandomPickerSetup(self, ctx):
		"""
		Setup a RandomPicker collection for the server
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
			data['users'] = []

			# We store them in a json file
			f = open("guilds/"+str(ctx.message.guild.id)+"/"+randomPicker_file, "w")
			json.dump(data, f)
			f.close()

			# We create the folder
			os.makedirs("guilds/"+str(ctx.message.guild.id)+"/playlists", exist_ok=True)

			msg = "RandomPicker are ready for this server"
		else:
			msg = "This server is already setup"

		await ctx.send(msg)

	@commands.command(aliases=["RPList"])
	async def RandomPickerList(self, ctx):
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			listChoice = []
			# If the user already have use this system
			if(ctx.user.id in data):
				listChoice = data[ctx.user.id]

			# We format the message
			msg_header = "List Choice"

			msg_content = ""
			for choice in listChoice:
				msg_content += f"{choice['name']} ({choice['weight']})\n"

			embed = nextcord.Embed(color=nextcord.Color.blurple())
			embed.title = msg_header
			embed.description = msg_content

			msg = embed
			errorMessage = False
		else:
			msg = "This server is not ready to manage RandomPicker"

		if(errorMessage):
			await ctx.send(msg)
		else:
			await ctx.send(embed=msg)

	@commands.command(aliases=["RPAdd"])
	async def RandomPickerAdd(self, ctx, choice, weight = 5):
		"""
		Add a choice
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			# If the user does not already have use this system, we add him
			if(not ctx.user.id in data):
				data[ctx.user.id] = []

			# We add the choice linked to the user
			data[ctx.user.id].append({"name": choice, "weight": weight%11})

			msg = "Choice added"
		else:
			msg = "This server is not ready to manage RandomPicker"
		
		return ctx.send(msg)