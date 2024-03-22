#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : login_signup.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import json
from datetime import datetime, timedelta

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from crud.crud import ConfirmStringCRUD
from db import schemas, models, get_db
from extension import response
from extension.dependencies import oauth2_scheme, SECRET_KEY, ALGORITHM, get_db_session, crud, get_password_hash, \
    ACCESS_TOKEN_EXPIRE_MINUTES
from lib.custom import check_code, jsonable_encoder_custom
from extension.redis_ import Service, Container
from tasks import tasks

router = APIRouter(
    prefix='/login-signup',
    tags=["user"],
    responses={404: {"message": "Not Found"}}
)

confirm_string_crud = ConfirmStringCRUD()


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据", )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(get_db_session(), email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """活跃用户"""
    if current_user.disabled == '停用':
        return response.response400(message='此用户已被禁用')
    return current_user


@router.get("/user", response_model=schemas.ResponseBase, tags=["login-signup"])
async def read_active_user(current_user: schemas.User = Depends(get_current_active_user)):
    current_user = schemas.User(**jsonable_encoder(current_user))
    return response.response200(jsonable_encoder(current_user))


@router.post("/send-email", response_model=schemas.ResponseBase, tags=["login-signup"], name='发送邮箱验证码')
@inject
async def send_active_email(email: schemas.Email, service: Service = Depends(Provide[Container.service]),
                            db: Session = Depends(get_db)):
    """发送邮件"""
    value = await service.get(email.email)
    if value:
        old_time = datetime.strptime(json.loads(value)['createTime'], "%Y-%m-%d %H:%M:%S")
        over_time = int(58 - (datetime.now() - old_time).total_seconds())  # 1分钟内只能发送一次，设置为58s
        if over_time >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"每次发送间隔 60 秒，剩余: {over_time} 秒")
        else:
            await service.delete(email.email)  # 删除缓存

    captcha = check_code()
    task = tasks.write_email.apply_async(args=[captcha, email.email])  # 分布式任务，发送邮件
    # 保存前先删除肯可能存在旧验证码
    confirm_string_crud.update_active_code(db, email.email, {models.ConfirmString.deleted: '1'})

    create_time = datetime.now()
    active_valid_time = (create_time + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    active_info = {
        "email": email.email,
        "activeCode": captcha,
        "activeValidityPeriod": active_valid_time,
        "createTime": create_time
    }
    await service.set(email.email, json.dumps(jsonable_encoder_custom(active_info)), ex=10 * 60)  # 保存
    active_info = schemas.ConfirmStringInDB(**jsonable_encoder(active_info))
    confirm_string_crud.save_active_code(db, active_info)
    return response.response200({"task_id": task.id})


def delete_active_code(email: str, db: Session):
    """删除激活信息"""
    return confirm_string_crud.update_active_code(db, email, {models.ConfirmString.deleted: '1'})


def check_captcha(captcha: str, email: str, db: Session):
    """检查验证码"""
    get_active_code = confirm_string_crud.get_active_code(db, email)
    if not get_active_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已失效，请重新发送邮件获取新验证码",
        )
    if datetime.now() > get_active_code.activeValidityPeriod:
        delete_active_code(email, db)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期，请重新发送邮件获取新验证码",
        )
    if captcha != get_active_code.activeCode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码不正确，请重新输入",
        )
    return get_active_code


def get_login_valid_time():
    """登录有效期"""
    return (datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")


@router.post("/sign-up", response_model=schemas.ResponseBase, tags=["login-signup"], name='用户注册')
async def sign_up_user(user: schemas.UserRegisterInDB, request: Request, db: Session = Depends(get_db)):
    db_user_email = crud.get_user_by_email(db, email=user.email)  # 查询邮箱是否已被注册
    db_user_username = crud.get_user_by_username(db, username=user.username)  # 查询账户是否已被注册
    if db_user_email:
        return response.response400('邮箱地址已经被使用，若忘记密码，可以使用邮箱修改密码')
    if db_user_username:
        return response.response400('此用户名已经被使用，请重新输入')
    check_captcha(user.captcha, user.email, db)
    delete_active_code(user.email, db)  # 删除激活信息
    user.password = get_password_hash(user.password)
    client_host = request.client.host  # 获取客户端IP
    user = schemas.UserRegister(**user.model_dump(), createTime=datetime.now(), clientHost=client_host)
    db_user = crud.create_user(db, user)
    if not db_user:
        return response.response400()
    return response.response200('Successfully sign up user')


@router.post('/update-password', response_model=schemas.ResponseBase, tags=["login-signup"], name='忘记密码')
async def update_password(user: schemas.UserUpdatePasswordInDB, request: Request, db: Session = Depends(get_db)):
    check_captcha(user.captcha, user.email, db)  # 验证验证码
    update_data = {
        models.User.password: get_password_hash(user.password),
        models.User.email: user.email,
        models.User.clientHost: request.client.host,
    }
    delete_active_code(user.email, db)  # 删除激活信息
    crud.update_user_password(db, user.email, update_data=update_data)
    return response.response200('Successfully updated user')
