# userga

一个可以不用密码的用户系统。默认只需要输入email即可注册或登录，如果需要密码，可以使用Google Authenticator扫描邮件中的二维码，使用GA生成的一次性密码登录。

## 基本功能

1. 注册：输入email即完成注册或登录。提示：本网站可以不用设置密码，直接使用email登录，如果需要设置密码，请收取邮件，并按邮件中的指示操作。
1. 登录：未设置密码：输入email直接登录。已设置密码：输入email后弹出密码提示，需要输入GA生成的一次性密码登录。
1. 设置密码：邮件内容：祝贺您成功注册本网站，您现在可以直接使用email登录网站

## 安装

    cd /usr/ports/databases/py-sqlite3 # for FreeBSD
    sudo make PYTHON_VERSION=python3.4 install  # for FreeBSD
    pip install -r requirements.txt
    python userga.py

## 配置

配置文件为当前目录下的config.json，内容为：

    {
        "db_url": "sqlite:///userga.dat",
        "web_path": "userga",
        "web_addr": "127.0.0.1",
        "web_port": 8001,
        "debug": True,
    }


## 依赖

* python 3.4+（其它版本未测试）
* bottle, mako, beaker, sqlalchemy, bottle-sqlalchemy
* [bottle-plugins](https://github.com/raptorz/bottle-plugins)
* 可选webserver前端（Apache/Nginx...）

## 贡献

程序代码中包含以下第三方前端库：

* jquery
* bootstrap

## 安全性

* 安全性不高：
* secret目前用的是base64编码随机字符后取10位，密钥空间为64^10
* OTP code只有6位数字，在30秒内试完其实是可能的
* 所以必须配合重试限制，目前是简单地限制30秒内只允许尝试一次（重置密码是5分钟）
