import typing as t

import discord

__all__ = ('MemberUser', 'Emoji')

MemberUser = t.Union[discord.Member, discord.User]
Emoji = t.Union[discord.Emoji, discord.PartialEmoji]
