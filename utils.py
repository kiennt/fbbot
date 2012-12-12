import urllib
import requests
import time
import random

class ParamAlreadyExistsException(Exception):
    pass

class RequestParams(object):
    def __init__(self):
        self._keys = []
        self._data = {}

    def add_param(self, key, value):
        if key in self._data:
            raise ParamAlreadyExistsException(key)
        self._keys.append(key)
        self._data[key] = value

    def __str__(self):
        data = ",".join('"%s":"%s"' % (key, self._data[key]) for key in self._keys)
        return "{" + data + "}"

class BaseRequest(object):
    SECRET_KEY = ""
    HEADERS = {}
    BASE_URL = ""

    def __init__(self):
        self.session = requests.session(headers=self.HEADERS)
        self._debug = False

    def _make_curl_request(self, method, url, data, headers):
        headers.update(self.HEADERS)
        headers_str = " ".join(
                ['-H "%s: %s"' % (key, value) for (key, value) in headers.items()])
        return 'curl -X%s %s %s -d "%s"' % (
                method, url, headers_str, urllib.urlencode(data))

    def _make_request(self, method, url_path, **kwargs):
        """ Make request to server

        @param :method - String method of request
        @param :url_path - String
        @param :params (optional) - Dictionary of  GET parameters
        @param :data (optional) - Dictionary of POST data
        @param :auth - Tuple with 2 element (user_name, password)
        """
        assert method in ["GET", "POST", "PUT", "DELETE"]
        if "http" in url_path:
            url = url_path
        else:
            url = "%s%s" % (self.BASE_URL, url_path)

        params = kwargs.get("params", None)
        if params:
            if "?" in url:
                url += "&" + urllib.urlencode(params)
            else:
                url += "?" + urllib.urlencode(params)

        data = kwargs.get("data", {})
        headers = kwargs.pop("headers", {})
        auth = kwargs.get("auth", None)
        debug = kwargs.pop("debug", self._debug)

        if method == "GET":
            res = self.session.get(url, **kwargs)
        elif method == "PUT":
            res = self.session.put(url, **kwargs)
        elif method == "POST":
            res = self.session.post(url, **kwargs)
        elif method == "DELETE":
            res = self.session.delete(url, **kwargs)

        if not res.ok and debug:
            print self._make_curl_request(method, url, data, headers)
        return res

    def get(self, url_path, **kwargs):
        return self._make_request("GET", url_path, **kwargs)

    def post(self, url_path, **kwargs):
        return self._make_request("POST", url_path, **kwargs)

    def put(self, url_path, **kwargs):
        return self._make_request("PUT", url_path, **kwargs)

    def delete(self, url_path, **kwargs):
        return self._make_request("DELETE", url_path, **kwargs)
