#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : celery_.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""

from celery import Celery
from celery.result import AsyncResult

from setting import CONFIG


def route_for_ask(name, *args, **kwargs):
    if ":" not in name:
        return {"queue": "celery"}
    queue, _ = name.split(":")
    return {"queue": queue}


def create_celery():
    celery = Celery(__name__)

    celery.conf.update(timezone=CONFIG.CELERY_TIMEZONE)  # 时区
    celery.conf.update(enable_utc=CONFIG.CELERY_ENABLE_UTC)  # 关闭UTC时区。默认启动
    celery.conf.update(task_routes=(route_for_ask,))  # 任务路由，为任务分配不同的队列

    celery.conf.update(task_track_started=CONFIG.CELERY_TASK_TRACK_STARTED)  # 启动任务跟踪
    celery.conf.update(task_serializer=CONFIG.CELERY_TASK_SERIALIZER)  # 任务序列化方式
    celery.conf.update(result_serializer=CONFIG.CELERY_RESULT_SERIALIZER)  # 结果序列化方式
    celery.conf.update(accept_content=CONFIG.CELERY_ACCEPT_CONTENT)  # 接受的类型
    celery.conf.update(result_expires=CONFIG.CELERY_RESULT_EXPIRES)  # 结 果过期时间，200s
    celery.conf.update(result_persistent=CONFIG.CELERY_RESULT_PERSISTENT)
    celery.conf.update(worker_send_task_events=CONFIG.CELERY_WORKER_SEND_TASK_EVENTS)
    celery.conf.update(worker_prefetch_multiplier=CONFIG.CELERY_WORKER_PREFETCH_MULTIPLIER)
    celery.conf.update(broker_connection_retry_on_startup=CONFIG.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP)  # 启动时重试代理连接

    return celery


def get_task_info(task_id):
    """返回给定task_id的任务信息"""
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result
