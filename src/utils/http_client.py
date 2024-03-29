import http.client
import json
import urllib.parse

import logging

LOG = logging.getLogger(__name__)


class HttpClient:
    DEFAULT_HOST = ""
    DEFAULT_HOST_PORT = 443
    DEFAULT_BASE_PATH = ""

    def __init__(self, base_url, output_curl=False):
        self.output_curl = output_curl

        if base_url:
            self.base_url = base_url

        if self.base_url:
            base_url_parts = urllib.parse.urlparse(self.base_url)
            self.host = base_url_parts.netloc
            self.host_port = base_url_parts.port or self.DEFAULT_HOST_PORT
            self.base_path = base_url_parts.path

        self.conn = None
        self.default_headers = {"Content-Type": "application/json"}
        self.default_query = {}

        self.init_connection()

    def init_connection(self):
        self.conn = http.client.HTTPSConnection(self.host, self.host_port)

    def build_headers(self, headers=None, default_headers=None):
        if headers is None:
            _headers = default_headers or self.default_headers
        else:
            if default_headers is None:
                default_headers = self.default_headers or {}
            _headers = {**default_headers, **headers}
        return _headers

    def build_query_string(self, query=None, default_query=None):
        if query is None:
            _query = default_query or self.default_query
        else:
            if default_query is None:
                default_query = self.default_query or {}
            _query = {**default_query, **query}
        return urllib.parse.urlencode(_query)

    def to_curl(self, method, path, headers=None, body=None):
        headers = headers or {}
        header_str = ' '.join(f'-H "{k}: {v}"' for k, v in headers.items())
        data_str = f"--data '{body}'" if body else ""
        full_url = f"https://{self.host}:{self.host_port}{path}"
        return f"curl -X {method} {header_str} {data_str} \"{full_url}\""

    @classmethod
    def handle_response(cls, response):
        response_body = response.read()
        content_type_header = response.getheader("Content-Type")
        if ";" in content_type_header:
            content_type, header_attribs_raw = content_type_header.split(";")
            header_attribs = dict(map(lambda x: x.strip().split("="), header_attribs_raw.split(",")))
            charset = header_attribs.get("charset", "utf-8")
        else:
            content_type = content_type_header
            charset = "utf-8"
        try:
            if content_type == 'text/plain:':
                return response_body.decode(charset)
            if content_type == "application/json":
                response_as_string = response_body.decode(charset)
                return json.loads(response_as_string) if response_as_string.strip() else None
            else:
                return response_body
        except json.JSONDecodeError as e:
            LOG.error(f"Error decoding response: {e}")
            return response_body

    def build_url(self, base_path, endpoint, query=None):
        url = base_path + "/" + endpoint
        url += "?" + self.build_query_string(query=query)
        return url

    def delete(self, endpoint, query=None, headers=None, default_headers=None):
        url = self.build_url(self.base_path, endpoint, query=query)
        headers = self.build_headers(headers=headers, default_headers=default_headers)
        if self.output_curl:
            print(self.to_curl("DELETE", url, headers))
        self.conn.request("DELETE", url, headers=headers)
        response = self.conn.getresponse()
        return self.__class__.handle_response(response)

    def get(self, endpoint, query=None, headers=None, default_headers=None):
        url = self.build_url(self.base_path, endpoint, query=query)
        headers = self.build_headers(headers=headers, default_headers=default_headers)
        if self.output_curl:
            print(self.to_curl("GET", url, headers))
        self.conn.request("GET", url, headers=headers)
        response = self.conn.getresponse()
        return self.__class__.handle_response(response)

    def put(self, endpoint, data, query=None, headers=None, default_headers=None):
        url = self.build_url(self.base_path, endpoint, query=query)
        headers = self.build_headers(headers=headers, default_headers=default_headers)
        body = json.dumps(data)
        if self.output_curl:
            print(self.to_curl("PUT", url, headers, body))
        self.conn.request("PUT", url, body=body,
                          headers=headers)
        response = self.conn.getresponse()
        return self.__class__.handle_response(response)

    def post(self, endpoint, data, query=None, headers=None, default_headers=None):
        url = self.build_url(self.base_path, endpoint, query=query)
        headers = self.build_headers(headers=headers, default_headers=default_headers)
        body = json.dumps(data)
        if self.output_curl:
            print(self.to_curl("POST", url, headers, data))
        self.conn.request("POST", url, body=body, headers=headers)
        response = self.conn.getresponse()
        return self.__class__.handle_response(response)

