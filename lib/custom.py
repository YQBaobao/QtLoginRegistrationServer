#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : custom.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import os
import string
import zipfile
from datetime import datetime
from random import randint, choices

from fastapi.encoders import jsonable_encoder


def jsonable_encoder_custom(obj):
    """自定义编码"""
    custom_encoder = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    return jsonable_encoder(obj, custom_encoder=custom_encoder)


def check_code() -> str:
    """六位验证码数字加大写字母"""
    code: str = ''
    for i in range(6):
        current = randint(0, 6)
        temp = chr(randint(65, 90)) if current != i else randint(0, 9)
        code += str(temp)
    return code


def check_code2() -> str:
    """六位验证码数字加大写字母"""
    return ''.join(choices(string.ascii_uppercase + string.digits, k=6))
