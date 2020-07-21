from discord.ext import commands
from cfg import bot

import cfg, currency, management

def check_message(ctx):

    message = ctx.content.lower()

    if "rumpus" in message:
        update_rumpus_count(ctx, 1)
        currency.add_doubloons(ctx, 1)


def update_rumpus_count(ctx, amount):
    cfg.db_cur.execute("UPDATE Users SET rumpus_count=rumpus_count+? WHERE uid=?;", (amount, str(ctx.author.id)))
    cfg.db_con.commit()


@bot.command(name="levelup")
async def levelup_rank(ctx):
    # Check if session exists
    if await management.check_session_exists(ctx):
        return
    
    else:
        management.add_session(ctx)

    cfg.db_cur.execute("SELECT rank, rumpus_count FROM Users WHERE uid=?;", (str(ctx.author.id),))
    result = cfg.db_cur.fetchone()
    
    rank = result['rank']
    r_count = result['rumpus_count']

    if (rank + 1) >= len(cfg.config['ranks']):
        await ctx.channel.send(">>> You are already the highest rank! Congratulations!")
        
        management.remove_session(ctx)
        return

    new_rank = cfg.config['ranks'][rank + 1]
    needed_to_upgrade = new_rank['count']

    if r_count >= needed_to_upgrade:
        upgrade_level(ctx, rank + 1)
        currency.add_doubloons(ctx, new_rank['reward'])

        to_send = ">>> Wow! You've upgraded to the rank of **"
        to_send += new_rank['name']
        to_send += "**! You've been awarded `"
        to_send += str(new_rank['reward'])
        to_send += "` doubloons!"

        await ctx.channel.send(to_send)

    else:
        to_send = ">>> Sorry, you need `"
        to_send += str(needed_to_upgrade - r_count)
        to_send += "` more rumpuses to upgrade to the next level!"

        await ctx.channel.send(to_send)

        management.remove_session(ctx)
        return

    management.remove_session(ctx)


def upgrade_level(ctx, new_rank):
    cfg.db_cur.execute("UPDATE Users SET rank=? WHERE uid=?;", (new_rank, str(ctx.author.id)))
    cfg.db_con.commit()


def get_user_level(ctx):
    cfg.db_cur.execute("SELECT rank FROM Users WHERE uid=?;", (str(ctx.author.id),))
    result = cfg.db_cur.fetchone()

    return result['rank']