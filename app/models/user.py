from typing import Dict


class User:
    def __init__(self, id:int=-1, name:str=None, email:str=None, password:str=None, role_id:int = None, typeU:str = None, image:str = None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role_id = role_id
        self.typeU = typeU
        self.image = image
    
    @classmethod
    def from_json(cls, json: Dict[str, any]):
      return cls(
        id=json.get("id"),
        name=json.get("name"),
        email=json.get("email"),
        password=json.get("password"),
        role_id=json.get("role_id"),
        typeU = json.get("type"),
        image =json.get("image")
      )
