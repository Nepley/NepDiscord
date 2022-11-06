import os
import json
from discord.ext import commands
import discord
import requests

anniversary_file = "anniversary.json"

f = open("config.json", "r")
config = json.load(f)
f.close()

urlAPI = config["urlAPI"]

class Anniversary(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def checkIfExist(self, id_guild):
		"""
		Function that check if the anniversary file of a server exist
		"""
		exist = False
		if(os.path.exists("guilds/"+id_guild+"/"+anniversary_file)):
			exist = True

		return exist

	def getInfos(self, id_guild):
		"""
		Function that retrieve the data from the anniversary file
		"""
		exist = self.checkIfExist(id_guild)
		content = {}
		if(exist):
			f = open("guilds/"+id_guild+"/"+anniversary_file, "r")
			content = json.load(f)
			f.close()

		return content

	def saveData(self, id_guild, data):
		"""
		Function to save new data to the anniversary file
		"""
		exist = self.checkIfExist(id_guild)
		if(exist):
			f = open("guilds/"+id_guild+"/"+anniversary_file, "w")
			json.dump(data, f)
			f.close()

	@commands.hybrid_command(name="anniversary-setup", aliases=["ASetup"])
	async def AnniversarySetup(self, ctx: commands.Context):
		"""
		Setup an anniversary collection for the server
		"""
		msg = "Unkown Error"
		# Check if it already exist
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(not exist):
			# We request the creation of a collection for the guild
			result = None
			try:
				result = requests.put(urlAPI+"anniversary/create")
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				# If the server doesn"t have a folder, we create it
				if(not os.path.exists("guilds/"+str(ctx.message.guild.id)+"/")):
					os.makedirs("guilds/"+str(ctx.message.guild.id)+"/", exist_ok=True)

				# We store them in a json file
				f = open("guilds/"+str(ctx.message.guild.id)+"/"+anniversary_file, "w")
				f.write(result.text)
				f.close()

				# We set the current channel to be the one notified
				data = self.getInfos(str(ctx.message.guild.id))
				data["channel"] = str(ctx.channel.id)

				self.saveData(str(ctx.message.guild.id), data)

				msg = "Anniversaries are ready for this server"
			else:
				msg = "Error while creating the collection for this server"
		else:
			msg = "This server is already setup"

		await ctx.send(msg)

	@commands.hybrid_command(name="anniversary-add", aliases=["AAdd", "AnniversaryAdd"])
	async def AddAnniversary(self, ctx: commands.Context, name: str, day: int, month: int, tag_1: str = "", tag_2: str = ""):
		"""
		Add an anniversary
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			keys = self.getInfos(str(ctx.message.guild.id))

			# Adding the quote
			result = None
			try:
				result = requests.put(urlAPI+"anniversary", params={"name": name, "day": day, "month": month, "tag_1": tag_1, "tag_2": tag_2, "id": keys["id"], "authKey": keys["authKey"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				msg = "Anniversary added"
			else:
				msg = "Error while adding the anniversary"
		else:
			msg = "This server is not ready to manage anniversaries"

		await ctx.send(msg)

	@commands.hybrid_command(name="anniversary-list", aliases=["AList", "AnniversaryList"])
	async def getListAnniversaries(self, ctx: commands.Context):
		"""
		Get a list of the anniversaries for this server
		"""
		msg = "Unkown Error"
		errorMessage = True
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			keys = self.getInfos(str(ctx.message.guild.id))

			result = None
			try:
				result = requests.get(urlAPI+"anniversary/getAll", params={"id": keys["id"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				anniversaries = result.json()

				msg_header = "List Anniversaries"

				msg_content = ""
				for anniversary in anniversaries:
					msg_content += anniversary["name"]+": **"+str(anniversary["day"])+"/"+str(anniversary["month"])+"**\n"

				embed = discord.Embed(color=discord.Color.blurple())
				embed.title = msg_header
				embed.description = msg_content

				msg = embed
				errorMessage = False
			else:
				msg = "Error while retrieving the anniversary list"
		else:
			msg = "This server is not ready to manage anniversaries"

		if(errorMessage):
			await ctx.send(msg)
		else:
			await ctx.send(embed=msg)

	@commands.hybrid_command(name="anniversary-set-sentence", aliases=["ASetS", "ASetSentence"])
	async def AnniversarySetSentence(self, ctx: commands.Context, sentence: str):
		"""
		Set the start of the sentence say for an anniversary
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			# We add the new sentence
			data["sentence"] = sentence

			# We save the modification
			self.saveData(str(ctx.message.guild.id), data)

			msg = "Sentence changed"
		else:
			msg = "This server is not ready to manage anniversaries"

		await ctx.send(msg)

	@commands.hybrid_command(name="anniversary-set-channel", aliases=["ASetC", "ASetChannel"])
	async def AnniversarySetChannel(self, ctx: commands.Context):
		"""
		Set the channel where the anniversaries will be notified
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
			msg = "This server is not ready to manage anniversaries"

		await ctx.send(msg)

	## Error Handling
	@AddAnniversary.error
	async def Anniversary_handler(self, ctx, error):
		# Check if an required argument is missing.
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("At least one argument is missing")
		else:
			print(error)

async def setup(bot):
	await bot.add_cog(Anniversary(bot))