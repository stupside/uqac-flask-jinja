import os

from flask import Config
from redis.client import StrictRedis, Redis


class AbstractConfig(Config):
    APPLICATION_DATABASE_NAME: str = os.getenv("APPLICATION_DATABASE_NAME")

    APPLICATION_DATABASE_HOST: str = os.getenv("APPLICATION_DATABASE_HOST")
    APPLICATION_DATABASE_PORT: int = os.getenv("APPLICATION_DATABASE_PORT")

    APPLICATION_DATABASE_USER: str = os.getenv("APPLICATION_DATABASE_USER")
    APPLICATION_DATABASE_PASSWORD: str = os.getenv("APPLICATION_DATABASE_PASSWORD")

    APPLICATION_REDIS_URI: str = os.getenv("APPLICATION_REDIS_URI")
    APPLICATION_REDIS_PORT: int = os.getenv("APPLICATION_REDIS_PORT")

    APPLICATION_PRODUCT_SERVICE: str = os.getenv("APPLICATION_PRODUCT_SERVICE")
    APPLICATION_SHOP_SERVICE: str = os.getenv("APPLICATION_SHOP_SERVICE")

    @property
    def REDIS_CONNECTION(self) -> Redis:
        return StrictRedis.from_url(url=self.APPLICATION_REDIS_URI, port=self.APPLICATION_REDIS_PORT)
