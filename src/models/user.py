from typing import Dict


class User:
    def __init__(self, id:int=-1, name:str=None, email:str=None, password:str=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
    
    @classmethod
    def from_json(cls, json: Dict[str, any]):
      return cls(
        id=json.get("id"),
        name=json.get("name"),
        email=json.get("email"),
        password=json.get("password")
      )
