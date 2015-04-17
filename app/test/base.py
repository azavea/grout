import unittest

import ashlar


class AshlarTestCase(unittest.TestCase):
    """Base class for Ashlar tests"""

    def setUp(self):
        ashlar.app.config['TESTING'] = True
        self.app = ashlar.app.test_client()

    def tearDown(self):
        pass
