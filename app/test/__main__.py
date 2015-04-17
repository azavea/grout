import os
import unittest

# TODO: Database

# Test discovery
suite = unittest.defaultTestLoader.discover(os.path.dirname(os.path.realpath(__file__)))

# Run
unittest.TextTestRunner(verbosity=1).run(suite)
