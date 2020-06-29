from discord.ext import commands
from cfg import bot
import cfg, management, shared


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

    kingdom_name = args[0].capitalize()

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


# Called if a user does not have a kingdom but should
async def handle_no_kingdom(ctx):
    await ctx.channel.send(
        "Please use the command: `"
        + cfg.PREFIX
        + "init <kingdom name>` to create a new kingdom."
    )


# Called if a user already has a kingdom but shouldn't
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

    new_name = args[0].capitalize()

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


# Command to purchase new units
@bot.command(name="purchase")
async def buy_troops(ctx, *args):
    # User doesn't have a kingdom
    if not check_has_kingdom(ctx):
        await handle_no_kingdom(ctx)
        return

    # Show purchase options
    if len(args) == 0 or not args[0].isnumeric():
        await show_purchase_options(ctx)
        return

    index = int(args[0]) - 1

    # Check if index is valid
    if not (
        index >= 0
        and index <= len(cfg.attack_options) + len(cfg.defence_options) - 1
    ):
        await ctx.channel.send("Index out of range! Cancelling.")
        return

    # Check if amount is valid
    if len(args) == 2 and args[1].isnumeric() and int(args[1]) > 0:
        amount_to_purchase = int(args[1])
    else:
        amount_to_purchase = 1

    number_attack_units = len(cfg.attack_options)

    # Purchase attack unit
    if index > number_attack_units - 1:
        to_purchase = cfg.defence_options[index - number_attack_units]
        total_price = to_purchase['price'] * amount_to_purchase

        if not shared.check_funds_available(ctx, to_purchase['price'], amount_to_purchase):
            await ctx.channel.send(
                ">>> Sorry, you need at least `"
                + str(total_price)
                + "` doubloons to purchase those defence units. Purchase cancelled."
            )
            return

        purchased = await purchase_defence_unit(ctx, to_purchase, amount_to_purchase)

    # Purchase defence unit
    else:
        to_purchase = cfg.attack_options[index]
        total_price = to_purchase['price'] * amount_to_purchase

        if not shared.check_funds_available(ctx, to_purchase['price'], amount_to_purchase):
            await ctx.channel.send(
                ">>> Sorry, you need at least `"
                + str(total_price)
                + "` doubloons to purchase those attack units. Purchase cancelled."
            )         
            return

        purchased = await purchase_attack_unit(ctx, to_purchase, amount_to_purchase)

    # Purchase was cancelled
    if purchased == None:
        return

    await ctx.channel.send(
        ">>> Purchased "
        + str(amount_to_purchase)
        + " '"
        + str(purchased["name"])
        + "' unit(s) for `"
        + str(total_price)
        + "` doubloons."
    )


# Displays all purchasable units
# todo: this code is messy
async def show_purchase_options(ctx):
    # Generate string of categories
    to_send = ">>> "
    to_send += shared.create_table(
        "Attack Units",
        ["Name", "Price", "Attack"],
        ["name", "price", "attack"],
        cfg.attack_options,
        0,
    )
    to_send += "\n"
    to_send += shared.create_table(
        "Defence Units",
        ["Name", "Price", "Defence"],
        ["name", "price", "defence"],
        cfg.defence_options,
        len(cfg.attack_options),
    )
    to_send += "\nUse the command `" + cfg.PREFIX + "purchase <index> [amount]` to purchase units."

    await ctx.channel.send(to_send)


# Purchase an attack unit
# Returns the purchased unit
async def purchase_attack_unit(ctx, to_purchase, amount):
    total_price = to_purchase['price'] * amount

    # Pre-condition check for wait_for function
    def check(msg):
        return msg.content.lower() in {"y", "n"} and msg.author.id == ctx.author.id

    await ctx.channel.send(
        ">>> Are you sure you would like to purchase "
        + str(amount)
        + " '"
        + str(to_purchase['name'])
        + "' for `"
        + str(total_price)
        + str("` doubloon(s)? (y/n)")
    )

    msg = await bot.wait_for("message", check=check)

    # User cancelled the purchase
    if msg.content.lower() == "n":
        await ctx.channel.send(">>> Purchase cancelled!")
        return

    # Remove price from user's doubloon balance
    shared.detract_funds(ctx, to_purchase['price'] * amount,)

    # Add attack value to kingdom
    cfg.db_cur.execute(
        "UPDATE Kingdoms SET attack=attack + ? WHERE uid=?;",
        (to_purchase['attack'] * amount, str(ctx.author.id)),
    )
    
    cfg.db_conn.commit()

    return to_purchase


# Purchase a defence unit
# Returns the purchased unit
async def purchase_defence_unit(ctx, to_purchase, amount):
    total_price = to_purchase['price'] * amount

    # Pre-condition check for wait_for function
    def check(msg):
        return msg.content.lower() in {"y", "n"} and msg.author.id == ctx.author.id

    await ctx.channel.send(
        ">>> Are you sure you would like to purchase "
        + str(amount)
        + " '"
        + str(to_purchase['name'])
        + "' for `"
        + str(total_price)
        + str("` doubloon(s)? (y/n)")
    )

    msg = await bot.wait_for("message", check=check)

    # User cancelled the purchase
    if msg.content.lower() == "n":
        await ctx.channel.send(">>> Purchase cancelled!")
        return

    # Remove price from user's doubloon balance
    shared.detract_funds(ctx, to_purchase['price'] * amount)
    
    # Add defence value to kingdom
    cfg.db_cur.execute(
        "UPDATE Kingdoms SET defence=defence + ? WHERE uid=?;",
        (to_purchase["defence"] * amount, str(ctx.author.id)),
    )

    cfg.db_conn.commit()

    return to_purchase
