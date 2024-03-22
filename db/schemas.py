#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : schemas.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 创建初始 Pydantic模型,用于关联ORM
"""
from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict, EmailStr, constr


class ResponseBase(BaseModel):
    code: int
    message: str
    data: Union[list, dict, str] = []
    # https://docs.pydantic.dev/2.0/usage/models/#arbitrary-class-instances
    # 仅适用于模型响应,自定义响应需要使用 jsonable_encoder
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")})


class CommonBase(BaseModel):
    createTime: datetime


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[EmailStr, None] = None


# ConfirmString
class ConfirmStringBase(BaseModel):
    createTime: datetime


class ConfirmStringInDB(ConfirmStringBase):
    email: EmailStr
    activeCode: constr(max_length=255)
    activeValidityPeriod: datetime


# User
class UserRegisterInDB(BaseModel):
    """注册请求体"""
    username: constr(max_length=255)
    password: constr(max_length=255)
    email: EmailStr
    captcha: constr(max_length=8)


class UserRegister(UserRegisterInDB, CommonBase):
    disabled: int = 1
    deleted: int = 0
    clientHost: constr(max_length=20)


class UserUpdatePasswordInDB(BaseModel):
    """修改密码"""
    password: constr(max_length=255)
    email: EmailStr
    captcha: constr(max_length=8)


class UserBase(BaseModel):
    name: constr(max_length=255)
    username: constr(max_length=20)
    email: EmailStr
    disabled: int


class UserPassword(UserBase):
    password: Union[constr(max_length=255), None]


class UserCreateInDB(UserPassword):
    """创建请求体"""
    pass


class UserCreate(UserCreateInDB):
    createTime: datetime
    loginNumber: int = 0
    deleted: int = 0
    clientHost: constr(max_length=20)


class UserUpdateInDB(UserPassword):
    id: int


class User(CommonBase):
    id: int
    name: Union[constr(max_length=255), None] = None
    username: Union[constr(max_length=20), None] = None
    email: EmailStr
    disabled: int = None
    lastLoginTime: Union[datetime, None] = None
    loginValidTime: Union[datetime, None] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")}
    )


class Email(BaseModel):
    """发送验证码"""
    email: EmailStr
