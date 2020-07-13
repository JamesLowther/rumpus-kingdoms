from discord.ext import commands
from cfg import bot
from random import randint

import json, os
import cfg


CONFIG_FILE = os.path.dirname(os.path.realpath(__file__)) + "/config.json"


# Shuts down the bot and closes any open connections
# Only users with root access can use this command
@bot.command(name="shutdown")
async def shutdown(ctx):
    print(str(ctx.author.id) + " (" + str(ctx.author) + ") called for shutdown")

    if check_root(ctx.author.id):
        cfg.db_con.close()
        cfg.scheduler.shutdown_threads()

        await ctx.channel.send(
            ">>> The rumpus room remains unguarded. Tread carefully."
        )
        await bot.logout()

    else:
        await ctx.channel.send(">>> Sorry! You don't have permission to do that!")


# Reload game data from config file
@bot.command(name="reload")
async def reload_config(ctx):
    print(str(ctx.author.id) + " (" + str(ctx.author) + ") called for reload")

    if check_root(ctx.author.id):
        read_json()
        await ctx.channel.send(">>> Reload successful!")

    else:
        await ctx.channel.send(">>> Sorry! You don't have permission to do that!")


# Checks if the id is in the ROOT_IDS list
def check_root(user_id):
    return user_id in cfg.config["root_ids"]


# Create the user in the database
def create_user(ctx):
    cfg.db_cur.execute(
        "INSERT INTO Users VALUES (?, ?, ?, 0, 0, 0, 0, NULL);",
        (str(ctx.author.id), str(ctx.author.name), cfg.config["starter_balance"]),
    )
    cfg.db_con.commit()

def update_all_usernames():
    cfg.db_cur.execute("SELECT uid FROM Users;")
    all_users = cfg.db_cur.fetchall()

    for user in all_users:
        uid = user['uid']
        update_username(str(uid), cfg.bot.get_user(int(uid)).name)


def update_username(uid, name):
    cfg.db_cur.execute(
        "UPDATE Users SET username=? WHERE uid=?;",
        (name, uid)
    )

    cfg.db_con.commit()


# Generate a random ID for a table
def unique_ID(table, column):
    while True:
        new_id = randint(100000, 999999)

        cfg.db_cur.execute("SELECT * FROM " + table + "  WHERE ?=?;", (column, new_id))

        if not cfg.db_cur.fetchone():
            break

    return str(new_id)


# Read the configuration file
# Sets the global variables in cfg.py
def read_json():
    with open(CONFIG_FILE) as f:
        data = json.load(f)

        token_path = os.path.dirname(os.path.realpath(__file__)) + "/" + data["token_name"]
        db_path = os.path.dirname(os.path.realpath(__file__)) + "/" + data["db_name"]
        cfg.config = data

        f.close()

        return (db_path, token_path)
