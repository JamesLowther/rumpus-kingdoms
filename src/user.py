from discord.ext import commands
from cfg import bot
import cfg, kingdoms

# Displays the number of doubloons that you have
@bot.command(name="info")
async def display_user_info(ctx):

    cfg.db_cur.execute(
        "SELECT k.k_name, u.doubloons, u.rank FROM Users u, Kingdoms k WHERE u.uid=k.uid AND u.uid=?;",
        (str(ctx.author.id),),
    )

    result = cfg.db_cur.fetchone()

    if result:
        to_send = ">>> **" + str(ctx.author) + " of " + str(result["k_name"]) + "**\n\n"
        to_send += "**Rank:** `" + str(result["rank"]) + "`\n"
        to_send += "**Doubloons:** `" + str(result["doubloons"]) + "`"

        await ctx.channel.send(to_send)

    else:
        await kingdoms.handle_no_kingdom(ctx)
