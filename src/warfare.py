from discord.ext import commands
from cfg import bot

import cfg, shared

@bot.command(name="players")
async def list_players(ctx):

    all_kingdoms = get_all_kingdoms()

    converted_all_kingdoms = shared.convert_id_to_name(all_kingdoms, 'uid')

    kingdom_table = shared.create_table("Kingdoms", ["Name", "Kingdom", "# Villages"], ['uid', 'k_name', 'count'], converted_all_kingdoms, 0, False)

    await ctx.channel.send(kingdom_table)


# Returns all kingdoms
# uid, k_name, number of villages
def get_all_kingdoms():
    cfg.db_cur.execute("SELECT k.uid, k.k_name, s.count FROM Kingdoms k LEFT JOIN (SELECT k2.uid, COUNT(v2.vid) as count FROM Kingdoms k2 LEFT JOIN Villages v2 on k2.kid=v2.kid GROUP BY k2.uid) s ON s.uid=k.uid;")
    return cfg.db_cur.fetchall()