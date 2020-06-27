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


@bot.command(name="purchase")
async def buy_troops(ctx, *args):
    # User doesn't have a kingdom
    if not check_has_kingdom(ctx):
        await handle_no_kingdom(ctx)
        return

    # Show purchase options
    if len(args) == 0:
        await show_purchase_options(ctx)
        return


# Displays all purchasable units
# todo: this code is messy
async def show_purchase_options(ctx):

    # Generate string of categories
    to_send = ">>> "
    to_send += create_table(
        "Attack Units",
        ["Name", "Price", "Attack"],
        ["name", "price", "attack"],
        cfg.attack_options,
        0,
    )
    to_send += "\n"
    to_send += create_table(
        "Defence Units",
        ["Name", "Price", "Defence"],
        ["name", "price", "defence"],
        cfg.defence_options,
        len(cfg.attack_options),
    )
    to_send += "\nEnter the index of the unit you would like to purchase, or type 'cancel' to exit."

    await ctx.channel.send(to_send)

    # Pre-condition check for wait_for function
    def check(msg):
        return (
            msg.content.lower() in {"cancel"} or msg.content.isnumeric()
        ) and msg.author.id == ctx.author.id

    # Continue until valid index is entered
    while True:
        msg = await bot.wait_for("message", check=check)

        # User cancelled the unit purchase
        if msg.content.lower() == "cancel":
            await ctx.channel.send("Unit purchase cancelled!")
            return

        index = int(msg.content) - 1

        # Check if index is valid
        if (
            index >= 0
            and index <= len(cfg.attack_options) + len(cfg.defence_options) - 1
        ):
            break

        await ctx.channel.send("Index out of range!")

    number_attack_units = len(cfg.attack_options)

    # Purchase attack unit
    if index > number_attack_units - 1:
        to_purchase = cfg.defence_options[index - number_attack_units]

        if not check_funds_available(ctx, to_purchase['price']):
            await ctx.channel.send(">>> Sorry, you don't have enough doubloons to purchase that defence unit. Purchase cancelled.")
            return

        purchased = purchase_defence_unit(ctx, to_purchase)

    # Purchase defence unit
    else:
        to_purchase = cfg.attack_options[index]

        if not check_funds_available(ctx, to_purchase['price']):
            await ctx.channel.send(">>> Sorry, you don't have enough doubloons to purchase that attack unit. Purchase cancelled.")
            return

        purchased = purchase_attack_unit(ctx, to_purchase)

    await ctx.channel.send(
        ">>> Purchased unit '"
        + str(purchased["name"])
        + "' for `"
        + str(purchased["price"])
        + "` doubloons."
    )


# Creates a table from the data in a discord markup string
# headers and key lists must be the same length
def create_table(category, headers, keys, data, offset):
    assert len(headers) == len(keys)

    # Category
    to_send = "**" + category + "**\n"

    # Get header sizes
    header_size = []

    for i in range(len(keys)):
        key_size = 0
        for element in data:
            key_size = max(key_size, len(str(element[keys[i]])))
        header_size.append(max(key_size, len(headers[i])))

    to_send += "```"

    # Headers
    headers_to_send = "Index | "

    for i in range(len(headers)):
        headers_to_send += str(headers[i]).ljust(header_size[i])
        headers_to_send += " | "
    headers_to_send = headers_to_send[:-3] + "\n"

    to_send += headers_to_send
    to_send += "-" * len(headers_to_send)
    to_send += "\n"

    # Data
    for i in range(len(data)):
        to_send += f"{i+1+offset:02d}".ljust(5) + " | "
        for j in range(len(keys)):
            to_send += str(data[i][keys[j]]).ljust(header_size[j])
            to_send += " | "
        to_send = to_send[:-3] + "\n"

    to_send += "```"

    return to_send


# Check if a user can afford a certain price
def check_funds_available(ctx, price):
    cfg.db_cur.execute("SELECT doubloons FROM Users WHERE uid=?;", (ctx.author.id,))
    result = cfg.db_cur.fetchone()

    return result['doubloons'] >= price


# Purchase an attack unit
# Returns the purchased unit
def purchase_attack_unit(ctx, to_purchase):
    cfg.db_cur.execute(
        "UPDATE Kingdoms SET attack=attack + ? WHERE uid=?;",
        (to_purchase['attack'], str(ctx.author.id)),
    )

    cfg.db_cur.execute("UPDATE Users SET doubloons=doubloons - ? WHERE uid=?",
        (to_purchase['price'], str(ctx.author.id))
    )
    
    cfg.db_conn.commit()

    return to_purchase


# Purchase a defence unit
# Returns the purchased unit
def purchase_defence_unit(ctx, to_purchase):
    cfg.db_cur.execute(
        "UPDATE Kingdoms SET defence=defence + ? WHERE uid=?;",
        (to_purchase["defence"], str(ctx.author.id)),
    )

    cfg.db_cur.execute("UPDATE Users SET doubloons=doubloons - ? WHERE uid=?",
        (to_purchase['price'], str(ctx.author.id))
    )

    cfg.db_conn.commit()

    return to_purchase
