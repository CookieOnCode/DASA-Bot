import connectRankDB
from connectRankDB import connectDB
import discord
from discord.ext import commands
from discord.ui import *
import Paginator, asyncio
db = connectDB()

class DASACommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dbconnect = connectRankDB.connectDB()

    @commands.Cog.listener()
    async def on_ready(self):
        print("DASA COMMANDS cog loaded")

    @commands.hybrid_command()
    async def cutoff(self, ctx,
                        college: str = commands.parameter(description = "example: nitc, nitt, nitk, nits, nsut, (use quotes for split names)"),
                        year: str = commands.parameter(description = "example: 2021, 2022"), ciwg: str= commands.parameter(description = "example: y, n, Y, N"),
                        round: str= commands.parameter(description = "example: 1, 2, 3"),
                        branch: str = commands.parameter(default = None,
                                                            description = "example: CSE, ECE, EEE, MEC")):
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

        """Get cutoffs.
                usage : ?cutoff <college>, <year>, <ciwg>, <round> [,branchcode]"""
        college = college.lower()
        if year not in ['2021', '2022', '2023']:  # checks if the year is given as 2021 or 2022
            return await ctx.send("Invalid year.")

        if int(round) not in [1, 2, 3]:  # checks if the round is 1,2 or 3
            await ctx.send("Invalid round.")
            return

        if ciwg.lower() not in "yn":
            await ctx.send("Invalid Category. Please enter y/n for ciwgc status")

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

    @commands.hybrid_command()
    async def airport(self, ctx,
                    college_name: str = commands.parameter(description = "example: nitc, nitt, nitk, nits, nsut, (use quotes for split names)")):
        embed = None
        """usage : ?airport college 
        college, ex: nitk, nitc, nitt, nsut
        """
        delete = Button(label="Delete", style=discord.ButtonStyle.danger)
        dms = Button(label="Send in DMs", style=discord.ButtonStyle.green)
        view = View()
        view.add_item(dms)
        view.add_item(delete)

        college_name = college_name.lower()
        college_list = db.request_college_list_air()
        try:
            college_name = db.nick_to_air(college_name)
        except:
            return await ctx.send("Invalid college name.")


        stats = db.get_airport_stats(college_name)
        embed = discord.Embed(
            title=f'Cutoffs for {college_name}', color=discord.Color.random())
        embed.set_thumbnail(
            url='https://dasanit.org/dasa2023/images/dasa_new.png')
        embed.add_field(name="College name: ", value=stats[0])
        embed.add_field(name="State: ", value=stats[1])
        embed.add_field(
            name="Closest Airport: ", value=stats[2])
        embed.add_field(
            name="Airport Code: " , value='(' + stats[3] + ')')
        embed.add_field(
            name="Distance of airport from college: " , value=stats[4] + 'KM')
        embed.set_footer(text = 'This message will be automatically deleted in 120s.\nTo receive this message in your DMs, press "Send in DMs".\nTo delete this message, press "Delete".')
        m = await ctx.send(embed=embed, delete_after=120, view = view)

        async def dms_callback(interaction):
            await self.bot.send_message(ctx.message.author, embed=embed)
            await interaction.response.send_message("Cutoffs have been sent in your DMs.")

                        

        async def dms_callback(interaction):
            if interaction.user.id == ctx.author.id:
                dmuser = await self.bot.fetch_user(ctx.author.id)
            else:
                dmuser = await self.bot.fetch_user(interaction.user.id)
            embed.remove_footer()
            await dmuser.send(embed = embed)
            await ctx.send("Airport details have been sent in your DMs.")

        async def delete_callback(interaction):
            if interaction.user.id == ctx.author.id:
                await m.delete()


        delete.callback = delete_callback
        dms.callback = dms_callback


    @commands.hybrid_command()
    async def analyse(self, ctx, rank:str, ciwg:str, branch:str = None):
        embed = None
        m = None
        delete = Button(label="Delete", style=discord.ButtonStyle.danger)
        dms = Button(label="Send in DMs", style=discord.ButtonStyle.green)
        view = View()
        view.add_item(dms)
        view.add_item(delete)
        
        ciwg = True if ciwg == 'y' else False
        if branch is not None:
            cutoffs, colleges = db.reverse_engine(rank, ciwg, branch)
            embed = discord.Embed(
                title="Chances based off of your JEE(Main) CRL-Rank",
                color=discord.Color.random(),
                description=f"Closing ranks for {branch.upper()}{'' if not ciwg else '(CIWG)'}")
            embed.set_thumbnail(
                url='https://dasanit.org/dasa2023/images/dasa_new.png')
            for i in range(10):
                embed.add_field(
                    name=f"{i+1}. {colleges[i]}", value=f"JEE CLOSING RANK: {cutoffs[i]}", inline=True)
                embed.set_footer(
                    text='This message will be automatically deleted in 120s.\nTo receive this message in your DMs, press "Send in DMs".\nTo delete this message, press "Delete".')
            m = await ctx.send(embed=embed, delete_after=120, view=view)
        else:
            cutoffs, colleges, branches = db.reverse_engine(rank, ciwg, branch)
            dic = {}  # {college : [[branch, cutoff], [branch, cutoff]}
            for i in range(len(colleges)):
                if colleges[i] not in list(dic.keys()):
                    dic[colleges[i]] = [[branches[i], cutoffs[i]]]
                else:
                    dic[colleges[i]] += [[branches[i], cutoffs[i]]]
            pages = []
            for i in dic:
                embed = discord.Embed(title=f"Closing Ranks for {i} in all branches {'(UNDER CIWG CATEGORY)' if ciwg else ''}",
                                      color=discord.Color.random())
                embed.set_thumbnail(
                    url='https://dasanit.org/dasa2023/images/dasa_new.png')
                for j in dic[i]:
                    embed.add_field(
                        name=f"{j[0][:-1]}" if ciwg else f"{j[0]}", value=f"JEE CLOSING RANK: {j[1]}", inline=True)
                    embed.set_footer(
                        text='This message will be automatically deleted in 5 minutes.\n')
                pages.append(embed)
            m = await Paginator.Simple(timeout=300).start(ctx, pages=pages)
            await asyncio.sleep(300)
            await m.delete()

        async def dms_callback(interaction):
            if interaction.user.id == ctx.author.id:
                dmuser = await self.bot.fetch_user(ctx.author.id)
            else:
                dmuser = await self.bot.fetch_user(interaction.user.id)
            embed.remove_footer()
            await dmuser.send(embed=embed)
            await ctx.send(f"Cutoffs have been sent in your DMs. {interaction.user.mention}")

        async def delete_callback(interaction):
            if interaction.user.id == ctx.author.id:
                await m.delete()

        delete.callback = delete_callback
        dms.callback = dms_callback
        await asyncio.sleep(5)
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(DASACommands(bot))
