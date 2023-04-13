from peewee import FloatField, CharField, BooleanField, AutoField
from playhouse.hybrid import hybrid_property

from .. import BaseModel


class Transaction(BaseModel):
    id = AutoField(primary_key=True)

    external_id = CharField(unique=True)

    success = BooleanField(default=False)
    error = CharField(null=True)

    amount_charged = FloatField(default=0)
