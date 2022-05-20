from typing import Dict


class Program:
  def __init__(self, id:int = None, name:str = None, updated_at:str = None, created_at:int=None):
    self.id = id
    self.name = name
    self.updated_at = updated_at
    self.created_at = created_at

  @classmethod
  def from_json(cls, json:Dict[str, any]):
    return cls(
      id = json.get('id'),
      name = json.get('name'),
      updated_at= json.get('updated_at'),
      created_at= json.get('created_at'),
    )
