from datetime import datetime
from discord.ext import commands
import discord
import json
import os


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_statistic(self, member, attribute, table):
        query = f'SELECT {attribute} FROM {table} WHERE user_id=%s ORDER BY id DESC'
        entry = await self.bot.db.fetchone(query, member.id)
        if entry is not None and entry[0] == str(getattr(member, attribute, member)):
            return

        query = f'INSERT IGNORE INTO {table} (user_id, {attribute}, updated_at) VALUES (%s, %s, %s)'
        await self.bot.db.execute(query, (member.id, str(getattr(member, attribute, member)), datetime.utcnow()))

    async def update_batch_statistic(self, member, attribute, table):
        query = f'SELECT {attribute} FROM {table} WHERE user_id=%s ORDER BY id DESC'
        entries = await self.bot.db.fetchone(query, member.id)
        batch = json.dumps([x.to_dict() for x in getattr(member, attribute)])
        if entries is not None and entries[0] == batch:
            return

        query = f'INSERT IGNORE INTO {table} (user_id, activities, updated_at) VALUES (%s, %s, %s)'
        await self.bot.db.execute(query, (member.id, batch, datetime.utcnow()))

    async def update_avatar(self, user):
        path = f'resources/avatars/{user.avatar}.webp'
        if not os.path.isfile(path):
            await user.avatar_url_as().save(path)

        query = 'SELECT avatar_hash FROM avatars WHERE user_id=%s ORDER BY id DESC'
        avatar = await self.bot.db.fetchone(query, user.id)
        if avatar is not None and avatar[0] == user.avatar:
            return

        query = 'INSERT IGNORE INTO avatars (user_id, avatar_hash, updated_at)VALUES (%s, %s, %s)'
        await self.bot.db.execute(query, (user.id, user.avatar, datetime.utcnow()))

    @commands.Cog.listener()
    async def on_ready(self):
        for member in self.bot.guild.members:
            await self.update_batch_statistic(member, 'activities', 'activities')
            await self.update_statistic(member, 'nick', 'nicknames')
            await self.update_statistic(member, 'status', 'statuses')

        for user in self.bot.users:
            await self.update_avatar(user)
            await self.update_statistic(user, 'discriminator', 'discriminators')
            await self.update_statistic(user, 'name', 'names')
            await self.update_statistic(user, 'username', 'usernames')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_avatar(member)
        await self.update_batch_statistic(member, 'activities', 'activities')
        await self.update_statistic(member, 'discriminator', 'discriminators')
        await self.update_statistic(member, 'name', 'names')
        await self.update_statistic(member, 'nick', 'nicknames')
        await self.update_statistic(member, 'status', 'statuses')
        await self.update_statistic(member, 'username', 'usernames')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.activities != after.activities:
            await self.update_batch_statistic(after, 'activities', 'activities')

        if before.nick != after.nick:
            await self.update_statistic(after, 'nick', 'nicknames')

        if before.status != after.status:
            await self.update_statistic(after, 'status', 'statuses')

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.avatar != after.avatar:
            await self.update_avatar(after)

        if before.discriminator != after.discriminator:
            await self.update_statistic(after, 'discriminator', 'discriminators')

        if before.name != after.name:
            await self.update_statistic(after, 'name', 'names')

        if before.name != after.name or before.discriminator != after.discriminator:
            await self.update_statistic(after, 'username', 'usernames')


def setup(bot):
    bot.add_cog(Statistics(bot))
