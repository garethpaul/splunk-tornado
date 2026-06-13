import unittest
from functools import partial
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
        self.code = error.code if error is not None else 200


class FakeHTTPError(object):
    def __init__(self, code):
        self.code = code


class FakeHTTPClient(object):
    instances = []
    response = Response("text/plain", b"ok")

    def __init__(self, **kwargs):
        self.calls = []
        self.closed = False
        self.kwargs = kwargs
        self.instances.append(self)

    def fetch(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response

    def close(self):
        self.closed = True


class FakeFuture(object):
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    def add_done_callback(self, callback):
        callback(self)

    def result(self):
        if self.error is not None:
            raise self.error
        return self.response


class FakeAsyncHTTPClient(object):
    instances = []
    response = Response("text/plain", b"ok")
    fetch_error = None

    def __init__(self, **kwargs):
        self.calls = []
        self.closed = False
        self.kwargs = kwargs
        self.instances.append(self)

    def fetch(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.fetch_error is not None:
            raise self.fetch_error
        return FakeFuture(self.response)

    def close(self):
        self.closed = True


class SplunkMixinTests(unittest.TestCase):
    def test_request_timeout_accepts_positive_finite_real_values(self):
        handler = DummyHandler()
        handler.request = type("Request", (), {
            "connection": type("Connection", (), {
                "stream": type("Stream", (), {"closed": lambda self: False})()
            })()
        })()
        original_sync_client = tornado.httpclient.HTTPClient
        original_async_client = auth_module.SimpleAsyncHTTPClient
        tornado.httpclient.HTTPClient = FakeHTTPClient
        auth_module.SimpleAsyncHTTPClient = FakeAsyncHTTPClient
        try:
            for request_timeout in (1, 0.25):
                with self.subTest(path="sync", request_timeout=request_timeout):
                    FakeHTTPClient.instances = []
                    handler.sync_request(
                        "/services/search/jobs",
                        request_timeout=request_timeout,
                    )
                    self.assertEqual(
                        request_timeout,
                        FakeHTTPClient.instances[0].calls[0][1]["request_timeout"],
                    )

                with self.subTest(path="async", request_timeout=request_timeout):
                    FakeAsyncHTTPClient.instances = []
                    handler.async_request(
                        "/services/search/jobs",
                        lambda response, **kwargs: None,
                        request_timeout=request_timeout,
                    )
                    request = FakeAsyncHTTPClient.instances[0].calls[0][0]
                    self.assertEqual(request_timeout, request.request_timeout)
        finally:
            tornado.httpclient.HTTPClient = original_sync_client
            auth_module.SimpleAsyncHTTPClient = original_async_client

    def test_requests_reject_invalid_timeouts_before_client_construction(self):
        handler = DummyHandler()
        invalid_timeouts = (0, -1, float("inf"), float("-inf"), float("nan"), True, False, None, "5")
        original_sync_client = tornado.httpclient.HTTPClient
        original_async_client = auth_module.SimpleAsyncHTTPClient
        tornado.httpclient.HTTPClient = FakeHTTPClient
        auth_module.SimpleAsyncHTTPClient = FakeAsyncHTTPClient
        try:
            for request_timeout in invalid_timeouts:
                with self.subTest(path="sync", request_timeout=request_timeout):
                    FakeHTTPClient.instances = []
                    with self.assertRaisesRegex(
                        ValueError,
                        "request_timeout must be a positive finite real number",
                    ):
                        handler.sync_request(
                            "/services/search/jobs",
                            request_timeout=request_timeout,
                        )
                    self.assertEqual([], FakeHTTPClient.instances)

                with self.subTest(path="async", request_timeout=request_timeout):
                    FakeAsyncHTTPClient.instances = []
                    with self.assertRaisesRegex(
                        ValueError,
                        "request_timeout must be a positive finite real number",
                    ):
                        handler.async_request(
                            "/services/search/jobs",
                            lambda response, **kwargs: None,
                            request_timeout=request_timeout,
                        )
                    self.assertEqual([], FakeAsyncHTTPClient.instances)
        finally:
            tornado.httpclient.HTTPClient = original_sync_client
            auth_module.SimpleAsyncHTTPClient = original_async_client

    def test_parse_response_decodes_json(self):
        response = Response("application/json", b'{"ok": true}')

        xml, payload, text = SplunkMixin().parse_response(response)

        self.assertIsNone(xml)
        self.assertEqual({"ok": True}, payload)
        self.assertIsNone(text)

    def test_parse_response_accepts_body_at_limit(self):
        handler = SplunkMixin()
        handler.max_response_body_size = 2

        xml, payload, text = handler.parse_response(Response("text/plain", b"ok"))

        self.assertIsNone(xml)
        self.assertIsNone(payload)
        self.assertEqual(b"ok", text)

    def test_parse_response_rejects_oversized_supported_content_types(self):
        handler = SplunkMixin()
        handler.max_response_body_size = 2

        for content_type, body in (
            ("text/xml", b"<x>"),
            ("application/json", b"{} "),
            ("text/plain", b"abc"),
        ):
            with self.subTest(content_type=content_type):
                self.assertEqual(
                    (None, None, None),
                    handler.parse_response(Response(content_type, body)),
                )

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

    def test_request_headers_rejects_non_text_session_key(self):
        handler = DummyHandler()

        with self.assertRaises(ValueError):
            handler.request_headers(session_key=object())

    def test_request_session_key_accepts_safe_login_key(self):
        handler = DummyHandler()
        handler.settings = dict(
            DummyHandler.settings,
            splunk_username="user",
            splunk_password="password",
        )
        calls = []

        def sync_request(*args, **kwargs):
            calls.append((args, kwargs))
            xml = auth_module.et.fromstring(
                b"<response><sessionKey>fresh</sessionKey></response>"
            )
            return Response("text/xml", b""), xml, None, None

        handler.sync_request = sync_request

        self.assertEqual("fresh", handler.request_session_key())
        self.assertEqual("/services/auth/login", calls[0][0][0])
        self.assertEqual(False, calls[0][1]["retry_on_unauthorized"])

    def test_request_session_key_rejects_missing_or_unsafe_login_keys(self):
        handler = DummyHandler()
        handler.settings = dict(
            DummyHandler.settings,
            splunk_username="user",
            splunk_password="password",
        )

        for xml in (
            auth_module.et.fromstring(b"<response />"),
            auth_module.et.fromstring(
                b"<response><sessionKey>bad\nkey</sessionKey></response>"
            ),
        ):
            with self.subTest(xml=auth_module.et.tostring(xml)):
                handler.sync_request = lambda *args, **kwargs: (
                    Response("text/xml", b""),
                    xml,
                    None,
                    None,
                )
                self.assertIsNone(handler.request_session_key())

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
        self.assertEqual(
            {
                "async_client_class": auth_module.SimpleAsyncHTTPClient,
                "max_body_size": handler.max_response_body_size,
            },
            client.kwargs,
        )
        self.assertEqual(1, len(client.calls))
        url, kwargs = client.calls[0]
        self.assertEqual("https://splunk.example:8089/services/search/jobs", url)
        self.assertEqual(False, kwargs["raise_error"])
        self.assertEqual(20.0, kwargs["request_timeout"])
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

    def test_sync_request_preserves_positional_retry_control_and_default_timeout(self):
        handler = DummyHandler()
        original_client = tornado.httpclient.HTTPClient
        FakeHTTPClient.instances = []
        FakeHTTPClient.response = Response("text/plain", b"unauthorized", error=FakeHTTPError(401))
        tornado.httpclient.HTTPClient = FakeHTTPClient
        handler.refresh_session_key = lambda: self.fail("disabled positional retry must be preserved")
        try:
            handler.sync_request("/services/search/jobs", None, None, False)
        finally:
            tornado.httpclient.HTTPClient = original_client
            FakeHTTPClient.response = Response("text/plain", b"ok")

        self.assertEqual(1, len(FakeHTTPClient.instances))
        self.assertEqual(20.0, FakeHTTPClient.instances[0].calls[0][1]["request_timeout"])

    def test_request_session_key_uses_default_sync_timeout(self):
        handler = DummyHandler()
        handler.settings = dict(handler.settings, splunk_username="user", splunk_password="password")
        original_client = tornado.httpclient.HTTPClient
        FakeHTTPClient.instances = []
        FakeHTTPClient.response = Response("text/xml", b"<response><sessionKey>fresh</sessionKey></response>")
        tornado.httpclient.HTTPClient = FakeHTTPClient
        try:
            self.assertEqual("fresh", handler.request_session_key())
        finally:
            tornado.httpclient.HTTPClient = original_client
            FakeHTTPClient.response = Response("text/plain", b"ok")

        self.assertEqual(20.0, FakeHTTPClient.instances[0].calls[0][1]["request_timeout"])

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
                request_timeout=9.0,
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
            [
                {"max_body_size": handler.max_response_body_size},
                {"max_body_size": handler.max_response_body_size},
            ],
            [
                {"max_body_size": client.kwargs["max_body_size"]}
                for client in FakeHTTPClient.instances
            ],
        )
        self.assertEqual(
            {"Authorization": "Splunk stale"},
            FakeHTTPClient.instances[0].calls[0][1]["headers"],
        )
        self.assertEqual(
            {"Authorization": "Splunk fresh"},
            FakeHTTPClient.instances[1].calls[0][1]["headers"],
        )
        self.assertEqual(
            [9.0, 9.0],
            [client.calls[0][1]["request_timeout"] for client in FakeHTTPClient.instances],
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

    def test_async_request_uses_tornado_future_api(self):
        handler = DummyHandler()
        handler.request = type("Request", (), {
            "connection": type("Connection", (), {
                "stream": type("Stream", (), {"closed": lambda self: False})()
            })()
        })()
        callback_calls = []
        original_client = auth_module.SimpleAsyncHTTPClient
        FakeAsyncHTTPClient.instances = []
        auth_module.SimpleAsyncHTTPClient = FakeAsyncHTTPClient
        try:
            handler.async_request(
                "/services/search/jobs",
                lambda response, **kwargs: callback_calls.append((response, kwargs)),
                post_args={"search": "index=main"},
                session_key="abc123",
                request_timeout=9.0,
            )
        finally:
            auth_module.SimpleAsyncHTTPClient = original_client

        self.assertEqual(1, len(FakeAsyncHTTPClient.instances))
        client = FakeAsyncHTTPClient.instances[0]
        request, fetch_kwargs = client.calls[0]
        self.assertEqual(
            {
                "force_instance": True,
                "max_body_size": handler.max_response_body_size,
            },
            client.kwargs,
        )
        self.assertTrue(client.closed)
        self.assertEqual("https://splunk.example:8089/services/search/jobs", request.url)
        self.assertEqual({"raise_error": False}, fetch_kwargs)
        self.assertEqual("POST", request.method)
        self.assertEqual(b"search=index%3Dmain", request.body)
        self.assertEqual("Splunk abc123", request.headers["Authorization"])
        self.assertEqual(9.0, request.request_timeout)
        self.assertEqual(1, len(callback_calls))
        self.assertEqual(b"ok", callback_calls[0][1]["text"])

    def test_async_get_request_uses_no_body(self):
        handler = DummyHandler()
        handler.request = type("Request", (), {
            "connection": type("Connection", (), {
                "stream": type("Stream", (), {"closed": lambda self: False})()
            })()
        })()
        callback_calls = []
        original_client = auth_module.SimpleAsyncHTTPClient
        FakeAsyncHTTPClient.instances = []
        auth_module.SimpleAsyncHTTPClient = FakeAsyncHTTPClient
        try:
            handler.async_request(
                "/services/search/jobs",
                lambda response, **kwargs: callback_calls.append((response, kwargs)),
                session_key="abc123",
            )
        finally:
            auth_module.SimpleAsyncHTTPClient = original_client

        request, fetch_kwargs = FakeAsyncHTTPClient.instances[0].calls[0]
        self.assertEqual("GET", request.method)
        self.assertIsNone(request.body)
        self.assertEqual({"raise_error": False}, fetch_kwargs)
        self.assertEqual(1, len(callback_calls))
        self.assertEqual(b"ok", callback_calls[0][1]["text"])

    def test_async_request_preserves_streaming_callback_with_body_limit(self):
        handler = DummyHandler()
        handler.request = type("Request", (), {
            "connection": type("Connection", (), {
                "stream": type("Stream", (), {"closed": lambda self: False})()
            })()
        })()
        chunks = []
        def on_chunk(chunk):
            chunks.append(chunk)

        original_client = auth_module.SimpleAsyncHTTPClient
        FakeAsyncHTTPClient.instances = []
        auth_module.SimpleAsyncHTTPClient = FakeAsyncHTTPClient
        try:
            handler.async_request(
                "/services/search/jobs",
                lambda response, **kwargs: None,
                streaming_callback=on_chunk,
            )
        finally:
            auth_module.SimpleAsyncHTTPClient = original_client

        client = FakeAsyncHTTPClient.instances[0]
        request = client.calls[0][0]
        request.streaming_callback(b"chunk")
        self.assertEqual([b"chunk"], chunks)
        self.assertEqual(handler.max_response_body_size, client.kwargs["max_body_size"])
        self.assertTrue(client.closed)

    def test_async_request_reports_transport_failures_to_callback(self):
        handler = DummyHandler()
        handler.request = type("Request", (), {
            "connection": type("Connection", (), {
                "stream": type("Stream", (), {"closed": lambda self: False})()
            })()
        })()
        callback_calls = []
        request = tornado.httpclient.HTTPRequest("https://splunk.example:8089/services/search/jobs")
        error = ConnectionRefusedError("connection refused")
        response_callback = partial(
            handler._on_async_response,
            "/services/search/jobs",
            lambda response, **kwargs: callback_calls.append((response, kwargs)),
        )

        client = FakeAsyncHTTPClient()
        handler._on_async_fetch_complete(
            response_callback,
            request,
            client,
            FakeFuture(error=error),
        )

        self.assertEqual(1, len(callback_calls))
        response, kwargs = callback_calls[0]
        self.assertEqual({"xml": None, "json": None, "text": None}, kwargs)
        self.assertEqual(599, response.code)
        self.assertIs(error, response.error)
        self.assertEqual(request.url, response.effective_url)
        self.assertTrue(client.closed)

    def test_async_request_closes_client_when_fetch_raises_synchronously(self):
        handler = DummyHandler()
        original_client = auth_module.SimpleAsyncHTTPClient
        FakeAsyncHTTPClient.instances = []
        FakeAsyncHTTPClient.fetch_error = RuntimeError("fetch failed")
        auth_module.SimpleAsyncHTTPClient = FakeAsyncHTTPClient
        try:
            with self.assertRaisesRegex(RuntimeError, "fetch failed"):
                handler.async_request("/services/search/jobs", lambda response: None)
        finally:
            auth_module.SimpleAsyncHTTPClient = original_client
            FakeAsyncHTTPClient.fetch_error = None

        self.assertEqual(1, len(FakeAsyncHTTPClient.instances))
        self.assertTrue(FakeAsyncHTTPClient.instances[0].closed)

    def test_async_request_retries_unauthorized_once(self):
        handler = DummyHandler()
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
        handler.refresh_session_key = lambda: self.fail("async retry must not block on sync refresh")
        handler._request_session_key_async = lambda callback: (
            refreshes.append(True),
            callback("fresh"),
        )
        callback_calls = []
        streaming_callback = lambda chunk: None

        handler._on_async_response(
            "/services/search/jobs",
            lambda response, **kwargs: callback_calls.append((response, kwargs)),
            Response("text/plain", b"unauthorized", error=FakeHTTPError(401)),
            post_args={"search": "index=main"},
            streaming_callback=streaming_callback,
            request_timeout=9.0,
            output_mode="json",
        )

        self.assertEqual([], callback_calls)
        self.assertEqual([True], refreshes)
        self.assertEqual(1, len(async_calls))
        args, kwargs = async_calls[0]
        self.assertEqual("/services/search/jobs", args[0])
        self.assertEqual("fresh", kwargs["session_key"])
        self.assertEqual({"search": "index=main"}, kwargs["post_args"])
        self.assertIs(streaming_callback, kwargs["streaming_callback"])
        self.assertEqual(9.0, kwargs["request_timeout"])
        self.assertEqual(False, kwargs["retry_on_unauthorized"])
        self.assertEqual("json", kwargs["output_mode"])
        self.assertEqual("fresh", handler.session_key)

    def test_async_request_returns_original_unauthorized_when_refresh_fails(self):
        handler = DummyHandler()
        handler.session_key = "stale"
        handler.request = type("Request", (), {
            "connection": type("Connection", (), {
                "stream": type("Stream", (), {"closed": lambda self: False})()
            })()
        })()
        original_response = Response("text/plain", b"unauthorized", error=FakeHTTPError(401))
        callback_calls = []
        handler.async_request = lambda *args, **kwargs: self.fail("request must not retry")
        handler.refresh_session_key = lambda: self.fail("async retry must not block on sync refresh")
        handler._request_session_key_async = lambda callback: callback(None)

        handler._on_async_response(
            "/services/search/jobs",
            lambda response, **kwargs: callback_calls.append((response, kwargs)),
            original_response,
        )

        self.assertEqual([(original_response, {})], callback_calls)
        self.assertIsNone(handler.session_key)

    def test_async_session_key_request_uses_bounded_login_without_retry(self):
        handler = DummyHandler()
        handler.settings = dict(
            DummyHandler.settings,
            splunk_username="user",
            splunk_password="password",
        )
        requests = []
        callback_calls = []
        handler.async_request = lambda *args, **kwargs: requests.append((args, kwargs))

        handler._request_session_key_async(callback_calls.append)

        self.assertEqual(1, len(requests))
        args, kwargs = requests[0]
        self.assertEqual("/services/auth/login", args[0])
        self.assertEqual(
            {"username": "user", "password": "password"},
            kwargs["post_args"],
        )
        self.assertEqual(False, kwargs["retry_on_unauthorized"])
        args[1](
            Response("text/xml", b""),
            xml=auth_module.et.fromstring(b"<response><sessionKey>fresh</sessionKey></response>"),
        )
        self.assertEqual(["fresh"], callback_calls)

    def test_async_session_key_request_rejects_missing_or_unsafe_keys(self):
        handler = DummyHandler()
        callback_calls = []

        for response, xml in (
            (Response("text/xml", b"", error=FakeHTTPError(503)), None),
            (Response("text/xml", b""), auth_module.et.fromstring(b"<response />")),
            (
                Response("text/xml", b""),
                auth_module.et.fromstring(b"<response><sessionKey>bad\nkey</sessionKey></response>"),
            ),
        ):
            handler._on_async_session_key(callback_calls.append, response, xml=xml)

        self.assertEqual([None, None, None], callback_calls)


if __name__ == "__main__":
    unittest.main()
