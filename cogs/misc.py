import discord
from discord.ext import commands, tasks
from itertools import cycle
from .modules import modules_moderation as modules_moderation
from .modules import modules_misc as modules_misc
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

class Misc(commands.Cog):

    def __init__(self, bot):

        try:

            with open(f'{dir_path}/db.json', 'r' ) as f:

                settings = json.load(f)

        except Exception as error:

            print(error)

            settings = {   
                            'bot_id':595011002215563303,
                            'roles_allowed': [243854949522472971],
                            } 
        try:

            with open(f'{dir_path}/misc_settings.json', 'r' ) as f:

                misc_settings = json.load(f)

        except Exception as error:

            # print(error)

            # settings = {   
            #                 'bot_id':595011002215563303,
            #                 'roles_allowed': [243854949522472971],
            #                 } 

            misc_settings = {
                        'guildId':243838819743432704,
                        'countMembersChannel':[{"id": 362397839864627201, "name": "Information"}],
                        'dailyGoal': {},
                        'goalChannel': {},
                        'rank':{},
                        'nightmareMode':{
                            'role_id': 738808953265455154,
                            'channels_id':[739127911650557993]
                        },
                        'dailyGoalRoles':
                        {
                            'ln_sp':297415063302832128,
                            'ln_en':247021017740869632,
                        },

            }

        else:

            pass

        self.settings = settings 
        self.misc_settings = misc_settings
        self.bot = bot 
        self.reset_goals.start()

    @tasks.loop(minutes=1440)
    async def reset_goals(self):
        self.misc_settings["dailyGoal"] = {}
        modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
        

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

        pixel_bot_id = self.settings["bot_id"]

        if message.author.id != pixel_bot_id:

            await modules_moderation.react_corrections(self.bot, message)

            if(message.guild.id == self.misc_settings["guildId"]):
                roles = []
                ultra_hardcore = self.misc_settings["nightmareMode"]["role_id"]
                stripped_msg = modules_misc.rem_emoji_url(message)
                if stripped_msg[0] not in 'p=;!>' and len(stripped_msg) > 5:

                    #lang = await modules_misc.detect_language(stripped_msg)
                    lang = modules_misc.detect_language(stripped_msg)
                    
                    for role in message.author.roles:
                        roles.append(role.id)

                    if(ultra_hardcore in roles or message.channel.id in self.misc_settings["nightmareMode"]["channels_id"] ): #Nightmare mode 
                        print("uwu")
                        await self.sp_serv_hardcore( await self.bot.get_context(message), message,roles,lang)

                    if(f"{message.author.id}" in self.misc_settings["dailyGoal"]): #Daily Goal Feature
                        learning_eng = self.misc_settings["dailyGoalRoles"]["ln_en"]
                        learning_sp = self.misc_settings["dailyGoalRoles"]["ln_sp"]

                        if learning_eng in roles:  
                            if lang == 'en':

                                await self.goal_completion_checker(message)
                                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
                          
                        elif learning_sp in roles:  
                            if lang == 'es':
                                
                                await self.goal_completion_checker(message)
                                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
                                        

    async def goal_completion_checker(self, message):

        self.misc_settings["dailyGoal"][f"{message.author.id}"]["messages_sent"]+=1
        modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
        messages_sent = self.misc_settings["dailyGoal"][f"{message.author.id}"]["messages_sent"]
        goal = self.misc_settings["dailyGoal"][f"{message.author.id}"]["goal"]

        if(messages_sent >= goal):
            if(f"{message.guild.id}" in self.misc_settings["goalChannel"]):

                channel = message.guild.get_channel(int(self.misc_settings["goalChannel"][f"{message.guild.id}"]))

                await channel.send(f"<@{message.author.id}> You have successfully reached today's goal. 🥳"  
                +"You should be proud of how hard you have worked today, and I recommend you to take a break because you deserve it ❤️ Congratulations!")

                await self.rank_updater(message, channel)

                del self.misc_settings["dailyGoal"][f"{message.author.id}"] 


    async def rank_updater(self, message, channel):

        year =  self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][0]
        month = self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][1]
        day = self.misc_settings["dailyGoal"][f"{message.author.id}"]["date"][2]
        date_formatted = f"{year}/{month}/{day}"
        if(date_formatted not in self.misc_settings['rank']):
            self.misc_settings['rank'][date_formatted] = {
                f"{message.author.id}": 1,
            }

            await channel.send(f"You are also the first person who completed a goal today!")

        else:
            if (f"{message.author.id}" in self.misc_settings['rank'][date_formatted]):
                self.misc_settings['rank'][date_formatted][f"{message.author.id}"]+=1
            else:
                self.misc_settings['rank'][date_formatted][f"{message.author.id}"] = 1


                            
    def cog_unload(self):
        self.reset_goals.cancel()

    """Spanish server hardcore thanks to @Ryry013#9234"""
    async def sp_serv_hardcore(self, ctx, msg,roles,lang):
        learning_eng = self.misc_settings["dailyGoalRoles"]["ln_en"]    
        learning_sp = self.misc_settings["dailyGoalRoles"]["ln_sp"]
        if learning_eng in roles:  # learning English, delete all Spanish
            if lang == 'es':
                try:
                    await msg.delete()
                except discord.errors.NotFound:
                    return

        elif learning_sp in roles:  # learning Spanish, delete all English
            if lang == 'en':
                try:
                    await msg.delete()
                except discord.errors.NotFound:
                    return

    @commands.command()
    async def set_goal(self, ctx, nmessages):

        """Sets a goal
        
        Parameters:
        
        nmessages: the amount of messages of your goal"""
            
        if f"{ctx.message.author.id}" in self.misc_settings["dailyGoal"]:
                await ctx.send("You already have a goal, try completing or deleting it using ``p!delGoal``")
                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
                return
        
        else:

            if(int(nmessages) >= 20):

                self.misc_settings["dailyGoal"][f"{ctx.message.author.id}"] = {
                    "messages_sent": 0,
                    "goal": int(nmessages),
                    "date": time.localtime()
                }

                await ctx.send("Goal added succesfully! ✅ You have one day to complete it, and you can see your goal's info by typing ``p!show_goal`` \n\n **Remember to set a language learning role otherwise this won't work for you**")

                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
            
            else:

                await ctx.send("Error: the minimum amount of messages for a goal has to be 20")
    
    @commands.command()
    async def del_goal(self, ctx):

        """Deletes your current goal"""

        if f"{ctx.message.author.id}" in self.misc_settings["dailyGoal"]:
            del self.misc_settings["dailyGoal"][f"{ctx.message.author.id}"]
            modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
            await ctx.send("Goal deleted succesfully! ✅")
        else:
            await ctx.send("You have no goals set yet, try ``p!set_goal [number of messages]``")

    @commands.command()
    async def set_goal_channel(self, ctx, channel_id):

        """Sets a goal channel, this has to be set otherwise members won't be alerted when they complete their goals
        
        parameters:
        
        channel_id: ID of the goal channel"""

        if ctx.message.author.id in self.settings['roles_allowed'] or ctx.message.author.id==155422817540767745:
            if(modules_moderation.channel_existance(channel_id, self.bot)):
                if f"{ctx.message.guild.id}" not in self.misc_settings["goalChannel"]:
                    self.misc_settings["goalChannel"][f"{ctx.message.guild.id}"] = channel_id
                    await ctx.send(f"{channel_id} added succesfully! ✅")
                    modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
                else:
                    await ctx.send(f"the channel <#{self.misc_settings['goalChannel'][f'{ctx.message.guild.id}']}> is already the goal channel. Remove it by using ``p!del_goal_channel [channel_ID]``")
            else:
                await ctx.send(f"{channel_id} not found! 🤔")
        else:
            await ctx.send(f"You don't have enough permissions to perform this action! ❌")

    @commands.command()
    async def del_goal_channel(self, ctx, channel_id):

        """Deletes the current goal channel
        
        parameters:
        
        channel_id: ID of the current goal channel"""

        if ctx.message.author.id in self.settings['roles_allowed'] or ctx.message.author.id==155422817540767745:
            if f"{ctx.message.guild.id}" in self.misc_settings["goalChannel"]:
                del self.misc_settings["goalChannel"][f"{ctx.message.guild.id}"]
                await ctx.send(f"{channel_id} deleted succesfully! ✅")
                modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
            else:
                await ctx.send(f"There's no goal channel set yet. Add one by using ``p!set_goal channel [channel_ID]``")
        else:
            await ctx.send(f"You don't have enough permissions to perform this action! ❌")

             

    @commands.command()
    async def show_goal(self, ctx):

        """Shows the current status of a member goal"""

        if f"{ctx.message.author.id}" in self.misc_settings["dailyGoal"]:

            emb = discord.Embed(title = await self.show_member(ctx, ctx.message.author.id), color=discord.Color(int('00ff00', 16)))

            messages_sent = self.misc_settings["dailyGoal"][f"{ctx.message.author.id}"]["messages_sent"]
            goal = self.misc_settings["dailyGoal"][f"{ctx.message.author.id}"]["goal"]
            remaining = int(goal) - int(messages_sent)
            value = f"Today's goal: {messages_sent}/{goal} messages \n"
            value += f"you are {remaining} messages away from your goal! Keep working hard!\n" 

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
    
    @commands.command()
    async def goal_leaderboard(self, ctx):

        """Shows the goal leaderboard of the past 30 days"""

        if(len(self.misc_settings['rank']) > 30):
            keys = self.misc_settings['rank'].keys()
            iterator = iter(self.misc_settings['rank'].keys())
            first_key = next(iterator)
            del self.misc_settings['rank'][first_key]

        emb_dict = {}
        mes = ""
        for rank_date in self.misc_settings['rank']:
            for user in self.misc_settings['rank'][f'{rank_date}']:
                if user in emb_dict:
                    emb_dict[user]+= self.misc_settings['rank'][rank_date][user]
                else:
                     emb_dict[user] = self.misc_settings['rank'][rank_date][user]

        sort_users = sorted(emb_dict.items(), key = lambda x: x[1], reverse=True)
        pos = 1
        emb = discord.Embed(title = "Goals Leaderboard", color=discord.Color(int('00ff00', 16)))

        for i in sort_users:    
            mes += f"**{pos}) {await self.show_member(ctx,i[0])}**\n {i[1]}\n"
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

        guild = modules_moderation.get_guild(self.bot, ctx.message.guild.id) #Retrieves the server ID
        category_id = int(category_id) #Converts the ID of the category, that we want to add the count to, to int

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1 or ctx.message.author.id == 155422817540767745: #Checks whether the user who's using this command has perms or not
            if modules_moderation.category_existance([{'id':category_id}], guild.categories) == 1: #Checks whether the category exists or not
                try:
                    category = modules_moderation.get_category([{'id':category_id}], guild.categories) #Retrieves the category object
                except Exception as e:
                    await ctx.send('Error when trying to retrieve the category object')#Error message
                else:
                    try:
                        self.misc_settings['countMembersChannel'].append({'id':category_id, 'name':category.name}) #Saves the server and category 
                    except Exception as e:
                        await ctx.send('Error when trying to change the category name') #Error message
                    else:
                        await ctx.send(f'{category_id} updated !') #If everything works, pixel will let the user know
                        modules_moderation.saveSpecific(self.misc_settings, 'misc_settings.json') #Applies changes
            else:
                await ctx.send(f'{category_id} doesnt exist!') #Error message
        else:
            await ctx.send("**You don't have enough permissions**") #Error message

      

        
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
