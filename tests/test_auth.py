import unittest
import tornado.httpclient
import splunktornado.auth as auth_module

try:
    from urllib.parse import parse_qs, urlsplit
except ImportError:
    from urlparse import parse_qs, urlsplit

from splunktornado.auth import SplunkMixin


class DummyHandler(SplunkMixin):
    settings = {"splunk_host_path": "https://splunk.example:8089"}

    def __init__(self):
        self.application = type("Application", (), {})()

    def require_setting(self, name, feature):
        if name not in self.settings:
            raise RuntimeError("%s missing for %s" % (name, feature))


class Response(object):
    def __init__(self, content_type, body, error=None):
        self.headers = {"Content-Type": content_type}
        self.body = body
        self.error = error


class FakeHTTPError(object):
    def __init__(self, code):
        self.code = code


class FakeHTTPClient(object):
    instances = []
    response = Response("text/plain", b"ok")

    def __init__(self):
        self.calls = []
        self.closed = False
        self.instances.append(self)

    def fetch(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response

    def close(self):
        self.closed = True


class SplunkMixinTests(unittest.TestCase):
    def test_parse_response_decodes_json(self):
        response = Response("application/json", b'{"ok": true}')

        xml, payload, text = SplunkMixin().parse_response(response)

        self.assertIsNone(xml)
        self.assertEqual({"ok": True}, payload)
        self.assertIsNone(text)

    def test_parse_response_normalizes_json_content_type(self):
        response = Response("Application/JSON; charset=utf-8", b'{"ok": true}')

        xml, payload, text = SplunkMixin().parse_response(response)

        self.assertIsNone(xml)
        self.assertEqual({"ok": True}, payload)
        self.assertIsNone(text)

    def test_parse_response_decodes_application_xml(self):
        response = Response("Application/XML; charset=utf-8", b"<response />")

        xml, payload, text = SplunkMixin().parse_response(response)

        self.assertEqual("response", xml.tag)
        self.assertIsNone(payload)
        self.assertIsNone(text)

    def test_parse_response_ignores_near_match_content_types(self):
        response = Response("application/jsonp", b'{"ok": true}')

        xml, payload, text = SplunkMixin().parse_response(response)

        self.assertIsNone(xml)
        self.assertIsNone(payload)
        self.assertIsNone(text)

    def test_parse_response_passes_safe_xml_parser(self):
        response = Response("text/xml", b"<response />")
        calls = []
        original_fromstring = auth_module.et.fromstring

        def fromstring(body, parser=None):
            calls.append((body, parser))
            return original_fromstring(b"<response />", parser=parser)

        auth_module.et.fromstring = fromstring
        try:
            xml, payload, text = SplunkMixin().parse_response(response)
        finally:
            auth_module.et.fromstring = original_fromstring

        self.assertEqual("response", xml.tag)
        self.assertIsNone(payload)
        self.assertIsNone(text)
        self.assertEqual(b"<response />", calls[0][0])
        self.assertIsNotNone(calls[0][1])

    def test_parse_response_does_not_resolve_xml_entities(self):
        body = (
            b'<!DOCTYPE response ['
            b'<!ENTITY external SYSTEM "file:///etc/passwd">'
            b']><response>&external;</response>'
        )

        xml, payload, text = SplunkMixin().parse_response(Response("text/xml", body))

        self.assertIsNotNone(xml)
        self.assertIsNone(xml.text)
        self.assertEqual("response", xml.tag)
        self.assertIsNone(payload)
        self.assertIsNone(text)

    def test_parse_response_returns_empty_result_for_invalid_xml(self):
        response = Response("text/xml", b"<response>")

        xml, payload, text = SplunkMixin().parse_response(response)

        self.assertIsNone(xml)
        self.assertIsNone(payload)
        self.assertIsNone(text)

    def test_parse_response_returns_empty_result_for_invalid_json(self):
        response = Response("application/json", b"{")

        xml, payload, text = SplunkMixin().parse_response(response)

        self.assertIsNone(xml)
        self.assertIsNone(payload)
        self.assertIsNone(text)

    def test_request_url_encodes_query_parameters(self):
        handler = DummyHandler()

        url = handler.request_url(
            "/services/search/jobs",
            search="index=main status=200",
            earliest_time="-15m",
        )

        parts = urlsplit(url)
        self.assertEqual("https://splunk.example:8089/services/search/jobs", parts.scheme + "://" + parts.netloc + parts.path)
        self.assertEqual(
            {
                "search": ["index=main status=200"],
                "earliest_time": ["-15m"],
            },
            parse_qs(parts.query),
        )

    def test_request_url_encodes_repeated_query_parameters(self):
        handler = DummyHandler()

        url = handler.request_url(
            "/services/search/jobs",
            f=["host", "source"],
        )

        parts = urlsplit(url)
        self.assertEqual(
            {"f": ["host", "source"]},
            parse_qs(parts.query),
        )

    def test_request_headers_rejects_newline_session_key(self):
        handler = DummyHandler()

        with self.assertRaises(ValueError):
            handler.request_headers(session_key="abc\r\nX-Splunk-User: admin")

    def test_sync_request_preserves_error_responses_and_closes_client(self):
        handler = DummyHandler()
        original_client = tornado.httpclient.HTTPClient
        FakeHTTPClient.instances = []
        FakeHTTPClient.response = Response("text/plain", b"ok")
        tornado.httpclient.HTTPClient = FakeHTTPClient
        try:
            response, xml, payload, text = handler.sync_request(
                "/services/search/jobs",
                post_args={"search": "index=main"},
                session_key="abc123",
            )
        finally:
            tornado.httpclient.HTTPClient = original_client
            FakeHTTPClient.response = Response("text/plain", b"ok")

        self.assertIsNone(response.error)
        self.assertIsNone(xml)
        self.assertIsNone(payload)
        self.assertEqual(b"ok", text)
        self.assertEqual(1, len(FakeHTTPClient.instances))
        client = FakeHTTPClient.instances[0]
        self.assertTrue(client.closed)
        self.assertEqual(1, len(client.calls))
        url, kwargs = client.calls[0]
        self.assertEqual("https://splunk.example:8089/services/search/jobs", url)
        self.assertEqual(False, kwargs["raise_error"])
        self.assertEqual("POST", kwargs["method"])
        self.assertEqual("search=index%3Dmain", kwargs["body"])
        self.assertEqual({"Authorization": "Splunk abc123"}, kwargs["headers"])

    def test_sync_request_encodes_repeated_post_parameters(self):
        handler = DummyHandler()
        original_client = tornado.httpclient.HTTPClient
        FakeHTTPClient.instances = []
        FakeHTTPClient.response = Response("text/plain", b"ok")
        tornado.httpclient.HTTPClient = FakeHTTPClient
        try:
            handler.sync_request(
                "/services/search/jobs",
                post_args={"f": ["host", "source"]},
                session_key="abc123",
            )
        finally:
            tornado.httpclient.HTTPClient = original_client
            FakeHTTPClient.response = Response("text/plain", b"ok")

        body = FakeHTTPClient.instances[0].calls[0][1]["body"]
        self.assertEqual(["host", "source"], parse_qs(body)["f"])

    def test_sync_request_retries_unauthorized_once(self):
        handler = DummyHandler()
        handler.session_key = "stale"
        refreshes = []

        def refresh_session_key():
            refreshes.append(True)
            handler.session_key = "fresh"

        handler.refresh_session_key = refresh_session_key

        original_client = tornado.httpclient.HTTPClient
        FakeHTTPClient.instances = []
        FakeHTTPClient.response = Response("text/plain", b"unauthorized", error=FakeHTTPError(401))
        tornado.httpclient.HTTPClient = FakeHTTPClient
        try:
            response, xml, payload, text = handler.sync_request(
                "/services/search/jobs",
                session_key=handler.session_key,
            )
        finally:
            tornado.httpclient.HTTPClient = original_client
            FakeHTTPClient.response = Response("text/plain", b"ok")

        self.assertEqual(401, response.error.code)
        self.assertIsNone(xml)
        self.assertIsNone(payload)
        self.assertEqual(b"unauthorized", text)
        self.assertEqual([True], refreshes)
        self.assertEqual(2, len(FakeHTTPClient.instances))
        self.assertEqual(
            {"Authorization": "Splunk stale"},
            FakeHTTPClient.instances[0].calls[0][1]["headers"],
        )
        self.assertEqual(
            {"Authorization": "Splunk fresh"},
            FakeHTTPClient.instances[1].calls[0][1]["headers"],
        )

    def test_sync_request_does_not_retry_without_refreshed_session_key(self):
        handler = DummyHandler()
        handler.session_key = "stale"
        refreshes = []

        def refresh_session_key():
            refreshes.append(True)
            handler.session_key = None

        handler.refresh_session_key = refresh_session_key

        original_client = tornado.httpclient.HTTPClient
        FakeHTTPClient.instances = []
        FakeHTTPClient.response = Response("text/plain", b"unauthorized", error=FakeHTTPError(401))
        tornado.httpclient.HTTPClient = FakeHTTPClient
        try:
            response, xml, payload, text = handler.sync_request(
                "/services/search/jobs",
                session_key=handler.session_key,
            )
        finally:
            tornado.httpclient.HTTPClient = original_client
            FakeHTTPClient.response = Response("text/plain", b"ok")

        self.assertEqual(401, response.error.code)
        self.assertIsNone(xml)
        self.assertIsNone(payload)
        self.assertEqual(b"unauthorized", text)
        self.assertEqual([True], refreshes)
        self.assertEqual(1, len(FakeHTTPClient.instances))
        self.assertEqual(
            {"Authorization": "Splunk stale"},
            FakeHTTPClient.instances[0].calls[0][1]["headers"],
        )

    def test_async_request_retries_unauthorized_once(self):
        handler = DummyHandler()
        handler.session_key = "fresh"
        handler.request = type("Request", (), {
            "connection": type("Connection", (), {
                "stream": type("Stream", (), {"closed": lambda self: False})()
            })()
        })()
        async_calls = []
        refreshes = []

        def async_request(*args, **kwargs):
            async_calls.append((args, kwargs))

        handler.async_request = async_request
        handler.refresh_session_key = lambda: refreshes.append(True)
        callback_calls = []

        handler._on_async_response(
            "/services/search/jobs",
            lambda response, **kwargs: callback_calls.append((response, kwargs)),
            Response("text/plain", b"unauthorized", error=FakeHTTPError(401)),
            request_timeout=9.0,
            search="index=main",
        )

        self.assertEqual([], callback_calls)
        self.assertEqual([True], refreshes)
        self.assertEqual(1, len(async_calls))
        args, kwargs = async_calls[0]
        self.assertEqual("/services/search/jobs", args[0])
        self.assertEqual("fresh", kwargs["session_key"])
        self.assertEqual(9.0, kwargs["request_timeout"])
        self.assertEqual(False, kwargs["retry_on_unauthorized"])
        self.assertEqual("index=main", kwargs["search"])


if __name__ == "__main__":
    unittest.main()
