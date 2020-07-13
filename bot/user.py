from discord.ext import commands
from cfg import bot
import cfg, kingdoms, villages, currency


@bot.command(name="help")
async def show_help(ctx):
    to_send = ">>> "
    to_send += get_general_help_string()
    to_send += kingdoms.get_shop_help_string()
    to_send += villages.get_village_help_string()
    to_send += currency.get_tax_help_string()

    await ctx.channel.send(to_send)


def get_general_help_string():
    to_send = "**General Commands** ```"
    to_send += (
        cfg.PREFIX + "help                           :  Show available all available\n"
    )
    to_send += (
        cfg.PREFIX
        + "info                           :  Show your current player/kingdom information\n"
    )
    to_send += (
        cfg.PREFIX
        + "levelup                        :  Level up to the next rank\n"
    )
    to_send += (
        cfg.PREFIX
        + "attack                         :  Attack another kingdom\n"
    )
    to_send += cfg.PREFIX + "players                        :  List all players\n"
    to_send += (
        cfg.PREFIX
        + "init <kingdom_name>            :  Create your kingdom called <kingdom_name>\n"
    )
    to_send += (
        cfg.PREFIX
        + "rename_kingdom <name>          :  Rename your kingdom to <name>```"
    )

    return to_send


# Displays the number of doubloons that you have
@bot.command(name="info")
async def display_user_info(ctx):

    cfg.db_cur.execute(
        "SELECT k.k_name, k.attack, k.defence, u.doubloons, u.rank, u.rumpus_count FROM Users u, Kingdoms k WHERE u.uid=k.uid AND u.uid=?;",
        (str(ctx.author.id),),
    )

    result = cfg.db_cur.fetchone()

    if result:
        to_send = ">>> **" + str(ctx.author) + "** of **" + str(result["k_name"]) + "**\n\n"
        to_send += "**Rank:** `" + str(cfg.config['ranks'][result["rank"]]['name']) + "`\n"
        to_send += "**Rumpuses:** `" + str(result["rumpus_count"]) + "`\n"
        to_send += "**Total Pop:** `" + str(villages.get_total_population(ctx)) + "`\n"
        to_send += "**Doubloons:** `" + str(result["doubloons"]) + "`\n"
        to_send += "**Attack:** `" + str(result["attack"]) + "`\n"
        to_send += "**Defence:** `" + str(result["defence"]) + "`\n"

        await ctx.channel.send(to_send)

    else:
        await kingdoms.handle_no_kingdom(ctx)
