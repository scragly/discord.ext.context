# discord.ext.context

A globally accessible context object for discord.py events.

Able to be used in both base clients and the commands extension.


## Register a bot/client

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
Accessing a context value before it's set will have this exception raised. To have a fallback value, 

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

### `ctx.fallback(*, message=None, emoji=None, user=None, channel=None, guild=None)`
Context manager for registering context values to be used in the case they're not already set. On leaving the context manager's scope, `ctx` will revert to original state.

#### Examples
```python
with ctx.fallback(channel=fallback_channel, user=None):
    if ctx.user:
        await ctx.channel.send(f"{ctx.user.display_name}")
```

If `ctx.channel` or `ctx.user` is not yet set, it'll be assigned the fallback arguments. This includes being able to set a value to `None` instead of raising `ContextNotSet`.

It can also be used as a decorator for a function.

```python
@ctx.fallback(channel=fallback_channel, user=None)
async def show_name():
    if ctx.user:
        await ctx.channel.send(f"{ctx.user.display_name}")
```

### `ctx.ephemeral(*, message=None, emoji=None, user=None, channel=None, guild=None)`
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
