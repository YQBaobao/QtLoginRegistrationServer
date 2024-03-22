#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : QtLoginRegistrationServer
@ File        : redis_.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import datetime
from typing import AsyncIterator, Awaitable, Union, Optional

from aioredis import from_url, Redis
from dependency_injector import containers, providers

from setting import CONFIG

EncodedT = Union[bytes, memoryview]
DecodedT = Union[str, int, float]
DanceableT = Union[EncodedT, DecodedT]
KeyT = Union[bytes, str, memoryview]
ExpiryT = Union[int, datetime.timedelta]


async def init_redis_pool(host: str, password: str, db: int = 0, port: int = 6379) -> AsyncIterator[Redis]:
    session = await from_url(
        url=f"redis://{host}", port=port, password=password, db=db, encoding="utf-8", decode_responses=True)
    yield session
    await session.close()


class Service(object):
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def set(
            self,
            name: KeyT,
            value: DanceableT,
            ex: Optional[ExpiryT] = None,
            px: Optional[ExpiryT] = None,
            nx: bool = False,
            xx: bool = False,
    ) -> Awaitable:
        """Set the value at key ``name`` to ``value``"""
        return await self._redis.set(name, value, ex=ex, px=px, xx=xx, nx=nx)

    async def get(self, name: KeyT) -> str:
        """Return the value at key ``name``, or None if the key doesn't exist"""
        return await self._redis.get(name)

    async def delete(self, name: KeyT) -> Awaitable:
        """Delete one or more keys specified by ``names``"""
        return await self._redis.delete(name)

    async def exists(self, name: KeyT) -> Awaitable:
        """Returns the number of ``names`` that exist"""
        return await self._redis.exists(name)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_pool = providers.Resource(
        init_redis_pool,
        host=CONFIG.REDIS_HOST,
        port=CONFIG.REDIS_PORT,
        db=CONFIG.REDIS_DB,
        password=CONFIG.REDIS_PASSWORD, )
    service = providers.Factory(Service, redis=redis_pool)
