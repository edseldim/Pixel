import discord
from discord.ext import commands, tasks
from itertools import cycle
from .modules import modules_moderation as modules_moderation
from .modules import modules_misc as modules_misc
import json
import os
import asyncio
import matplotlib.pyplot as plt
import time
from random import randint, choice
import io
from textblob import TextBlob as tb
import time
import re
from datetime import datetime, timedelta, date
import string
from Levenshtein import distance as LDist

dir_path = os.path.dirname(os.path.realpath('python_bot.py'))


class Misc(commands.Cog):

    def __init__(self, bot):

        try:

            with open(f'{dir_path}/db.json', 'r') as f:

                settings = json.load(f)

        except Exception as error:

            print(error)

            settings = {'bot_id': 595011002215563303,
                        'roles_allowed': [243854949522472971]}
        try:

            with open(f'{dir_path}/misc_settings.json', 'r') as f:

                misc_settings = json.load(f)

        except Exception as error:

            misc_settings = {'guildId': 243838819743432704,
                             'local_day': time.localtime().tm_mday,
                             'countMembersChannel': [{"id": 362397839864627201, "name": "Information"}],
                             'dailyGoal': {},
                             'goalChannel': {},
                             'rank': {},
                             'nightmareMode': {'role_id': 738808953265455154,
                                               'channels_id': [739127911650557993]},
                             'dailyGoalRoles': {'ln_sp': 297415063302832128,
                                                'ln_en': 247021017740869632}}

        else:

            pass

        misc_settings["welcomeFeature"] = 1
        self.settings = settings
        self.misc_settings = misc_settings
        self.bot = bot
        self.reset_goals.start()
        # welcome_channel = None
        # bot_info = await self.bot.application_info()
        # if bot_info.id == 595011002215563303:  # esp eng pixel
        #     welcome_channel = self.bot.get_guild(self.misc_settings['guildId']).get_channel(243838819743432704)
        # elif bot_info.id == 635114071175331852:  # pixel test
        #     welcome_channel = self.bot.get_guild(self.misc_settings['guildId']).get_channel(811997637326012446)

        # misc_settings["welcomeChannel"] = welcome_channel

    # @tasks.loop(minutes=5)
    # async def is_rai_down(self):

    #     rai_obj = self.bot.get_guild(self.misc_settings['guildId']).get_member(270366726737231884)
    #     if str(rai_obj.status) == 'offline':
    #         self.misc_settings["welcomeFeature"] = 1  # the welcome feature is set to on
    #     else:
    #         if self.misc_settings["welcomeFeature"] == 1:  # if the welcome feature is set to on
    #             self.misc_settings["welcomeFeature"] = 0  # the welcome feature is set to off

    @tasks.loop(minutes=10)
    async def reset_goals(self):
        if self.misc_settings["local_day"] != time.localtime().tm_mday:
            self.misc_settings["local_day"] = time.localtime().tm_mday
            users_id = []
            for user_goal in self.misc_settings["dailyGoal"]:
                if self.misc_settings["dailyGoal"][f"{user_goal}"]["date"][2] != self.misc_settings["local_day"]:
                    users_id.append(user_goal)
            for user in users_id:
                del self.misc_settings["dailyGoal"][f"{user}"]
            modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        if len(before.roles) == 3 and len(after.roles) > 3:
            bot_info = await self.bot.application_info()
            if bot_info.id == 595011002215563303:  # esp eng pixel
                await self.bot.get_guild(self.misc_settings['guildId']).get_channel(296491080881537024).send(f'Welcome / Bienvenido/a, <@{after.id}>!')
            elif bot_info.id == 635114071175331852:  # pixel test
                await self.bot.get_guild(self.misc_settings['guildId']).get_channel(501861392593453078).send(f'Welcome / Bienvenido/a, <@{after.id}>!')

    @commands.Cog.listener()
    async def on_member_join(self, member):

        await modules_moderation.member_count_update(member, self.misc_settings)

        rai_obj = self.bot.get_guild(self.misc_settings['guildId']).get_member(270366726737231884)
        welcome_channel = None
        bot_info = await self.bot.application_info()
        if bot_info.id == 595011002215563303:  # esp eng pixel
            welcome_channel = self.bot.get_guild(self.misc_settings['guildId']).get_channel(243838819743432704)
        elif bot_info.id == 635114071175331852:  # pixel test
            welcome_channel = self.bot.get_guild(self.misc_settings['guildId']).get_channel(811997637326012446)

        if str(rai_obj.status) == 'online':
            await welcome_channel.send(f"{member.mention}\n"
                                       f"Hello! Welcome to the server!          Is your **native language**: "
                                       f"__English__, __Spanish__, __both__, or __neither__?\n"
                                       f"¡Hola! ¡Bienvenido(a) al servidor!    ¿Tu **idioma materno** es: "
                                       f"__el inglés__, __el español__, __ambos__ u __otro__?")

            # await self.welcomeSetup(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        await modules_moderation.member_count_update(member, self.misc_settings)

    @commands.Cog.listener()
    async def on_message(self, message):

        """Checks if the word that was just sent in a channel has to be 
        deleted"""

        # pixel_bot_id = self.settings["bot_id"]
        bot_info = await self.bot.application_info()

        if bot_info.id != pixel_bot_id:
            welcome_channel = None
            if bot_info.id == 595011002215563303:  # esp eng pixel
                welcome_channel = self.bot.get_guild(self.misc_settings['guildId']).get_channel(243838819743432704)
            elif bot_info.id == 635114071175331852:  # pixel test
                welcome_channel = self.bot.get_guild(self.misc_settings['guildId']).get_channel(811997637326012446)

            if len(message.author.roles) == 3 and message.channel.id == welcome_channel.id:
                rai_obj = self.bot.get_guild(self.misc_settings['guildId']).get_member(270366726737231884)
                if str(rai_obj.status) == 'online':
                    await self.welcomeSetup(message)

            await modules_moderation.react_corrections(self.bot, message)

            if(message.guild.id == self.misc_settings["guildId"]):
                roles = []
                ultra_hardcore = self.misc_settings["nightmareMode"]["role_id"]
                stripped_msg = modules_misc.rem_emoji_url(message)
                if stripped_msg[0] not in 'p=;!>' and len(stripped_msg) > 5:
                    lang = modules_misc.detect_language(stripped_msg)
                    for role in message.author.roles:
                        roles.append(role.id)
                    if(ultra_hardcore in roles or message.channel.id in self.misc_settings["nightmareMode"]["channels_id"]):  # Nightmare mode
                        print("uwu")
                        await self.sp_serv_hardcore(await self.bot.get_context(message), message, roles, lang)
                    if(f"{message.author.id}" in self.misc_settings["dailyGoal"]):  # Daily Goal Feature
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

    async def welcomeSetup(self, msg):
        # welcome_channel = None
        bot_info = await self.bot.application_info()
        # if bot_info.id == 595011002215563303:  # esp eng pixel
        #     welcome_channel = self.bot.get_guild(self.misc_settings['guildId']).get_channel(243838819743432704)
        # elif bot_info.id == 635114071175331852:  # pixel test
        #     welcome_channel = self.bot.get_guild(self.misc_settings['guildId']).get_channel(811997637326012446)

        # await welcome_channel.send(f"{member.mention}\n"
        #                            f"Hello! Welcome to the server!          Is your **native language**: "
        #                            f"__English__, __Spanish__, __both__, or __neither__?\n"
        #                            f"¡Hola! ¡Bienvenido(a) al servidor!    ¿Tu **idioma materno** es: "
        #                            f"__el inglés__, __el español__, __ambos__ u __otro__?")

        # def check(msg):
        #     if msg.author.id == member.id and msg.channel.id == welcome_channel.id:
        #         return True
        #     else:
        #         return False

        # msg = await self.bot.wait_for('message', check=check, timeout=1800)

        # while True:
        # if msg.author.id == member.id and msg.channel.id == welcome_channel.id:
        # break
        # else:
        # msg = await self.bot.wait_for('message', check=check, timeout=1800)

        content = re.sub('> .*\n', '', msg.content.casefold())  # remove quotes in case the user quotes bot
        content = content.translate(str.maketrans('', '', string.punctuation))  # remove punctuation
        for word in ['hello', 'hi', 'hola', 'thanks', 'gracias']:
            if content == word:
                return  # ignore messages that are just these single words
        if msg.content == '<@270366726737231884>':  # ping to Rai
            return  # ignore pings to Rai
        if bot_info.id == 595011002215563303:  # esp eng pixel
            english_role = msg.guild.get_role(243853718758359040)
            spanish_role = msg.guild.get_role(243854128424550401)
            other_role = msg.guild.get_role(247020385730691073)

        elif bot_info.id == 635114071175331852:  # pixel test
            english_role = msg.guild.get_role(812126949157634068)
            spanish_role = msg.guild.get_role(738813650738872380)
            other_role = msg.guild.get_role(812126954886135858)

        for role in [english_role, spanish_role, other_role]:
            if role in msg.author.roles:
                return  # ignore messages by users with tags already
        if datetime.utcnow() - msg.author.joined_at < timedelta(seconds=3):
            return

        english = ['english', 'inglés', 'anglohablante', 'angloparlante']
        spanish = ['spanish', 'español', 'hispanohablante', 'hispanoparlante', 'castellano']
        other = ['other', 'neither', 'otro', 'otra', 'arabic', 'french', 'árabe', 'francés', 'portuguese',
                 'brazil', 'portuguesa', 'brazilian']
        both = ['both', 'ambos', 'los dos']
        txt1 = ''
        language_score = {'english': 0, 'spanish': 0, 'other': 0, 'both': 0}  # eng, sp, other, both
        split = content.split()

        def check_language(language, index):
            skip_next_word = False  # just defining the variable
            for language_word in language:  # language = one of the four word lists above
                for content_word in split:  # content_word = the words in their message
                    if len(content_word) <= 3:
                        continue  # skip words three letters or less
                    if content_word in ['there']:
                        continue  # this triggers the word "other" so I skip it
                    if skip_next_word:  # if i marked this true from a previous loop...
                        skip_next_word = False  # ...first, reset it to false...
                        continue  # then skip this word
                    if content_word.startswith("learn") or content_word.startswith('aprend') \
                            or content_word.startswith('estud') or content_word.startswith('stud') or \
                            content_word.startswith('fluent'):
                        skip_next_word = True  # if they say any of these words, skip the *next* word
                        continue  # example: "I'm learning English, but native Spanish", skip "English"
                    if LDist(language_word, content_word) < 3:
                        language_score[language[0]] += 1

        check_language(english, 0)  # run the function I just defined four times, once for each of these lists
        check_language(spanish, 1)
        check_language(other, 2)
        check_language(both, 3)

        num_of_hits = 0
        for lang in language_score:
            if language_score[lang]:  # will add 1 if there's any value in that dictionary entry
                num_of_hits += 1  # so "english spanish" gives 2, but "english english" gives 1

        if num_of_hits != 1:  # the bot found more than one language statement in their message, so ask again
            await msg.channel.send(f"{msg.author.mention}\n"
                                   f"Hello! Welcome to the server!          Is your **native language**: "
                                   f"__English__, __Spanish__, __both__, or __neither__?\n"
                                   f"¡Hola! ¡Bienvenido(a) al servidor!    ¿Tu **idioma materno** es: "
                                   f"__el inglés__, __el español__, __ambos__ u __otro__?")
            return

        if msg.content.startswith(';') or msg.content.startswith('.'):
            return

        if language_score['english']:
            txt1 = " I've given you the `English Native` role! ¡Te he asignado el rol de `English Native`!\n\n"
            await msg.author.add_roles(english_role)
        if language_score['spanish']:
            txt1 = " I've given you the `Spanish Native` role! ¡Te he asignado el rol de `Spanish Native!`\n\n"
            await msg.author.add_roles(spanish_role)
        if language_score['other']:
            txt1 = " I've given you the `Other Native` role! ¡Te he asignado el rol de `Other Native!`\n\n"
            await msg.author.add_roles(other_role)
        if language_score['both']:
            txt1 = " I've given you both roles! ¡Te he asignado ambos roles! "
            await msg.author.add_roles(english_role, spanish_role)

        await msg.channel.send(txt1)

        txt2 = "You can add more roles in <#703075065016877066>:\n" \
               "Puedes añadirte más en <#703075065016877066>:\n\n" \
               "Before using the server, please read the rules in <#243859172268048385>.\n" \
               "Antes de usar el servidor, por favor lee las reglas en <#499544213466120192>."

        await msg.channel.send(txt2)

    async def goal_completion_checker(self, message):

        self.misc_settings["dailyGoal"][f"{message.author.id}"]["messages_sent"] += 1
        modules_moderation.saveSpecific(self.misc_settings, "misc_settings.json")
        messages_sent = self.misc_settings["dailyGoal"][f"{message.author.id}"]["messages_sent"]
        goal = self.misc_settings["dailyGoal"][f"{message.author.id}"]["goal"]

        if(messages_sent >= goal):
            if(f"{message.guild.id}" in self.misc_settings["goalChannel"]):

                channel = message.guild.get_channel(int(self.misc_settings["goalChannel"][f"{message.guild.id}"]))

                await channel.send(f"<@{message.author.id}> You have successfully reached today's goal. 🥳" +
                                   "You should be proud of how hard you have worked today, and I recommend you to take a break because you deserve it ❤️ Congratulations!")

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
            name = f"{member.name}"

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
        char_length = 0
        for i in sort_users:    
            char_length += len(f"**{pos}) {await self.show_member(ctx,i[0])}**\n {i[1]}\n")
            if(char_length < 2048):
                mes += f"**{pos}) {await self.show_member(ctx,i[0])}**\n {i[1]}\n"
                pos+=1

        emb.add_field(name = "last 30 days",
                        value = mes,
                        inline = False)
        mes = ""
        pos = 0
        for i in sort_users:
            if(int(i[0])==ctx.message.author.id):
                mes = f"You: {pos}) {await self.show_member(ctx,i[0])}\n {i[1]}\n"
                emb.set_footer(text = mes)
                break
            pos+=1

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
