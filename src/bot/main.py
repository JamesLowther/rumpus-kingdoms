import discord
from discord.ext import commands
import sqlite3
import os, sys, re
import cfg

cfg.init()

# Configure and create the bot
# The bot is being stored as a builtin
bot = commands.Bot(command_prefix=cfg.PREFIX)
bot.remove_command("help")
cfg.bot = bot

import management, kingdoms, user, villages, currency, scheduled, warfare, rank


def main():
    (db_path, token_path) = management.read_json()

    bot_token = read_bot_token(token_path)
    connect_db(db_path)

    # Removed scheduler until a solution to database threading can be found
    # cfg.scheduler = scheduled.Scheduler()

    cfg.bot.run(bot_token)


# Connect to the sqlite3 database
# Sets global connection objects in cfg.py
def connect_db(db_path):
    cfg.db_con = sqlite3.connect(db_path)
    cfg.db_con.row_factory = sqlite3.Row
    cfg.db_cur = cfg.db_con.cursor()

    print("Connected to database at path: " + str(db_path))


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))


@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return

    if ctx.content.startswith(cfg.PREFIX):
        message_content = ctx.content[len(cfg.PREFIX) : len(ctx.content) + 1]

        # Check to see if user exists in the database
        if not check_user_exists(ctx.author.id):
            management.create_user(ctx)

        # Handle actual bot commands
        if bot.get_command(message_content):
            await bot.process_commands(ctx)

    else:
        # Add here to add custom chatting functionality
        rank.check_message(ctx)


# Checks to see if the user is in the database
def check_user_exists(user_id):
    cfg.db_cur.execute("SELECT * FROM Users WHERE uid = ?;", (user_id,))

    return cfg.db_cur.fetchone() != None


def read_bot_token(token_path):

    token_file = open(token_path, "r")
    bot_token = token_file.readline()
    token_file.close()

    return bot_token


main()
