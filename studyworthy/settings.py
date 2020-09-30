"""
The only purpose of this module is to detect environment and import appropriate settings for it.
Do not define any config vars in this module. Instead use settings_default.py of specific settings_*.py
"""
import os

deployment_default = 'local'
deployment = os.environ.get('DEPLOYMENT', deployment_default)

if deployment == 'local':
    from .settings_local import *
else:
    from .settings_default import *
