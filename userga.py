# -*- coding: UTF-8 -*-
#!/usr/local/bin/python

# userga 一个可以免密码的用户系统示例
# author : raptor.zh@gmail.com
# create : 2016-02-04
from bottle import Bottle, run, request, response, redirect, static_file, MakoTemplate, mako_template, error
from beaker.middleware import SessionMiddleware
from bottle.ext.sqlalchemy import Plugin as SAPlugin

from bottle_plugins.beaker import BeakerPlugin
from bottle_plugins.login import LoginPlugin
from bottle_plugins.params import ParamsPlugin
from bottle_plugins.webexceptions import WebUnauthorizedError
from config import config, get_fullname
import saprovider
from model import engine, metadata

import logging

logger = logging.getLogger(__name__)


mako={"template_adapter": MakoTemplate}


def login(orm, session):
    email = session.get('email', None)
    if email:
        return saprovider.get_user(orm, email)
    else:
        redirect("/%s/login" % config['web_path'])

app = Bottle()
app.install(SAPlugin(engine, metadata, keyword="orm", create=True, commit=True))
app.install(BeakerPlugin(keyword="session"))
app.install(LoginPlugin(login_func=login, keyword="login", dbkeyword="orm", sessionkeyword="session"))
app.install(ParamsPlugin())


@app.get("/static/<filename:path>")
def get_static(filename):
    return static_file(filename, root=get_fullname("static"))


@app.get("/login", template=("login.html", mako))
@app.get("/login/<email>", template=("login.html", mako))
def get_login(email=""):
    return dict(base=config["web_path"], email=email)


@app.post("/login")
def post_login(orm, session, email, password):
    user = saprovider.get_user(orm, email)
    if not user:
        user = saprovider.add_user(orm, email)
        reset_url = "http://localhost:8001" + app.get_url("setpw", key=user.key)
        saprovider.send_email(orm, user, reset_url, "register")
    if not user.expires or user.resetpw:
        if not password:
            redirect("/%s/login/%s" % (config['web_path'], email))
        elif not saprovider.check_password(orm, user, password):
            redirect("/%s/login" % config['web_path'])
    session['email'] = email
    redirect("/%s" % config['web_path'])


@app.get("/logout")
def get_logout(session):
    session["email"] = None
    redirect("/%s/login" % config['web_path'])


@app.get("/setpw/<key>", template=("setpw.html", mako), sqlalchemy=dict(use_kwargs=True), name="setpw")
def get_setpw(orm, key):
    user = saprovider.get_user_by_key(orm, key)
    if not user:
        raise WebUnauthorizedError("无效的链接，可能已经超过有效期限")
    return dict(base=config['web_path'], email=user.email)


@app.post("/setpw", sqlalchemy=dict(use_kwargs=True))
def post_setpw(orm, email, password):
    if saprovider.set_password(orm, email, password):
        redirect("/%s" % config['web_path'])
    else:
        raise WebUnauthorizedError("错误的密码或重复操作过于频繁！")

@app.get("/resetpw", template=("resetpw.html", mako))
def get_resetpw():
    return dict(base=config['web_path'])


@app.post("/resetpw", sqlalchemy=dict(use_kwargs=True))
def post_resetpw(orm, email):
    if saprovider.reset_password(orm, email):
        user = saprovider.get_user(orm, email)
        reset_url = "http://localhost:8001" + app.get_url("setpw", key=user.key)
        saprovider.send_email(orm, user, reset_url, "resetpw")
        redirect("/%s" % config['web_path'])
    else:
        raise WebUnauthorizedError("请勿频繁操作！")


@app.get("/", template=("index.html", mako), sqlalchemy=dict(use_kwargs=True))
def get_(orm, session, login):
    return dict(base=config['web_path'], email=login.email)


def error_page(error):
    return mako_template("error.html", base=config['web_path'], login=None, error=error)


handlers = {}
errors = [400, 401, 403, 404, 500]
[handlers.__setitem__(i, error_page) for i in errors]
app.error_handler = handlers


approot = Bottle()

approot.mount("/%s" % config["web_path"], app)

session_opts = {
        "session.type": "memory",
        "session.cookie_expires": 3600,
        "session.auto": True
        }

application = SessionMiddleware(approot, session_opts)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if config['debug'] else logging.WARNING)
    run(application, host=config['web_addr'], port=config['web_port'], debug=config['debug'], reloader=config['debug'])
