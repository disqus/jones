"""
Copyright 2012 DISQUS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging_config
logging_config.configure()

import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TESTING = True
SECRET_KEY = 'developement key'
ZK_CONNECTION_STRING = ''
ZK_DIGEST_PASSWORD = 'changeme'

