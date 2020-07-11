from discord.ext import commands
from cfg import bot

import cfg

def check_message(ctx):

    message = ctx.content

    if "rumpus" in message:
        update_rumpus_count(ctx, 1)


def update_rumpus_count(ctx, amount):
    cfg.db_cur.execute("UPDATE Users SET rumpus_count=rumpus_count+? WHERE uid=?;", (amount, str(ctx.author.id)))
    cfg.db_con.commit()


@bot.command(name="levelup")
async def levelup_rank(ctx):
    cfg.db_cur.execute("SELECT rank, rumpus_count FROM Users WHERE uid=?;", (str(ctx.author.id),))
    result = cfg.db_cur.fetchone()
    
    rank = result['rank']
    r_count = result['rumpus_count']

    if (rank + 1) >= len(cfg.config['ranks']):
        await ctx.channel.send(">>> You are already the highest rank! Congratulations!")
        return

    new_rank = cfg.config['ranks'][rank + 1]
    needed_to_upgrade = new_rank['count']

    if r_count >= needed_to_upgrade:
        upgrade_level(ctx, rank + 1)

        to_send = ">>> Wow! You've upgraded to the rank of **"
        to_send += new_rank['name']
        to_send += "**!"

        await ctx.channel.send(to_send)

    else:
        to_send = ">>> Sorry, you need `"
        to_send += str(needed_to_upgrade - r_count)
        to_send += "` more rumpuses to upgrade to the next level!"

        await ctx.channel.send(to_send)
        return


def upgrade_level(ctx, new_rank):
    cfg.db_cur.execute("UPDATE Users SET rank=? WHERE uid=?;", (new_rank, str(ctx.author.id)))
    cfg.db_con.commit()