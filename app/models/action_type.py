from enum import Enum

# IMPORTANT: Keep updated with the database

class ActionType(Enum):
  # User Actions
  USER_ADD = 1
  USER_UPDATE = 2
  USER_DELETE = 3
  USER_LOGIN = 10
  USER_LOGOUT = 11

  # Medicine Actions
  MEDICINE_ADD = 4
  MEDICINE_UPDATE = 5
  MEDICINE_DELETE = 6

  # Patient Actions
  PATIENT_ADD = 7
  PATIENT_UPDATE = 8
  PATIENT_DELETE = 9

  # Delivery Actions
  DELIVERY_ADD = 12
  DELIVERY_UPDATE = 13
  DELIVERY_DELETE = 14
  
  # Delivery Actions
  PROGRAM_ADD = 15
  PROGRAM_UPDATE = 16
  PROGRAM_DELETE = 17
  
