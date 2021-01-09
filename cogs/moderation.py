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
                            'bot_id':595011002215563303,
                            'roles_allowed': [243854949522472971],
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

        pixel_bot_id = 595011002215563303

        if message.author.id != pixel_bot_id:

            await modules_moderation.react_corrections(self.bot, message)


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