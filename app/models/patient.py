from typing import Dict


class Patient:
  def __init__(self, id:int = None, name:str = None, age:int = None, phoneNumber:str=None, gender:str='U', observations:str=None, program:str=None):
    self.id = id
    self.name = name
    self.age = age
    self.phoneNumber = phoneNumber
    self.observations = observations
    self.program = program
    self.gender= gender

  @classmethod
  def from_json(cls, json:Dict[str, any]):
    return cls(
      id = json.get('id'),
      name = json.get('name'),
      age= json.get('age'),
      phoneNumber= json.get('phone_number'),
      observations= json.get('observations'),
      gender= json.get('gender'),
      program= json.get('program'),
    )
