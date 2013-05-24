import unittest2
from mock import Mock, patch

from eve_mlp.common import *


class TestCommon(unittest2.TestCase):
    def test_encrypt(self):
        plaintext = "Hello!"
        encrypted1 = encrypt(plaintext, "password")
        encrypted2 = encrypt(plaintext, "password")
        self.assertNotEqual(encrypted1, encrypted2)

    def test_decrypt(self):
        plaintext = "Hello!"
        encrypted = encrypt(plaintext, "password")
        decrypted = decrypt(encrypted, "password")
        self.assertEqual(plaintext, decrypted)

    def test_config(self):
        config = load_config()
        self.assertIsInstance(config, dict)
        save_config(config)

    @patch("subprocess.Popen")
    @patch("platform.system")
    def test_launch(self, system, popen):
        system.return_value = "generic"
        launch("TOKEN", Mock(dry=False, singularity=False))
        popen.assert_called_with("bin/ExeFile.exe /ssoToken=TOKEN /noconsole", shell=True)

        system.return_value = "generic"
        launch("TOKEN", Mock(dry=True, singularity=False))
        popen.assert_called_with("echo bin/ExeFile.exe /ssoToken=TOKEN /noconsole", shell=True)

        system.return_value = "generic"
        launch("TOKEN", Mock(dry=False, singularity=True))
        popen.assert_called_with("bin/ExeFile.exe /ssoToken=TOKEN /noconsole /server:Singularity", shell=True)

        system.return_value = "Linux"
        launch("TOKEN", Mock(dry=False, singularity=False))
        popen.assert_called_with("wine bin/ExeFile.exe /ssoToken=TOKEN /noconsole", shell=True)
