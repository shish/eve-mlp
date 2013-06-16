import unittest2
from mock import Mock, patch

from eve_mlp.common import *


class TestCommon(unittest2.TestCase):
    def test_encrypt(self):
        plaintext = "Hello!"
        encrypted1 = encrypt(plaintext, "password")
        encrypted2 = encrypt(plaintext, "password")
        self.assertNotEqual(encrypted1, encrypted2)
        self.assertNotEqual(encrypted1, None)

    def test_decrypt(self):
        plaintext = "Hello!"
        encrypted = encrypt(plaintext, "password")
        decrypted = decrypt(encrypted, "password")
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, None)

    def test_encrypt_pad(self):
        plaintext = "Hello!"
        encrypted1 = encrypt(plaintext, "password", True)
        encrypted2 = encrypt(plaintext, "password", True)
        self.assertNotEqual(encrypted1, encrypted2)
        self.assertNotEqual(encrypted1, None)

    def test_decrypt_pad(self):
        plaintext = "Hello!"
        encrypted = encrypt(plaintext, "password", True)
        decrypted = decrypt(encrypted, "password", True)
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, None)

    def test_decrypt_unpad(self):
        plaintext = "Hello!"
        encrypted = encrypt(plaintext, "password")
        decrypted = decrypt(encrypted, "password", True)
        self.assertEqual(plaintext, decrypted)
        self.assertNotEqual(plaintext, None)

    @patch("os.path.exists")
    @patch("subprocess.Popen")
    def test_launch_ok(self, popen, exists):
        exists.return_value = True

        co = Config()
        co.defaults.gamepath = "/home/games/EVE Online"
        co.defaults.winecmd = None
        lc = LaunchConfig(co.defaults)
        to = "TOKEN"
        launch(co, lc, to)

        popen.assert_called_with('"/home/games/EVE Online/bin/ExeFile.exe" /ssoToken=TOKEN /noconsole', shell=True)

    @patch("os.path.exists")
    @patch("subprocess.Popen")
    def test_launch_badpath(self, popen, exists):
        exists.return_value = False

        co = Config()
        co.defaults.gamepath = "/home/games/EVE Online"
        lc = LaunchConfig(co.defaults)
        to = "TOKEN"

        self.assertRaises(LaunchFailed, launch, co, lc, to)


class TestLaunchConfig(unittest2.TestCase):
    # attribute setting / getting / inheriting is the tricky bit
    def test_basic(self):
        # base object, all None
        lc = LaunchConfig(None, {})
        self.assertEqual(lc.serverid, None)

    def test_init_attr(self):
        # pass some settings at creation time
        lc = LaunchConfig(None, {"serverid": "tranquility"})
        self.assertEqual(lc.serverid, "tranquility")

    def test_set_attr(self):
        # set some settings at run time
        lc = LaunchConfig(None, {})
        lc.serverid = "tranquility"
        self.assertEqual(lc.serverid, "tranquility")

    def test_inherit_attr(self):
        # test that sub-config inherits from the base
        base = LaunchConfig(None, {"serverid": "tranquility"})
        lc = LaunchConfig(base, {})
        self.assertEqual(lc.serverid, "tranquility")

        # and that when the base is modified, the child sees it
        base.serverid = "singularity"
        self.assertEqual(lc.serverid, "singularity")

    def test_override_attr(self):
        # test that a child can override the base
        base = LaunchConfig(None, {"serverid": "tranquility"})
        lc = LaunchConfig(base, {})
        lc.serverid = "singularity"
        self.assertEqual(lc.serverid, "singularity")

        # and go back to default
        lc.serverid = None
        self.assertEqual(lc.serverid, "tranquility")

    def test_override_attr_false(self):
        # test that a child can override the base
        base = LaunchConfig(None, {"console": True})
        lc = LaunchConfig(base, {})
        # false is a valid setting, don't go for the parent
        lc.console = False
        self.assertEqual(lc.console, False)
        # none = do go for the parent
        lc.console = None
        self.assertEqual(lc.console, True)

    # other bits
    def test_json(self):
        base = LaunchConfig(None, {"serverid": "tranquility"})
        d = base.__json__()
        self.assertEqual(d["confname"], None)
        self.assertEqual(d["serverid"], "tranquility")
        for key, value in d.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, (basestring, type(None)))

    def test_str(self):
        lc = LaunchConfig(None, {"confname": "My Config"})
        self.assertEqual(str(lc), "LaunchConfig('My Config')")
