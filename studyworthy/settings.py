"""
The only purpose of this module is to detect environment and import appropriate settings for it.
Do not define any config vars in this module. Instead use settings_default.py of specific settings_*.py
"""
import os

if 'DYNO' in os.environ:
    from .settings_heroku import *
else:
    from .settings_dev import *
