#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : startup.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import uvicorn

if __name__ == '__main__':
    config = uvicorn.Config('main:app', host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)
    server.run()
