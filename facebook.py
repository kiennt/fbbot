import time
import re
import requests
import hashlib
import sleekxmpp

import logging
import threading
from utils import BaseRequest
from utils import RequestParams

#logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')


class FacebookLoginFailedException(Exception):
    pass


class FacebookChatBot(sleekxmpp.ClientXMPP):
    def __init__(self, uid):
        jid = '%s@chat.facebook.com' % uid
        sleekxmpp.ClientXMPP.__init__(self, jid, '')
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.process_message)
        self.add_event_handler("roster_update", self.update_roster)

    def start(self, event):
        self.send_presence()
        self.get_roster()

    def process_message(self, message):
        if message['type'] in ('chat', 'normal'):
            sender = self.friends[message['from']]
            body = message['body']
            print '[%s]: %s' % (sender, body)

    def update_roster(self, iq):
        self.friends = {}
        friends = iq['roster'].get_items()
        for k, v in friends.items():
            self.friends[k] = v['name']

class XMPPThreading(threading.Thread):
    def __init__(self, xmpp):
        threading.Thread.__init__(self)
        self.xmpp = xmpp

    def run(self):
        if self.xmpp.connect():
            self.xmpp.process(block=True)


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
            self.uid = res.json['uid']
        return res.json

    def send_message(self, friend_id, message):
        if not hasattr(self, 'xmpp'):
            self.xmpp = FacebookChatBot(self.uid)
            self.xmpp.credentials['api_key'] = self.API_KEY
            self.xmpp.credentials['access_token'] = self.access_token
            xmpp_thread = XMPPThreading(self.xmpp)
            xmpp_thread.start()

        self.xmpp.send_message(mto='-%s@chat.facebook.com' % friend_id,
                mbody=message, mtype='chat')


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


