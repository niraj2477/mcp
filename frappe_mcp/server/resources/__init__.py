from __future__ import annotations

from collections.abc import Callable
from inspect import getdoc
from typing import Any, TypedDict

from frappe_mcp.server.resources.handlers import (
    handle_list_resource_templates,
    handle_list_resources,
    handle_read_resource,
)

__all__ = [
    'Resource',
    'ResourceOptions',
    'get_resource',
    'handle_list_resource_templates',
    'handle_list_resources',
    'handle_read_resource',
]


class Resource(TypedDict):
    uri: str
    name: str
    title: str | None
    description: str | None
    mime_type: str | None
    meta: dict[str, Any] | None
    fn: Callable


class ResourceOptions(TypedDict, total=False):
    name: str | None
    title: str | None
    description: str | None
    mime_type: str | None
    meta: dict[str, Any] | None


def get_resource(
    fn: Callable, uri: str, options: ResourceOptions | None = None
) -> Resource:
    if options is None:
        options = ResourceOptions()

    return Resource(
        fn=fn,
        uri=uri,
        name=options.get('name') or fn.__name__,
        title=options.get('title'),
        description=options.get('description') or getdoc(fn) or None,
        mime_type=options.get('mime_type'),
        meta=options.get('meta'),
    )
