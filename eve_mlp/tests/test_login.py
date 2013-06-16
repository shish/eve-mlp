import unittest2
from mock import Mock, patch

from eve_mlp.login import *


class TestDoLogin(unittest2.TestCase):
    @patch("eve_mlp.login.submit_login", Mock())
    @patch("eve_mlp.login.get_launch_token", Mock(return_value="TOKEN"))
    def test_do_login(self):
        token = do_login("username", "password")
        self.assertEqual(token, "TOKEN")


class TestSubmitLogin(unittest2.TestCase):
    @patch("requests.post")
    def test_submit_login_ok(self, post):
        post.return_value = Mock(
            text = "",
            url = "http://server/success#access_token=TOKEN",
        )
        token = submit_login("http://server/login", "username", "password")
        self.assertEqual(token, "TOKEN")

    @patch("requests.post")
    def test_submit_login_fail(self, post):
        post.return_value = Mock(
            text = "",
            url = "http://server/fail",
        )
        self.assertRaises(LoginFailed, submit_login, "http://server/login", "username", "password")

    @patch("requests.post")
    def test_submit_login_eula(self, post):
        post.return_value = Mock(
            text = "<title>License Agreement Update</title>",
            url = "http://server/eula",
        )
        self.assertRaises(LoginFailed, submit_login, "http://server/login", "username", "password")


class TestGetLaunchToken(unittest2.TestCase):
    @patch("requests.get")
    def test_get_launch_token_ok(self, post):
        post.return_value = Mock(
            text = "",
            url = "http://server/success#access_token=TOKEN",
        )
        token = get_launch_token("ACCESS")
        self.assertEqual(token, "TOKEN")

    @patch("requests.get")
    def test_get_launch_token_fail(self, post):
        post.return_value = Mock(
            text = "",
            url = "http://server/fail",
        )
        self.assertRaises(LoginFailed, get_launch_token, "ACCESS")
