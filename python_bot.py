import discord
from discord.ext import commands
from discord.ext.commands import Bot
import re
import os
from discord.utils import get
import ast
import json
import sys, traceback

dir_path = os.path.dirname(os.path.realpath(__file__))


bot = commands.Bot(command_prefix='p!', description='Created by Edsel Di Meo#6428', owner_id=594956772733878303, activity=discord.Game('p!help'))


initial_extensions = ['cogs.owner', 'cogs.moderation','cogs.misc','cogs.stats']
for extension in initial_extensions:
    try:
        print(f"Loaded {extension}")
        bot.load_extension(extension)
    except Exception as error:
        print('Failed to load extension {}.'.format(extension), file=sys.stderr)
        traceback.print_exc()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


with open(f"{dir_path}/APIKey.txt") as f:
    bot.run(f.read().strip())




