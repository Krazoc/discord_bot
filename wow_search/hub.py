from discord.ext.commands import Bot

import discord
import os

from function import wow_character, wow_guild, wow_affix, wow_help, wow_auction, wow_realm, wow_token

description = "WoW Search"
discord_token = os.environ.get("DISCORD_TOKEN")
Client = discord.Client()
client = Bot(command_prefix="\\", description=description)


@client.event
async def on_message(message):
    if message.content.startswith("wow-character!"):
        recap = wow_character(message)
        await message.channel.send("```css\n" + recap + "```")

    elif message.content.startswith("wow-guild!"):
        recap = wow_guild(message)
        await message.channel.send("```css" + recap + "```")

    elif message.content.startswith("wow-affix!"):
        recap = wow_affix()
        await message.channel.send("```css\n" + recap + "\n```")

    elif message.content.startswith("wow-auction!"):
        recap = wow_auction(message)
        await message.channel.send("```css\n" + recap + "\n```")

    elif message.content.startswith("wow-realm!"):
        recap = wow_realm(message)
        await message.channel.send("```css\n" + recap + "\n```")

    elif message.content.startswith("wow-token!"):
        recap = wow_token(message)
        await message.channel.send("```css\n" + recap + "\n```")

    elif message.content.startswith("wow-help!"):
        recap = wow_help()
        await message.channel.send(recap)
client.run(discord_token)
