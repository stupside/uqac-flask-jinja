from peewee import Model

from peewee import Proxy

database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy
