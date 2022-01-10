#!/usr/bin/env python3

##> Imports
# > Standard library
import asyncio
import sys

# > 3rd Party Dependencies
import yaml

# Discord libraries
import discord
from discord.ext import commands

bot = commands.Bot()

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.full_load(f)


@bot.event
async def on_ready():
    """This gets printed on boot up"""

    guild = discord.utils.get(
        bot.guilds,
        name=config["DISCORD"]["GUILD_NAME"],
    )

    # Load instagram extension
    bot.load_extension("instagram")

    print(f"{bot.user} is connected to {guild.name} (id: {guild.id}) \n")


if __name__ == "__main__":

    TOKEN = config["DISCORD"]["TOKEN"]

    # Main event loop
    try:
        bot.loop.run_until_complete(bot.run(TOKEN))
    except KeyboardInterrupt:
        print("Caught interrupt signal.")
        print("exiting...")
        bot.loop.run_until_complete(
            asyncio.wait(
                [bot.change_presence(status=discord.Status.invisible), bot.logout()]
            )
        )
    finally:
        bot.loop.close()
        sys.exit(0)
