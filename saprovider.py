# -*- coding: utf-8 -*-
"""
    saprovider
    ~~~~~~~~~~~~~~~~
    sqlalchemy data provider.

    :copyright: 20160223 by raptor.zh@gmail.com
"""
import time
from os import urandom
from urllib.parse import urlencode
from base64 import b64encode
from uuid import uuid4

from config import config

from model import User

from otpauth import OtpAuth

from mail import sendmail

import logging

logger = logging.getLogger(__name__)


def get_secret():
    return b64encode(urandom(7)).decode('utf-8')[:10]


def get_user(orm, email):
    user = orm.query(User).filter(User.email==email).first()
    return user


def add_user(orm, email):
    user = User(email=email, secret=get_secret(),
            expires=time.time()+86400,
            key=str(uuid4()).replace("-", ""))
    orm.add(user)
    orm.commit()
    return user


def send_email(orm, user, reset_url, mail_type):
    """
    mail_type: register ro resetpw
    """
    secret = user.secret if mail_type=="register" else user.resetpw
    logger.debug(secret)
    auth = OtpAuth(secret)
    uri = auth.to_uri('totp', user.email, 'userga')
    qrurl = "?".join(['https://chart.googleapis.com/chart', urlencode({'cht': 'qr', 'chs': '200x200', 'chl': uri})])
    logger.debug(qrurl)
    logger.debug(mail_type)
    sendmail(user.email, secret, uri, qrurl, reset_url, mail_type)


def get_user_by_key(orm, key):
    user = orm.query(User).filter(User.key==key).first()
    if user and user.expires and user.expires>time.time():
        return user
    return None


def set_password(orm, email, code):
    user = get_user(orm, email)
    if not user or (user.inv_setpw and user.inv_setpw>time.time()):
        logger.debug("interval error")
        return False
    user.inv_setpw = time.time()+30
    secret = user.resetpw if user.resetpw else user.secret
    auth = OtpAuth(secret)
    logger.debug(auth.valid_totp(code))
    if user.expires and user.expires>time.time() and auth.valid_totp(code):
        user.inv_setpw = None
        if user.resetpw:
            user.secret = user.resetpw
            user.resetpw = None
        user.expires = None
        orm.commit()
        return True
    orm.commit()
    return False


def check_password(orm, user, code):
    if not user or (user.inv_login and user.inv_login>time.time()):
        logger.debug("interval error")
        return False
    user.inv_login = time.time()+30
    auth = OtpAuth(user.secret)
    result = False
    if auth.valid_totp(code):
        user.inv_login = None
        result = True
    orm.commit()
    return result


def reset_password(orm, email):
    user = get_user(orm, email)
    if not user or (user.inv_reset and user.inv_reset>time.time()):
        logger.debug("interval error")
        return False
    user.inv_reset = time.time() + 300
    user.expires = time.time() + 86400
    user.resetpw = get_secret()
    user.key = str(uuid4()).replace("-", "")
    orm.commit()
    return True
