import unittest
import nose

from facebook import FacebookClient

class TestFacebookClient(unittest.TestCase):
    def setUp(self):
        self.client = FacebookClient()
        pass

    def tearDown(self):
        pass

    def test_login(self):
        res = self.client.login("thangmeo2020@gmail.com", "@123456@")
        self.assertIn("session_key", res)
        self.assertIn("uid", res)
        self.assertEquals(res["uid"], 100003590157421L)
        self.assertIn("secret", res)
        self.assertIn("access_token", res)
        self.assertIn("machine_id", res)
        self.assertIn("session_cookies", res)
