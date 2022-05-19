from datetime import date
from typing import Dict

class Delivery:
  def __init__(self, id:int = None, description:str = None, delivery_date:str = None, stock:int=None, price:float=None, medicine_id:str=None, user_id:int=None, patient_id:str=None):
    self.id = id
    self.description = description
    self.delivery_date = delivery_date
    self.stock = stock
    self.price = price
    self.user_id = user_id
    self.medicine_id = medicine_id
    self.patient_id = patient_id
  @classmethod
  def from_json(cls, json:Dict[str, any]):
    return cls(
      id = json.get('id'),
      description = json.get('description'),
      delivery_date= json.get('delivery_date'),
      stock= json.get('stock'),
      price= json.get('price'),
      user_id= json.get('user_id'),
      medicine_id = json.get('medicine_id'),
      patient_id = json.get('patient_id'),
    )