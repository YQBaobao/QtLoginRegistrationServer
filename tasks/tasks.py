#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : tasks.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""

import smtplib

from celery import shared_task
from lib.send_email import SendEmail


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2},
             name='user:write_email')
def write_email(self, captcha: str, email: str):
    try:
        send_email = SendEmail()
        send_email.send_active_email(captcha, email)
    except smtplib.SMTPDataError:
        return {'status': 550, "msg": "邮箱地址可能不存在，请检查"}
    except Exception as e:
        return {'status': 500, "msg": str(e.args)}
    return {'status': 200, "msg": "Successfully sent email"}
