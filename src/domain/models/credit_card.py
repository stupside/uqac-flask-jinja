from peewee import CharField, IntegerField, AutoField

from .. import BaseModel


class CreditCard(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    first_digits = CharField()
    last_digits = CharField()
    expiration_year = IntegerField()
    expiration_month = IntegerField()
