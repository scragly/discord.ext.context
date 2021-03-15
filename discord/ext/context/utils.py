import typing as t

from . import ctx
from .types import MemberUser


def get_member_instances(user: discord.User):
    return [guild.get_member(user.id) for guild in ctx.bot.guilds if guild.get_member(user.id)]


def ensure_member(user, *, guild: discord.Guild = None, guild_id: int = None) -> t.Optional[MemberUser]:
    if isinstance(user, discord.Member):
        return user

    if guild_id:
        guild = ctx.bot.get_guild(guild_id)

    if guild:
        user_id = getattr(user, "id", user)
        return guild.get_member(user_id)

    if isinstance(user, int):
        user: discord.User = ctx.bot.get_user(user)

    if not user:
        return None

    member_instances = get_member_instances(user)
    if len(member_instances) == 1:
        return member_instances[0]

    return user
