from discord.ext import commands
from cfg import bot

import cfg


@bot.command(name="village"):
async def village_options(ctx, *args):
    if len(args) == 0:
        show_village_help(ctx)
        return

    action = args[0].lower()

    if action == "list":

    else if action == "buy":
        if len(args) < 2:
            await ctx.channel.send("Use the command `" + cfg.PREFIX + "buy <name>` to purchase a new village.")
            return

    else if action == "upgrade":
        if len(args) < 2:
            await ctx.channel.send("Use the command `" + cfg.PREFIX + "upgrade <index>` to upgrade a village.")
            return

    else if action == "rename":
        if len(args) < 2:
            await ctx.channel.send("Use the command `" + cfg.PREFIX + "rename <index> <name>` to rename a village.")
            return
    else:
        show_village_help(ctx)


async def show_village_help(ctx):
    pass


async def list_villages(ctx):
    
    cfg.db_cur.execute("SELECT * FROM Villages v, Kingdoms k WHERE ")


async def buy_village(ctx, args):
    pass


async def upgrade_village(ctx, args):
    pass


async def rename_village(ctx, args):
    pass