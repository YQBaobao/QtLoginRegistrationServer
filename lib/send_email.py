#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : send_email.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import smtplib

import yagmail

from setting import CONFIG


class BasicEmail(object):

    def __init__(self, user, password, host='smtp.qq.com'):
        """使用的 QQ邮箱服务"""
        self.yag = yagmail.SMTP(user=user, password=password, host=host)

    def send(self, subject, contents: list, to: list, attachments: list = None):
        """发送"""
        self.yag.send(subject=subject, contents=contents, to=to, attachments=attachments)

    def close(self):
        """关闭"""
        self.yag.close()


class SendEmail(BasicEmail):
    def __init__(self):
        user = CONFIG.EMAIL_USERNAME
        password = CONFIG.EMAIL_PASSWORD
        super().__init__(user, password)

    def send_active_email(self, captcha, to: str):
        """发送激活邮件"""
        subject = 'QtLoginRegistration 邮箱验证码：{}'.format(captcha)
        contents = [
            '''<div style="width:500px;margin: auto;">
                您好！<br>
                欢迎使用并注册 QtLoginRegistration<br>
                这是你的邮箱激活验证码，有效期为 <b>5</b> 分钟，且仅可使用一次，过期或使用后均将失效。<br>
                如你同意激活，请将下方的六位数验证码，输入到 QtLoginRegistration 邮箱确认框中<br>
                <P><b style="font-size:20px">{}</b><P>
                若你没有注册 QtLoginRegistration 且收到了此邮件，则请忽略，因为本邮件并不会有任何的安全隐患！<br>
                祝福您<br>
                QtLoginRegistration 开发团队<br>
            </div>'''.format(captcha)
        ]
        to = [to, ]
        try:
            self.send(subject=subject, contents=contents, to=to)
        except smtplib.SMTPDataError as e:
            print(e)
        finally:
            self.close()

