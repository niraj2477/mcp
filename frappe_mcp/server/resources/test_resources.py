from __future__ import annotations

import base64
from collections import OrderedDict

import pytest

from frappe_mcp.server.resources import ResourceOptions, get_resource
from frappe_mcp.server.resources.handlers import (
    handle_list_resource_templates,
    handle_list_resources,
    handle_read_resource,
)

APP_MIME_TYPE = 'text/html;profile=mcp-app'
UI_META = {'ui': {'csp': {'connectDomains': []}, 'prefersBorder': True}}


def _registry(*resources):
    return OrderedDict((r['uri'], r) for r in resources)


# ---------------------------------------------------------------------------
# get_resource
# ---------------------------------------------------------------------------


class TestGetResource:
    def test_name_from_function(self):
        def my_view():
            pass

        r = get_resource(my_view, 'ui://app/view')
        assert r['uri'] == 'ui://app/view'
        assert r['name'] == 'my_view'

    def test_description_from_docstring(self):
        def my_view():
            """Interactive view."""

        r = get_resource(my_view, 'ui://app/view')
        assert r['description'] == 'Interactive view.'

    def test_options_override_defaults(self):
        def my_view():
            """Interactive view."""

        r = get_resource(
            my_view,
            'ui://app/view',
            ResourceOptions(
                name='custom',
                title='Custom View',
                description='Custom desc',
                mime_type=APP_MIME_TYPE,
                meta=UI_META,
            ),
        )
        assert r['name'] == 'custom'
        assert r['title'] == 'Custom View'
        assert r['description'] == 'Custom desc'
        assert r['mime_type'] == APP_MIME_TYPE
        assert r['meta'] == UI_META

    def test_optional_fields_default_to_none(self):
        def my_view():
            pass

        r = get_resource(my_view, 'ui://app/view')
        assert r['title'] is None
        assert r['description'] is None
        assert r['mime_type'] is None
        assert r['meta'] is None

    def test_fn_stored(self):
        def fn():
            pass

        assert get_resource(fn, 'ui://app/view')['fn'] is fn


# ---------------------------------------------------------------------------
# handle_list_resources
# ---------------------------------------------------------------------------


class TestHandleListResources:
    def test_empty_registry(self):
        assert handle_list_resources({}, OrderedDict()) == {'resources': []}

    def test_lists_registered_resources(self):
        def view():
            """Interactive view."""

        registry = _registry(
            get_resource(
                view,
                'ui://app/view',
                ResourceOptions(mime_type=APP_MIME_TYPE, meta=UI_META),
            )
        )

        result = handle_list_resources({}, registry)
        assert result == {
            'resources': [
                {
                    'uri': 'ui://app/view',
                    'name': 'view',
                    'description': 'Interactive view.',
                    'mimeType': APP_MIME_TYPE,
                    '_meta': UI_META,
                }
            ]
        }

    def test_omits_unset_fields(self):
        def view():
            pass

        result = handle_list_resources({}, _registry(get_resource(view, 'ui://a')))
        assert result['resources'] == [{'uri': 'ui://a', 'name': 'view'}]


# ---------------------------------------------------------------------------
# handle_list_resource_templates
# ---------------------------------------------------------------------------


def test_list_resource_templates_is_empty():
    assert handle_list_resource_templates({}) == {'resourceTemplates': []}


# ---------------------------------------------------------------------------
# handle_read_resource
# ---------------------------------------------------------------------------


class TestHandleReadResource:
    def test_text_content(self):
        def view():
            return '<!DOCTYPE html><html></html>'

        registry = _registry(
            get_resource(
                view,
                'ui://app/view',
                ResourceOptions(mime_type=APP_MIME_TYPE, meta=UI_META),
            )
        )

        result = handle_read_resource({'uri': 'ui://app/view'}, registry)
        assert result == {
            'contents': [
                {
                    'uri': 'ui://app/view',
                    'mimeType': APP_MIME_TYPE,
                    'text': '<!DOCTYPE html><html></html>',
                    '_meta': UI_META,
                }
            ]
        }

    def test_bytes_content_is_base64_blob(self):
        def logo():
            return b'\x89PNG'

        registry = _registry(
            get_resource(logo, 'file://logo', ResourceOptions(mime_type='image/png'))
        )

        (contents,) = handle_read_resource({'uri': 'file://logo'}, registry)['contents']
        assert base64.b64decode(contents['blob']) == b'\x89PNG'
        assert contents['mimeType'] == 'image/png'
        assert 'text' not in contents
        assert '_meta' not in contents

    def test_unknown_uri_raises(self):
        with pytest.raises(ValueError, match='not found'):
            handle_read_resource({'uri': 'ui://missing'}, OrderedDict())

    def test_invalid_return_type_raises(self):
        def bad():
            return {'not': 'content'}

        registry = _registry(get_resource(bad, 'ui://bad'))
        with pytest.raises(ValueError, match='must return str or bytes'):
            handle_read_resource({'uri': 'ui://bad'}, registry)

    def test_missing_uri_raises(self):
        with pytest.raises(ValueError):
            handle_read_resource({}, OrderedDict())
