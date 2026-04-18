# skyflight

skyBot is a Discord bot built with `discord.py` using a modular Cog architecture.

## Setup

1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your bot token:
   ```bash
   export DISCORD_BOT_TOKEN="your-token"
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Persistent configuration

The bot persists runtime configuration in `/home/runner/work/skyflight/skyflight/config.json`.

Stored keys:
- `admin_role_ids` (list of role IDs)
- `mod_role_ids` (list of role IDs)
- `logging_channel_id` (channel ID)
- `automod_enabled` (boolean)
- `mute_duration_default` (integer, in **minutes**)

## Configuration commands

Only members that have at least one role ID listed in `admin_role_ids` can run `!configure` commands.

- `!configure show`
- `!configure admin_role add <role_id>`
- `!configure set <key> <value>`

Examples:
- `!configure set automod_enabled true`
- `!configure set logging_channel_id 123456789012345678`
- `!configure set mute_duration_default 30`
- `!configure set mod_role_ids 111,222,333`
