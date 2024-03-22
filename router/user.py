#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : user.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends, Request, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from db import schemas, get_db, models
from extension import response
from extension.dependencies import crud, get_password_hash, oauth2_scheme
from lib.custom import jsonable_encoder_custom

router = APIRouter(
    tags=["user"],
    dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not Found"}}
)


@router.get("/list", response_model=schemas.ResponseBase)
async def read_users(search: Union[str, None] = Query(default=None),
                     skip: int = 0,
                     limit: int = 20,
                     db: Session = Depends(get_db)):
    """获取列表"""
    search = search if search else None
    total = crud.get_user_total(db)
    users = crud.get_users(db, search, skip, limit)
    users = [schemas.User(**jsonable_encoder(user)) for user in users]
    return response.response200(jsonable_encoder_custom(users), total)


@router.post("/create", response_model=schemas.ResponseBase)
async def create_user(user: schemas.UserCreateInDB, request: Request, db: Session = Depends(get_db)):
    """创建"""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        return response.response400('电子邮件已注册')
    user.password = get_password_hash(user.password)
    time = datetime.now()
    client_host = request.client.host
    user = schemas.UserCreate(**user.model_dump(), createTime=time, clientHost=client_host)
    db_user = crud.create_user(db, user)
    if not db_user:
        return response.response400()
    return response.response200('Successfully created user')


@router.get("/get-user-info/{user_id}", response_model=schemas.ResponseBase)
async def get_user_info(user_id: int, db: Session = Depends(get_db)):
    """根据ID获取信息"""
    user = crud.get_user_by_id(db, uid=user_id)
    if not user:
        return response.response200('')
    user = schemas.User(**jsonable_encoder(user))
    return response.response200(jsonable_encoder(user))


@router.put("/update", response_model=schemas.ResponseBase, response_model_exclude_defaults=True)
async def update_user_info(user: schemas.UserUpdateInDB, request: Request, db: Session = Depends(get_db)):
    """更新用户信息"""
    update_data = {
        models.User.name: user.name,
        models.User.email: user.email,
        models.User.sex: user.sex,
        models.User.disabled: user.disabled,
        models.User.clientHost: request.client.host,
    }
    if user.password:
        update_data.update({models.User.password: get_password_hash(user.password)})
    crud.update_user(db, uid=user.id, update_data=update_data)
    return response.response200('Successfully updated user')


@router.delete("/delete/{user_id}", response_model=schemas.ResponseBase)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    crud.delete_user(db, uid=user_id)
    return response.response200("Successfully deleted user")
