import os
import json
from discord.ext import commands
import discord
import requests

echo_file = "echo.json"

f = open("config.json", "r")
config = json.load(f)
f.close()

urlAPI = config["urlAPI"]

class Echo(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def checkIfExist(self, id_guild):
		"""
		Function that check if the echo file of a server exist
		"""
		exist = False
		if(os.path.exists("guilds/"+id_guild+"/"+echo_file)):
			exist = True

		return exist

	def getInfos(self, id_guild):
		"""
		Function that retrieve the data from the echo file
		"""
		exist = self.checkIfExist(id_guild)
		content = {}
		if(exist):
			f = open("guilds/"+id_guild+"/"+echo_file, "r")
			content = json.load(f)
			f.close()

		return content

	@commands.hybrid_command(name="echo-setup", aliases=["ESetup"])
	async def EchoSetup(self, ctx: commands.Context):
		"""
		Setup a echo collection for the server
		"""
		msg = "Unkown Error"
		# Check if it already exist
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(not exist):
			# We request the creation of a collection for the guild
			result = None
			try:
				result = requests.put(urlAPI+"echo/create")
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				# If the server doesn"t have a folder, we create it
				if(not os.path.exists("guilds/"+str(ctx.message.guild.id)+"/")):
					os.makedirs("guilds/"+str(ctx.message.guild.id)+"/", exist_ok=True)

				# We store them in a json file
				f = open("guilds/"+str(ctx.message.guild.id)+"/"+echo_file, "w")
				f.write(result.text)
				f.close()

				msg = "Echo are ready for this server"
			else:
				msg = "Error while creating the collection for this server"
		else:
			msg = "This server is already setup"

		await ctx.send(msg)

	@commands.hybrid_command(name="echo-add", aliases=["EAdd", "EchoAdd"])
	async def AddEcho(self, ctx: commands.Context, tag: str, echo: str):
		"""
		Add an echo
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			keys = self.getInfos(str(ctx.message.guild.id))

			# Adding the quote
			result = None
			try:
				result = requests.put(urlAPI+"echo", params={"echo": echo, "tag": tag, "id": keys["id"], "authKey": keys["authKey"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				msg = f"Echo {tag} added"
			else:
				msg = "Error while adding the quote"
		else:
			msg = "This server is not ready to manage echo"

		await ctx.send(msg)

	@commands.hybrid_command(name="echo", aliases=["Echo", "E"])
	async def getEcho(self, ctx: commands.Context, tag: str):
		"""
		Retrieve an echo
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			keys = self.getInfos(str(ctx.message.guild.id))

			result = None
			try:
				result = requests.get(urlAPI+"echo", params={"tag": tag, "id": keys["id"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				echo = result.json()

				if(echo["id"] != ""):
					msg = echo["echo"]
				else:
					msg = "No echo found for this tag"
			else:
				msg = "Error while retrieving the echo"
		else:
			msg = "This server is not ready to manage echo"

		await ctx.send(msg)

	@commands.hybrid_command(name="echo-list-tags", aliases=["ETag", "Etags", "EchoTag", "EchoTags", "ListTag", "ListTags"])
	async def getListTagEcho(self, ctx: commands.Context):
		"""
		Get a list of the existing tag for this server
		"""
		msg = "Unkown Error"
		errorMessage = True
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			keys = self.getInfos(str(ctx.message.guild.id))

			result = None
			try:
				result = requests.get(urlAPI+"echo/list", params={"id": keys["id"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				tags = result.json()

				msg_header = "List Tags"

				msg_content = ""
				for tag in tags:
					msg_content += tag["tag"]+"\n"

				embed = discord.Embed(color=discord.Color.blurple())
				embed.title = msg_header
				embed.description = msg_content

				msg = embed
				errorMessage = False
			else:
				msg = "Error while retrieving the tag list"
		else:
			msg = "This server is not ready to manage echo"

		if(errorMessage):
			await ctx.send(msg)
		else:
			await ctx.send(embed=msg)

	## Error Handling
	@AddEcho.error
	@getEcho.error
	async def Echo_handler(self, ctx, error):
		# Check if an required argument is missing.
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("At least one argument is missing")
		else:
			print(error)

async def setup(bot):
	await bot.add_cog(Echo(bot))