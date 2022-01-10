##> Imports
# > Standard libraries
from datetime import datetime

# > 3rd party dependencies
import aiohttp
import yaml

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.full_load(f)


class Instagram(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.instagram.start()

    async def get_last_post(self):
        headers = {
            "Host": "www.instagram.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 "
            "Safari/537.11 ",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.instagram.com/"
                + config["INSTAGRAM"]["USERNAME"]
                + "/feed/?__a=1",
                headers=headers,
            ) as r:
                response = await r.json()
                return response

    @loop(hours=config["INSTAGRAM"]["HOURS"])
    async def instagram(self):
        """Checks if a new instagram posts has been uploaded
        If a new post is available it will be posted in the social media channel
        """

        all_info = await self.get_last_post()
        last_post = all_info["graphql"]["user"]["edge_owner_to_timeline_media"][
            "edges"
        ][0]["node"]

        # Set variables
        img_url = last_post["display_url"]
        caption = last_post["edge_media_to_caption"]["edges"][0]["node"]["text"]
        comments = last_post["edge_media_to_comment"]["count"]
        likes = last_post["edge_liked_by"]["count"]
        timestamp = datetime.utcfromtimestamp(last_post["taken_at_timestamp"])
        post_url = "https://www.instagram.com/" + "p/" + last_post["shortcode"]

        # Profile data
        username = last_post["owner"]["username"]
        acc_url = "https://www.instagram.com/" + username
        # Could use server pic url instead, this is not saved in last_post :(
        profile_pic = all_info["graphql"]["user"]["profile_pic_url_hd"]

        # Send message in discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name=config["DISCORD"]["GUILD_NAME"],
            name=config["INSTAGRAM"]["CHANNEL"],
        )

        # Last message sent by the bot
        last_message = await channel.history().find(
            lambda m: m.author.id == self.bot.user.id
        )

        try:
            old_description = last_message.embeds[0].to_dict()["description"]
        except Exception:
            old_description = None

        # Do nothing
        if old_description == caption:
            return

        e = discord.Embed(
            title=f"New Instagram post published on {timestamp}",
            description=caption,
            url=post_url,
            color=0x00FFFF,
        )

        e.set_image(url=img_url)
        e.set_footer(text=f"❤️ {likes} | 💬 {comments}")
        e.set_author(name=username, icon_url=profile_pic, url=acc_url)

        await channel.send(embed=e)


def setup(bot):
    bot.add_cog(Instagram(bot))
