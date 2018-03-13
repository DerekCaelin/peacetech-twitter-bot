from __future__ import print_function
from __future__ import with_statement
import contextlib
import re
import string
import sys
import curses
from curses.ascii import isdigit
import sys
import urllib

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import os
import time
from time import gmtime, strftime
import datetime
from datetime import datetime
import argparse


from distutils.core import setup

setup(
    name='peacetechbot',
    version='1.0',
    py_modules=['requests','bs4','BeautifulSoup','certifi','urllib2','httplib2','gspred','apiclient','apiclient.discovery',
    'oauth2client','oauth2client.client','oauth2client.tools','oauth2client.file.Storage','oauth2client.service_account.ServiceAccountCredentials',
    'appscheduler','apscheduler.schedulers.blocking.BlockingScheduler',
    'profanity','profanity.profanity','argparse','urllib3.contrib.pyopenssl',
    'credentials']
    )
      
