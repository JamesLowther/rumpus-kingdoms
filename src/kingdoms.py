from discord.ext import commands
from cfg import bot
import cfg, management


# Create a new kingdom for the user
@bot.command(name="init")
async def init_kingdom(ctx, *args):
    # User already has a kingdom
    if check_has_kingdom(ctx):
        await handle_existing_kingdom(ctx)
        return

    # Incorrect number of arguments
    if len(args) == 0:
        await handle_no_kingdom(ctx)
        return

    kingdom_name = args[0]

    await ctx.channel.send(
        "Are you sure you would like to name your kingdom '" + kingdom_name + "'? (y/n)"
    )

    # Pre-condition check for wait_for function
    def check(msg):
        return msg.content.lower() in {"y", "n"} and msg.author.id == ctx.author.id

    msg = await bot.wait_for("message", check=check)

    # User cancelled the kingdom creation
    if msg.content.lower() == "n":
        await ctx.channel.send("Kingdom creation cancelled!")
        return

    create_kingdom(ctx, kingdom_name)

    await ctx.channel.send("Kingdom '" + kingdom_name + "' created!")


# Insert the kingdom into the database
def create_kingdom(ctx, kingdom_name):
    new_id = management.unique_ID("Kingdoms", "kid")
    cfg.db_cur.execute(
        "INSERT INTO Kingdoms VALUES (?, ?, 0, 0, '', ?);",
        (new_id, kingdom_name, str(ctx.author.id)),
    )
    cfg.db_conn.commit()


async def handle_no_kingdom(ctx):
    await ctx.channel.send(
        "Please use the command: `"
        + cfg.PREFIX
        + "init <kingdom name>` to create a new kingdom."
    )


async def handle_existing_kingdom(ctx):
    await ctx.channel.send("You already have a kingdom " + str(ctx.author) + "!")


# Return if a user already has a kingdom
def check_has_kingdom(ctx):
    cfg.db_cur.execute("SELECT * FROM Kingdoms WHERE uid=?;", (str(ctx.author.id),))
    return cfg.db_cur.fetchone() != None


# Rename your kingdom
@bot.command(name="rename")
async def rename_kingdom(ctx, *args):
    # User doesn't have a kingdom
    if not check_has_kingdom(ctx):
        await handle_no_kingdom(ctx)
        return

    if len(args) == 0:
        await ctx.channel.send(
            "Please use the commnd: `"
            + cfg.PREFIX
            + "rename <new name>` to rename your kingdom."
        )
        return

    new_name = args[0]

    await ctx.channel.send(
        "Are you sure you would like to name your kingdom '" + new_name + "'? (y/n)"
    )

    # Pre-condition check for wait_for function
    def check(msg):
        return msg.content.lower() in {"y", "n"} and msg.author.id == ctx.author.id

    msg = await bot.wait_for("message", check=check)

    # User cancelled the kingdom creation
    if msg.content.lower() == "n":
        await ctx.channel.send("Kingdom rename cancelled!")
        return

    cfg.db_cur.execute(
        "UPDATE Kingdoms SET k_name=? WHERE uid=?;", (new_name, str(ctx.author.id))
    )
    cfg.db_conn.commit()

    await ctx.channel.send("Kingdom renamed to '" + new_name + "'.")
