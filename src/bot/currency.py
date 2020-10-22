from discord.ext import commands
from cfg import bot

from random import uniform, choice
from time import time, strftime, gmtime
import cfg, kingdoms, management


# Collect tax from village population
@bot.command(name="collect")
async def collect_tax(ctx):
    # Check if session exists
    if await management.check_session_exists(ctx):
        return

    else:
        management.add_session(ctx)

    # Check if user has a kingdom
    if not kingdoms.check_has_kingdom(ctx):
        await kingdoms.handle_no_kingdom(ctx)
        management.remove_session(ctx)
        return

    # Check if user has already collected tax
    if check_tax_collected_today(ctx):
        to_send = ">>> "
        to_send += "You already collected tax today! You can collect tax again in **"
        to_send += get_collect_time_remaining(ctx)
        to_send += "**!"

        await ctx.channel.send(to_send)

        management.remove_session(ctx)
        return

    # Count the total population of a kingdom
    cfg.db_cur.execute(
        "SELECT SUM(v.population) as total_pop, COUNT(v.vid) as num_villages FROM Villages v, Kingdoms k WHERE v.kid=k.kid AND k.uid=?;",
        (str(ctx.author.id),),
    )
    result = cfg.db_cur.fetchone()

    if result["num_villages"] == 0:
        await ctx.channel.send(
            ">>> You need to have at least one village before you can collect taxes!"
        )
        management.remove_session(ctx)
        return

    total_pop = result["total_pop"]
    tax_collected = calculate_tax_amount(total_pop)
    num_villages = result["num_villages"]

    add_doubloons(ctx, tax_collected)
    update_tax_collected(ctx)

    await send_tax_collected_message(ctx, tax_collected, num_villages, total_pop)

    management.remove_session(ctx)


@bot.command(name="tax_rate")
async def show_tax_rate(ctx):
    # Check if session exists
    if await management.check_session_exists(ctx):
        return

    else:
        management.add_session(ctx)

    tax_rate = get_tax_rate()

    to_send = ">>> "
    to_send += "The current tax rate for today is `" + str(tax_rate)
    to_send += "` doubloons per Rumplin."

    await ctx.channel.send(to_send)

    management.remove_session(ctx)


# Returns true if tax collection flag is set
def check_tax_collected_today(ctx):
    cfg.db_cur.execute("SELECT tax_collected FROM Users WHERE uid=?;", (ctx.author.id,))
    prev_time = cfg.db_cur.fetchone()["tax_collected"]
    delta_time = int(time()) - prev_time

    return delta_time < cfg.config["collect_timeout"]


def get_collect_time_remaining(ctx):

    cfg.db_cur.execute("SELECT tax_collected FROM Users WHERE uid=?;", (ctx.author.id,))
    prev_time = cfg.db_cur.fetchone()["tax_collected"]
    delta_time = int(time()) - prev_time

    remaining_time = cfg.config["collect_timeout"] - delta_time

    remaining_time_string = strftime(
        "%H hour(s), %M minute(s), and %S second(s)", gmtime(remaining_time)
    )
    return remaining_time_string


# Sets the tax collected to a new value
def update_tax_collected(ctx):

    cfg.db_cur.execute(
        "UPDATE Users SET tax_collected=? WHERE uid=?;", (int(time()), ctx.author.id)
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
    to_send += "` villages! You can collect tax again in **"
    to_send += get_collect_time_remaining(ctx)
    to_send += "**!"

    await ctx.channel.send(to_send)


def get_tax_help_string():
    to_send = "**Taxation Commands** ```"
    to_send += (
        cfg.PREFIX + "tax_rate                       :  Show the current tax rate\n"
    )
    to_send += (
        cfg.PREFIX
        + "collect                        :  Collect taxes from your kingdom```"
    )

    return to_send
