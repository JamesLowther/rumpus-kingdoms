#!/usr/bin/python3

import discord
from discord.ext import commands
import json, sqlite3
import os, sys, re
import cfg

# Configure and create the bot
# The bot is being stored as a builtin
CONFIG_FILE = os.path.dirname(os.path.realpath(__file__)) + "/config.json"
PREFIX = "$rumpus "
bot = commands.Bot(command_prefix=PREFIX)
cfg.bot = bot

import management


def main():
    (bot_token, root_ids, db_path) = read_json()
    cfg.root_ids = root_ids

    connect_db(db_path)

    cfg.bot.run(bot_token)


# Read the configuration file
# Sets the global variables in cfg.py
def read_json():
    with open(CONFIG_FILE) as f:
        data = json.load(f)

        bot_token = data["bot_token"]
        root_ids = data["root_ids"]
        db_path = os.path.dirname(os.path.realpath(__file__)) + "/" + data["db_name"]

        f.close()

        return (bot_token, root_ids, db_path)


# Connect to the sqlite3 database
# Sets global connection objects in cfg.py
def connect_db(db_path):
    cfg.db_conn = sqlite3.connect(db_path)
    cfg.db_conn.row_factory = sqlite3.Row
    cfg.db_cur = cfg.db_conn.cursor()

    print("Connected to database at path: " + str(db_path))


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))


@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return

    if ctx.content.startswith(PREFIX):
        message_content = ctx.content[len(PREFIX) : len(ctx.content) + 1]

        # Check to see if user exists in the database
        if not check_user_exists(ctx.author.id):
            management.create_user(ctx)

        # Handle actual bot commands
        if bot.get_command(message_content):
            await bot.process_commands(ctx)

    else:
        pass
        # Add here to add custom chatting functionality


# Checks to see if the user is in the database
def check_user_exists(user_id):
    cfg.db_cur.execute("SELECT * FROM Users WHERE uid = ?;", (user_id,))

    return cfg.db_cur.fetchone() != None


main()
