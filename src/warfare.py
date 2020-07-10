from discord.ext import commands
from cfg import bot

import cfg, shared, kingdoms

@bot.command(name="players")
async def list_players(ctx):
    all_kingdoms = get_all_kingdoms()

    converted_all_kingdoms = shared.convert_id_to_name_key(all_kingdoms, 'uid', 'username')

    kingdom_table = shared.create_table("Kingdoms", ["Name", "Kingdom", "# Villages", "Attacked Today"], ['username', 'k_name', 'count', 'been_attacked'], converted_all_kingdoms, 0, False)

    await ctx.channel.send(kingdom_table)


# Returns all kingdoms
# uid, k_name, number of villages
def get_all_kingdoms():
    #cfg.db_cur.execute("SELECT k.uid, k.k_name, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid;")
    cfg.db_cur.execute("SELECT k.uid, k.been_attacked, k.k_name, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid;")
    return cfg.db_cur.fetchall()

# Returns all kingdoms
# uid, k_name, number of villages
def get_all_non_attacked_kingdoms():
    #cfg.db_cur.execute("SELECT k.uid, k.k_name, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid;")
    cfg.db_cur.execute("SELECT *, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid WHERE k.been_attacked != 1;")
    return cfg.db_cur.fetchall()


@bot.command(name="attack")
async def attack_user(ctx):
    
    # Check if user has a kingdom
    if not kingdoms.check_has_kingdom(ctx):
        await kingdoms.handle_no_kingdom(ctx)
        return
    
    if not await check_attack_prereqs(ctx):
        return

    all_kingdoms = get_all_non_attacked_kingdoms()
    converted_all_kingdoms = shared.convert_id_to_name_key(all_kingdoms, 'uid', 'username')
    
    kingdom = await choose_kingdom_to_attack(ctx, converted_all_kingdoms)
    if not kingdom:
        return

    number_attack_units = await choose_number_attack_units(ctx)
    if not number_attack_units:
        return

    print(dict(kingdom))
    print(number_attack_units)

async def check_attack_prereqs(ctx):
    if not get_village_count(ctx) > 0:
        await ctx.channel.send("You need to have at least 1 village to attack another user!")
        return False
    
    if not get_number_units(ctx)['attack'] > 0:
        await ctx.channel.send("You need to have at least 1 attack unit to attack another user!")
        return False

    if get_has_attacked(ctx) == 1:
        await ctx.channel.send("You have already attacked another kingdom today! Please wait until tomorrow!")
        return False

    return True
    

def get_number_units(ctx):
    cfg.db_cur.execute("SELECT k.attack, k.defence FROM Users u, Kingdoms k WHERE u.uid=k.uid AND u.uid=?;", (str(ctx.author.id),))
    return cfg.db_cur.fetchone()


def get_village_count(ctx):
    cfg.db_cur.execute("SELECT COUNT(v.vid) as count FROM Kingdoms k LEFT JOIN Villages v on k.kid=v.kid WHERE k.uid=? GROUP BY k.uid;", (str(ctx.author.id),))
    return cfg.db_cur.fetchone()['count']


def get_has_attacked(ctx):
    cfg.db_cur.execute("SELECT k.has_attacked FROM Users u, Kingdoms k WHERE u.uid=k.uid AND u.uid=?;", (str(ctx.author.id),))
    return cfg.db_cur.fetchone()['has_attacked']


async def choose_kingdom_to_attack(ctx, all_kingdoms):
    to_send = ">>> "
    to_send += shared.create_table("Kingdoms", ["Name", "Kingdom", "# Villages"], ['username', 'k_name', 'count'], all_kingdoms, 0)
    to_send += "\nPlease select the index of the kingdom you want to attack or type 'cancel' to stop the attack"

    await ctx.channel.send(to_send)

    # Pre-condition check for wait_for function
    def check(msg):
        return (msg.content.isnumeric() or msg.content.lower() in {"cancel"}) and msg.author.id == ctx.author.id

    msg = await bot.wait_for("message", check=check)

    if msg.content.lower() == "cancel":
        await ctx.channel.send("Attack canceled!")
        return False

    index_range = len(all_kingdoms)
    index = int(msg.content)

    if index <= 0 or index > index_range:
        await ctx.channel.send("Index out of range! Canceling attack!")
        return False

    return all_kingdoms[index - 1]
    

async def choose_number_attack_units(ctx):
    
    number_units = get_number_units(ctx)
    
    to_send = ">>> "
    to_send += "Please enter the number of attack units to send or type 'cancel' to stop the attack.\n\nYou have `"
    to_send += str(number_units['attack'])
    to_send += "` attack unit(s)."

    await ctx.channel.send(to_send)

    # Pre-condition check for wait_for function
    def check(msg):
        return (msg.content.isnumeric() or msg.content.lower() in {"cancel"}) and msg.author.id == ctx.author.id

    msg = await bot.wait_for("message", check=check)

    if msg.content.lower() == "cancel":
        await ctx.channel.send("Attack canceled!")
        return False

    number_select = int(msg.content)

    if number_select <= 0 or number_select > number_units['attack']:
        await ctx.channel.send("Invalid number of attack units! Canceling attack!")
        return False

    return number_select
