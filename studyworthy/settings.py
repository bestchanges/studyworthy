import os

if 'DYNO' in os.environ:
    from .settings_heroku import *
else:
    from .settings_dev import *
