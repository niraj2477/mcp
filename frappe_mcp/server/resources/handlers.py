from __future__ import annotations

import base64
from collections import OrderedDict

from frappe_mcp.server import types


def handle_list_resources(params, resource_registry: OrderedDict) -> dict:
    types.ListResourcesRequestParams.model_validate(params)
    resource_list = [
        types.Resource(
            uri=resource_info['uri'],
            name=resource_info['name'],
            title=resource_info.get('title'),
            description=resource_info.get('description'),
            mimeType=resource_info.get('mime_type'),
            meta=resource_info.get('meta'),
        )
        for resource_info in resource_registry.values()
    ]
    result = types.ListResourcesResult(resources=resource_list)
    return result.model_dump(exclude_none=True, by_alias=True)


def handle_list_resource_templates(params) -> dict:
    # URI templates are not supported, so there are never any to list.
    types.ListResourceTemplatesRequestParams.model_validate(params)
    result = types.ListResourceTemplatesResult(resourceTemplates=[])
    return result.model_dump(exclude_none=True, by_alias=True)


def handle_read_resource(params, resource_registry: OrderedDict) -> dict:
    read_params = types.ReadResourceRequestParams.model_validate(params)
    uri = read_params.uri

    if uri not in resource_registry:
        raise ValueError(f"Resource '{uri}' not found.")

    resource_info = resource_registry[uri]
    data = resource_info['fn']()
    mime_type = resource_info.get('mime_type')
    # Repeated on the content item: MCP Apps hosts read `_meta.ui` (CSP, border)
    # from resources/read and fall back to the resources/list entry.
    meta = resource_info.get('meta')

    if isinstance(data, str):
        contents = types.TextResourceContents(
            uri=uri, mimeType=mime_type, text=data, meta=meta
        )
    elif isinstance(data, bytes):
        contents = types.BlobResourceContents(
            uri=uri,
            mimeType=mime_type,
            blob=base64.b64encode(data).decode('ascii'),
            meta=meta,
        )
    else:
        raise ValueError(
            f"Resource '{uri}' must return str or bytes, got {type(data).__name__}."
        )

    result = types.ReadResourceResult(contents=[contents])
    return result.model_dump(exclude_none=True, by_alias=True)
