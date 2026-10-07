from __future__ import annotations


def handle_initialize(params, name: str, has_resources: bool = False):
    """
    Handles the initialize request from the client.

    Resources are only advertised when some are registered, so servers without
    any don't send clients looking for them.
    """
    capabilities = {
        'tools': {'listChanged': False},
        'prompts': {'listChanged': False},
        # Not yet implemented
        # "completions": {},
        # "logging": {},
    }
    if has_resources:
        capabilities['resources'] = {'subscribe': False, 'listChanged': False}

    return {
        'protocolVersion': '2025-03-26',
        # "protocolVersion": "2024-11-05",
        'serverInfo': {'name': name, 'version': '0.1.0'},
        'capabilities': capabilities,
    }


def handle_ping(_):
    """
    Handles the ping request from the client.
    https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/ping#ping
    """
    return {}


def handle_complete(_params):
    raise NotImplementedError('handle_complete not implemented')


def handle_set_level(_params):
    raise NotImplementedError('handle_set_level not implemented')


def handle_subscribe(_params):
    raise NotImplementedError('handle_subscribe not implemented')


def handle_unsubscribe(_params):
    raise NotImplementedError('handle_unsubscribe not implemented')


def handle_cancelled(_params): ...
def handle_progress(_params): ...
def handle_initialized(_params): ...
def handle_roots_list_changed(_params): ...
