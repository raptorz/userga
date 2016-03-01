# -*- coding: UTF-8 -*
'''
    email utils
    ~~~~~~~~~~~~~~~~
    build an email contains qrcode and send it.

    :copyright: 20160211 by raptor.zh@gmail.com.
'''
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import pyqrcode

from config import config

import logging

logger = logging.getLogger(__name__)


register_text = """
您好，
    欢迎注册本网站。
    为方便起见，本网站设计为可以不必设置和输入密码，您只需要使用email即可登录。
    如果您认为需要更加安全，也可以按如下操作启用密码功能（24小时内有效，过期请登录网站，在设置页面点击重新发送密码设置邮件）：
    首先，通过Android或iOS手机或平板电脑在Google Play或App Store下载安装免费的Google Authenticator软件：
    Android版：https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2
    iOS版：https://itunes.apple.com/us/app/google-authenticator/id388497605
    然后运行这个软件，在其中选择添加－扫描条形码，然后扫描下面这个二维码：
    %(qrurl)s
    如果无法打开这个二维码链接，也可以选择添加－手动输入验证码，然后输入您的email地址和下面这个验证码：
    %(secret)s
    添加完成后点击下面的链接：
    %(reset_url)s
    按提示输入生成的6位密码并提交，即可完成密码功能启用设置，以后登录本网站时就需要输入密码，每次的密码都由此APP临时生成，仅供一次性使用。
    再次感谢您注册本网站。
"""

register_html = """
<!DOCTYPE HTML>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>密码设置说明</title>
</head>
<body>
<p>您好，</p>
<p>欢迎注册本网站。</p>
<p>为方便起见，本网站设计为可以不必设置和输入密码，您只需要使用email即可登录。</p>
<p>如果您认为需要更加安全，也可以按如下操作启用密码功能（24小时内有效，过期请登录网站，在设置页面点击重新发送密码设置邮件）：</p>
<p>首先，通过Android或iOS手机或平板电脑在Google Play或App Store下载安装免费的Google Authenticator软件：</p>
<p><a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2">Android版</a></p>
<p><a href="https://itunes.apple.com/us/app/google-authenticator/id388497605">iOS版</a></p>
<p>然后运行这个软件，在其中选择添加－扫描条形码，然后扫描下面这个二维码：</p>
<p><img src="cid:image1" /></p>
<p>添加完成后点击下面的链接：</p>
<p><a href="%(reset_url)s">设置密码</a></p>
<p>按提示输入生成的6位密码并提交，即可完成密码功能启用设置，以后登录本网站时就需要输入密码，每次的密码都由此APP临时生成，仅供一次性使用。</p>
<p>再次感谢您注册本网站。</p>
</body>
</html>
"""

resetpw_text = """
您好，
    您收到此邮件是因为有人申请重新设置此账号的密码，如果不是您本人的操作，请忽略本邮件。
    如您确实需要重设密码，请按以下操作重设密码（24小时内有效，过期请重新申请密码重置）：
    首先，通过Android或iOS手机或平板电脑在Google Play或App Store下载安装免费的Google Authenticator软件：
    Android版：https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2
    iOS版：https://itunes.apple.com/us/app/google-authenticator/id388497605
    然后运行这个软件，在其中选择添加－扫描条形码，然后扫描下面这个二维码：
    %(qrurl)s
    如果无法打开这个二维码链接，也可以选择添加－手动输入验证码，然后输入您的email地址和下面这个验证码：
    %(secret)s
    添加完成后点击下面的链接：
    %(reset_url)s
    按提示输入生成的6位密码并提交，即可完成密码功能的重设，以后登录本网站时就需要输入这个APP生成的密码，以前如果在其它手机或平板电脑上设置过本账号的密码，那些将失效，以本次设置为准。
    再次感谢您使用本网站。
"""

resetpw_html = """
<!DOCTYPE HTML>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>密码重置说明</title>
</head>
<body>
<p>您好，</p>
<p>您收到此邮件是因为有人申请重新设置此账号的密码，如果不是您本人的操作，请忽略本邮件。</p>
<p>如您确实需要重设密码，请按以下操作重设密码（24小时内有效，过期请重新申请密码重置）：</p>
<p>首先，通过Android或iOS手机或平板电脑在Google Play或App Store下载安装免费的Google Authenticator软件：</p>
<p><a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2">Android版</a></p>
<p><a href="https://itunes.apple.com/us/app/google-authenticator/id388497605">iOS版</a></p>
<p>然后运行这个软件，在其中选择添加－扫描条形码，然后扫描下面这个二维码：</p>
<p><img src="cid:image1" /></p>
<p>添加完成后点击下面的链接：</p>
<p><a href="%(reset_url)s">设置密码</a></p>
<p>按提示输入生成的6位密码并提交，即可完成密码功能的重设，以后登录本网站时就需要输入这个APP生成的密码，以前如果在其它手机或平板电脑上设置过本账号的密码，那些将失效，以本次设置为准。</p>
<p>再次感谢您使用本网站。</p>
</body>
</html>
"""


def generate_qrcode(uri):
    qrc = pyqrcode.create(uri, error="M")
    buf = BytesIO()
    qrc.png(buf, scale=8)
    buf.seek(0)
    return buf


def build_email(addr_from, addr_to, mail_type, secret, uri, qrurl, reset_url):
    data = {"secret": secret, "qrurl": qrurl, "reset_url": reset_url}
    if mail_type=="register":
        subject = "密码设置说明"
        content_text = register_text % data
        content_html = register_html % data
    else:
        subject = "密码重置说明"
        content_text = resetpw_text % data
        content_html = resetpw_html % data
    
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = addr_from
    msgRoot['To'] = addr_to
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText(content_text)
    msgAlternative.attach(msgText)

    msgText = MIMEText(content_html, 'html')
    msgAlternative.attach(msgText)

    msgImage = MIMEImage(generate_qrcode(uri).read())

    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)
    return msgRoot


def sendmail(addr_to, secret, uri, qrurl, reset_url, mail_type):
    msgRoot = build_email(config['smtp_user'], addr_to, mail_type, secret, uri, qrurl, reset_url)
    smtp = smtplib.SMTP()
    logger.debug(smtp.connect(config['smtp_server'], config['smtp_port']))
    logger.debug(smtp.ehlo())
    logger.debug(smtp.starttls())
    logger.debug(smtp.ehlo())
    logger.debug(smtp.login(config['smtp_user'], config['smtp_pass']))
    logger.debug(smtp.sendmail(config['smtp_user'], addr_to, msgRoot.as_string()))
    logger.debug(smtp.quit())
