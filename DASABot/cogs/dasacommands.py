import connectRankDB
from connectRankDB import connectDB
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import *
db = connectDB()

class DASACommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dbconnect = connectRankDB.connectDB()

    @commands.Cog.listener()
    async def on_ready(self):
        print("DASA COMMANDS cog loaded")

    @commands.command()
    async def cutoff(self, ctx,*,  input_str:str):
        embed = None
        """usage : ?cutoff college year round ciwg(y/n) [branch]
        NOTE: arguments need not be in same order
        college, ex: nitk, nitc, nitt, nsut
        year, ex: 2021, 2022, 2023
        round, ex: 1, 2, 3
        ciwg, ex: y, n
        branch(optional), ex: cse, ece, eee, mec"""
        delete = Button(label="Delete", style=discord.ButtonStyle.danger)
        dms = Button(label="Send in DMs", style=discord.ButtonStyle.green)
        view = View()
        view.add_item(dms)
        view.add_item(delete)

        values = input_str.split()
        college, year, round, branch, ciwg = "", None, None, None, None
        for arg in values:
            if arg.isnumeric():
                if int(arg) in [2021, 2022, 2023]:
                    year = arg
                elif int(arg) in [1, 2, 3]:
                    round = arg
            elif arg.isalpha():
                if len(arg) > 3 or arg == "nit":
                    college += f"{arg} "
                elif len(arg) in [2,3]:
                    branch = arg
                elif arg in ['y', 'n']:
                    ciwg = arg
        college = college[:-1]
        try:
            college = db.nick_to_college(str(year), str(round), str(college))
        except:
            return await ctx.send("Invalid college name.")
        ciwg = True if ciwg == 'y' else False
        branch_list = db.request_branch_list(year, round, college, ciwg)
        if branch is not None:
            if ciwg:
                branch = f"{branch.upper()}1"
            while branch.upper() not in branch_list:
                await ctx.send("Invalid branch name, re-enter. Press Q to Quit.")
                branch_msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)
                branch = branch_msg.content
                if branch == 'Q':
                    return await ctx.send('Quitting...')

            stats = db.get_statistics(
                year, round, college, branch.upper(), ciwg)
            embed = discord.Embed(
                title=f'Cutoffs for {college}',
                            description=f'Course: {branch[:-1]} (CIWG)\n Round {round}({year})' if ciwg else f'Course: {branch.upper()}\n Round {round}',
                            color=discord.Color.random())
            embed.set_thumbnail(
                url='https://dasanit.org/dasa2023/images/dasa_new.png')
            embed.add_field(name="JEE Opening Rank: ", value=stats[0])
            embed.add_field(name="JEE Closing Rank: ", value=stats[1])
            embed.add_field(
                name="DASA Opening Rank: " if not ciwg else f"CIWG Opening Rank: ", value=stats[2])
            embed.add_field(
                name="DASA Closing Rank: " if not ciwg else f"CIWG Closing Rank: ", value=stats[3])
            embed.set_footer(text = 'This message will be automatically deleted in 120s.\nTo receive this message in your DMs, press "Send in DMs".\nTo delete this message, press "Delete".')
            m = await ctx.send(embed=embed, delete_after=120, view = view)

            async def dms_callback(interaction):
                await self.bot.send_message(ctx.message.author, embed=embed)
                await interaction.response.send_message("Cutoffs have been sent in your DMs.")

        else:
            stats = db.get_statistics_for_all(year, round, college, ciwg)
            embed = discord.Embed(
                title=f"Cutoffs for {college}", description=f"Round {round}({year})", color=discord.Color.random())
            embed.set_thumbnail(
                url='https://dasanit.org/dasa2023/images/dasa_new.png')
            for i in stats:
                if ciwg == False:
                    embed.add_field(
                        name=i[0],
                        value=f"JEE OPENING: {i[1][0]}\nJEE CLOSING: {i[1][1]}\nDASA OPENING: {i[1][2]}\nDASA CLOSING: {i[1][3]}",
                        inline=True)
                else:
                    if i[0][-1] !='1':
                        continue
                    else:
                        embed.add_field(
                        name=f"{i[0][:-1]} (CIWG)",
                        value=f"JEE OPENING: {i[1][0]}\nJEE CLOSING: {i[1][1]}\nCIWG OPENING: {i[1][2]}\nCIWG CLOSING: {i[1][3]}",
                        inline=True)
            embed.set_footer(
                text='This message will be automatically deleted in 120s.\nTo receive this message in your DMs, press "Send in DMs".\nTo delete this message, press "Delete".')
            m = await ctx.send(embed=embed, delete_after=120, view = view)

        async def dms_callback(interaction):
            if interaction.user.id == ctx.author.id:
                dmuser = await self.bot.fetch_user(ctx.author.id)
            else:
                dmuser = await self.bot.fetch_user(interaction.user.id)
            embed.remove_footer()
            await dmuser.send(embed = embed)
            await ctx.send("Cutoffs have been sent in your DMs.")

        async def delete_callback(interaction):
            if interaction.user.id == ctx.author.id:
                await m.delete()


        delete.callback = delete_callback
        dms.callback = dms_callback


async def setup(bot):
    await bot.add_cog(DASACommands(bot))