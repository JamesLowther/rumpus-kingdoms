from discord.ext import commands
from cfg import bot
import cfg, management


# Create a new kingdom for the user
@bot.command(name="init")
async def init_kingdom(ctx, *args):
    cfg.db_cur.execute("SELECT * FROM Kingdoms WHERE uid=?;", (str(ctx.author.id),))

    # User already has a kingdom
    if cfg.db_cur.fetchone():
        await ctx.channel.send("You already have a kingdom " + str(ctx.author) + "!")
        return

    # Incorrect number of arguments
    if len(args) == 0:
        await ctx.channel.send("Please use the command: `$rumpus init <kingdom name>` to create a new kingdom.")
        return

    kingdom_name = args[0]

    await ctx.channel.send("Are you sure you would like to name your kingdom " + kingdom_name + "? (y/n)")

    def check(msg):
        return msg.content.lower() in {"y", "n"}

    msg = await bot.wait_for('message', check=check)

    if (msg.content.lower() == "y"):
        create_kingdom(ctx, kingdom_name)

        await ctx.channel.send("Kingdom " + kingdom_name + " created!")


# Insert the kingdom into the database
def create_kingdom(ctx, kingdom_name):
    new_id = management.unique_ID("Kingdoms", "kid")

    cfg.db_cur.execute("INSERT INTO Kingdoms VALUES (?, ?, 0, 0, '', ?);", (new_id, kingdom_name, str(ctx.author.id)))

    cfg.db_conn.commit()
    