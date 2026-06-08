import unittest

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
    def __init__(self, content_type, body):
        self.headers = {"Content-Type": content_type}
        self.body = body


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


if __name__ == "__main__":
    unittest.main()
