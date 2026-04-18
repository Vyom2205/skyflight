from __future__ import annotations

from typing import Any

from discord.ext import commands

from skybot.config_manager import ConfigStore


class ConfigurationCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config_store: ConfigStore) -> None:
        self.bot = bot
        self.config_store = config_store

    def _is_admin(self, ctx: commands.Context[Any]) -> bool:
        admin_role_ids = set(self.config_store.get("admin_role_ids"))
        if not admin_role_ids:
            return False
        return any(role.id in admin_role_ids for role in getattr(ctx.author, "roles", []))

    async def cog_check(self, ctx: commands.Context[Any]) -> bool:
        if self._is_admin(ctx):
            return True
        await ctx.reply(
            "You do not have permission to use configure commands. "
            "Only users with an admin role can run these commands."
        )
        return False

    @commands.group(name="configure", invoke_without_command=True)
    async def configure(self, ctx: commands.Context[Any]) -> None:
        await ctx.send("Use `!configure show`, `!configure admin_role add <role_id>`, or `!configure set <key> <value>`")

    @configure.command(name="show")
    async def configure_show(self, ctx: commands.Context[Any]) -> None:
        config = self.config_store.get_all()
        await ctx.send(
            "Current configuration:\n"
            f"- admin_role_ids: {config['admin_role_ids']}\n"
            f"- mod_role_ids: {config['mod_role_ids']}\n"
            f"- logging_channel_id: {config['logging_channel_id']}\n"
            f"- automod_enabled: {config['automod_enabled']}\n"
            f"- mute_duration_default (minutes): {config['mute_duration_default']}"
        )

    @configure.group(name="admin_role", invoke_without_command=True)
    async def configure_admin_role(self, ctx: commands.Context[Any]) -> None:
        await ctx.send("Use `!configure admin_role add <role_id>`")

    @configure_admin_role.command(name="add")
    async def configure_admin_role_add(self, ctx: commands.Context[Any], role_id: int) -> None:
        self.config_store.add_to_list("admin_role_ids", role_id)
        await ctx.send(f"Added role ID `{role_id}` to admin_role_ids.")

    @configure.command(name="set")
    async def configure_set(self, ctx: commands.Context[Any], key: str, *, value: str) -> None:
        if key not in self.config_store.valid_keys:
            await ctx.send(f"Invalid key `{key}`. Valid keys: {', '.join(self.config_store.valid_keys)}")
            return

        parsed = self._parse_value(key, value)
        self.config_store.update(key, parsed)
        await ctx.send(f"Updated `{key}` to `{parsed}`")

    def _parse_value(self, key: str, value: str) -> Any:
        if key in {"admin_role_ids", "mod_role_ids"}:
            raw_parts = [part.strip() for part in value.split(",") if part.strip()]
            try:
                return [int(part) for part in raw_parts]
            except ValueError as exc:
                raise commands.BadArgument(
                    f"{key} must be a comma-separated list of integer role IDs"
                ) from exc

        if key in {"logging_channel_id", "mute_duration_default"}:
            return int(value)

        if key == "automod_enabled":
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "on", "enabled"}:
                return True
            if lowered in {"false", "0", "no", "off", "disabled"}:
                return False
            raise commands.BadArgument(
                "automod_enabled must be true/false "
                "(accepted values: true, false, 1, 0, yes, no, on, off, enabled, disabled)"
            )

        raise commands.BadArgument(f"Unsupported key: {key}")


async def setup(bot: commands.Bot) -> None:
    if not hasattr(bot, "config_store"):
        raise RuntimeError("ConfigurationCog requires bot.config_store")
    await bot.add_cog(ConfigurationCog(bot, bot.config_store))
