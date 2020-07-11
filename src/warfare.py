from discord.ext import commands
from cfg import bot

import asyncio
import cfg, shared, kingdoms


@bot.command(name="players")
async def list_players(ctx):
    all_kingdoms = get_all_kingdoms()

    converted_all_kingdoms = shared.convert_id_to_name_key(
        all_kingdoms, "uid", "username"
    )

    kingdom_table = shared.create_table(
        "Kingdoms",
        ["Name", "Kingdom", "# Villages", "Has Attacked Today", "Been Attacked Today"],
        ["username", "k_name", "count", "has_attacked", "been_attacked"],
        converted_all_kingdoms,
        0,
        False,
    )

    await ctx.channel.send(">>> " + kingdom_table)


# Returns all kingdoms
# uid, k_name, number of villages
def get_all_kingdoms():
    # cfg.db_cur.execute("SELECT k.uid, k.k_name, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid;")
    cfg.db_cur.execute(
        "SELECT k.uid, k.been_attacked, k.has_attacked, k.k_name, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid;"
    )
    return cfg.db_cur.fetchall()


# Returns all kingdoms
# uid, k_name, number of villages
def get_all_non_attacked_kingdoms(ctx):
    cfg.db_cur.execute(
        "SELECT *, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid WHERE k.been_attacked != 1 AND k.uid != ? AND s.count > 0;",
        (str(ctx.author.id),),
    )
    # cfg.db_cur.execute(
    #    "SELECT *, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid WHERE k.been_attacked != 1 AND s.count > 0;",
    # )
    return cfg.db_cur.fetchall()


@bot.command(name="attack")
async def attack_user(ctx):

    # Check if user has a kingdom
    if not kingdoms.check_has_kingdom(ctx):
        await kingdoms.handle_no_kingdom(ctx)
        return

    if not await check_attack_prereqs(ctx):
        return

    all_kingdoms = get_all_non_attacked_kingdoms(ctx)
    converted_all_kingdoms = shared.convert_id_to_name_key(
        all_kingdoms, "uid", "username"
    )

    if len(all_kingdoms) == 0:
        await ctx.channel.send(">>> There are currently no kingdoms that can be attacked!")
        return

    attacked_kingdom = await choose_kingdom_to_attack(ctx, converted_all_kingdoms)
    if not attacked_kingdom:
        return

    number_attack_units = await choose_number_attack_units(ctx)
    if not number_attack_units:
        return

    attacked_kingdom_units = get_number_units(str(attacked_kingdom["uid"]))

    if number_attack_units > attacked_kingdom_units["defence"]:
        await handle_successful_attack(ctx, attacked_kingdom, number_attack_units)

    else:
        await handle_failed_attack(ctx, attacked_kingdom, number_attack_units)


async def check_attack_prereqs(ctx):
    if not get_village_count(ctx) > 0:
        await ctx.channel.send(
            ">>> You need to have at least one village to attack another user!"
        )
        return False

    if not get_number_units(str(ctx.author.id))["attack"] > 0:
        await ctx.channel.send(
            ">>> You need to have at least one attack unit to attack another user!"
        )
        return False

    if get_has_attacked(ctx) == 1:
        await ctx.channel.send(
            ">>> You have already attacked another kingdom today! Please wait until tomorrow!"
        )
        return False

    return True


def get_number_units(uid):
    cfg.db_cur.execute(
        "SELECT k.attack, k.defence FROM Users u, Kingdoms k WHERE u.uid=k.uid AND u.uid=?;",
        (uid,),
    )
    return cfg.db_cur.fetchone()


def get_village_count(ctx):
    cfg.db_cur.execute(
        "SELECT COUNT(v.vid) as count FROM Kingdoms k LEFT JOIN Villages v on k.kid=v.kid WHERE k.uid=? GROUP BY k.uid;",
        (str(ctx.author.id),),
    )
    return cfg.db_cur.fetchone()["count"]


def get_has_attacked(ctx):
    cfg.db_cur.execute(
        "SELECT k.has_attacked FROM Users u, Kingdoms k WHERE u.uid=k.uid AND u.uid=?;",
        (str(ctx.author.id),),
    )
    return cfg.db_cur.fetchone()["has_attacked"]


async def choose_kingdom_to_attack(ctx, all_kingdoms):
    to_send = ">>> "
    to_send += shared.create_table(
        "Kingdoms",
        ["Name", "Kingdom", "# Villages"],
        ["username", "k_name", "count"],
        all_kingdoms,
        0,
    )
    to_send += "\nPlease select the index of the kingdom you want to attack or type 'cancel' to stop the attack"

    await ctx.channel.send(to_send)

    # Pre-condition check for wait_for function
    def check(msg):
        return (
            msg.content.isnumeric() or msg.content.lower() in {"cancel"}
        ) and msg.author.id == ctx.author.id

    try:
        msg = await bot.wait_for(
            "message", check=check, timeout=cfg.config["wait_timeout"]
        )

    except asyncio.TimeoutError:
        await ctx.channel.send(">>> You took too long to reply! Command cancelled.")
        return

    if msg.content.lower() == "cancel":
        await ctx.channel.send(">>> Attack cancelled!")
        return False

    index_range = len(all_kingdoms)
    index = int(msg.content)

    if index <= 0 or index > index_range:
        await ctx.channel.send(">>> Index out of range! Cancelling attack!")
        return False

    return all_kingdoms[index - 1]


