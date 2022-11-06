import os
import json
import random
from discord.ext import commands
import discord

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

	@commands.hybrid_command(name="random-picker-setup", aliases=["RPSetup"])
	async def RandomPickerSetup(self, ctx: commands.Context):
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

	@commands.hybrid_command(name="random-picker-list", aliases=["RPList", "RPL"])
	async def RandomPickerList(self, ctx: commands.Context):
		"""
			List choice
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			listChoice = []
			author = str(ctx.author.id)

			# If the user already have use this system
			if(author in data):
				listChoice = data[author]

			# We format the message
			msg_header = "List Choice"

			msg_content = ""
			for choice in listChoice:
				msg_content += f"{choice['name']} ({choice['weight']})\n"

			embed = discord.Embed(color=discord.Color.blurple())
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

	@commands.hybrid_command(name="random-picker-add", aliases=["RPAdd", "RPA"])
	async def RandomPickerAdd(self, ctx: commands.Context, choice: str, weight: int):
		"""
		Add a choice
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):

			# We check if the weight is a valid number
			if(isinstance(weight, int)):
				data = self.getInfos(str(ctx.message.guild.id))

				author = str(ctx.author.id)

				# If the user does not already have use this system, we add him
				if(not author in data):
					data[author] = []

				# We check if it already exist
				newChoice = True
				for existingChoice in data[author]:
					if(choice == existingChoice['name']):
						newChoice = False
						break

				if(newChoice):
					# We add the choice linked to the user
					data[author].append({"name": choice, "weight": weight%11})

					# We save the modification
					self.saveData(str(ctx.message.guild.id), data)

					msg = "Choice added"
				else:
					msg = "This choice already exist"
			else:
				msg = "Weight is not a valid number"
		else:
			msg = "This server is not ready to manage RandomPicker"

		await ctx.send(msg)

	@commands.hybrid_command(name="random-picker-change-weight", aliases=["RPChange", "RPC"])
	async def RandomPickerChangeWeight(self, ctx: commands.Context, choice: str, new_weight: int):
		"""
		Change a weight of a choice
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):

			# We check if the weight is a valid number
			if(isinstance(new_weight, int)):
				data = self.getInfos(str(ctx.message.guild.id))

				author = str(ctx.author.id)
				# If the user does not already have use this system, or have no choice
				if(author in data or data[author] != []):
					# We check if the choice exist
					exist = False
					for existingChoice in data[author]:
						if(choice == existingChoice['name']):
							exist = True
							# We change the value
							existingChoice['weight'] = int(new_weight)%11

					if(not exist):
						msg = "This choice doesn't exist"
					else:
						# We save the modification
						self.saveData(str(ctx.message.guild.id), data)

						msg = "Weight changed"

				else:
					msg = "You don't have any choice"
			else:
				msg = "New weight is not a valid number"
		else:
			msg = "This server is not ready to manage RandomPicker"

		await ctx.send(msg)

	@commands.hybrid_command(name="random-picker", aliases=["RP"])
	async def RandomPicker(self, ctx: commands.Context):
		"""
		Choose a random option
		"""
		msg = "Unkown Error"
		errorMessage = True
		exist = self.checkIfExist(str(ctx.message.guild.id))
		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			author = str(ctx.author.id)

			# We retrieve the user vocal channel
			voice = ctx.message.author.voice
			voice_client = ctx.guild.get_channel(ctx.message.author.voice.channel.id)

			listChoice = []
			if voice:
				# We retrieve the choice of the other users
				listMember = voice.channel.members

				listAllChoice = []

				# We have a list that are all the item where a member has a zero and therefor, doesn't want it
				ZeroList = []
				for member in listMember:
					# If the user already have use this system
					if(str(member.id) in data):
						listAllChoice.append(data[str(member.id)])

				# We regroup all the choice into one lise
				for choiceList in listAllChoice:
					for choice in choiceList:
						# We check if it already exist
						exist = False
						for existingChoice in listChoice:
							if(choice['name'] == existingChoice['name']):
								exist = True
								# We add the weight if it's not zero, else we remove and ban it
								if(choice['weight'] != 0):
									existingChoice['weight'] += choice['weight']
								else:
									ZeroList.append(existingChoice['name'])
									listChoice.remove(existingChoice)
								break

						# If it was not found, we try to add it
						if(not exist):
							# If it's not zero, we add it, else we ban it
							if(choice['weight'] != 0 and choice['name'] not in ZeroList):
								listChoice.append(choice)
							else:
								ZeroList.append(choice['name'])
			else:
				# We retrieve the choice of the author
				listChoice = data[str(ctx.author.id)]

				# We remove each choice with a zero weight
				for choice in listChoice:
					if(choice['weight'] == 0):
						listChoice.remove(choice)

			if(listChoice != []):
				# We split the name and weight into two list
				listName = []
				listWeight = []

				for choice in listChoice:
					listName.append(choice['name'])
					listWeight.append(choice['weight'])

				#We choose randomly
				itemChoose = random.choices(listName, listWeight)

				# We format the message
				msg_header = "Item Choose"

				embed = discord.Embed(color=discord.Color.blurple())
				embed.title = msg_header
				embed.description = itemChoose[0]

				msg = embed
				errorMessage = False
			else:
				msg = "No choice possible"
		else:
			msg = "This server is not ready to manage RandomPicker"

		if(errorMessage):
			await ctx.send(msg)
		else:
			await ctx.send(embed=msg)

	@commands.hybrid_command(name="random-picker-delete", aliases=["RPDelete", "RPD"])
	async def RandomPickerDelete(self, ctx: commands.Context, choice: str):
		"""
		Delete a choice
		"""
		msg = "Unkown Error"
		exist = self.checkIfExist(str(ctx.message.guild.id))

		if(exist):
			data = self.getInfos(str(ctx.message.guild.id))

			author = str(ctx.author.id)

			# If the user does not already have use this system
			if(author in data):
				found = False
				# We search the choice to delete
				for existingChoice in data[author]:
					if(choice == existingChoice['name']):
						found = True
						data[author].remove(existingChoice)
						break

				if(found):
					# We save the modification
					self.saveData(str(ctx.message.guild.id), data)

					msg = "Choice deleted"
				else:
					msg = "Choice doesn't exist"

			else:
				msg = "you don't have any choice"
		else:
			msg = "This server is not ready to manage RandomPicker"

		await ctx.send(msg)

async def setup(bot):
	await bot.add_cog(RandomPicker(bot))