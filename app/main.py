import imp
import json
import os
from datetime import date, datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token, get_jwt_identity,
                                jwt_required)
from flask_mysqldb import MySQL

from app.constants import PAGE_SIZE
from app.models.action_type import ActionType
from app.models.delivery import Delivery
from app.models.medicine import Medicine
from app.models.patient import Patient
from app.models.program import Program
from app.models.user import User

load_dotenv()

app = Flask(__name__)

# Configure CORS
web = '*' #os.getenv("WEB_URL")
cors = CORS(app, resources={r"*": {"origins": web}})
app.config['CORS_HEADERS'] = 'Content-Type'

# Configure JWT Tokens
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

# Configure MYSQL Connection
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] =os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 3600000
app.config["MYSQL_CUSTOM_OPTIONS"] = {
  "ssl": {"ca": "./certificado.pem"},
  "ssl_mode": "VERIFY_IDENTITY"
}
mysql = MySQL(app)


""" --------------------- PATIENTS ENDPOINTS --------------------- """
@app.route('/patients', methods=["GET"])
@cross_origin(origin="*")
def getPatients():
    limitFrom = int(request.args.get('from', 0))
    limitTo = int(request.args.get('to', PAGE_SIZE))

    cursor = mysql.connection.cursor()

    cursor.execute('''
      SELECT JSON_OBJECT(
        'id', id, 
        'name', name, 
        'age', age, 
        'phone_number', phone_number, 
        'gender', gender, 
        'observations', observations,
        'program', program  
      ) FROM patient
        LIMIT %d,%d
      '''% (limitFrom, limitTo)
      )
    queryResult = cursor.fetchall()
    patients = []
    for row in queryResult:
      patient = json.loads(row[0])
      patients.append(patient)

    # Props
    cursor.execute('''SELECT count(*) FROM patient''')
    queryResult = cursor.fetchone()
    total = queryResult[0]

    cursor.close()

    res = {
      'patients': patients,
      'total': total,
      'paging': {
        'from': limitFrom,
        'to': limitTo
      }
    }

    return jsonify(res), 200

@app.route('/patients/<int:id>', methods=["PUT"])
@jwt_required()
@cross_origin(origin="*")
def updatePatient(id):
  data = request.get_json()
  p = Patient.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    UPDATE patient
    SET name = COALESCE(%s, name),
     age = COALESCE(%s, age),
     phone_number = COALESCE(%s, phone_number),
     program = COALESCE(%s, program),
     observations = COALESCE(%s, observations),
     gender = %s
    WHERE id = %d
  ''' % (
    f"'{p.name}'" if p.name is not None else 'NULL',
    f"{p.age}" if p.age is not None else 'NULL',
    f"'{p.phoneNumber}'" if p.phoneNumber is not None else 'NULL',
    f"'{p.program}'" if p.program is not None else 'NULL',
    f"'{p.observations}'" if p.observations is not None else 'NULL',
    f"'{p.gender}'" if p.gender is not None else 'U',
    int(id)
  )
  cursor.execute(query)

  userId = get_jwt_identity()
  addAction(action=ActionType.PATIENT_UPDATE, dataId=id, userId=userId)
  

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/patients/<int:id>', methods=["DELETE"])
@jwt_required()
@cross_origin(origin="*")
def deletePatient(id):
  cursor = mysql.connection.cursor()
  query = '''
    DELETE FROM patient
    WHERE id = %d
  ''' % (int(id))
  cursor.execute(query)

  userId = get_jwt_identity()
  addAction(action=ActionType.PATIENT_DELETE, dataId=id, userId=userId)

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/patients', methods=["POST"])
@jwt_required()
@cross_origin(origin="*")
def createPatient():
  data = request.get_json()
  p = Patient.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    INSERT INTO patient (name, age, phone_number, program, observations, gender)
    VALUES (%s, %s, %s, %s, %s, %s)
  ''' % (
    f"'{p.name}'" if p.name is not None else 'NULL',
    f"{p.age}" if p.age is not None else 'NULL',
    f"'{p.phoneNumber}'" if p.phoneNumber is not None else 'NULL',
    f"'{p.program}'" if p.program is not None else 'NULL',
    f"'{p.observations}'" if p.observations is not None else 'NULL',
    f"'{p.gender}'" if p.gender is not None else "'N'" 
  )
  cursor.execute(query)

  cursor.execute("SELECT LAST_INSERT_ID()")
  patientId = cursor.fetchone()[0]
  userId = get_jwt_identity()
  addAction(action=ActionType.PATIENT_ADD, dataId=patientId, userId=userId)
  

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200



