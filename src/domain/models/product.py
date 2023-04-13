from peewee import CharField, IntegerField, FloatField, Check, BooleanField, AutoField
from playhouse.hybrid import hybrid_property

from .. import BaseModel


class Product(BaseModel):
    id = AutoField(primary_key=True)

    name = CharField(unique=True)
    description = CharField()

    price = FloatField(constraints=[Check("price > 0")])

    height = IntegerField(constraints=[Check("height > 0")])
    weight = IntegerField(constraints=[Check("weight > 0")])

    image = CharField()
    type = CharField()

    in_stock = BooleanField(default=False)

    @hybrid_property
    def shipping_price(self):

        if self.weight <= 500:
            return 5
        elif self.weight <= 2000:
            return 10

        return 25
