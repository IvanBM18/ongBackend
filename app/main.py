import imp
import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token, get_jwt_identity,
                                jwt_required)
from flask_mysqldb import MySQL

from app.constants import PAGE_SIZE
from app.models.patient import Patient
from app.models.medicine import Medicine
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
  mysql.connection.commit()
  cursor.close()

  return jsonify({'message': 'ok'}), 200

@app.route('/patients/<int:id>', methods=["DELETE"])
@cross_origin(origin="*")
def deletePatient(id):
  cursor = mysql.connection.cursor()
  query = '''
    DELETE FROM patient
    WHERE id = %d
  ''' % (int(id))
  cursor.execute(query)
  mysql.connection.commit()
  cursor.close()

  return jsonify({'message': 'ok'}), 200

@app.route('/patients', methods=["POST"])
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
  mysql.connection.commit()
  cursor.close()

  return jsonify({'message': 'ok'}), 200



'''- - - - - - - - - MEDICINE ENDPOINTS - - - - - - - - - '''
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
  mysql.connection.commit()
  cursor.close()

  return jsonify({'message': 'ok'}), 200

@app.route('/medicines/<int:id>', methods=["PUT"])
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
  mysql.connection.commit()
  cursor.close()
  
  return jsonify({'message': 'ok'}), 200

'''- - - - - - - - - AUTH ENDPOINTS - - - - - - - - - '''
@app.route('/auth/login', methods=['POST'])
@cross_origin()
def authLogin():
    # email = request.json.get("email", None)
    # password = request.json.get("password", None)

    cursor = mysql.connection.cursor()
    # cursor.execute('''SELECT id FROM user WHERE email = 'diegomzepeda11@gmail.com' AND password = '123455678';''')
    cursor.execute("SELECT JSON_OBJECT('id', id, 'name', name, 'email', email, 'role_id', role_id, 'image', image) FROM user WHERE email = %(email)s AND password = %(password)s LIMIT 1", request.json)
    queryResult = cursor.fetchone()

    if queryResult == None: 
          # el usuario no se encontró en la base de datos
        return jsonify({"msg": "Credenciales invalidas, verifique los datos introducidos."}), 401
    
    userJson = json.loads(queryResult[0])
    user = User.from_json(userJson)
    
    # crea un nuevo token con el id de usuario dentro
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token, user=userJson), 200



@app.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
@cross_origin()
def authRefresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200

