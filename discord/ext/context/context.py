from __future__ import annotations

import typing as t
from contextlib import contextmanager

from contextvars import ContextVar

import discord
from discord.ext import commands

from .types import MemberUser, Emoji

_ctx_message: ContextVar[t.Optional[discord.PartialMessage]] = ContextVar("message")
_ctx_emoji: ContextVar[t.Optional[discord.PartialMessage]] = ContextVar("emoji")
_ctx_user: ContextVar[t.Optional[MemberUser]] = ContextVar("user", default=None)
_ctx_channel: ContextVar[t.Optional[discord.abc.Messageable]] = ContextVar("channel")
_ctx_guild: ContextVar[t.Optional[discord.Guild]] = ContextVar("guild")
_ctx_cmd: ContextVar[t.Optional[commands.Context]] = ContextVar("cmd_ctx")
_ctx_event: ContextVar[t.Optional[str]] = ContextVar("event")
_ctx_client: ContextVar[t.Optional[discord.Client]] = ContextVar("client")


class ContextNotSet(Exception):
    """Raised when an EventContext value was accessed before it was set."""
    pass


class EventContext:
    """Holder and manager for all context values originating from triggered discord.py events."""

    hooks: t.Dict[str, t.Callable] = dict()
    _instance = None

    def __new__(cls, *args, **kwds):
        """Set the class to act as a singleton."""
        if cls._instance is not None:
            return cls._instance
        cls._instance = object.__new__(cls)
        return cls._instance

    def __repr__(self):
        """A representative view of the current context."""
        ctx_previews = []
        if self.event:
            ctx_previews.append(f"event='{self.event}'")
        if self.message:
            ctx_previews.append(f"message={self.message.id}")
        if self.emoji:
            ctx_previews.append(f"message='{self.emoji.name}'")
        if self.user:
            ctx_previews.append(f"user='{self.user}'")
        if self.channel:
            ctx_previews.append(f"channel='{self.channel}'")
        if self.guild:
            ctx_previews.append(f"guild='{self.guild}'")
        if self.cmd_ctx:
            ctx_previews.append(f"command='{self.cmd_ctx.command}'")

        output = ", ".join(ctx_previews)
        return f"<EventContext {output}>"

    @property
    def message(self) -> t.Optional[discord.PartialMessage]:
        """The current message in context."""
        try:
            return _ctx_message.get()
        except KeyError:
            raise ContextNotSet

    @property
    def emoji(self) -> t.Optional[Emoji]:
        """The current emoji in context."""
        try:
            return _ctx_emoji.get()
        except KeyError:
            raise ContextNotSet

    @property
    def user(self) -> t.Optional[MemberUser]:
        """The current user in context."""
        try:
            return _ctx_user.get()
        except KeyError:
            raise ContextNotSet

    @property
    def channel(self) -> t.Optional[discord.abc.Messageable]:
        """The current channel in context."""
        try:
            return _ctx_channel.get()
        except KeyError:
            raise ContextNotSet

    @property
    def guild(self) -> t.Optional[discord.Guild]:
        """The current guild in context."""
        try:
            return _ctx_guild.get()
        except KeyError:
            raise ContextNotSet

    @property
    def cmd_ctx(self) -> t.Optional[commands.Context]:
        """The current command context instance."""
        try:
            return _ctx_cmd.get()
        except KeyError:
            raise ContextNotSet

    @property
    def event(self) -> t.Optional[str]:
        """The current event in context."""
        try:
            return _ctx_event.get()
        except KeyError:
            raise ContextNotSet

    @property
    def client(self) -> t.Optional[discord.Client]:
        """The current discord.py client in context."""
        try:
            return _ctx_client.get()
        except KeyError:
            raise ContextNotSet

    @property
    def bot(self) -> t.Optional[discord.Client]:
        """The current discord.py client in context. Alias of `ctx.client`."""
        return self.client

    def set(
        self,
        *,
        message: discord.PartialMessage = None,
        emoji: Emoji = None,
        user: MemberUser = None,
        channel: discord.abc.Messageable = None,
        guild: discord.Guild = None,

    ) -> EventContext:
        """Set the context values given."""
        _ctx_message.set(message)
        _ctx_emoji.set(emoji)
        _ctx_user.set(user)
        _ctx_channel.set(channel)
        _ctx_guild.set(guild)
        return self

    def set_event(self, event: str):
        """Set the event for the context"""
        _ctx_event.set(event)
        return self.hooks.get(event)

    def set_client(self, client: discord.Client):
        """Set the client for the context."""
        _ctx_client.set(client)
        return self

    def set_cmd_ctx(self, cmd_ctx: commands.Context = None):
        """Set the command context for the event context."""
        _ctx_cmd.set(cmd_ctx)
        self.set(
            message=discord.PartialMessage(channel=cmd_ctx.channel, id=cmd_ctx.message.id),
            user=cmd_ctx.author,
            channel=cmd_ctx.channel,
            guild=cmd_ctx.guild,
        )
        return self

    def event_hook(self, event_name: str, *args, **_kwargs):
        """Sets the event value and runs the event hook if one is registered."""
        hook = self.set_event(event_name)
        if hook:
            hook(self, *args)

    @staticmethod
    def register_hook(event: str):
        """Adds a callable to handle registering context variables for a specific event type."""
        def decorator(func):
            EventContext.hooks[event] = func
            return func
        return decorator

    @contextmanager
    def fallback(
        self,
        *,
        message: discord.PartialMessage = None,
        emoji: Emoji = None,
        user: MemberUser = None,
        channel: discord.abc.Messageable = None,
        guild: discord.Guild = None,
    ):
        """Sets the given context values if isn't already set."""
        tokens = dict()
        if not self.message:
            tokens[_ctx_message] = _ctx_message.set(message)
        if not self.emoji:
            tokens[_ctx_emoji] = _ctx_emoji.set(emoji)
        if not self.user:
            tokens[_ctx_user] = _ctx_user.set(self.ensure_member(user, guild=guild or self.guild))
        if not self.channel:
            tokens[_ctx_channel] = _ctx_channel.set(channel)
        if not self.guild:
            tokens[_ctx_guild] = _ctx_guild.set(guild)
        try:
            yield
        finally:
            for ctx, token in tokens.items():
                ctx.reset(token)

    @contextmanager
    def ephemeral(
        self,
        *,
        message: discord.PartialMessage = None,
        emoji: Emoji = None,
        user: MemberUser = None,
        channel: discord.abc.Messageable = None,
        guild: discord.Guild = None
    ):
        """Sets the given context values, overriding existing values."""
        tokens = dict()
        if message:
            tokens[_ctx_message] = _ctx_message.set(message)
        if emoji:
            tokens[_ctx_emoji] = _ctx_emoji.set(message)
        if user:
            tokens[_ctx_user] = _ctx_user.set(self.ensure_member(user, guild=guild or self.guild))
        if channel:
            tokens[_ctx_channel] = _ctx_channel.set(channel)
        if guild:
            tokens[_ctx_guild] = _ctx_guild.set(guild)
        try:
            yield
        finally:
            for ctx, token in tokens.items():
                ctx.reset(token)

    def get_member_instances(self, user: discord.User):
        return [guild.get_member(user.id) for guild in self.bot.guilds if guild.get_member(user.id)]

    def ensure_member(self, user, *, guild: discord.Guild = None) -> t.Optional[MemberUser]:
        if isinstance(user, discord.Member):
            return user

        if isinstance(user, int):
            user: discord.User = self.bot.get_user(user)
            if not user:
                return None

        if guild:
            member = guild.get_member(user.id)
            return member or user

        member_instances = self.get_member_instances(user)
        if len(member_instances) == 1:
            return member_instances[0]

        return user
