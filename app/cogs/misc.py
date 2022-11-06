import requests
from nextcord.ext import commands
import nextcord
import json

f = open("config.json", "r")
config = json.load(f)
f.close()

urlAPI = config["urlAPI"]

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def Dice(self, ctx, dices, faces, minValue = 1):
        """
        Roll a dice
        """
        result = None
        try:
            result = requests.get(urlAPI+"dice", params={"dices": dices, "faces": faces})
        except Exception as e:
            print("Error while contacting the main API")
            return

        if(result):
            dice = result.json()
            await ctx.reply(dice)

    @commands.command()
    async def Booru(self, ctx, tag1, tag2 = ""):
        """
        Retrieve a random image from SafeBooru
        """
        result = None
        try:
            result = requests.get(urlAPI+"booru", params={"tag1": tag1, "tag2": tag2})
        except Exception as e:
            print("Error while contacting the main API")

        if(result):
            url = result.json()["url"]
            await ctx.send(url)
        
    @commands.command(aliases=["help"])
    async def Help(self, ctx):
        # Citations
        quote_header = "Citations"
        quote_content = "**CSetup**: Setup a citation collection for the server\n"
        quote_content += "**CAdd / CitationAdd [quote] [author] [~date]**: Add a citation\n"
        quote_content += "**C / Citation [~author]**: Get a random citation\n"
        quote_content += "**CStats / CitationStats**: Get the usage stat of this server\n"

        quote_help = nextcord.Embed(color=nextcord.Color.blue())
        quote_help.title = quote_header
        quote_help.description = quote_content

        # Echo
        echo_header = "Echo"
        echo_content = "**ESetup**: Setup an echo collection for the server\n"
        echo_content += "**EAdd / EchoAdd [tag] [message]**: Add an echo\n"
        echo_content += "**E / Echo [tag]**: Retrieve an echo\n"
        echo_content += "**ETags / ListTags**: Get a list of the existing tag for this server\n"

        echo_help = nextcord.Embed(color=nextcord.Color.red())
        echo_help.title = echo_header
        echo_help.description = echo_content

        # Anniversary
        anniv_header = "Anniversary"
        anniv_content = "**ASetup**: Setup an anniversary collection for the server\n"
        anniv_content += "**AAdd [name] [day] [month] [~tag_1] [~tag_2]**: Add an anniversary\n"
        anniv_content += "**AList / AnniversaryList**: Get a list of the anniversaries for this server\n"
        anniv_content += "**ASetChannel**: Set the channel where the anniversaries will be notified\n"
        anniv_content += "**ASetSentence [sentence]**: Set the start of the sentence\n"

        anniv_help = nextcord.Embed(color=nextcord.Color.green())
        anniv_help.title = anniv_header
        anniv_help.description = anniv_content

        # Playlist Alarm
        playlist_header = "Playlist Alarm"
        playlist_content = "**PSetup**: Setup the playlist alarm for the server\n"
        playlist_content += "**PAdd [name] [url]**: Add a playlist\n"
        playlist_content += "**PList / PlaylistList**: Get a list of the playlist for this server\n"
        playlist_content += "**PSetChannel**: Set the channel where the playlist change will be notified\n"
        playlist_content += "**PDelete [name]**: Delete a playlist\n"

        playlist_help = nextcord.Embed(color=nextcord.Color.orange())
        playlist_help.title = playlist_header
        playlist_help.description = playlist_content

        # Random Picker
        random_picker_header = "Random Picker"
        random_picker_content = "**RPSetup**: Setup the random picker for the server\n"
        random_picker_content += "**RPAdd / RPA [choice] [weight]**: Add a choice with a weight between 0 and 10\n"
        random_picker_content += "**RPList / RPL**: Get a list of the choice\n"
        random_picker_content += "**RPDelete / RPD [choice]**: Delete a choice\n"
        random_picker_content += "**RPChange / RPC [choice] [newWeight]**: Change the weight of a choice\n"
        random_picker_content += "**RP**: Choose a random item from your list of choice, if your in a vocal channel with other people, merge the list choice of the other member\n"

        random_picker_help = nextcord.Embed(color=nextcord.Color.yellow())
        random_picker_help.title = random_picker_header
        random_picker_help.description = random_picker_content

        # Misc
        misc_header = "Miscellaneous"
        misc_content = "**Dice [nbDice] [nbFace] [~minValue]**: Roll a dice\n"
        misc_content += "**Booru [tag_1] [~tag_2]**: Retrieve a random image from SafeBooru\n"
        misc_content += "**Help**: Get this message\n"

        misc_help = nextcord.Embed(color=nextcord.Color.blurple())
        misc_help.title = misc_header
        misc_help.description = misc_content

        # Sending the message
        await ctx.send(embed=quote_help)
        await ctx.send(embed=echo_help)
        await ctx.send(embed=anniv_help)
        await ctx.send(embed=playlist_help)
        await ctx.send(embed=random_picker_help)
        await ctx.send(embed=misc_help)

    # Error Handling
    @Booru.error
    @Dice.error
    async def Misc_handler(self, ctx, error):
        # Check if our required argument tag1 is missing.
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("At least one argument is missing")

def setup(bot):
    bot.add_cog(Misc(bot))
