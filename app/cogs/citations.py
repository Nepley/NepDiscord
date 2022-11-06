import os
import json
from discord.ext import commands
import discord
import requests
import hashlib

citation_file = "citations.json"

f = open("config.json", "r")
config = json.load(f)
f.close()

urlAPI = config["urlAPI"]

def StringToColor(str):
	return hashlib.md5(str.encode()).hexdigest()[:6]

class Citations(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def checkIfExist(self, id_guild):
		"""
		Function that check if the citation file of a server exist
		"""
		exist = False
		if(os.path.exists("guilds/"+id_guild+"/"+citation_file)):
			exist = True

		return exist

	def getInfos(self, id_guild):
		"""
		Function that retrieve the data from the citation file
		"""
		exist = self.checkIfExist(id_guild)
		content = {}
		if(exist):
			f = open("guilds/"+id_guild+"/"+citation_file, "r")
			content = json.load(f)
			f.close()

		return content

	@commands.command(aliases=["CSetup"])
	async def CitationsSetup(self, ctx):
		"""
		Setup a citation collection for the server
		"""
		msg = "Unkown Error"
		# Check if it already exist
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(not exist):
			# We request the creation of a collection for the guild
			result = None
			try:
				result = requests.put(urlAPI+"quote/create")
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				# If the server doesn"t have a folder, we create it
				if(not os.path.exists("guilds/"+str(ctx.message.guild.id)+"/")):
					os.makedirs("guilds/"+str(ctx.message.guild.id)+"/", exist_ok=True)

				# We store them in a json file
				f = open("guilds/"+str(ctx.message.guild.id)+"/"+citation_file, "w")
				f.write(result.text)
				f.close()

				msg = "Citations are ready for this server"
			else:
				msg = "Error while creating the collection for this server"
		else:
			msg = "This server is already setup"

		await ctx.send(msg)

	@commands.command(aliases=["CAdd", "CitationAdd"])
	async def AddCitation(self, ctx, quote, author, date = ""):
		"""
		Add a citation
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			keys = self.getInfos(str(ctx.message.guild.id))

			# Adding the quote
			result = None
			try:
				result = requests.put(urlAPI+"quote", params={"quote": quote, "author": author, "date": date, "id": keys["id"], "authKey": keys["authKey"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				msg = "Citations added"
			else:
				msg = "Error while adding the quote"
		else:
			msg = "This server is not ready to manage citations"

		await ctx.send(msg)

	@commands.command(aliases=["Citation", "C"])
	async def getCitation(self, ctx, author = ""):
		"""
		Get a random citation
		"""
		msg = "Unkown Error"
		errorMessage = True
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			keys = self.getInfos(str(ctx.message.guild.id))

			result = None
			try:
				result = requests.get(urlAPI+"quote", params={"author": author, "id": keys["id"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				quote = result.json()

				# Forming embed Message
				col = StringToColor(quote["author"])
				embed = discord.Embed(color=int(col, 16))
				embed.description = quote["quote"]
				embed.set_footer(text= quote["author"] + " ("+ quote["date"] +")")

				msg = embed
				errorMessage = False
			else:
				msg = "Error while retrieving a quote"
		else:
			msg = "This server is not ready to manage citations"

		if(errorMessage):
			await ctx.send(msg)
		else:
			await ctx.send(embed=msg)

	@commands.command(aliases=["CStats", "CStat", "CitationStats"])
	async def getCitationStats(self, ctx):
		"""
		Get the usage stat of this server
		"""
		msg = "Unkown Error"
		errorMessage = True
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			keys = self.getInfos(str(ctx.message.guild.id))

			result = None
			try:
				result = requests.get(urlAPI+"quote/stats", params={"id": keys["id"]})
			except Exception as e:
				print("Error while contacting the main API")

			if(result):
				stats = result.json()

				msg_header = "Stats Citation"

				msg_content = ""
				for key, value in stats["stats"].items():
					msg_content += str(key) + " : **" + str(value) + "**\n"

				embed = discord.Embed(color=discord.Color.blurple())
				embed.title = msg_header
				embed.description = msg_content
				embed.set_footer(text="Total : " + str(stats["Total"]))

				msg = embed
				errorMessage = False
			else:
				msg = "Error while retrieving the stats"
		else:
			msg = "This server is not ready to manage citations"

		if(errorMessage):
			await ctx.send(msg)
		else:
			await ctx.send(embed=msg)

	## Error Handling
	@AddCitation.error
	@getCitation.error
	async def Citations_handler(self, ctx, error):
		# Check if an required argument is missing.
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send("At least one argument is missing")
		else:
			print(error)

async def setup(bot):
	await bot.add_cog(Citations(bot))