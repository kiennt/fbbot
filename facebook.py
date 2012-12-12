import time
import re
import requests
import hashlib

from utils import BaseRequest
from utils import RequestParams

class FacebookLoginFailedException(Exception):
    pass

class FacebookClient(BaseRequest):
    API_KEY = "882a8490361da98702bf97a021ddc14d"
    API_SECRET = "62f8ce9f74b12f84c123cc23437a4a32"
    HEADERS = {
        "User-Agent" : "[FBAN/FB4A;FBAV/1.9.9;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]"
    }
    BASE_URL = "https://api.facebook.com/restserver.php"
    CONST_ARRAY = [ 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 97, 98, 99, 100, 101, 102]

    def _add_signature(self, data):
        """ Add generate signature for data

        @param data - Dictionary of POST parameters
        """
        # Generate message
        keys = sorted(data.keys())
        message = "".join(["%s=%s" % (k, data[k]) for k in keys])
        message = "%s%s" % (message, self.API_SECRET)

        # Generate signature for message
        message = message.encode("utf-8")
        m = hashlib.md5()
        m.update(message)
        digest_message = m.digest()
        arr = []
        for i in digest_message:
            k = 0xFF & ord(i)
            arr.append(chr(self.CONST_ARRAY[(k >> 4)]))
            arr.append(chr(self.CONST_ARRAY[(k & 0xF)]))
        sig = ''.join(arr)
        data["sig"] = sig

    def _add_default_value(self, data):
        """ Add default parameter to data

        @data - Dictionary
        """
        default_parameters = {
            "api_key" : self.API_KEY,
            "format" : "JSON",
            "generate_session_cookies" : 1,
            "locale" : "en_US",
            "migrations_override" : "{'empty_json':true}",
            "return_ssl_resources" : 0,
            "v" : "1.0",
        }
        for k, v in default_parameters.items():
            if k not in data:
                data[k] = v

    def _add_call_id(self, data):
        """ Add call id for data """
        data["call_id"] = int(round(time.time() * 1000))

    def _make_request_with_data(self, method, url_path, data):
        """ Make post request with data

        @param data - Dictionary of POST parameters
        """
        self._add_default_value(data)
        self._add_signature(data)

        if method == "POST":
            return self.post(url_path, data=data)
        elif method == "GET":
            return self.get(url_path, params=data)

    def login(self, email, password):
        data = {
            "generate_machine_id" : 1,
            "credentials_type" : "password",
            "method" : "auth.login",
            "email" : email,
            "password" : password,
        }
        res = self._make_request_with_data("GET", "", data)
        if not res.json:
            raise FacebookLoginFailedException(res.content)
        if 'access_token' in res.json:
            self.access_token = res.json['access_token']
        return res.json

    def upload_profile_picture(self, image_path):
        pass

    def request_friend(self, user_id):
        pass

    def accept_all_friends_request(self, user_id):
        pass

    def like_object(self, object_id):
        pass

    def unlike_object(self, object_id):
        pass

    def commend_on_object(self, object_id):
        pass

    def upload_picture(self, image_path):
        pass

    def update_profile(self, data):
        pass

    def _fql_query(self, query):
        if not hasattr(self, 'access_token'):
            raise Exception("Dont have access_token")
        return self.get('https://graph.facebook.com/fql', params={
            'access_token': self.access_token,
            'q': query
        })