'''- - - - - - - - -  MEDICINE ENDPOINTS - - - - - - - - - '''
@app.route('/medicines', methods=["GET"])
@cross_origin(origin="*")
def getMedicines():
    limitFrom = int(request.args.get('from', 0))
    limitTo = int(request.args.get('to', PAGE_SIZE))

    cursor = mysql.connection.cursor()

    cursor.execute('''
      SELECT JSON_OBJECT(
        'id', id, 
        'concept', concept, 
        'creation_date', creation_date, 
        'stock', stock, 
        'price', price, 
        'type', type,
        'location', location,  
        'user_id', user_id,  
        'expiration_date', expiration_date  
      ) FROM medicine
        LIMIT %d,%d
      '''% (limitFrom, limitTo)
      )
    queryResult = cursor.fetchall()
    medicines = []
    for row in queryResult:
      medicine = json.loads(row[0])
      medicines.append(medicine)

    # Props
    cursor.execute('''SELECT count(*) FROM medicine''')
    queryResult = cursor.fetchone()
    total = queryResult[0]

    cursor.close()

    res = {
      'medicines': medicines,
      'total': total,
      'paging': {
        'from': limitFrom,
        'to': limitTo
      }
    }

    return jsonify(res), 200

@app.route('/medicines', methods=["POST"])
@jwt_required()
@cross_origin(origin="*")
def createMedicine():
  data = request.get_json()
  p = Medicine.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    INSERT INTO medicine (concept, stock, price, type, location, user_id, expiration_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
  ''' % (
    f"'{p.concept}'" if p.concept is not None else 'NULL',
    f"'{p.stock}'" if p.stock is not None else 'NULL',
    f"'{p.price}'" if p.price is not None else 'NULL',
    f"'{p.typeM}'" if p.typeM is not None else 'NULL',
    f"'{p.location}'" if p.location is not None else 'NULL' ,
    f"'{p.user_id}'" if p.user_id is not None else '0' ,
    f"'{p.expiration_date}'" if p.expiration_date is not None else 'NULL' ,
  )
  cursor.execute(query)

  cursor.execute("SELECT LAST_INSERT_ID()")
  medId = cursor.fetchone()[0]
  userId = get_jwt_identity()
  addAction(action=ActionType.MEDICINE_ADD, dataId=medId, userId=userId)

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/medicines/<int:id>', methods=["PUT"])
@jwt_required()
@cross_origin(origin="*")
def updateMedicine(id):
  data = request.get_json()
  m = Medicine.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    UPDATE medicine
    SET concept = COALESCE(%s, concept),
     stock = COALESCE(%s, stock),
     price = COALESCE(%s, price),
     type = COALESCE(%s, type),
     location = COALESCE(%s, location),
     expiration_date = COALESCE(%s, expiration_date)
    WHERE id = %d
  ''' % (
    f"'{m.concept}'" if m.concept is not None else 'NULL',
    f"{m.stock}" if m.stock is not None else 'NULL',
    f"'{m.price}'" if m.price is not None else 'NULL',
    f"'{m.typeM}'" if m.typeM is not None else 'NULL',
    f"'{m.location}'" if m.location is not None else 'NULL',
    f"'{m.expiration_date}'" if m.expiration_date is not None else 'NULL',
    int(id)
  )
  cursor.execute(query)
  
  userId = get_jwt_identity()
  addAction(action=ActionType.MEDICINE_UPDATE, dataId=id, userId=userId)

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/medicines/<int:id>', methods=["DELETE"])
@jwt_required()
@cross_origin(origin="*")
def deleteMedicine(id):
  cursor = mysql.connection.cursor()
  query = '''
    DELETE FROM medicine 
    WHERE id = %d
  ''' % (int(id))
  cursor.execute(query)


  userId = get_jwt_identity()
  addAction(action=ActionType.MEDICINE_DELETE, dataId=id, userId=userId)

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200


'''- - - - - - - - - Delivery ENDPOINTS - - - - - - - - - '''
@app.route('/delivery', methods=["GET"])
@cross_origin(origin="*")
def getDelivery():
    limitFrom = int(request.args.get('from', 0))
    limitTo = int(request.args.get('to', PAGE_SIZE))

    cursor = mysql.connection.cursor()

    cursor.execute('''
      SELECT JSON_OBJECT(
        'id', id, 
        'description', description, 
        'delivery_date', delivery_date, 
        'stock', stock, 
        'price', price, 
        'user_id', user_id,
        'medicine_id', medicine_id,
        'patient_id', patient_id,
        'expiration_date', expiration_date
      ) FROM delivery 
        LIMIT %d,%d
      '''% (limitFrom, limitTo)
      )
    queryResult = cursor.fetchall()
    deliveries = []
    for row in queryResult:
      delivery = json.loads(row[0])
      deliveries.append(delivery)

    # Props
    cursor.execute('''SELECT count(*) FROM delivery''')
    queryResult = cursor.fetchone()
    total = queryResult[0]

    cursor.close()

    res = {
      'deliveries': deliveries,
      'total': total,
      'paging': {
        'from': limitFrom,
        'to': limitTo
      }
    }

    return jsonify(res), 200

@app.route('/delivery', methods=["POST"])
@jwt_required()
@cross_origin(origin="*")
def createDelivery():
  data = request.get_json()
  p = Delivery.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    INSERT INTO delivery (description, stock, price, user_id,medicine_id, patient_id, expiration_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
  ''' % (
    f"'{p.description}'" if p.description is not None else 'NULL',
    f"'{p.stock}'" if p.stock is not None else 'NULL',
    f"{p.price}" if p.price is not None else 'NULL',
    f"{p.user_id}" if p.user_id is not None else '0' ,
    f"{p.medicine_id}" if p.medicine_id is not None else '0' ,
    f"{p.patient_id}" if p.patient_id is not None else '0' ,
    f"'{p.expiration_date}'" if p.expiration_date is not None else '0',
  )
  print(query)
  cursor.execute(query)

  cursor.execute("SELECT LAST_INSERT_ID()")
  deliveryId = cursor.fetchone()[0]
  userId = get_jwt_identity()
  addAction(action=ActionType.DELIVERY_ADD, dataId=deliveryId, userId=userId)

  cursor.execute('UPDATE medicine SET stock = stock - %d WHERE id = %d' % (p.stock, p.medicine_id))
  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/delivery/<int:id>', methods=["PUT"])
@jwt_required()
@cross_origin(origins="*")
def updateDelivery(id):
  data = request.get_json()
  d = Delivery.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    UPDATE delivery
    SET description = COALESCE(%s, description),
      stock = COALESCE(%s, stock),
      delivery_date = COALESCE(%s, delivery_date),
      price = COALESCE(%s, price),
      user_id = COALESCE(%s, user_id),
      medicine_id = COALESCE(%s, medicine_id),
      patient_id = COALESCE(%s, patient_id),
      expiration_date = COALESCE(%s, expiration_date)
    WHERE id = %d
  ''' % (
    f"'{d.description}'" if d.description is not None else 'NULL',
    f"'{d.stock}'" if d.stock is not None else 'NULL',
    f"'{d.delivery_date}'" if d.delivery_date is not None else 'NULL',
    f"'{d.price}'" if d.price is not None else 'NULL',
    f"'{d.user_id}'" if d.user_id is not None else 'NULL',
    f"'{d.medicine_id}'" if d.medicine_id is not None else 'NULL',
    f"'{d.patient_id}'" if d.patient_id is not None else 'NULL',
    f"'{d.expiration_date}'" if d.expiration_date is not None else 'NULL',
    int(id)
  )

  userId = get_jwt_identity()
  addAction(action=ActionType.DELIVERY_UPDATE, dataId=id, userId=userId)

  cursor.execute(query)

  mysql.connection.commit()
  cursor.close()
  return jsonify({"message":"ok"}), 200

@app.route('/delivery/<int:id>', methods=["DELETE"])
@jwt_required()
@cross_origin(origin="*")
def deleteDelivery(id):
  cursor = mysql.connection.cursor()
  userId = get_jwt_identity()
  query = '''
    DELETE FROM delivery 
    WHERE id = %d
  ''' % (int(id))
  cursor.execute(query)

  id = get_jwt_identity()
  addAction(action=ActionType.DELIVERY_DELETE, dataId=id, userId=userId)

  mysql.connection.commit()
  cursor.close()
  addAction(userId=userId, action=ActionType.USER_LOGIN)

  return jsonify({'message': 'ok'}), 200


'''- - - - - - - - - Programs ENDPOINTS - - - - - - - - - '''
@app.route('/program', methods=["GET"])
@cross_origin(origin="*")
def getPrograms():
    cursor = mysql.connection.cursor()

    cursor.execute('''
      SELECT JSON_OBJECT(
        'id', id, 
        'name', name,
        'created_at', created_at,
        'updated_at', updated_at
      ) FROM program 
      '''
      )
    queryResult = cursor.fetchall()
    programs = []
    for row in queryResult:
      program = json.loads(row[0])
      programs.append(program)

    # Props
    cursor.execute('''SELECT count(*) FROM program''')
    queryResult = cursor.fetchone()
    total = queryResult[0]

    cursor.close()

    res = {
      'programs': programs,
      'total': total,
    }

    return jsonify(res), 200

@app.route('/program', methods=["POST"])
@jwt_required()
@cross_origin(origin="*")
def createProgram():
  data = request.get_json()
  p = Program.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    INSERT INTO program (name)
    VALUES (%s)
  ''' % (
    f"'{p.name}'" if p.name is not None else 'NULL'
  )
  print(query)
  cursor.execute(query)

  cursor.execute("SELECT LAST_INSERT_ID()")
  programId = cursor.fetchone()[0]
  userId = get_jwt_identity()
  addAction(action=ActionType.PROGRAM_ADD , dataId=programId, userId=userId)

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/program/<int:id>', methods=["PUT"])
@jwt_required()
@cross_origin(origin="*")
def updateProgram(id):
  data = request.get_json()
  p = Program.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    UPDATE program
    SET name = COALESCE(%s, name)
    WHERE id = %d
  ''' % (
    f"'{p.name}'" if p.name is not None else 'NULL',
    int(id)
  )
  cursor.execute(query)

  userId = get_jwt_identity()
  addAction(action=ActionType.PROGRAM_UPDATE , dataId=id, userId=userId)
  
  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/program/<int:id>', methods=["DELETE"])
@jwt_required()
@cross_origin(origin="*")
def deleteProgram(id):
  cursor = mysql.connection.cursor()
  userId = get_jwt_identity()
  
  ""
  query = '''
    UPDATE patient SET program=-1 WHERE program=%d
  ''' % (int(id))
  cursor.execute(query)
  
  query = '''
    DELETE FROM program 
    WHERE id = %d
  ''' % (int(id))
  cursor.execute(query)
  

  userId = get_jwt_identity()
  addAction(action=ActionType.PROGRAM_DELETE, dataId=id, userId=userId)

  mysql.connection.commit()
  cursor.close()

  return jsonify({'message': 'ok'}), 200



'''- - - - - - - - - USER ENDPOINTS - - - - - - - - - '''
@app.route('/users', methods=["GET"])
@cross_origin(origin="*")
def getUsers():
    limitFrom = int(request.args.get('from', 0))
    limitTo = int(request.args.get('to', PAGE_SIZE))

    cursor = mysql.connection.cursor()

    cursor.execute('''
      SELECT JSON_OBJECT(
        'id', id, 
        'name', name, 
        'email', email, 
        'password', password,
        'role_id', role_id,
        'type', type,
        'image',image
      ) FROM user
        LIMIT %d,%d
      '''% (limitFrom, limitTo)
      )
    queryResult = cursor.fetchall()
    users = []
    for row in queryResult:
      user = json.loads(row[0])
      users.append(user)

    # Props
    cursor.execute('''SELECT count(*) FROM user''')
    queryResult = cursor.fetchone()
    total = queryResult[0]

    cursor.close()

    res = {
      'users': users,
      'total': total,
      'paging': {
        'from': limitFrom,
        'to': limitTo
      }
    }

    return jsonify(res), 200

@app.route('/users', methods=["POST"])
@jwt_required()
@cross_origin(origin="*")
def createUser():
  data = request.get_json()
  u = User.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    INSERT INTO user (name, email, password, role_id, type, image)
    VALUES (%s, %s, %s, %s, %s, %s)
  ''' % (
    f"'{u.name}'" if u.name is not None else 'NULL',
    f"'{u.email}'" if u.email is not None else 'NULL',
    f"'{u.password}'" if u.password is not None else 'NULL',
    f"'{u.role_id}'" if u.role_id is not None else 'NULL' ,
    f"'{u.typeU}'" if u.typeU is not None else 'NULL',
    f"'{u.image}'" if u.image is not None else 'NULL' ,
  )
  cursor.execute(query)

  cursor.execute("SELECT LAST_INSERT_ID()")
  indexId = cursor.fetchone()[0]
  userId = get_jwt_identity()
  addAction(action=ActionType.USER_ADD,dataId=indexId, userId=userId)

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/users/<int:id>', methods=["PUT"])
@jwt_required()
@cross_origin(origin="*")
def updateUser(id):
  data = request.get_json()
  u = User.from_json(data)

  cursor = mysql.connection.cursor()
  query = '''
    UPDATE user
    SET name = COALESCE(%s, name),
     email = COALESCE(%s, email),
     password = COALESCE(%s, password),
     type = COALESCE(%s, type),
     role_id = COALESCE(%s, role_id),
     image = COALESCE(%s, image)
    WHERE id = %d
  ''' % (
    f"'{u.name}'" if u.name is not None else 'NULL',
    f"'{u.email}'" if u.email is not None else 'NULL',
    f"'{u.password}'" if u.password is not None else 'NULL',
    f"'{u.typeU}'" if u.typeU is not None else 'NULL',
    f"'{u.role_id}'" if u.role_id is not None else 'NULL',
    f"'{u.image}'" if u.image is not None else 'NULL',
    int(id)
  )
  cursor.execute(query)
  
  

  mysql.connection.commit()
  cursor.close()
  return jsonify({'message': 'ok'}), 200

@app.route('/users/<int:id>', methods=["DELETE"])
@jwt_required()
@cross_origin(origin="*")
def deleteUser(id):
  cursor = mysql.connection.cursor()
  userId = get_jwt_identity()
  query = '''
    DELETE FROM user 
    WHERE id = %d
  ''' % (int(id))

  cursor.execute(query)

  id = get_jwt_identity()
  addAction(action=ActionType.USER_DELETE, userId=userId)

  mysql.connection.commit()
  cursor.close()

  return jsonify({'message': 'ok'}), 200



'''- - - - - - - - - AUTH ENDPOINTS - - - - - - - - - '''
@app.route('/auth/login', methods=['POST'])
@cross_origin(origins="*")
def authLogin():
    cursor = mysql.connection.cursor()
    # cursor.execute('''SELECT id FROM user WHERE email = 'diegomzepeda11@gmail.com' AND password = '123455678';''')
    cursor.execute("SELECT JSON_OBJECT('id', id, 'name', name, 'email', email, 'role_id', role_id, 'image', image) FROM user WHERE email = %(email)s AND password = %(password)s LIMIT 1", request.json)
    queryResult = cursor.fetchone()

    if queryResult == None: 
          # el usuario no se encontró en la base de datos
        return jsonify({"msg": "Credenciales invalidas, verifique los datos introducidos."}), 401
    
    userJson = json.loads(queryResult[0])
    user = User.from_json(userJson)

    userId = user.id
    addAction(userId=userId, action=ActionType.USER_LOGIN)

    # crea un nuevo token con el id de usuario dentro
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id, )
    return jsonify(access_token=access_token, refresh_token=refresh_token, user=userJson), 200

@app.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
@cross_origin(origin="*")
def authRefresh():
    print('refresh')
    userId = get_jwt_identity()
    access_token = create_access_token(identity=userId)
    return jsonify(access_token=access_token), 200


@app.route('/auth/logut', methods=['POST'])
@jwt_required()
@cross_origin()
def authLogout():
    userId = get_jwt_identity()
    addAction(userId=userId, action=ActionType.USER_LOGOUT)
    return jsonify({"msg": "Token revocado."}), 200




'''------------------ STATS ENDPOINT ------------------'''
@app.route('/stats', methods=['GET'])
@cross_origin()
def getStats():
    currentMonth = datetime.now().month
    
    cursor = mysql.connection.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM patient')
    totalPatients = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM medicine')
    totalMedicines = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM delivery')
    totalDeliveries = cursor.fetchone()[0]


    cursor.execute('SELECT COUNT(*) FROM action WHERE type_id = %s AND MONTH(createdAt) = %s', (ActionType.PATIENT_ADD.value, currentMonth))
    patientsMonth = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM action WHERE type_id = %s AND MONTH(createdAt) = %s', (ActionType.PATIENT_DELETE.value, currentMonth))
    deletedPatientsMonth = cursor.fetchone()[0]
  
    patientStats = getStatsByAction(ActionType.PATIENT_ADD)


    cursor.execute('SELECT COUNT(*) FROM action WHERE type_id = %s AND MONTH(createdAt) = %s', (ActionType.DELIVERY_ADD.value, currentMonth))
    countDeliveriesMonth = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM action WHERE type_id = %s AND MONTH(createdAt) = %s', (ActionType.DELIVERY_DELETE.value, currentMonth))
    deletedDeliveriesMonth = cursor.fetchone()[0]

    deliveriesStats = getStatsByAction(ActionType.DELIVERY_ADD)


    cursor.execute('SELECT COUNT(*) FROM action WHERE type_id = %s AND MONTH(createdAt) = %s', (ActionType.MEDICINE_ADD.value, currentMonth))
    countDeliveriesMonth = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM action WHERE type_id = %s AND MONTH(createdAt) = %s', (ActionType.MEDICINE_DELETE.value, currentMonth))
    deletedMedicinesMonth = cursor.fetchone()[0]

    medicinesStats = getStatsByAction(ActionType.MEDICINE_ADD)

    return jsonify(
      total_patients=totalPatients,
      total_medicines=totalMedicines,
      total_deliveries=totalDeliveries,
      month={
        'patients': {
          'total':(patientsMonth-deletedPatientsMonth),
          'statistics':patientStats
        },
        'deliveries': {
          'total': (countDeliveriesMonth-deletedDeliveriesMonth),
          'statistics': deliveriesStats
        },
        'medicines': {
          'total': (countDeliveriesMonth-deletedMedicinesMonth),
          'statistics': medicinesStats
        },
      }), 200



# Used to log actions in the database
def addAction(userId:int, action: ActionType, dataId:int = None):
    cursor = mysql.connection.cursor()
    text = ""
  
    if action == ActionType.PATIENT_ADD:
      text = f"El usuario [{userId}] ha agregado un nuevo paciente"
    elif action == ActionType.PATIENT_UPDATE:
      text = f"El usuario [{userId}] ha actualizado la información de un paciente"
    elif action == ActionType.PATIENT_DELETE:
      text = f"El usuario [{userId}] ha eliminado un paciente"
    
    elif action == ActionType.USER_ADD:
      text = f"El usuario [{userId}] ha agregado un nuevo usuario"
    elif action == ActionType.USER_UPDATE:
      text = f"El usuario [{userId}] ha actualizado la información de un usuario"
    elif action == ActionType.USER_DELETE:
      text = f"El usuario [{userId}] ha eliminado un usuario"
    elif action == ActionType.USER_LOGIN:
      text = f"El usuario [{userId}] ha iniciado sesión"
    elif action == ActionType.USER_LOGOUT:
      text = f"El usuario [{userId}] ha cerrado sesión"
    
    elif action == ActionType.MEDICINE_ADD:
      text = f"El usuario [{userId}] ha agregado un nuevo medicamento"
    elif action == ActionType.MEDICINE_UPDATE:
      text = f"El usuario [{userId}] ha actualizado la información de un medicamento"
    elif action == ActionType.MEDICINE_DELETE:
      text = f"El usuario [{userId}] ha eliminado un medicamento"

    elif action == ActionType.DELIVERY_ADD:
      text = f"El usuario [{userId}] ha agregado una nueva entrega"
    elif action == ActionType.DELIVERY_UPDATE:
      text = f"El usuario [{userId}] ha actualizado la información de una entrega"
    elif action == ActionType.DELIVERY_DELETE:
      text = f"El usuario [{userId}] ha eliminado una entrega"

    elif action == ActionType.PROGRAM_ADD:
      text = f"El usuario [{userId}] ha agregado un nuevo programa"
    elif action == ActionType.PROGRAM_UPDATE:
      text = f"El usuario [{userId}] ha actualizado la información de un program"
    elif action == ActionType.DELIVERY_DELETE:
      text = f"El usuario [{userId}] ha eliminado una entrega"
    query = '''
      INSERT INTO action (type_id, type_name, text, user_id, data_id)
      VALUES (%d, '%s', '%s', %s, %d)
    ''' % (action.value, action.name, text, userId, dataId if dataId is not None else -1)

    cursor.execute(query)
    mysql.connection.commit()
    cursor.close()


def getStatsByAction(action: ActionType):
  cursor = mysql.connection.cursor()
  cursor.execute('SELECT createdAt FROM action WHERE type_id = %s', (action.value,))
  actions = cursor.fetchall()
  stats = {}
  for _ in actions:
    d : datetime.datetime = _[0]
    dS = d.strftime('%d-%m-%Y')
    stats[dS] = stats.get(dS, 0) + 1
  stats = [{
    'count': value,
    'date': key
  } for key, value in stats.items()]
  stats.sort(key=lambda x: x['date'])
  return stats
