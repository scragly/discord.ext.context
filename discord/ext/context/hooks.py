from __future__ import annotations

from datetime import datetime

import discord
from discord.ext import commands

from .context import EventContext
from .types import MemberUser


__all__ = (
    'message_hook', 'raw_message_hook', 'typing_hook', 'reaction_hook', 'raw_reaction_hook',
    'reaction_clear_hook', 'raw_reaction_clear_hook', 'reaction_clear_emoji_hook', 'guild_channel_hook',
    'guild_hook', 'member_hook', 'guild_role_hook', 'member_ban_hook', 'command_hook'
)


@EventContext.register_hook("message")
@EventContext.register_hook("message_delete")
@EventContext.register_hook("message_edit")
def message_hook(ctx: EventContext, message: discord.Message, *_args):
    ctx.set(
        message=discord.PartialMessage(channel=message.channel, id=message.id),
        user=ctx.ensure_member(message.author),
        channel=message.channel,
        guild=message.guild,
    )


@EventContext.register_hook("raw_message_delete")
@EventContext.register_hook("raw_message_edit")
def raw_message_hook(ctx: EventContext, payload: discord.RawMessageDeleteEvent):
    if payload.cached_message:
        channel = payload.cached_message.channel
        guild = payload.cached_message.guild
        user = ctx.ensure_member(payload.cached_message.author, guild=guild)
    else:
        channel = ctx.client.get_channel(payload.channel_id)
        user = None
        guild = getattr(channel, "guild", None)

    ctx.set(
        message=discord.PartialMessage(channel=channel, id=payload.message_id),
        user=user,
        channel=channel,
        guild=guild
    )


@EventContext.register_hook("typing")
def typing_hook(ctx: EventContext, channel: discord.abc.Messageable, user: MemberUser, _when: datetime):
    ctx.set(
        channel=channel,
        user=ctx.ensure_member(user),
        guild=getattr(channel, "guild", None),
    )


@EventContext.register_hook("reaction_add")
@EventContext.register_hook("reaction_remove")
def reaction_hook(ctx: EventContext, reaction: discord.Reaction, user: discord.User):
    ctx.set(
        message=discord.PartialMessage(channel=reaction.message.channel, id=reaction.message.id),
        user=ctx.ensure_member(user),
        channel=reaction.message.channel,
        guild=reaction.message.guild,
    )


@EventContext.register_hook("raw_reaction_add")
@EventContext.register_hook("raw_reaction_remove")
def raw_reaction_hook(ctx: EventContext, payload: discord.RawReactionActionEvent):
    channel = ctx.client.get_channel(payload.channel_id)
    guild = ctx.client.get_guild(payload.guild_id) if payload.guild_id else None
    ctx.set(
        message=discord.PartialMessage(channel=channel, id=payload.message_id),
        user=ctx.ensure_member(payload.user_id, guild=guild),
        channel=channel,
        guild=guild,
    )


@EventContext.register_hook("reaction_clear")
def reaction_clear_hook(ctx: EventContext, message: discord.Message, _reaction: discord.Reaction):
    ctx.set(
        message=discord.PartialMessage(channel=message.channel, id=message.id),
        channel=message.channel,
        guild=message.guild,
    )


@EventContext.register_hook("reaction_clear_emoji")
def reaction_clear_emoji_hook(ctx: EventContext, reaction: discord.Reaction):
    ctx.set(
        message=discord.PartialMessage(channel=reaction.message.channel, id=reaction.message.id),
        channel=reaction.message.channel,
        guild=reaction.message.guild,
    )


@EventContext.register_hook("raw_reaction_clear")
@EventContext.register_hook("raw_reaction_clear_emoji")
def raw_reaction_clear_hook(ctx: EventContext, payload: discord.RawReactionClearEvent):
    channel = ctx.client.get_channel(payload.channel_id)
    ctx.set(
        message=discord.PartialMessage(channel=channel, id=payload.message_id),
        channel=channel,
        guild=ctx.client.get_guild(payload.guild_id) if payload.guild_id else None,
    )


@EventContext.register_hook("guild_channel_update")
@EventContext.register_hook("guild_channel_create")
@EventContext.register_hook("guild_channel_delete")
@EventContext.register_hook("guild_channel_pins_update")
@EventContext.register_hook("webhooks_update")
def guild_channel_hook(ctx: EventContext, channel: discord.abc.GuildChannel, *_args):
    ctx.set(channel=channel, guild=channel.guild)


@EventContext.register_hook("guild_update")
@EventContext.register_hook("guild_join")
@EventContext.register_hook("guild_remove")
@EventContext.register_hook("guild_integrations_update")
@EventContext.register_hook("guild_emojis_update")
@EventContext.register_hook("guild_available")
@EventContext.register_hook("guild_unavailable")
def guild_hook(ctx: EventContext, guild: discord.Guild, *_args):
    ctx.set(guild=guild)


@EventContext.register_hook("member_update")
@EventContext.register_hook("member_join")
@EventContext.register_hook("member_remove")
def member_hook(ctx: EventContext, member: discord.Member, *_args):
    ctx.set(
        user=member,
        guild=member.guild,
    )


@EventContext.register_hook("guild_role_update_hook")
@EventContext.register_hook("guild_role_create_hook")
@EventContext.register_hook("guild_role_delete_hook")
def guild_role_hook(ctx: EventContext, role: discord.Role, *_args):
    ctx.set(guild=role.guild)


@EventContext.register_hook("member_ban_hook")
@EventContext.register_hook("member_unban_hook")
def member_ban_hook(ctx: EventContext, guild: discord.Guild, user: MemberUser):
    ctx.set(user=user, guild=guild)


@EventContext.register_hook("command")
def command_hook(ctx: EventContext, cmd_ctx: commands.Context):
    ctx.set_cmd_ctx(cmd_ctx)
