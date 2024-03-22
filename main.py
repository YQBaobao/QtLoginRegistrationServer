#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : main.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import os.path

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html

from extension.celery_ import get_task_info, create_celery
from extension.redis_ import Container
from lib.logger import Logger
from extension import dependencies
from internal import login_signup
from router import user
from setting import CONFIG

title = "QtLoginRegistrationServer"
openapi_url = "/api/openapi.json"
swagger_ui_oauth2_redirect_url = "/docs/oauth2-redirect"
description = """
使用PyQt5+SQLAlchemy+FastAPI做的一个登录注册页，使用邮箱注册与验证，前后分离,其中：
QtLoginRegistrationClient仓库存放 GUI，QtLoginRegistrationServer仓库存放 API
"""


def create_dir(path):
    dirname = os.path.dirname(os.path.join(os.getcwd(), path))
    if not os.path.exists(dirname):
        os.mkdir(dirname)


# 日志
create_dir(CONFIG.LOG_SERVER)
server_log = Logger(filename=CONFIG.LOG_SERVER, name='uvicorn.access', level=CONFIG.LOG_SERVER_LIVE)
if CONFIG.LOG_SQLALCHEMY_STATUS:
    create_dir(CONFIG.LOG_SQLALCHEMY)
    Logger(filename=CONFIG.LOG_SQLALCHEMY, name='sqlalchemy.engine', level=CONFIG.LOG_SQLALCHEMY_LIVE)

app = FastAPI(
    title=title,
    version="1.0.0",
    openapi_url=openapi_url,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
    description=description,
    summary="QtLoginRegistration backend services",
    contact={
        "name": "yqbaowo",
        "email": "yqbaowo@foxmail.com",
    },
    license_info={
        "name": "LGPLv3",
        "url": "https://www.gnu.org/licenses/lgpl-3.0.html",
    },
)

celery = create_celery()
celery.conf.update(broker_url=CONFIG.CELERY_BROKER_URL)  # 代理
celery.conf.update(result_backend=CONFIG.CELERY_RESULT_BACKEND)  # 结果存储


# 事件
@app.on_event("startup")
async def startup_event():
    server_log.info('Application startup')


@app.on_event("shutdown")
async def shutdown_event():
    server_log.info('Application shutdown')


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Hello Qt Login Registration Server", "docs": "/docs", "redoc": "/redoc"}


@app.get("/task/{task_id}", tags=["task"])
async def get_task_status(task_id: str) -> dict:
    return get_task_info(task_id)


# 替换默认错误响应
# https://fastapi.tiangolo.com/zh/tutorial/handling-errors/#requestvalidationerror
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(exc.errors()),
    )


app.include_router(router=dependencies.router)
# 业务
app.include_router(router=login_signup.router, prefix="/user")
app.include_router(router=user.router, prefix="/user")

# 本地文档
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title="FShuttleFrameworkServer" + " - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/js/swagger-ui-bundle.js",
        swagger_css_url="/static/css/swagger-ui.css",
        swagger_favicon_url='/static/favicon.ico',
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=openapi_url,
        title=title + " - ReDoc",
        redoc_js_url="/static/js/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico"
    )


# redis依赖
container = Container()
container.config.redis_host.from_value("192.167.6.139")
container.config.redis_password.from_env("REDIS_PASSWORD")
container.config.redis_db.from_value(0)
container.config.redis_port.from_value(6379)
container.wire(modules=[login_signup.__name__])
