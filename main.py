import discord
from discord.ext import commands
from discord import File
import os
import io
import ast
import subprocess

class developer(commands.Cog):
    """Lithia.py Developer Module"""
    def __init__(self, client):
        self.client = client


    def insert_returns(self, body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)
        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)


    @commands.command(hidden=True, aliases=['eval', 'Eval', 'Eval_fn', 'sandbox'])
    @commands.is_owner()
    async def eval_fn(self, ctx, *, cmd):
        """Multi-line Evaluation Tool"""
        fn_name = "_eval_expr"
        cmd = cmd.strip("` ")
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
        body = f"async def {fn_name}():\n{cmd}"
        parsed = ast.parse(body)
        body = parsed.body[0].body
        self.insert_returns(body)
        env = {
            'client': self.client,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = (await eval(f"{fn_name}()", env))
        except Exception as e:
            await ctx.reply(f'`🔴{type(e).__name__}` - {e}')
        if result == None:
            return
        else:
            await ctx.reply(result)


    @commands.command(hidden=True, aliases=['CMD', 'term', 'cmd', "terminal"])
    @commands.is_owner()
    async def dterm(self, ctx, *, inputs):
        """Discord Terminal Access Tool"""
        try:
            result = subprocess.check_output(inputs.split())
        except Exception as e:
            await ctx.reply(f'`🔴{type(e).__name__}` - {e}')
            return
        await ctx.reply(file=File(fp=io.StringIO(result.decode('utf-8')), filename="terminal_output.log"))


    @commands.command(hidden=True)
    @commands.is_owner()
    async def m2f(self, ctx, message):
        try:
            await ctx.reply(file=File(fp=io.StringIO(message), filename="message.txt"))
        except Exception as e:
            await ctx.reply(f'`🔴{type(e).__name__}` - {e}')


    @commands.command(hidden=True)
    @commands.is_owner()
    async def probe(self, ctx, path):
        conts = str(os.listdir(path)).replace(",", "\n- ").replace("[", "\n-  ").replace("]", "")
        output = f"+ {path}{conts}"
        try:
            await ctx.reply(file=File(fp=io.StringIO(output), filename="probe.diff"))
        except Exception as e:
            await ctx.reply(f'`🔴{type(e).__name__}` - {e}')


def setup(client):
    client.add_cog(developer(client))