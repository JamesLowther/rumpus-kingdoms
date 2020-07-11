from discord.ext import commands
from cfg import bot

import asyncio
import cfg, management, shared, kingdoms


@bot.command(name="village")
async def village_options(ctx, *args):

    # Check if user has a kingdom
    if not kingdoms.check_has_kingdom(ctx):
        await kingdoms.handle_no_kingdom(ctx)
        return

    if len(args) == 0:
        await show_village_help(ctx)
        return

    action = args[0].lower()

    if action == "list":
        await list_villages(ctx)

    elif action == "buy":
        if len(args) < 2:
            await ctx.channel.send(
                ">>> Use the command `"
                + cfg.PREFIX
                + "village buy <name>` to purchase a new village."
            )
            return

        await buy_village(ctx, args)

    elif action == "upgrade":
        if len(args) < 2:
            await ctx.channel.send(
                ">>> Use the command `"
                + cfg.PREFIX
                + "village upgrade <index>` to upgrade a village."
            )
            return

        await upgrade_village(ctx, args)

    elif action == "rename":
        if len(args) < 3:
            await ctx.channel.send(
                ">>> Use the command `"
                + cfg.PREFIX
                + "village rename <index> <name>` to rename a village."
            )
            return

        await rename_village(ctx, args)

    else:
        await show_village_help(ctx)


async def show_village_help(ctx):
    await ctx.channel.send(">>> " + get_village_help_string())


def get_village_help_string():
    to_send = "**Village Commands**\n```"
    to_send += (
        cfg.PREFIX
        + "village help                   :  Show available village commands\n"
    )
    to_send += (
        cfg.PREFIX + "village list                   :  List all of your villages\n"
    )
    to_send += (
        cfg.PREFIX
        + "village buy <name>             :  Buy a new village titled <name>\n"
    )
    to_send += (
        cfg.PREFIX
        + "village upgrade <index>        :  Increase the population of the village at <index>\n"
    )
    to_send += (
        cfg.PREFIX
        + "village rename <index> <name>  :  Rename village at <index> to <name>```"
    )

    return to_send


async def list_villages(ctx):
    cfg.db_cur.execute(
        "SELECT * FROM Villages v, Kingdoms k WHERE k.kid=v.kid AND k.uid=? ORDER BY v_name COLLATE NOCASE ASC, population DESC, vid ASC;",
        (str(ctx.author.id),),
    )

    results = cfg.db_cur.fetchall()

    if len(results) == 0:
        await ctx.channel.send(">>> You currently have no villages in your kingdom!")
        return

    to_send = ">>> "
    to_send += shared.create_table(
        "Villages", ["Name", "Population"], ["v_name", "population"], results, 0
    )

    await ctx.channel.send(to_send)


async def buy_village(ctx, args):
    village_name = " ".join(args[1:])
    village_price = calculate_village_price()

    if not shared.check_funds_available(ctx, village_price, 1):
        await ctx.channel.send(
            ">>> Sorry, you need at least `"
            + str(village_price)
            + "` doubloons to purchase a new village. Purchase cancelled."
        )
        return

    await ctx.channel.send(
        ">>> Are you sure you would like to buy the village called **"
        + village_name
        + "** for `"
        + str(village_price)
        + "` doubloons? (y/n)"
    )

    # Pre-condition check for wait_for function
    def check(msg):
        return msg.content.lower() in {"y", "n"} and msg.author.id == ctx.author.id

    try:
        msg = await bot.wait_for(
            "message", check=check, timeout=cfg.config["reply_timeout"]
        )

    except asyncio.TimeoutError:
        await ctx.channel.send(">>> You took too long to reply! Command cancelled.")
        return

    # User cancelled the kingdom creation
    if msg.content.lower() == "n":
        await ctx.channel.send(">>> Village purchase cancelled!")
        return

    # Remove price from user's doubloon balance
    shared.detract_funds(ctx, village_price)

    # Get user's kingdom kid
    cfg.db_cur.execute(
        "SELECT k.kid FROM Kingdoms k, Users u WHERE u.uid=k.uid AND u.uid=?;",
        (str(ctx.author.id),),
    )

    result = cfg.db_cur.fetchone()
    kid = result["kid"]

    # Add new village to database

    new_id = management.unique_ID("Villages", "vid")

    cfg.db_cur.execute(
        "INSERT INTO Villages VALUES (?, ?, 100, ?)", (new_id, village_name, kid)
    )

    cfg.db_con.commit()

    await ctx.channel.send(
        ">>> Purchased **"
        + str(village_name)
        + "** for `"
        + str(village_price)
        + "` doubloons."
    )


