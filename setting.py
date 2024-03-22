#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : setting.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""

import os


# 使用方法：若需要修改默认参数，则直接在子类中用相同参数名称重新设置即可
# 需要配置的环境变量：EMAIL_PASSWORD，DB_USERNAME,DB_PASSWORD,REDIS_PASSWORD
class Setting(object):
    BASE_PATH = os.path.dirname(__file__)  # Setting.py 所在的绝对路径
    BASE_DIR = os.path.abspath(BASE_PATH)

    EMAIL_USERNAME = "wuniuwo@foxmail.com"  # 发送邮件的邮箱
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # 邮箱密码,配置环境变量：EMAIL_PASSWORD

    # ASGI 日志
    LOG_SERVER = 'log/server.log'  # 服务日志路径（日志路径前不能加'/'否则会被创建在根目录）
    LOG_SERVER_LIVE = 'INFO'  # 日志级别

    LOG_SQLALCHEMY_STATUS = False  # 是否记录，若开启记录，则表示默认开启 SQLALCHEMY_ECHO=True
    LOG_SQLALCHEMY = 'log/database.log'  # 数据库日志路径（日志路径前不能加'/'否则会被创建在根目录）
    LOG_SQLALCHEMY_LIVE = 'INFO'  # 日志级别

    # Database 默认参数
    # 使用SQLALCHEMY + PYMYSQL操作数据库
    # 配置参见：https://www.osgeo.cn/sqlalchemy/core/engines.html
    DB = {
        'HOST': '192.167.6.139',
        'PORT': 3307,
        'USERNAME': os.getenv('DB_USERNAME'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'DBNAME': 'login-register'
    }
    URI = f"mysql+pymysql://{DB['USERNAME']}:{DB['PASSWORD']}@{DB['HOST']}:{DB['PORT']}/{DB['DBNAME']}"
    SQLALCHEMY_DATABASE_URI = URI
    SQLALCHEMY_AUTO_COMMIT = False  # 自动提交事务
    SQLALCHEMY_AUTO_FLUSH = False  # 自动发送变更
    SQLALCHEMY_POOL_SIZE = 10  # 连接数，默认5
    SQLALCHEMY_MAX_OVERFLOW = 20  # 超出连接数时，允许再新建的连接数,但是这5个人时不使用时，直接回收，默认10
    SQLALCHEMY_POOL_TIMEOUT = 30  # 等待可用连接时间，超时则报错，默认为30秒
    SQLALCHEMY_POOL_RECYCLE = 3600  # 连接生存时长（秒），超过则该连接被回收，再生存新连接,默认-1不回收连接
    SQLALCHEMY_POOL_PRE_PING = True  # 连接池的“预ping”，在每次签出时测试连接的活动性,若出现disconnect错误，该连接将立即被回收

    SQLALCHEMY_ECHO = False  # 显示原始SQL语句
    SQLALCHEMY_ECHO_POOL = False  # 连接池记录信息

    # Redis 默认参数
    REDIS_HOST = DB['HOST']
    REDIS_PORT = 6379
    REDIS_DB = 0  # 0-15
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

    # Celery 默认参数
    # 使用Redis做代理，需要安装库：pip install celery[redis]
    CELERY_BROKER_URL = f"redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"  # 代理服务
    CELERY_RESULT_BACKEND = f"redis://default:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"  # 结果存储
    CELERY_TIMEZONE = "Asia/Shanghai"  # 时区
    CELERY_ENABLE_UTC = False  # 关闭UTC时区。默认启动
    CELERY_TASK_TRACK_STARTED = True  # 启动任务跟踪
    CELERY_TASK_SERIALIZER = "pickle"  # 任务序列化方式
    CELERY_RESULT_SERIALIZER = "pickle"  # 结果序列化方式
    CELERY_ACCEPT_CONTENT = ['pickle', 'json']  # 接受的类型
    CELERY_RESULT_EXPIRES = 60 * 60 * 24  # 结果过期时间，60 * 60 * 24 s
    CELERY_RESULT_PERSISTENT = True
    CELERY_WORKER_SEND_TASK_EVENTS = False
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # 启动时重试代理连接

    def __getitem__(self, key):
        return self.__getattribute__(key)


class DevelopConfig(Setting):
    """开发环境"""
    # Database
    SQLALCHEMY_ECHO = False  # 显示原始SQL语句
    SQLALCHEMY_ECHO_POOL = False  # 连接池记录信息


# 环境映射关系
mapping = {
    'develop': DevelopConfig,
}

CONFIG = mapping[os.environ.get('APP_ENV', 'develop').lower()]()  # 获取指定的环境
