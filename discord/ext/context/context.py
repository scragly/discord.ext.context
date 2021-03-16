from __future__ import annotations

import typing as t
from contextlib import contextmanager

from contextvars import ContextVar

import discord
from discord.ext import commands

from .types import MemberUser, Emoji

_ctx_message: ContextVar[t.Optional[discord.PartialMessage]] = ContextVar("message")
_ctx_emoji: ContextVar[t.Optional[discord.PartialMessage]] = ContextVar("emoji")
_ctx_user: ContextVar[t.Optional[MemberUser]] = ContextVar("user")
_ctx_channel: ContextVar[t.Optional[discord.abc.Messageable]] = ContextVar("channel")
_ctx_guild: ContextVar[t.Optional[discord.Guild]] = ContextVar("guild")
_ctx_cmd: ContextVar[t.Optional[commands.Context]] = ContextVar("cmd_ctx")
_ctx_event: ContextVar[t.Optional[str]] = ContextVar("event")
_ctx_client: ContextVar[t.Optional[discord.Client]] = ContextVar("client")


class ContextNotSet(Exception):
    """Raised when an EventContext value was accessed before it was set."""
    pass


class _NoValue:
    pass


class EventContext:
    """Holder and manager for all context values originating from triggered discord.py events."""

    hooks: t.Dict[str, t.Callable] = dict()
    ctx = None

    def __new__(cls, *args, **kwds):
        """Set the class to act as a singleton."""
        if cls.ctx is not None:
            return cls.ctx
        cls.ctx = object.__new__(cls)
        return cls.ctx

    def __repr__(self):
        """A representative view of the current context."""
        ctx_previews = []
        with self.default(None):
            if self.event:
                ctx_previews.append(f"event='{self.event}'")
            if self.message:
                ctx_previews.append(f"message={self.message.id}")
            if self.emoji:
                ctx_previews.append(f"emoji='{self.emoji.name}'")
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
            with self.default(None):
                raise ContextNotSet(f"Event '{self.event}' does not set a value for `ctx.message`.")

    @property
    def emoji(self) -> t.Optional[Emoji]:
        """The current emoji in context."""
        try:
            return _ctx_emoji.get()
        except KeyError:
            with self.default(None):
                raise ContextNotSet(f"Event '{self.event}' does not set a value for `ctx.emoji`.")

    @property
    def user(self) -> t.Optional[MemberUser]:
        """The current user in context."""
        try:
            return _ctx_user.get()
        except KeyError:
            with self.default(None):
                raise ContextNotSet(f"Event '{self.event}' does not set a value for `ctx.user`.")

    @property
    def channel(self) -> t.Optional[discord.abc.Messageable]:
        """The current channel in context."""
        try:
            return _ctx_channel.get()
        except KeyError:
            with self.default(None):
                raise ContextNotSet(f"Event '{self.event}' does not set a value for `ctx.channel`.")

    @property
    def guild(self) -> t.Optional[discord.Guild]:
        """The current guild in context."""
        try:
            return _ctx_guild.get()
        except KeyError:
            with self.default(None):
                raise ContextNotSet(f"Event '{self.event}' does not set a value for `ctx.guild`.")

    @property
    def cmd_ctx(self) -> t.Optional[commands.Context]:
        """The current command context instance."""
        try:
            return _ctx_cmd.get()
        except KeyError:
            with self.default(None):
                raise ContextNotSet(f"Only 'command' events will set the `ctx.cmd_ctx` value, not '{self.event}' event.")

    @property
    def event(self) -> t.Optional[str]:
        """The current event in context."""
        try:
            return _ctx_event.get()
        except KeyError:
            with self.default(None):
                raise ContextNotSet(f"EventContext has no origin event in the current call stack.")

    @property
    def client(self) -> t.Optional[discord.Client]:
        """The current discord.py client in context."""
        try:
            return _ctx_client.get()
        except KeyError:
            with self.default(None):
                raise ContextNotSet(f"Event '{self.event}' does not set a value for `ctx.client`.")

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

    def set_cmd_ctx(self, cmd_ctx: commands.Context):
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
    def default(
        self,
        all_default: t.Any = _NoValue,
        *,
        message: discord.PartialMessage = _NoValue,
        emoji: Emoji = _NoValue,
        user: MemberUser = _NoValue,
        channel: discord.abc.Messageable = _NoValue,
        guild: discord.Guild = _NoValue,
        cmd_ext: commands.Context = _NoValue,
    ):
        """Sets the given context values if isn't already set."""
        tokens = dict()

        message_default = message if message is not _NoValue else all_default
        emoji_default = emoji if emoji is not _NoValue else all_default
        user_default = user if user is not _NoValue else all_default
        channel_default = channel if channel is not _NoValue else all_default
        guild_default = guild if guild is not _NoValue else all_default
        cmd_ext_default = cmd_ext if cmd_ext is not _NoValue else all_default

        if (message_default is not _NoValue) and (_ctx_message.get(_NoValue) is not _NoValue):
            tokens[_ctx_message] = _ctx_message.set(message_default)
        if (emoji_default is not _NoValue) and (_ctx_emoji.get(_NoValue) is not _NoValue):
            tokens[_ctx_emoji] = _ctx_emoji.set(emoji_default)
        if (user_default is not _NoValue) and (_ctx_user.get(_NoValue) is not _NoValue):
            tokens[_ctx_user] = _ctx_user.set(self.ensure_member(user_default, guild=guild or self.guild))
        if (channel_default is not _NoValue) and (_ctx_channel.get(_NoValue) is not _NoValue):
            tokens[_ctx_channel] = _ctx_channel.set(channel_default)
        if (guild_default is not _NoValue) and (_ctx_guild.get(_NoValue) is not _NoValue):
            tokens[_ctx_guild] = _ctx_guild.set(guild_default)
        if (cmd_ext_default is not _NoValue) and (_ctx_cmd.get(_NoValue) is not _NoValue):
            tokens[_ctx_cmd] = _ctx_cmd.set(guild_default)
        try:
            yield
        finally:
            for ctx, token in tokens.items():
                ctx.reset(token)

    @contextmanager
    def ephemeral(
        self,
        *,
        message: discord.PartialMessage = _NoValue,
        emoji: Emoji = _NoValue,
        user: MemberUser = _NoValue,
        channel: discord.abc.Messageable = _NoValue,
        guild: discord.Guild = _NoValue,
        cmd_ext: commands.Context = _NoValue,
    ):
        """Sets the given context values, overriding existing values."""
        tokens = dict()
        if message is not _NoValue:
            tokens[_ctx_message] = _ctx_message.set(message)
        if emoji is not _NoValue:
            tokens[_ctx_emoji] = _ctx_emoji.set(message)
        if user is not _NoValue:
            tokens[_ctx_user] = _ctx_user.set(self.ensure_member(user, guild=guild or self.guild))
        if channel is not _NoValue:
            tokens[_ctx_channel] = _ctx_channel.set(channel)
        if guild is not _NoValue:
            tokens[_ctx_guild] = _ctx_guild.set(guild)
        if cmd_ext is not _NoValue:
            tokens[_ctx_cmd] = _ctx_cmd.set(cmd_ext)
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
