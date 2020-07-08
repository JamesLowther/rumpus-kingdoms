from discord.ext import commands
from cfg import bot

from random import uniform, choice
import cfg, kingdoms


# Collect tax from village population
@bot.command(name="collect")
async def collect_tax(ctx):
    # Check if user has a kingdom
    if not kingdoms.check_has_kingdom(ctx):
        await kingdoms.handle_no_kingdom(ctx)
        return

    # Check if user has already collected tax
    if check_tax_collected_today(ctx):
        to_send = ">>> "
        to_send += "You already collected tax today! Please try again tomorrow!"

        await ctx.channel.send(to_send)
        return

    # Count the total population of a kingdom
    cfg.db_cur.execute(
        "SELECT SUM(v.population) as total_pop, COUNT(v.vid) as num_villages FROM Villages v, Kingdoms k WHERE v.kid=k.kid AND k.uid=?;",
        (str(ctx.author.id),),
    )
    result = cfg.db_cur.fetchone()

    total_pop = result["total_pop"]
    tax_collected = calculate_tax_amount(total_pop)
    num_villages = result["num_villages"]

    add_doubloons(ctx, tax_collected)
    set_tax_collected_flag(ctx, 1)

    await send_tax_collected_message(ctx, tax_collected, num_villages, total_pop)


@bot.command(name="tax_rate")
async def show_tax_rate(ctx):
    tax_rate = get_tax_rate()

    to_send = ">>> "
    to_send += "The current tax rate for today is `" + str(tax_rate)
    to_send += "` doubloons per Rumplin."

    await ctx.channel.send(to_send)


# Returns true if tax collection flag is set
def check_tax_collected_today(ctx):
    cfg.db_cur.execute("SELECT tax_collected FROM Users WHERE uid=?;", (ctx.author.id,))
    result = cfg.db_cur.fetchone()

    return result["tax_collected"]


# Sets the tax collected to a new value
def set_tax_collected_flag(ctx, value):
    assert value in {0, 1}

    cfg.db_cur.execute(
        "UPDATE Users SET tax_collected=? WHERE uid=?;", (value, ctx.author.id)
    )
    cfg.db_con.commit()


# Return the amount made in taxes
def calculate_tax_amount(total_pop):
    return int(total_pop * get_tax_rate())


# Get the tax rate from the database
def get_tax_rate():
    cfg.db_cur.execute("SELECT value FROM Variables WHERE name='tax_rate';")
    result = cfg.db_cur.fetchone()

    return result["value"]


# Calculate the new tax rate
# Commit new rate to database
def calculate_new_tax_rate():
    tax_base = cfg.config["tax_base"]
    tax_change = cfg.config["tax_change"]

    # Calculate change (+/-)
    random_change = round(uniform(0, tax_change), 2)
    random_change *= choice([-1, 1])

    new_tax_rate = tax_base + random_change

    # Commit to database
    cfg.db_cur.execute(
        "UPDATE Variables SET value=? WHERE name='tax_rate';", (new_tax_rate,)
    )
    cfg.db_con.commit()


# Reset the tax_collected flag for all users
def reset_tax_collected_flag():
    cfg.db_cur.execute("UPDATE Users SET tax_collected=0;")
    cfg.db_con.commit()


# Add doubloons to a user's balance
def add_doubloons(ctx, to_add):
    cfg.db_cur.execute(
        "UPDATE Users SET doubloons=doubloons+? WHERE uid=?;", (to_add, ctx.author.id)
    )
    cfg.db_con.commit()


# Send the message about how much tax is collected
async def send_tax_collected_message(ctx, tax_collected, num_villages, total_pop):
    to_send = ">>> "
    to_send += "You collected `" + str(tax_collected)
    to_send += "` doubloons from `" + str(total_pop)
    to_send += "` Rumplins in `" + str(num_villages)
    to_send += "` villages! Don't forget to collect tax again tomorrow!"

    await ctx.channel.send(to_send)
