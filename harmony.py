from discord.ext import commands
from extensions.utils import db
import config
import discord
import io
import sys
import traceback


class Harmony(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=config.PREFIX, case_insensitive=True)
        self.load_extensions()
        self.db = db.DB(config.MYSQL_HOST, config.MYSQL_USERNAME, config.MYSQL_PASSWORD, config.MYSQL_DATABASE, self.loop)

    def load_extensions(self):
        for extension in config.EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f"Extension '{extension}' has been loaded")
            except Exception:
                print(f"Extension '{extension}' failed to load", file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print(f'Using version {discord.__version__} of discord.py')

    async def on_command_error(self, ctx, error):
        print(error)

    @property
    def guild(self):
        return self.get_guild(config.GUILD_ID)

    def run(self):
        super().run(config.TOKEN)


if __name__ == '__main__':
    harmony = Harmony()
    harmony.run()
