from datetime import date
from typing import Dict


class Medicine:
  def __init__(self, id:int = None, concept:str = None, creation_date:date = None, stock:int=None, price:float=None, typeM:str=None, user_id:int=None, expiration_date:date=None, location:str=None):
    self.id = id
    self.concept = concept
    self.creation_date = creation_date
    self.stock = stock
    self.price = price
    self.typeM = typeM
    self.location = location
    self.user_id = user_id
    self.expiration_date= expiration_date

  @classmethod
  def from_json(cls, json:Dict[str, any]):
    return cls(
      id = json.get('id'),
      concept = json.get('concept'),
      creation_date= json.get('creation_date'),
      stock= json.get('stock'),
      price= json.get('price'),
      typeM= json.get('type'),
      location= json.get('location'),
      user_id= json.get('user_id'),
      expiration_date= json.get('expiration_date'),
    )

