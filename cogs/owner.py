import discord
from discord.ext import commands
from .modules import modules_moderation as modules_moderation
import os
import ast
import json
import io
import time

dir_path = os.path.dirname(os.path.realpath('python_bot.py'))

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

class Owner(commands.Cog):

    """Only the owner of the bot can use this commands"""

    def __init__(self, bot):


        self.settings = settings
        self.bot = bot 

    def insert_returns(self, body):
        # insert return stmt if the last expression is a expression statement
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        # for if statements, we insert returns into the body and the orelse
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        # for with blocks, again we insert returns into the body
        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)

    @commands.command()
    async def kill(self,ctx):

        """Shuts down the bot(Admins can use this command too)"""

        if modules_moderation.check_roles(ctx.message.author.roles, self.settings['roles_allowed']) == 1 or ctx.message.author.id == 155422817540767745:

            await ctx.message.add_reaction('☠')

            await self.bot.close()

        else:

            await ctx.send("**You don't have enough permissions**")
        


    @commands.command()
    async def eval_fn(self, ctx, *, cmd):

        if ctx.message.author.id == 155422817540767745:
            """Evaluates input.
            Input is interpreted as newline seperated statements.
            If the last statement is an expression, that is the return value.
            Usable globals:
            - `bot`: the bot instance
            - `discord`: the discord module
            - `commands`: the discord.ext.commands module
            - `ctx`: the invokation context
            - `__import__`: the builtin `__import__` function
            Such that `>eval 1 + 1` gives `2` as the result.
            The following invokation will cause the bot to send the text '9'
            to the channel of invokation and return '3' as the result of evaluating
            >eval ```
            a = 1 + 2
            b = a * 2
            await ctx.send(a + b)
            a
            ```
            """

            fn_name = "_eval_expr"

            cmd = cmd.strip("` ")

            # add a layer of indentation
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            self.insert_returns(body)

            env = {
                'bot': ctx.bot,
                'discord': discord,
                'commands': commands,
                'ctx': ctx,
                '__import__': __import__
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            await ctx.message.delete()

        else:

            await ctx.send("**You don't have enough permissions**")

    @commands.command(hidden=True)
    async def load(self, ctx, *, cog: str):
        """Command which loads a module."""

        try:
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send('**`ERROR:`** {} - {}'.format(type(e).__name__, e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, cog: str):

        try:
            self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send('**`ERROR:`** {} - {}'.format(type(e).__name__, e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, cog: str):

        try:
            self.bot.reload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')


def setup(bot):

    bot.add_cog(Owner(bot))

