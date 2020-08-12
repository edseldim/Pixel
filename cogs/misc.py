import discord
from discord.ext import commands, tasks
from itertools import cycle
from .modules import modules_moderation as modules_moderation
from .modules import modules_misc
import json
import os
import asyncio
import matplotlib.pyplot as plt 
from random import randint, choice
import io
from textblob import TextBlob as tb
import time
from datetime import date

dir_path = os.path.dirname(os.path.realpath('python_bot.py'))
status = cycle(["status 1", "status 2"])
class Misc(commands.Cog):

    def __init__(self, bot):

        try:

            with open(f'{dir_path}/db.json', 'r' ) as f:

                settings = json.load(f)

            with open(f'{dir_path}/misc_settings.json', 'r' ) as f:

                misc_settings = json.load(f)

        except Exception as error:

            print(error)

            settings = {   
                            'roles_allowed': [243854949522472971],
                            } 

            misc_settings = {
                        'countMembersChannel':[],
                        'dailyGoal': {},
                        'goalChannel':{},
                        'rank':{}
            }

        else:

            pass

        self.settings = settings 
        self.misc_settings = misc_settings
        self.bot = bot 
        self.reset_goals.start()

    @tasks.loop(days=1)
    async def reset_goals(self):
        self.misc_settings["dailyGoal"] = {}
        modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
        if()

    @commands.Cog.listener()
    async def on_member_join(self, member):

        await modules_moderation.member_count_update(member, self.misc_settings)

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        await modules_moderation.member_count_update(member, self.misc_settings)

    @commands.Cog.listener()
    async def on_message(self, message):

        """Checks if the word that was just sent in a channel has to be 
        deleted"""

        banned_word = f' {message.content.lower()} '

        pixel_bot_id = 595011002215563303

        if message.author.id != pixel_bot_id:

            await modules_moderation.react_corrections(self.bot, message)

            if(message.guild.id == 501861392593453076):
                ultra_hardcore = message.guild.get_role(738813425333043312)
                stripped_msg = modules_misc.rem_emoji_url(message)
                if stripped_msg[0] not in '=;!>':
                    lang = tb(stripped_msg).detect_language()
                    if(ultra_hardcore in message.author.roles or message.channel.id == 501861392593453078):
                        await self.sp_serv_hardcore( await self.bot.get_context(message), message, lang)

                    if(f"{message.author.id}" in self.misc_settings["dailyGoal"]):
                        learning_eng = message.guild.get_role(738813394429411398)
                        learning_sp = message.guild.get_role(738813648369352804)

                        if learning_eng in message.author.roles:  
                            if lang == 'en':
                                self.misc_settings["dailyGoal"][f"{message.author.id}"]["messages_sent"]+=1
                                messages_sent = self.misc_settings["dailyGoal"][f"{message.author.id}"]["messages_sent"]
                                goal = self.misc_settings["dailyGoal"][f"{message.author.id}"]["goal"]
                                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
                                if(messages_sent >= goal):
                                    if(f"{message.guild.id}" in self.misc_settings["goalChannel"]):

                                        channel = message.guild.get_channel(int(self.misc_settings["goalChannel"][f"{message.guild.id}"]))
                                        await channel.send(f"<@{message.author.id}> You have successfully reached today's goal. 🥳"  
                                        +"You should be proud of how hard you have worked today, and I recommend you to take a break because you deserve it ❤️ Congratulations!")

                                        year =  self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][0]
                                        month = self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][1]
                                        day = self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][2]
                                        date_formatted = f"{year}/{month}/{day}"
                                        if(date_formatted not in self.misc_settings['rank']):
                                            self.misc_settings['rank'][date_formatted] = {
                                                f"{message.author.id}": 1,
                                            }
                                        else:
                                            if (f"{message.author.id}" in self.misc_settings['rank'][date_formatted]):
                                                self.misc_settings['rank'][date_formatted][f"{message.author.id}"]+=1
                                            else:
                                                self.misc_settings['rank'][date_formatted][f"{message.author.id}"] = 1
                                        
                                        del self.misc_settings["dailyGoal"][f"{message.author.id}"]

                                        modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
                          
                        elif learning_sp in message.author.roles:  
                            if lang == 'es':
                                self.misc_settings["dailyGoal"][f"{message.author.id}"]["messages_sent"]+=1
                                messages_sent = self.misc_settings["dailyGoal"][f"{message.author.id}"]["messages_sent"]
                                goal = self.misc_settings["dailyGoal"][f"{message.author.id}"]["goal"]
                                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
                                if(messages_sent >= goal):
                                    if(f"{message.guild.id}" in self.misc_settings["goalChannel"]):

                                        channel = message.guild.get_channel(int(self.misc_settings["goalChannel"][f"{message.guild.id}"]))
                                        await channel.send(f"<@{message.author.id}> You have successfully reached today's goal. 🥳"  
                                        +"You should be proud of how hard you have worked today, and I recommend you to take a break because you deserve it ❤️ Congratulations!")

                                        year =  self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][0]
                                        month = self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][1]
                                        day = self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][2]
                                        date_formatted = f"{year}/{month}/{day}"
                                        if(date_formatted not in self.misc_settings['rank']):
                                            self.misc_settings['rank'][date_formatted] = {
                                                f"{message.author.id}": 1,
                                            }
                                        else:
                                            if (f"{message.author.id}" in self.misc_settings['rank'][date_formatted]):
                                                self.misc_settings['rank'][date_formatted][f"{message.author.id}"]+=1
                                            else:
                                                self.misc_settings['rank'][date_formatted][f"{message.author.id}"] = 1
                                        
                                        del self.misc_settings["dailyGoal"][f"{message.author.id}"]
                                        modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")

                            
    def cog_unload(self):
        self.reset_goals.cancel()

    """Spanish server hardcore thanks to @Ryry013#9234"""
    async def sp_serv_hardcore(self, ctx, msg, lang):
        learning_eng = msg.guild.get_role(738813394429411398)
        learning_sp = msg.guild.get_role(738813648369352804)
        if learning_eng in msg.author.roles:  # learning English, delete all Spanish
            if lang == 'es':
                try:
                    await msg.delete()
                except discord.errors.NotFound:
                    return

        elif learning_sp in msg.author.roles:  # learning Spanish, delete all English
            if lang == 'en':
                try:
                    await msg.delete()
                except discord.errors.NotFound:
                    return

    @commands.command()
    async def set_goal(self, ctx, nmessages):
            
            if f"{ctx.message.author.id}" in self.misc_settings["dailyGoal"]:
                    await ctx.send("You already have a goal, try completing or deleting it using ``p!delGoal``")
                    modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
                    return
            
            else:
                self.misc_settings["dailyGoal"][f"{ctx.message.author.id}"] = {
                    "messages_sent": 0,
                    "goal": int(nmessages),
                    "date": time.localtime()
                }

                await ctx.send("Goal added succesfully! ✅ You have one day to complete it, and you can see your goal's info by typing ``p!show_goal``")

                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")

    
    @commands.command()
    async def del_goal(self, ctx):
        if f"{ctx.message.author.id}" in self.misc_settings["dailyGoal"]:
            del self.misc_settings["dailyGoal"][f"{ctx.message.author.id}"]
            modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
            await ctx.send("Goal deleted succesfully! ✅")
        else:
            await ctx.send("You have no goals set yet, try ``p!set_goal [number of messages]``")

    @commands.command()
    async def set_goal_channel(self, ctx, channel_id):
        if ctx.message.author.id in self.settings['roles_allowed'] or ctx.message.author.id==155422817540767745:
            if(modules_moderation.channel_existance(channel_id, self.bot)):
                self.misc_settings["goalChannel"][f"{ctx.message.guild.id}"] = channel_id
                await ctx.send(f"{channel_id} added succesfully! ✅")
                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
            else:
                await ctx.send(f"{channel_id} not found! 🤔")
        else:
            await ctx.send(f"You don't have enough permissions to perform this action! ❌")

    @commands.command()
    async def show_goal(self, ctx):

        """Creates am embed for the goal"""

        if f"{ctx.message.author.id}" in self.misc_settings["dailyGoal"]:

            emb = discord.Embed(title = await self.show_member(ctx, ctx.message.author.id), color=discord.Color(int('00ff00', 16)))

            messages_sent = self.misc_settings["dailyGoal"][f"{ctx.message.author.id}"]["messages_sent"]
            goal = self.misc_settings["dailyGoal"][f"{ctx.message.author.id}"]["goal"]
            remaining = int(goal) - int(messages_sent)
            value = f"Today's goal: {messages_sent}/{goal} words \n"
            value += f"you are {remaining} words away from your goal! Keep working hard!\n" 

            emb.add_field(name = f"{ctx.message.author.name}'s goal",
                            value = value,
                            inline = False)

            await ctx.send(embed = emb)

        else:
            await ctx.send(f"<@{ctx.message.author.id}> not found! 🤔")

    async def show_member(self, ctx, id):

        """Retrieves the nick of a member"""

        member = await modules_moderation.member_converter(ctx, id)

        if member:
            name = f"{member.name}#{member.discriminator} ({member.id})"

            return name

        else:

            name = 'Not found'

            return name
    
    @command.command()
    async def goal_leaderboard(self, ctx):

        if(len(self.misc_settings['rank']) > 30):
            keys = self.misc_settings['rank'].keys()
            iterator = iter(self.misc_settings['rank'].keys())
            first_key = next(iterator)
            del self.misc_settings['rank'][first_key]

        emb_dict = {}
        mes = ""
        for rank_date in self.misc_settings['rank']:
            for user in rank_date:
                if user in emb_dict:
                    emb_dict[user]+= self.misc_settings['rank'][date][user]
                else:
                     emb_dict[user] = self.misc_settings['rank'][date][user]

        sort_users = sorted(emb_dict.items(), key = lambda x: x[1], reverse=True)
        pos = 1
        emb = discord.Embed(title = "Goals Leaderboard", color=discord.Color(int('00ff00', 16)))

        for i in sort_users:    
            mes += f"**{pos}) {i[0]}**\n {i[1]}\n"
            pos+=1

        emb.add_field(name = "last 30 days",
                        value = mes,
                        inline = False)

        await ctx.send(embed = emb)



    @commands.command()
    async def uwu(self, ctx):

        await ctx.send('uwu')

    @commands.command()
    async def owo(self, ctx):

        await ctx.send('owo')

    @commands.command()
    async def random_walk(self, ctx, points, color_map = 'Blues', alpha_value = 0.5):

        """Generates a random walk"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            i = 0
            x_axis = [0]
            y_axis = [0]

            while i < int(points):

                x = randint(-10,10)
                y = randint(-10,10)
                x_direction = x + x_axis[-1]
                y_direction = y + y_axis[-1]

                if x_direction == x_axis[-1] and y_direction == y_axis[-1]:

                    continue

                else:

                    x_axis.append(x_direction)
                    y_axis.append(y_direction)


                i += 1

            fig, ax = plt.subplots()

            try:
                ax.scatter(x_axis, y_axis, c= [i for i in range(len(y_axis))], cmap = color_map, alpha = alpha_value,  edgecolor='none', s=15)
            
            except:

                await ctx.send("I think that color map doesn't exist, you'll find them in https://matplotlib.org/3.1.1/tutorials/colors/colormaps.html?highlight=colormap")
            
            else:

                ax.set_xticks([])
                ax.set_yticks([])
                
                with io.BytesIO() as walkIm:
                    plt.savefig(walkIm, format='png')
                    walkIm.seek(0)
                    await ctx.send(file=discord.File(walkIm, 'plot.png'))

            
        else:

                await ctx.send("**You don't have enough permissions**")

    @commands.command()
    async def cowboy(self,ctx):

        """Puts a cowboy emoji in your username"""

        try:

            await ctx.author.edit(nick=ctx.author.display_name + '🤠')
            await ctx.send("There you go!")

        except Exception as e:

            await ctx.send('Missing permissions 😭')

    @commands.command()
    async def rattlesnake(self,ctx):

        """Gets rid of all the cowboy emojis in your nickname
        credits: EsteemedRat#9914"""

        nick = ctx.author.nick

        nick = nick.replace('🤠','',1)

        try:

            await ctx.author.edit(nick = nick)

        except Exception as e:

            await ctx.send('Missing permissions 😭')

        else:

            await ctx.send("You're no longer a cowboy 🤠")

    @commands.command()
    async def add_member_count_category(self,ctx, category_id):

        guild = modules_moderation.get_guild(self.bot, ctx.message.guild.id)
        category_id = int(category_id)

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1 or ctx.message.author.id == 155422817540767745:
            if modules_moderation.category_existance([{'id':category_id}], guild.categories) == 1:
                await ctx.send(f'{category_id} added !')
                category = modules_moderation.get_category([{'id':category_id}], guild.categories)
                self.misc_settings['countMembersChannel'].append({'id':category_id, 'name':category.name})
                modules_moderation.saveSpecific(self.misc_settings, 'misc_settings.json')
            else:
                await ctx.send(f'{category_id} doesnt exists!')
        else:
            await ctx.send("**You don't have enough permissions**")

      

        
    @commands.command()
    async def say(self,ctx, *content):

        """Lets pixel say anything in any channel
        
        Syntaxis => message + | + channel where you want to send your message in

        You have to write your message and after your message put a | and after that the channel where you want to send your message in
        
        for example => p!say hello | general"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1: 

            pos = -1

            if len(content) > 0:

                content_sent = ''

                for word in content:

                    content_sent += word + ' '

                for position in range(len(content_sent)):

                    if content_sent[position] == '|':

                        pos = position

                #We use this for to check for all the | used, and the last one is going to count as the character that actually
                #divides the message to the channel's name

                if pos != -1:

                    message = content_sent[:pos]

                    channel = content_sent[pos+1:].strip()

                else:

                    message = content_sent

                    channel = ''

                if len(message) > 0:

                    if len(channel) > 0:

                        flag = 0

                        channels = ctx.bot.get_guild(ctx.message.guild.id.real).channels

                        for channel_server in channels:

                            if channel_server.name == channel:

                                await ctx.bot.get_guild(ctx.message.guild.id.real).get_channel(channel_server.id).send(message)

                                flag = 1

                        if flag == 0:

                            await ctx.send("**That channel doesn't exist**")


                    else:

                        await ctx.bot.get_guild(ctx.message.guild.id.real).get_channel(ctx.message.channel.id).send(message)
                
            else:

                await ctx.send("**Hey, the message's content is empty, please try again.**")

        else:

                await ctx.send("**You don't have enough permissions**")



def setup(bot):

    bot.add_cog(Misc(bot))