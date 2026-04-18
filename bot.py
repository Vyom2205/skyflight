from __future__ import annotations

import logging
import os
from pathlib import Path

import discord
from discord.ext import commands

from skybot.config_manager import ConfigStore


class SkyBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix="!", intents=intents)
        self.config_store = ConfigStore(Path(__file__).resolve().parent / "config.json")

    async def setup_hook(self) -> None:
        await self.load_extension("skybot.cogs.configuration")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[skyBot] %(levelname)s: %(message)s")
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN environment variable is required")

    bot = SkyBot()
    bot.run(token)


if __name__ == "__main__":
    main()