async def choose_number_attack_units(ctx):
    number_units = get_number_units(str(ctx.author.id))

    to_send = ">>> "
    to_send += "Please enter the number of attack units to send or type 'cancel' to stop the attack.\n\nYou have `"
    to_send += str(number_units["attack"])
    to_send += "` attack unit(s)."

    await ctx.channel.send(to_send)

    # Pre-condition check for wait_for function
    def check(msg):
        return (
            msg.content.isnumeric() or msg.content.lower() in {"cancel"}
        ) and msg.author.id == ctx.author.id

    try:
        msg = await bot.wait_for(
            "message", check=check, timeout=cfg.config["wait_timeout"]
        )

    except asyncio.TimeoutError:
        await ctx.channel.send(">>> You took too long to reply! Command cancelled.")
        return

    if msg.content.lower() == "cancel":
        await ctx.channel.send(">>> Attack cancelled!")
        return False

    number_select = int(msg.content)

    if number_select <= 0 or number_select > number_units["attack"]:
        await ctx.channel.send(">>> Invalid number of attack units! Cancelling attack!")
        return False

    return number_select


async def handle_successful_attack(ctx, attacked_kingdom, number_attack_units):
    remove_attack_units(
        str(ctx.author.id), number_attack_units
    )  # Remove all attack units from attacker
    remove_defence_units(
        str(attacked_kingdom["uid"]), number_attack_units // 2
    )  # Remove half defence units from defender

    user_kid = get_kid_from_uid(str(ctx.author.id))
    transferred_village = transfer_lowest_pop_village(attacked_kingdom["kid"], user_kid)

    set_been_attacked_flag(attacked_kingdom["kid"])
    set_has_attacked_flag(user_kid)

    to_send = ">>> "
    to_send += "Your attack against **"
    to_send += str(attacked_kingdom["k_name"])
    to_send += "** was successful! You lost `"
    to_send += str(number_attack_units)
    to_send += "` attack unit(s) in the battle!"
    to_send += "\nYou captured the village of **"
    to_send += str(transferred_village["v_name"])
    to_send += "** which has a population of `"
    to_send += str(transferred_village["population"])
    to_send += "`!\n\nYou must wait until tomorrow before you can attack again."

    await ctx.channel.send(to_send)


async def handle_failed_attack(ctx, attacked_kingdom, number_attack_units):
    remove_attack_units(
        str(ctx.author.id), number_attack_units
    )  # Remove all attack units from attacker
    remove_defence_units(
        str(attacked_kingdom["uid"]), number_attack_units
    )  # Remove all defence units from defender

    user_kid = get_kid_from_uid(str(ctx.author.id))
    transferred_village = transfer_lowest_pop_village(user_kid, attacked_kingdom["kid"])

    set_been_attacked_flag(attacked_kingdom["kid"])
    set_has_attacked_flag(user_kid)

    to_send = ">>> "
    to_send += "Your attack against **"
    to_send += str(attacked_kingdom["k_name"])
    to_send += "** failed! You lost `"
    to_send += str(number_attack_units)
    to_send += "` attack unit(s) in the battle!"
    to_send += "\nYou lost the village of **"
    to_send += str(transferred_village["v_name"])
    to_send += "** which had a population of `"
    to_send += str(transferred_village["population"])
    to_send += "`!\n\nYou must wait until tomorrow before you can attack again."

    await ctx.channel.send(to_send)


def remove_attack_units(uid, to_remove):
    cfg.db_cur.execute(
        "UPDATE Kingdoms SET attack=attack-? WHERE uid=?;", (to_remove, uid)
    )
    cfg.db_con.commit()


def remove_defence_units(uid, to_remove):
    cfg.db_cur.execute(
        "UPDATE Kingdoms SET defence = CASE WHEN (defence - ?) >= 0 THEN (defence - ?) ELSE 0 END WHERE uid=?;",
        (to_remove, to_remove, uid),
    )
    cfg.db_con.commit()


def get_kid_from_uid(uid):
    cfg.db_cur.execute("SELECT kid FROM Kingdoms WHERE uid=?;", (uid,))
    result = cfg.db_cur.fetchone()
    return result["kid"]


def transfer_lowest_pop_village(from_kid, to_kid):
    # Get vid of lowest village
    cfg.db_cur.execute(
        "SELECT * FROM Villages WHERE kid=? ORDER BY population ASC LIMIT 1;",
        (from_kid,),
    )
    lowest_village = cfg.db_cur.fetchone()

    cfg.db_cur.execute(
        "UPDATE Villages SET kid=? WHERE vid=?;", (to_kid, lowest_village["vid"])
    )
    cfg.db_con.commit()

    return lowest_village


def set_been_attacked_flag(kid):
    cfg.db_cur.execute("UPDATE Kingdoms SET been_attacked=1 WHERE kid=?;", (kid,))
    cfg.db_con.commit()


def set_has_attacked_flag(kid):
    cfg.db_cur.execute("UPDATE Kingdoms SET has_attacked=1 WHERE kid=?;", (kid,))
    cfg.db_con.commit()
