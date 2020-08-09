import discord
from discord.ext import commands
from .modules import modules_moderation as modules_moderation
import json
import os
import asyncio
from time import localtime


dir_path = os.path.dirname(os.path.realpath('python_bot.py'))
date = f'{localtime()[0]}/{localtime()[1]}/{localtime()[2]} {localtime()[3]}:{localtime()[4]}:{localtime()[5]} UTC'



class Moderation(commands.Cog):

    """Commands for Admins"""

    def __init__(self, bot):
        
        try:

            with open(f"{dir_path}/db.json",'r') as open_file:

                    settings = json.load(open_file)


        except Exception as error:

            print(error)

            settings = {

                'channels_to_censor': [],
                    'banned_words': [],
                    'roles_allowed': [243854949522472971],
                    'censored_people': [],
                    'admin_alert_channels':[]
                    } 

        else:

             pass

        self.bot = bot 
        self.settings = settings

    def make_embed(self, member, logs):

        """Creates am embed for the warnlog"""

        emb = discord.Embed(title = member, color=discord.Color(int('00ff00', 16)))

        value = ''

        i = 0

        for log in logs:

            value = f"__Reason__: {log['reason']}\n"
            value += f"[Jump URL]({log['link']})\n" 

            emb.add_field(name = f"{i}){log['time']}",
                          value = value,
                          inline = False)

            i = i + 1
                            

        return emb
    
    async def show_member(self, ctx, id):

        """Retrieves the nick of a member"""

        member = await modules_moderation.member_converter(ctx, id)

        if member:
            name = f"{member.name}#{member.discriminator} ({member.id})"

            return name

        else:

            name = 'Not found'

            return name



    @commands.Cog.listener()
    async def on_message(self, message):

        """Checks if the word that was just sent in a channel has to be 
        deleted"""

        banned_word = f' {message.content.lower()} '

        pixel_bot_id = 595011002215563303

        if message.author.id != pixel_bot_id:

            await modules_moderation.react_corrections(self.bot, message)

          

    @commands.command()
    async def slangwarn(self, ctx, id, *reason_s):

        reason = str()

        for word in reason_s:

            reason += f'{word} '

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            if modules_moderation.check_user_existance(ctx, int(id), self.bot) == 1:
           
                        for person_dictionary in self.settings['censored_people']:

                            if person_dictionary['user'] == int(id):
                                
                                person_dictionary['logs'].append({
                                    'reason': reason, 
                                    'time': date,
                                    'link':ctx.message.jump_url,
                                })

                                self.save()

                                # await ctx.send(f"```You just added this entry:\n"
                                #         +f"User:{self.bot.get_guild(ctx.message.guild.id).get_member(int(id)).nick}\n"
                                #         +f"Reason:{reason}```")

                                member = await self.show_member(ctx, id)

                                emb = discord.Embed(title = f'You just added this entry:', 
                                                    color=discord.Color(int('ff0000', 16)),
                                                    description=f'__User__: {member}\n'
                                                               +f'__Reason__: {reason}')   


                                await ctx.send(embed = emb)


                                break

                        else:

                            self.settings['censored_people'].append({
                                'user':int(id),
                                'logs':[{ 'reason': reason, 'time':date, 'link':ctx.message.jump_url,}]
                            })

                            self.save()

                            member = await self.show_member(ctx, id)

                            emb = discord.Embed(title = f'You just added this entry:', 
                                                color=discord.Color(int('ff0000', 16)),
                                                description=f'__User__: {member}\n'
                                                           +f'__Reason__: {reason}')   

                            await ctx.send(embed = emb)


                            # await ctx.send(f"```You just added this entry:\n"
                            #                     +f"User:{self.bot.get_guild(ctx.message.guild.id).get_member(int(id)).nick}\n"
                            #                     +f"Reason:{reason}```")

            else:

                await ctx.send("**The user doesn't exist**")

        else:

            await ctx.send("**You don't have enough permissions**")


    @commands.command()
    async def slanglog(self, ctx, id):

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            if modules_moderation.check_user_existance(ctx, int(id), self.bot) == 1:

                    for person_dictionary in self.settings['censored_people']:

                                if int(person_dictionary['user']) == int(id):

                                    if len(person_dictionary['logs']) > 0:

                                        member = await self.show_member(ctx, id)

                                        emb = self.make_embed(member, person_dictionary['logs'])

                                        await ctx.send(embed = emb)


                                    # content = []
                                    # i = 0

                                    # for log in person_dictionary['logs']:

                                    #     content.append( f"{i})"
                                    #                    +f"{log['time']}\n\n"
                                    #                    +f"reason: {log['reason']}\n\n")

                                    #     i = i + 1

                                    # if len(content) == 0:

                                    else:

                                        await ctx.send('**The user is not in my database**')

                                    # else:

                                    #     await ctx.send(modules_moderation.message_maker(content,f"Slang log for {self.bot.get_guild(ctx.message.guild.id).get_member(int(id)).nick}\n"
                                    #                                          +f"{person_dictionary['user']}"))

                                    break

                    else:

                        await ctx.send('**The user is not in my database**')

            else:

                await ctx.send("**The user doesn't exist**")

        else:

            await ctx.send("**You don't have enough permissions**")


    @commands.command()
    async def delslanglog(self, ctx, id, entry_pos):


        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            if modules_moderation.check_user_existance(ctx, int(id), self.bot) == 1:

                for person_dictionary in self.settings['censored_people']:

                    if int(person_dictionary['user']) == int(id):

                        number_list = entry_pos.split(',')

                        for number in number_list:


                            try:

                                deleted_log = person_dictionary['logs'][int(number)]
                                del person_dictionary['logs'][int(number)]

                            except:

                                await ctx.send(f"**The log #{number} doesn't exist**")

                            else:

                                member = await self.show_member(ctx, id)

                                emb = discord.Embed(title = f'You just deleted this entry:', 
                                                    color=discord.Color(int('ff0000', 16)),
                                                    description=f'__User__: {member}\n'
                                                               +f"__Reason__: {deleted_log['reason']}\n"
                                                               +f"__Time__: {deleted_log['time']}") 

                                # await ctx.send(f"```You just deleted this entry:\n"
                                #             +f"user:{self.bot.get_guild(ctx.message.guild.id).get_member(int(id)).nick}\n"
                                #             +f"reason:{deleted_log['reason']}\n"
                                #             +f"time:{deleted_log['time']}```")

                                await ctx.send(embed = emb)

                                self.save()


                        break

                                

                else:

                    await ctx.send('**This log is empty**')

            
            else:

                await ctx.send("**The user doesn't exist**")

        else:

            await ctx.send("**You don't have enough permissions**")



    @commands.command()
    async def find_in_attr(self, ctx, unique_code, attribute):

        """Uses a code like an id or a word to see all the coincidences in a attribute"""

        i = 0

        message = ""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:
            if modules_moderation.category_verifier(attribute, self.settings) == 1:
                if attribute.lower() != 'banned_words':
                    for attribute_item in self.settings[attribute]:
                        for key in attribute_item:
                                if attribute_item[key] == int(unique_code):
                                    for dict_key in attribute_item:                                
                                        if dict_key == 'words_deleted':
                                            message += f"{dict_key}: react 🆗 to show the banned words, "
                                        else:
                                            message += f"{dict_key}: {attribute_item[dict_key]}, "

                                    await ctx.send(f"```I just found something in my database:\n\n"
                                                +f"{message} in {attribute}```")

                                    if attribute.lower() == 'censored_people':

                                        await ctx.message.add_reaction('🆗')

                                        def check(reaction, user):
                                                    return user == ctx.message.author and str(reaction.emoji) == '🆗'

                                        try:
                                            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                                        except asyncio.TimeoutError:

                                            await ctx.send('**Try again please**')

                                        else:

                                            message = '```words deleted:\n'

                                            for word_deleted in attribute_item['words_deleted']:
                                                
                                                message += f'{word_deleted}, '

                                            message += '```'

                                            await ctx.send(message)

                                    
                                    i = 1
                                    break 
                    else:
                        if i == 0:
                            await ctx.send("**That item is not stored in my database**") 

                else:
                    for word in self.settings[attribute]:
                        if word.lower() == unique_code.lower():
                            await ctx.send(f"I just found something in my database:\n\n"
                                        +f"{word} in {attribute}")
                            break 
                    else:

                        await ctx.send("**That item is not stored in my database**")     
            else:

                await ctx.send("**That attribute doesn't exist**")
        else:
            await ctx.send("**You don't have enough permissions**")


    @commands.command()
    async def delete_all_info(self, ctx, attribute):

        """Deletes all the info in an attribute"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            for key in self.settings:

                if key.lower() == attribute.lower():

                    if len(self.settings[key]) > 0:

                        for i in range(len(self.settings[key])):

                            del self.settings[key][0]

                        await ctx.send("**Done!**")

                        self.save()

                        break

            else:


                try:

                    len(self.settings[attribute]) == 0

                except:

                    await ctx.send("**That attribute doesn't exist**")

                        # ctx.send('This attribute is already empty') 

                else:

                    await ctx.send('**This attribute is already empty**')

                    # await ctx.send("**That attribute doesn't exist**")

        else:

            await ctx.send("**You don't have enough permissions**")


    @commands.command()
    async def delete_alert_channel(self, ctx, alert_channel):

        """Deletes an admin alert channel using its ID"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            i = 0

            for channel in self.settings['admin_alert_channels']:

                if channel['channel_id'] == int(alert_channel):

                    del self.settings['admin_alert_channels'][i]

                    await ctx.send('**Done**')

                    self.save()

                    break

                i += 1

            else:

                await ctx.send("**That channel doesn't exist**")

        else:

            await ctx.send("**You don't have enough permissions**")

    @commands.command()
    async def show_all_attr(self, ctx):

        """Shows all the Attributes stored in the database"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            message = "```Attributes:\n\n"

            for key in self.settings:

                message += f'{key}, '

            message += "```"

            await ctx.send(message)

        else:

            await ctx.send("**You don't have enough permissions**")




    @commands.command()
    async def show_attr(self, ctx,  attribute):

        """Shows the info stored in just one attribute"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            try:

                message =  modules_moderation.print_info_attribute(attribute, self.settings[attribute], self.bot, ctx.guild.id)

            except:

                await ctx.send("**That attribute doesn't exist**")


            else:

                if message != -1:

                    await ctx.send(message)

                else:
                
                    await ctx.send("**This attribute is empty**")

                # await ctx.send("**That attribute doesn't exist or it's empty**")
        
        else:

            await ctx.send("**You don't have enough permissions**")

                
            
        
    @commands.command()
    async def add_alert_channel(self, ctx, alert_channel_id, alert_language):

        """Add a channel where the bot is going send messages about
        the users who have used a banned word three times"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            if modules_moderation.channel_avaliability_checker(alert_channel_id, 'admin_alert_channels', self.settings):

                if modules_moderation.channel_existance(alert_channel_id, self.bot):

                        channel_name = modules_moderation.get_channel_name(alert_channel_id, self.bot)

                        self.settings['admin_alert_channels'].append({
                            'channel_id':int(alert_channel_id),
                            'language':alert_language,
                            'channel_name':channel_name,
                            })

                        await ctx.send('**Done!**')

                        self.save()

                else:

                    await ctx.send("**That channel doesn't exist**")

            else:

                await ctx.send("**That channel is already in my database**")

        else:

            await ctx.send("**You don't have enough permissions**")


    @commands.command() 
    async def add_c_channel(self,ctx, channel_id, language = 'ES', delete_messages = 'False', alert_users = 'OFF', admin_alert = 'False'):

        """Gets the name of the channel where the bot will be allowed to deleted
            messages"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            if modules_moderation.channel_avaliability_checker(channel_id, 'channels_to_censor', self.settings):

                if modules_moderation.channel_existance(channel_id, self.bot):

                    channel_name = modules_moderation.get_channel_name(channel_id, self.bot)

                    if delete_messages.lower() == 'true' and alert_users.lower() == 'rc':

                        await ctx.send('**I can not react to any messages if delete_messages is true!**')

                    else:

                        if language.upper() == 'ES' or language.upper() == 'EN': 

                            self.settings['channels_to_censor'].append({
                                'channel_id':int(channel_id),
                                'language':language.upper(),
                                'channel_name':channel_name,
                                'delete_messages': delete_messages.title(),
                                'alert_users':alert_users,
                                'admin_alert': admin_alert.title(),
                            })

                            await ctx.send('**Done!**')

                            self.save()

                        else:

                            await ctx.send('**Check your input!**')

                else:

                    await ctx.send("**That Channel Doesn't Exist**")

            else:

                await ctx.send("**That channel is already in my database**")

        else:

            await ctx.send("**You don't have enough permissions**")
       
        
    @commands.command() 
    async def add_banned_word(self,ctx, *banned_word):

        """Adds a word to the lists of banned words"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            banned_word_list = []
            for word in banned_word:

                banned_word_list.append(word)
            compound_word = ""
            deleteWordList = []

            for i in range(len(banned_word_list)):

                if banned_word_list[i].startswith('"'):

                    compound_word += banned_word_list[i].lstrip('"')

                    for j in range((len(banned_word_list)-1)-i):

                        deleteWordList.append(banned_word_list[i+(j+1)])

                        if banned_word_list[i+(j+1)].endswith('"'):

                            word = banned_word_list[i+(j+1)].rstrip('"')

                            compound_word += f" {word}"

                            break

                        else:

                            compound_word += f' {banned_word_list[i+(j+1)]}'
          
                    banned_word_list.append(compound_word)

                    deleteWordList.append(banned_word_list[i])

            print(deleteWordList)

            for word in deleteWordList:

                banned_word_list.remove(word)
                    

            valid_words = modules_moderation.word_avaliability_checker(banned_word_list, self.settings)

            if valid_words != False:

                for word in valid_words:

                    self.settings['banned_words'].append(word)

                await ctx.send('**Done!**')

                self.save()

            else:

                await ctx.send('**The word is already in my database**')

        else:

            await ctx.send("**You don't have enough permissions**")



    @commands.command()
    async def delete_banned_word(self, ctx, banned_word):

        """Deletes a word from the banned words' list"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            if banned_word in self.settings['banned_words']:

                    self.settings['banned_words'].remove(banned_word)
            
                    await ctx.send('**Done!**')

            else:

                await ctx.send('**That word is not in my database**')

            self.save()

        else:

            await ctx.send("**You don't have enough permissions**")



    @commands.command() 
    async def delete_c_channel(self, ctx, c_channel_id):

        """Uses an ID to delete a channel from the list of censusing in channels"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            i = 0

            for channel in self.settings['channels_to_censor']:

                if channel['channel_id'] == int(c_channel_id):

                    del self.settings['channels_to_censor'][i]

                    await ctx.send('**Done!**')

                    self.save()

                    break

                i += 1


            else:
            
                await ctx.send('**That channel is not in my database**')

        else:

            await ctx.send("**You don't have enough permissions**")

    @commands.command()
    async def delete_role(self, ctx, role_id):

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            if modules_moderation.check_role_existance(int(role_id), self.settings['roles_allowed']) == 1:

                for i in range(len(self.settings['roles_allowed'])):

                    if self.settings['roles_allowed'][i] == int(role_id):

                        del self.settings['roles_allowed'][i]

                        await ctx.send('**Done!**')

                        self.save()

                        break

            else:

                await ctx.send("**The role is not in the database**")

        else:

            await ctx.send("**You don't have enough permissions**")


    @commands.command()
    async def add_role(self, ctx, role_id):

        """Uses an ID to add a role to the list of the roles that are allowed
        to use the bot"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1:

            if modules_moderation.check_role_existance(int(role_id), self.settings['roles_allowed']) == 0:

                self.settings['roles_allowed'].append(int(role_id))

                await ctx.send('**Done!**')

                self.save()

            else:

                await ctx.send("**The role is already in the database**")

        else:

            await ctx.send("**You don't have enough permissions**")

    def save(self):

        """Saves the settings in a json file"""

        with open(f"{dir_path}/db.json",'w') as write_file:

            json.dump(self.settings, write_file)

    


def setup(bot):

    bot.add_cog(Moderation(bot))