#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : logger.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import logging
from logging import handlers
from sys import stdout
from warnings import simplefilter


class Logger(logging.Logger):
    level_relations = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename, name=__name__, level='DEBUG', when='W0', back_count=10):
        super().__init__(name, level)
        self.format = "%(asctime)s - %(levelname)s - %(message)s"
        format_str = logging.Formatter(self.format)  # 设置日志格式

        # 忽略警告错误：ResourceWarning: Enable tracemalloc to get the object allocation traceback
        simplefilter(action='ignore', category=ResourceWarning)

        self.logger = logging.getLogger(name)
        self.logger.handlers.clear()  # 每次被调用后，清空已经存在handler
        self.logger.setLevel(self.level_relations.get(level.upper()))  # 设置日志级别
        sh = logging.StreamHandler(stdout)  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(
            filename=filename, when=when, backupCount=back_count, encoding='utf-8')  # 往文件里写入
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
