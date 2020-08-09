# import discord
from discord.ext import commands
# from .modules import modules_moderation as modules_moderation
from .modules import modules_stats as modules_stats
from .modules import modules_moderation
# import json
# import os
# import asyncio
import matplotlib.pyplot as plt 
from random import randint, choice
import io
import datetime,time,io,os,asyncio,json,discord


dir_path = os.path.dirname(os.path.realpath('python_bot.py'))

class Stats(commands.Cog):

    def __init__(self, bot):


        try:

            with open(f'{dir_path}/stats_db.json', 'r' ) as f:

                stats = json.load(f)

        except Exception as error:

            print(error)

            stats = {

                    'channels':[],

                            } 

        else:

            pass

        self.bot = bot
        self.stats = stats

    @commands.command()
    async def number_messages(self, ctx, Graphtype = 's', *dates):

        """Counts how many messages were sent in a channel from the 
        beginning of the month to the actual day"""

        if ctx.message.author.id == 155422817540767745 or modules_moderation.check_roles(ctx.message.author.roles, [243854949522472971]) == 1:
                

            for date in dates:

                option = int() # 0 - Single graph and the figure closes/ 1 - Comparison and the figure closes when date is the last date in dates

                if Graphtype.lower() == 'c': #comparison

                    if date == dates[-1]: #this date is the last one

                        option = 0 #single graph but actually we use 0 to close the multiple graphs generated

                    else: #this date is not the last one

                        option = 1

                else: #it's not a comparison

                    if Graphtype.lower() == 's': #single graph

                        option = 0 #single graph

                        

                print(date)

                formattedDate = date.split('/')

                print(formattedDate)

                result = modules_stats.verificator(ctx, formattedDate)

                if result == 0:

                    await ctx.send(f'The given date is wrong {date}')

                elif result == 1:

                    await ctx.send(f"The given channel doesn't exist {date}")

                elif result == 2:

                    await ctx.send(f'Not enough info given {date}')

                elif result == 3:

                    year = time.localtime()[0]
                    month = time.localtime()[1]
                    day = time.localtime()[2]
                    date = [month,day,year]
                    channel = modules_stats.giveChannel(ctx, formattedDate[0])
                    await modules_stats.graph(date,date,channel, option, ctx,discord)

                elif result == 4:

                    channel = modules_stats.giveChannel(ctx, formattedDate[0])
                    await modules_stats.graph(formattedDate[1:], formattedDate[1:], channel, option, ctx, discord)

                elif result == 5:

                    date1 = formattedDate[1:4]
                    date2 = formattedDate[4:]
                    channel = modules_stats.giveChannel(ctx, formattedDate[0])
                    await modules_stats.graph(date1, date2, channel, option, ctx, discord)



        else:

            await ctx.send("**You don't have enough permissions**")
        





def setup(bot):

    bot.add_cog(Stats(bot))