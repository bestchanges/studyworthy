"""
The only purpose of this module is to detect environment and import appropriate settings for it.
Do not define any config vars in this module.
"""
import os

if 'DYNO' in os.environ:
    from .settings_heroku import *
else:
    from .settings_dev import *
