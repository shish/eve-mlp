import unittest2
from StringIO import StringIO
from mock import Mock, patch

from eve_mlp.protocol import *


class TestProtocol(unittest2.TestCase):
    def test_hello(self):
        stream = StringIO((
            "3c0000007e00000000140704e8990200056e01044dab00000"
            "a9a99999999992040048d78080013174556452d4556452d54"
            "52414e5155494c4954594063637001"
        ).decode("hex"))

        p = get_packet(stream)
        self.assertDictContainsSubset({
            'name': 'EVE-EVE-TRANQUILITY@ccp',
            'online': 43853,
            'version': 8.3,
            'build': 555149,
        }, p)


