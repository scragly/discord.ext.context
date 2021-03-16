# discord.ext.context

A globally accessible context object for discord.py events.

Able to be used in both base clients and the commands extension.

## Installation
```shell
pip install discord.ext.context
```

## Requirements
- Python 3.7+
- [discord.py 1.6+](https://pypi.org/project/discord.py/)

## Register a Discord bot/client

Subclass the `context.ContextClient` base class, ensuring that it's first in inheritance order.

```python
import discord
from discord.ext import context

class Client(context.ContextClient, discord.Client):
    ...
```

## Using EventContext

Import `context.ctx` from anywhere, and it'll have its attributes set based on the event that your call stack originates from.

```python
import discord
from discord.ext.context import ctx

async def log_reaction():
    await ctx.channel.send(f"{ctx.user} reacted with {ctx.emoji}")

client = discord.Client()
    
@client.event
async def on_raw_reaction_add():
    await log_reaction()
```

## Exceptions
### `ContextNotSet`
Accessing a context value before it's set will have this exception raised. To have a fallback value used instead, use the contextmanager [`with ctx.default():`](https://github.com/scragly/discord.ext.context#ctxdefaultall_default--message_novalue-emoji_novalue-user_novalue-channel_novalue-guild_novalue-cmd_ext_novalue).

## Attributes

### `ctx.message`: [`discord.PartialMessage`](https://discordpy.readthedocs.io/en/latest/api.html#discord.PartialMessage)
Should always be a `PartialMessage`. If a `Message` instance is needed, an up to date copy can be retrieved with `PartialMessage.fetch()`.

### `ctx.emoji`: [`discord.Emoji`](https://discordpy.readthedocs.io/en/latest/api.html#discord.Emoji) or [`discord.PartialEmoji`](https://discordpy.readthedocs.io/en/latest/api.html#discord.PartialEmoji)
Often representing a reaction interacted with by a user; useful for user interactions that use reaction-based sessions.

### `ctx.channel`: [`discord.abc.Messageable`](https://discordpy.readthedocs.io/en/latest/api.html#discord.abc.Messageable)
Will always be a text channel or user-type object that's possible to send messages to. Does not include voice channels.

### `ctx.user`: [`discord.Member`](https://discordpy.readthedocs.io/en/latest/api.html#discord.Member) or [`discord.User`](https://discordpy.readthedocs.io/en/latest/api.html#discord.User)
If setting a `discord.User` instance and the user shares only a single guild with the client, it'll replace it with the `discord.Member` instance.

### `ctx.guild`: [`discord.Guild`](https://discordpy.readthedocs.io/en/latest/api.html#discord.Guild)
Will only be set on guild-specific events.

### `ctx.cmd_ctx`: [`discord.ext.commands.Context`](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context)
Will only be set on the command event, with other EventContext values being set using it.

### `ctx.event`: `str`
The name of the event type this context originates from.

### `ctx.client`: [`discord.Client`](https://discordpy.readthedocs.io/en/latest/api.html#discord.Client)
The instance of the discord.py client being hooked into.

### `ctx.bot`: [`discord.Client`](https://discordpy.readthedocs.io/en/latest/api.html#discord.Client)
Alias for `ctx.client`.

## Methods

### `ctx.set(*, message=None, emoji=None, user=None, channel=None, guild=None)`
Sets the values for the current context to be used across future call stacks. Won't impact asynchronous calls from other events.

### `@ctx.register_hook(event)`
Decorator for registering an event to be handled by the decorated function. Will override existing hooks if a duplicate exists.

### `ctx.default(all_default, *, message=_NoValue, emoji=_NoValue, user=_NoValue, channel=_NoValue, guild=_NoValue, cmd_ext=_NoValue)`
Context manager for registering default values to be used if a value isn't set. On leaving the context manager's scope, `ctx` will revert to original state.

Use `all_default` to set all the available ctx.values to the one value. This can be useful for allowing None to be returned for nonset contexts.

#### Examples
```python
with ctx.default(None):
    if ctx.channel:
        await ctx.channel.send("Yes")
```

```python
with ctx.default(channel=fallback_channel, user=None):
    if ctx.user:
        await ctx.channel.send(f"{ctx.user.display_name}")
```

If `ctx.channel` or `ctx.user` is not yet set, it'll be assigned the fallback arguments. This includes being able to set a value to `None` instead of raising `ContextNotSet`.

It can also be used as a decorator for a function.

```python
@ctx.default(channel=fallback_channel, user=None)
async def show_name():
    if ctx.user:
        await ctx.channel.send(f"{ctx.user.display_name}")
```

### `ctx.ephemeral(*, message=_NoValue, emoji=_NoValue, user=_NoValue, channel=_NoValue, guild=_NoValue, cmd_ext=_NoValue)`
Context manager for overriding context values. On leaving the context manager's scope, `ctx` will revert to original state.

### Examples
```python
with ctx.ephemeral(channel=log_channel, user=None):
    if ctx.user:
        await ctx.channel.send(f"{ctx.user.display_name} did a thing.")
```

If `ctx.channel` or `ctx.user` is not yet set, it'll be assigned the fallback arguments. This includes being able to set a value to `None` instead of raising `ContextNotSet`.

It can also be used as a decorator for a function.

```python
@ctx.ephemeral(channel=log_channel, user=None)
async def show_name():
    if ctx.user:
        await ctx.channel.send(f"{ctx.user.display_name} did a thing.")
```

## Events

By default, the following events are hooked by EventContext:

### Messages
- `message`
- `message_delete`
- `message_edit`
- `raw_message_delete`
- `raw_message_edit`

### Reactions
- `reaction_add`
- `reaction_remove`
- `raw_reaction_add`
- `raw_reaction_remove`
- `reaction_clear`
- `reaction_clear_emoji`
- `raw_reaction_clear`
- `raw_reaction_clear_emoji`

### Channels
- `typing`
- `guild_channel_update`
- `guild_channel_create`
- `guild_channel_delete`
- `guild_channel_pins_update`
- `webhooks_update`

### Guilds
- `guild_update`
- `guild_join`
- `guild_remove`
- `guild_integrations_update`
- `guild_emojis_update`
- `guild_available`
- `guild_unavailable`

### Members
- `member_update`
- `member_join`
- `member_remove`
- `member_ban_hook`
- `member_unban_hook`

### Roles
- `guild_role_update_hook`
- `guild_role_create_hook`
- `guild_role_delete_hook`

### Commands
- `command`


You can add more event hooks or replace the default ones with the decorator:
```python
@EventContext.register_hook(event_name)
def event_hook(*args, **kwargs):
    ...
```
