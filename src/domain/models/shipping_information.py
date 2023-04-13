from peewee import CharField, AutoField

from .. import BaseModel


class ShippingInformation(BaseModel):
    id = AutoField(primary_key=True)
    country = CharField()
    address = CharField()
    postal_code = CharField()
    city = CharField()
    province = CharField()
