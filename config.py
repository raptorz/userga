# -*- coding: utf-8 -*-
"""
    default config file

    :copyright: 20160204 by raptor.zh@gmail.com.
"""
#from __future__ import unicode_literals
import sys
PY3=sys.version>"3"

from os.path import dirname, abspath, expanduser, join as joinpath
import json

import logging

logger = logging.getLogger(__name__)


config_default = {
    "db_url": "sqlite:///userga.dat",
    "web_path": "userga",
    "web_addr": "127.0.0.1",
    "web_port": 8001,
    "smtp_server": "",
    "smtp_port": 25,
    "smtp_user": "",
    "smtp_pass": "",
    "debug": True,
}


def get_fullname(*args):
    root = dirname(abspath(__file__))
    return joinpath(root, joinpath(*args)) if len(args) > 0 else root


def uniencode(s, coding="utf-8"):
    return s.encode(coding) if s and (PY3 or not isinstance(s, str)) else s


def unidecode(s, coding="utf-8"):
    return unicode(s, coding) if s and (not PY3 or isinstance(s, str)) else s


try:
    with open(get_fullname("config.json"), "r") as f:
        config = json.loads(f.read())
    config_default.update(config)
    config = config_default
except IOError:
    config = config_default
