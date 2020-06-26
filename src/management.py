from discord.ext import commands
from cfg import bot
from random import randint

import cfg



# Shuts down the bot and closes any open connections
# Only users with root access can use this command
@bot.command(name="shutdown")
async def shutdown(ctx):
    print(str(ctx.author.id) + " (" + str(ctx.author) + ") called for shutdown")

    if check_root(ctx.author.id):
        cfg.db_conn.close()

        await ctx.channel.send("The rumpus room remains unguarded. Tread carefully.")
        await bot.logout()

    else:
        await ctx.channel.send("Sorry! You don't have permission to do that!")


# Checks if the id is in the ROOT_IDS list
def check_root(user_id):
    return user_id in cfg.root_ids


# Create the user in the database
def create_user(ctx):
    cfg.db_cur.execute(
        "INSERT INTO Users VALUES (?, 0, '', 'Serf', NULL);", (str(ctx.author.id),)
    )
    cfg.db_conn.commit()


# Generate a random ID for a table
def unique_ID(table, column):
    while True:
        new_id = randint(100000,999999)

        cfg.db_cur.execute("SELECT * FROM " + table + "  WHERE ?=?;", (column, new_id))

        if not cfg.db_cur.fetchone():
            break

    return new_id