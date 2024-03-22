#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : __init__.py.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 数据库操作
"""

from setting import CONFIG

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(
    CONFIG.SQLALCHEMY_DATABASE_URI,
    pool_size=CONFIG.SQLALCHEMY_POOL_SIZE,
    max_overflow=CONFIG.SQLALCHEMY_MAX_OVERFLOW,
    pool_recycle=CONFIG.SQLALCHEMY_POOL_RECYCLE,
    pool_timeout=CONFIG.SQLALCHEMY_POOL_TIMEOUT,
    pool_pre_ping=CONFIG.SQLALCHEMY_POOL_PRE_PING,
    echo=CONFIG.SQLALCHEMY_ECHO,
    echo_pool=CONFIG.SQLALCHEMY_ECHO_POOL
)

SessionLocal = sessionmaker(bind=engine, autocommit=CONFIG.SQLALCHEMY_AUTO_COMMIT,
                            autoflush=CONFIG.SQLALCHEMY_AUTO_FLUSH)

Base = declarative_base()


class BaseModules(Base):
    __abstract__ = True

    def single_to_dict(self):
        """单个对象方法1(.first())"""
        model_dict = dict(self.__dict__)
        del model_dict['_sa_instance_state']
        return model_dict

    Base.to_dict = single_to_dict

    def single_to_dict2(self):
        """单个对象方法2(.first())"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def double_to_dict(self):
        """多个对象(.all()),该方法可以将获取结果进行定制，例如如下是将所有非空值输出成str类型"""
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result

    def double_to_dict2(self):
        """多个对象(.all()),将时间戳值转为str类型，其他直接输出"""
        from datetime import datetime
        result = {}
        for key in self.__mapper__.c.keys():
            if type(getattr(self, key)) == datetime:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result


# 可正常使用yield时，则默认使用此函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 如无法使用，则配合中间件使用下方函数
# 详见：https://fastapi.tiangolo.com/zh/tutorial/sql-databases/#_14
