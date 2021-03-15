from .context import EventContext


class ContextClient:
    """Class to be subclassed by discord.py Client to register EventContext hooks."""
    def __init__(self, *args, **kwargs):
        # noinspection PyTypeChecker
        EventContext.ctx.set_client(self)
        super().__init__(*args, **kwargs)

    def dispatch(self, event_name, *args, **kwargs):
        EventContext.ctx.event_hook(event_name, *args, **kwargs)
        super().dispatch(event_name, *args, **kwargs)
