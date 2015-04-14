#!/usr/bin/env python

# Run a test server
from ashlar import app

app.run(host='0.0.0.0', port=4000, debug=True)
