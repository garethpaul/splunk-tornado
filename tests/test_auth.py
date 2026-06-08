import unittest
import tornado.httpclient

try:
    from urllib.parse import parse_qs, urlsplit
except ImportError:
    from urlparse import parse_qs, urlsplit

from splunktornado.auth import SplunkMixin


class DummyHandler(SplunkMixin):
    settings = {"splunk_host_path": "https://splunk.example:8089"}

    def require_setting(self, name, feature):
        if name not in self.settings:
            raise RuntimeError("%s missing for %s" % (name, feature))


class Response(object):
    def __init__(self, content_type, body, error=None):
        self.headers = {"Content-Type": content_type}
        self.body = body
        self.error = error


class FakeHTTPClient(object):
    instances = []

    def __init__(self):
        self.calls = []
        self.closed = False
        self.instances.append(self)

    def fetch(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return Response("text/plain", b"ok")

    def close(self):
        self.closed = True


class SplunkMixinTests(unittest.TestCase):
    def test_parse_response_decodes_json(self):
        response = Response("application/json", b'{"ok": true}')

        xml, payload, text = SplunkMixin().parse_response(response)

        self.assertIsNone(xml)
        self.assertEqual({"ok": True}, payload)
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

    def test_sync_request_preserves_error_responses_and_closes_client(self):
        handler = DummyHandler()
        original_client = tornado.httpclient.HTTPClient
        FakeHTTPClient.instances = []
        tornado.httpclient.HTTPClient = FakeHTTPClient
        try:
            response, xml, payload, text = handler.sync_request(
                "/services/search/jobs",
                post_args={"search": "index=main"},
                session_key="abc123",
            )
        finally:
            tornado.httpclient.HTTPClient = original_client

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


if __name__ == "__main__":
    unittest.main()
