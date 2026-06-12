#!/usr/bin/env python

import tornado.httpclient
from tornado.simple_httpclient import SimpleAsyncHTTPClient
from tornado import escape
from functools import partial
import logging
import lxml.etree as et

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    string_types = (basestring,)
except NameError:
    string_types = (str,)

class SplunkMixin(object):
    """General splunk services connection mixin with shared authentication and lazy session key updating if stale/non-existant."""
    retry_request = True
    max_response_body_size = 1024 * 1024
    
    def get_session_key(self):
        """Session key getter, elegantly retrieves from application global attributes."""
        if hasattr(self.application, "splunk_session_key"):
            return self.application.splunk_session_key
        else:
            return None
        
    def set_session_key(self, session_key):
        """Session key setter, stores in application global attributes."""
        self.application.splunk_session_key = session_key

    session_key = property(get_session_key, set_session_key)     

    def refresh_session_key(self):
        """Refreshes the session key application global attribute."""
        self.session_key = self.request_session_key()

    def encode_args(self, args):
        """Encode Splunk request arguments, preserving repeated parameters."""
        return urlencode(args, doseq=True)

    def request_url(self, pathname, **kwargs):
        """A fully qualified splunk services uri including encoded get params as **kwargs"""
        self.require_setting("splunk_host_path", "Splunk Connect")
        url = "%s%s" % (self.settings["splunk_host_path"], pathname)
        if kwargs:
            url += "?" + self.encode_args(kwargs)
        return url

    def request_headers(self, session_key=None):
        """The splunk request headers with the Authorization session key if provided."""
        headers = {}
        if session_key:
            if not isinstance(session_key, string_types):
                raise ValueError("session_key must be text")
            if "\r" in session_key or "\n" in session_key:
                raise ValueError("session_key must not contain newline characters")
            headers["Authorization"] = "Splunk %s" % session_key
        return headers
    
    def request_session_key(self):
        """Retrieve a session key from the splunk authentication endpoint as a syncronous request."""
        self.require_setting("splunk_username", "Splunk Connect")
        self.require_setting("splunk_password", "Splunk Connect")
        post_args = {
          "username": self.settings["splunk_username"],
          "password": self.settings["splunk_password"],
        }
        response, xml, json, text = self.sync_request(
            "/services/auth/login",
            post_args=post_args,
            retry_on_unauthorized=False,
        )
        session_key = self._session_key_from_xml(xml) if response.error is None else None
        if session_key:
            logging.info("Successfully retrieved Splunk session_key")
            return session_key
        logging.info("Could not retrieve Splunk session_key")
        return None

    def _request_session_key_async(self, callback):
        """Retrieve a session key without blocking Tornado's event loop."""
        self.require_setting("splunk_username", "Splunk Connect")
        self.require_setting("splunk_password", "Splunk Connect")
        post_args = {
          "username": self.settings["splunk_username"],
          "password": self.settings["splunk_password"],
        }
        self.async_request(
            "/services/auth/login",
            partial(self._on_async_session_key, callback),
            post_args=post_args,
            retry_on_unauthorized=False,
        )

    def _on_async_session_key(self, callback, response, xml=None, json=None, text=None):
        session_key = self._session_key_from_xml(xml) if response.error is None else None
        callback(session_key)

    def _session_key_from_xml(self, xml):
        if xml is None:
            return None
        session_key = xml.findtext("sessionKey")
        if not session_key:
            return None
        try:
            self.request_headers(session_key=session_key)
        except ValueError:
            return None
        return session_key

    def xml_parser(self):
        return et.XMLParser(resolve_entities=False, no_network=True)
    
    def sync_request(self, pathname, post_args=None, session_key=None, retry_on_unauthorized=True, **kwargs):
        """"
        A simplified syncronous http request method for splunk services.
        Returns a tuple based on parse_response method spec.
        """
        url = self.request_url(pathname, **kwargs)
        headers = self.request_headers(session_key=session_key)
        http = tornado.httpclient.HTTPClient(
            async_client_class=SimpleAsyncHTTPClient,
            max_body_size=self.max_response_body_size,
        )
        try:
            fetch_kwargs = {"headers": headers, "raise_error": False}
            if post_args is not None:
                fetch_kwargs.update({"method": "POST", "body": self.encode_args(post_args)})
            response = http.fetch(url, **fetch_kwargs)
        finally:
            http.close()
        if response.error:
            if response.code == 401 and self.retry_request and retry_on_unauthorized:
                self.refresh_session_key()
                if self.session_key:
                    return self.sync_request(
                        pathname,
                        post_args=post_args,
                        session_key=self.session_key,
                        retry_on_unauthorized=False,
                        **kwargs
                    )
        xml, json, text = self.parse_response(response)
        return response, xml, json, text
 
    def async_request(self, pathname, callback, post_args=None, session_key=None, streaming_callback=None, request_timeout=20.0, retry_on_unauthorized=True, **kwargs):
        """
        A simplified non-blocking asynchronous http request method for splunk services. 
        The callback is called with a response, and xml, json, and text keyword args where xml, json, and text are not passed if not serializable from response/content-type.
        """
        url = self.request_url(pathname, **kwargs)
        headers = self.request_headers(session_key=session_key)
        response_callback = partial(self._on_async_response, pathname, callback, post_args=post_args, session_key=session_key, streaming_callback=streaming_callback, request_timeout=request_timeout, retry_on_unauthorized=retry_on_unauthorized, **kwargs)
        http = SimpleAsyncHTTPClient(
            force_instance=True,
            max_body_size=self.max_response_body_size,
        )
        fetch_kwargs = {
            "headers": headers,
            "streaming_callback": streaming_callback,
            "request_timeout": request_timeout,
        }
        if post_args is not None:
            fetch_kwargs.update({"method": "POST", "body": self.encode_args(post_args)})
        request = tornado.httpclient.HTTPRequest(url, **fetch_kwargs)
        try:
            future = http.fetch(request, raise_error=False)
        except Exception:
            http.close()
            raise
        future.add_done_callback(partial(self._on_async_fetch_complete, response_callback, request, http))

    def _on_async_fetch_complete(self, callback, request, http, future):
        try:
            response = future.result()
        except Exception as error:
            response = getattr(error, "response", None)
            if response is None:
                response = tornado.httpclient.HTTPResponse(
                    request,
                    getattr(error, "code", 599),
                    effective_url=request.url,
                    error=error,
                    reason=str(error),
                )
        finally:
            http.close()
        callback(response)

    def _on_async_response(self, pathname, callback, response, post_args=None, session_key=None, streaming_callback=None, request_timeout=20.0, retry_on_unauthorized=True, **kwargs):
        """Reponse handler for asynchronous requests."""
        if self.request.connection.stream.closed():
            return
        else:
            if response.error:
                if response.code == 401 and self.retry_request and retry_on_unauthorized:
                    self._request_session_key_async(partial(
                        self._on_async_session_refresh,
                        pathname,
                        callback,
                        response,
                        post_args=post_args,
                        streaming_callback=streaming_callback,
                        request_timeout=request_timeout,
                        **kwargs
                    ))
                    return
            xml, json, text = self.parse_response(response)
            callback(response, xml=xml, json=json, text=text)    

    def _on_async_session_refresh(self, pathname, callback, original_response, session_key, post_args=None, streaming_callback=None, request_timeout=20.0, **kwargs):
        self.session_key = session_key
        if not session_key:
            callback(original_response)
            return
        logging.info("Retry request with fresh session key")
        self.async_request(
            pathname,
            callback,
            post_args=post_args,
            session_key=session_key,
            streaming_callback=streaming_callback,
            request_timeout=request_timeout,
            retry_on_unauthorized=False,
            **kwargs
        )

    def response_content_type(self, response):
        return response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()

    def parse_response(self, response):
        """
        General splunk http response parser based on reponse content-type.
        Returns a tuple xml, json and text where xml, json and text are None type if not serializable from response/content-type.
        """
        body = response.body or b""
        if len(body) > self.max_response_body_size:
            logging.warning("Splunk response body exceeded the configured limit")
            return None, None, None

        content = self.response_content_type(response)
        if content in ("text/xml", "application/xml"):
            try:
                xml = et.fromstring(response.body, parser=self.xml_parser())
            except (et.XMLSyntaxError, ValueError):
                logging.warning("Could not parse xml")
                return None, None, None
            return xml, None, None
        elif content == "application/json":
            try:
                json = escape.json_decode(response.body)
            except ValueError:
                logging.warning("Could not decode json")
                return None, None, None
            return None, json, None
        elif content == "text/plain":
            return None, None, response.body
        else:
            return None, None, None
