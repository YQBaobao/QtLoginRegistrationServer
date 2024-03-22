#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : response.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
from typing import Union

from fastapi.responses import JSONResponse
from fastapi import status


def content(data: Union[list, dict, str], total: int, message: str):
    return {'code': 0, 'message': message, 'detail': data, 'total': total}


def response200(data: Union[list, dict, str], total: int = 0, message: str = 'Success') -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=content(data, total, message)
    )


def response400(data: str = '', message: str = 'Bad Request') -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content(data, 0, message)

    )


def response401(data: str = '', message: str = 'Unauthorized') -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=content(data, 0, message)
    )


def response403(data: str = '', message: str = 'Forbidden Access') -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=content(data, 0, message)
    )


def response500(data: str = '', message: str = 'Internal Server Error') -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR_CODE,
        content=content(data, 0, message)
    )