async def upgrade_village(ctx, args):
    cfg.db_cur.execute(
        "SELECT * FROM Villages v, Kingdoms k WHERE k.kid=v.kid AND k.uid=? ORDER BY v_name COLLATE NOCASE ASC, population DESC, vid ASC;",
        (str(ctx.author.id),),
    )

    results = cfg.db_cur.fetchall()

    # If index is not valid
    if not args[1].isnumeric() or int(args[1]) < 1 or int(args[1]) > len(results):
        to_send = ">>> "
        to_send += "Index out of range!"
        await ctx.channel.send(to_send)

        return

    target_village = results[int(args[1]) - 1]
    upgrade_price = calculate_upgrade_price(target_village)
    pop_increase = calculate_population_increase()

    if not shared.check_funds_available(ctx, upgrade_price, 1):
        await ctx.channel.send(
            ">>> Sorry, you need at least `"
            + str(upgrade_price)
            + "` doubloons to upgrade this village. Upgrade cancelled."
        )
        return

    await ctx.channel.send(
        ">>> Are you sure you would like to upgrade **"
        + str(target_village["v_name"])
        + "** and boost its population by `"
        + str(pop_increase)
        + "` Rumplins for `"
        + str(upgrade_price)
        + "` doubloon(s)? (y/n)"
    )

    # Pre-condition check for wait_for function
    def check(msg):
        return msg.content.lower() in {"y", "n"} and msg.author.id == ctx.author.id

    try:
        msg = await bot.wait_for(
            "message", check=check, timeout=cfg.config["reply_timeout"]
        )

    except asyncio.TimeoutError:
        await ctx.channel.send(">>> You took too long to reply! Command cancelled.")
        return

    # User cancelled the kingdom creation
    if msg.content.lower() == "n":
        await ctx.channel.send(">>> Village upgrade cancelled!")
        return

    # Update village name in database
    cfg.db_cur.execute(
        "UPDATE Villages SET population=population + ? WHERE vid=?;",
        (pop_increase, str(target_village["vid"])),
    )

    cfg.db_con.commit()

    await ctx.channel.send("Village successfully upgraded!")


async def rename_village(ctx, args):
    cfg.db_cur.execute(
        "SELECT * FROM Villages v, Kingdoms k WHERE k.kid=v.kid AND k.uid=? ORDER BY v_name COLLATE NOCASE ASC, population DESC, vid ASC;",
        (str(ctx.author.id),),
    )

    results = cfg.db_cur.fetchall()

    # If index is not valid
    if not args[1].isnumeric() or int(args[1]) < 1 or int(args[1]) > len(results):
        to_send = ">>> "
        to_send += "Index out of range!"
        await ctx.channel.send(to_send)

        return

    target_village = results[int(args[1]) - 1]
    new_name = " ".join(args[2:])

    await ctx.channel.send(
        ">>> Are you sure you would like to rename **"
        + str(target_village["v_name"])
        + "** to **"
        + str(new_name)
        + "**? (y/n)"
    )

    # Pre-condition check for wait_for function
    def check(msg):
        return msg.content.lower() in {"y", "n"} and msg.author.id == ctx.author.id

    try:
        msg = await bot.wait_for(
            "message", check=check, timeout=cfg.config["reply_timeout"]
        )

    except asyncio.TimeoutError:
        await ctx.channel.send(">>> You took too long to reply! Command cancelled.")
        return

    # User cancelled the kingdom creation
    if msg.content.lower() == "n":
        await ctx.channel.send(">>> Village rename cancelled!")
        return

    # Update village name in database
    cfg.db_cur.execute(
        "UPDATE Villages SET v_name=? WHERE vid=?;",
        (new_name, str(target_village["vid"])),
    )

    cfg.db_con.commit()

    await ctx.channel.send(">>> Village successfully renamed!")


def calculate_village_price():
    return 0


def calculate_upgrade_price(village):
    return 0


def calculate_population_increase():
    return 1000
