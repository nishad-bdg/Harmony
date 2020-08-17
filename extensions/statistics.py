from datetime import datetime
from discord.ext import commands
import discord
import os
import json


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_status(self, member):
        query = 'SELECT status FROM status WHERE user_id=%s ORDER BY id DESC'
        status = await self.bot.db.fetchone(query, member.id)
        if status is not None and status[0] == str(member.status):
            return

        query = f"INSERT IGNORE INTO status (user_id, status, updated_at) VALUES (%s, %s, %s)"
        await self.bot.db.execute(query, (member.id, str(member.status), datetime.utcnow()))

    async def update_activities(self, member):
        query = 'SELECT activities FROM activities WHERE user_id=%s ORDER BY id DESC'
        activities = await self.bot.db.fetchone(query, member.id)
        activities_ = json.dumps([activity.to_dict() for activity in member.activities])
        if activities is not None and activities[0] == activities_:
            return

        query = f"INSERT IGNORE INTO activities (user_id, activities, updated_at) VALUES (%s, %s, %s)"
        await self.bot.db.execute(query, (member.id, activities_, datetime.utcnow()))

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

    async def update_username(self, user):
        query = 'SELECT username FROM usernames WHERE user_id=%s ORDER BY id DESC'
        username = await self.bot.db.fetchone(query, user.id)
        if username is not None and username[0] == str(user):
            return

        query = f"INSERT IGNORE INTO usernames (user_id, username, updated_at) VALUES (%s, %s, %s)"
        await self.bot.db.execute(query, (user.id, str(user), datetime.utcnow()))

    @commands.Cog.listener()
    async def on_ready(self):
        for user in self.bot.users:
            await self.update_avatar(user)
            await self.update_username(user)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.update_status(member)
        await self.update_activities(member)
        await self.update_avatar(member)
        await self.update_username(member)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.status != after.status:
            await self.update_status(after)

        if before.activities != after.activities:
            await self.update_activities(after)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.avatar != after.avatar:
            await self.update_avatar(after)

        if before.name != after.name or before.discriminator != after.discriminator:
            await self.update_username(after)


def setup(bot):
    bot.add_cog(Statistics(bot))
