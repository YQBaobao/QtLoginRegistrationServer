#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : crud.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 数据交互动作
"""
from typing import Union

from email_validator import validate_email, EmailNotValidError
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_

from db import models, schemas


class Crud(object):
    @staticmethod
    def _commit(db: Session, db_obj):
        try:
            db.commit()
            return db_obj
        except Exception:
            db.rollback()
            return


class ConfirmStringCRUD(Crud):

    @staticmethod
    def get_active_code(db: Session, email: str) -> Union[models.ConfirmString, None]:
        """获取"""
        return db.query(models.ConfirmString).filter(
            and_(models.ConfirmString.deleted == 0, models.ConfirmString.email == email)).first()

    def save_active_code(self, db: Session, active_info: schemas.ConfirmStringInDB):
        """保存激活信息"""
        db_active = models.ConfirmString(**active_info.model_dump())
        db.add(db_active)
        return self._commit(db, db_active)

    def update_active_code(self, db: Session, email: str, update_data: dict):
        """更新"""
        db_active = db.query(models.ConfirmString).filter(
            and_(models.ConfirmString.email == email, models.ConfirmString.deleted == 0)).update(update_data)
        return self._commit(db, db_active)


class UserCRUD(Crud):
    @staticmethod
    def get_user_total(db: Session):
        """返回总数"""
        return db.query(models.User).filter(and_(models.User.deleted == 0)).count()

    @staticmethod
    def get_users(db: Session, name: str, skip: int = 0, limit: int = 100):
        return db.query(models.User).filter(
            and_(or_(models.User.name.like(f"%{name}%"), name is None), models.User.deleted == '0')
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Union[models.User, None]:
        return db.query(models.User).filter(and_(models.User.email == email, models.User.deleted == '0')).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Union[models.User, None]:
        return db.query(models.User).filter(and_(models.User.username == username, models.User.deleted == '0')).first()

    @staticmethod
    def get_user_by_id(db: Session, uid: str) -> Union[models.User, None]:
        return db.query(models.User).filter(and_(models.User.id == uid, models.User.deleted == '0')).first()

    def create_user(self, db: Session, user: schemas.UserCreate):
        """新建"""
        db_user = models.User(**user.model_dump(exclude={'captcha'}))
        db.add(db_user)
        return self._commit(db, db_user)

    def update_user_token(self, db: Session, email_or_username: str, update_data: dict):
        """登录时更新"""
        try:
            valid = validate_email(email_or_username)
            email = valid.normalized
            db_user = db.query(models.User).filter(
                and_(models.User.email == email, models.User.deleted == '0')).update(update_data)
        except EmailNotValidError:
            db_user = db.query(models.User).filter(
                and_(models.User.username == email_or_username, models.User.deleted == '0')).update(update_data)
        return self._commit(db, db_user)

    def update_user_password(self, db: Session, email: str, update_data: dict):
        """更新密码"""
        db_user = db.query(models.User).filter(
            and_(models.User.email == email, models.User.deleted == '0')).update(update_data)
        return self._commit(db, db_user)

    def update_user(self, db: Session, uid: int, update_data: dict):
        """更新"""
        db_user = db.query(models.User).filter(
            and_(models.User.id == uid, models.User.deleted == '0')).update(update_data)
        return self._commit(db, db_user)

    def delete_user(self, db: Session, uid: int):
        """删除"""
        db_user = db.query(models.User).filter(and_(models.User.id == uid)).update({models.User.deleted: 1})
        return self._commit(db, db_user)
