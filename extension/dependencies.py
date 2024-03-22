#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : dependencies.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import os
from datetime import datetime, timedelta
from typing import Union

from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import SessionLocal, schemas, models, get_db
from crud.crud import UserCRUD

router = APIRouter(
    tags=["token"],
    responses={404: {"message": "Not Found"}}
)

# SECRET_KEY=openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

crud = UserCRUD()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db_session() -> Session:
    """数据库会话"""
    with SessionLocal() as session:
        return session


def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_current_user(db: Session, email_or_username: str):
    """获取用户"""
    try:
        valid = validate_email(email_or_username)
        email = valid.normalized
    except EmailNotValidError:
        user = crud.get_user_by_username(db, email_or_username)
    else:
        user = crud.get_user_by_email(db, email)
    return user


def authenticate_user(db: Session, email_or_username: str, password: str):
    """验证用户"""
    user = get_current_user(db, email_or_username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    if user.disabled == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="此用户已被禁用，无法登录",
        )
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """创建token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def update_user_login_info(db: Session, email_or_username: str, client_host: str):
    """更新用户登录信息"""
    user = get_current_user(db, email_or_username)
    update_data = {
        models.User.loginNumber: user.loginNumber + 1,
        models.User.clientHost: client_host,
        models.User.lastLoginTime: datetime.now()
    }
    return crud.update_user_token(db, email_or_username, update_data)


@router.post("/token", response_model=schemas.Token, name='获取token')
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    client_host = request.client.host
    user = authenticate_user(get_db_session(), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, 'name': user.username}, expires_delta=access_token_expires
    )
    update_user_login_info(db, form_data.username, client_host)
    return {"access_token": access_token, "token_type": "bearer"}
