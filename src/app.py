import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token, get_jwt_identity,
                                jwt_required)
from flask_mysqldb import MySQL

from src.constants import PAGE_SIZE
from src.models.patient import Patient
from src.models.user import User

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
  "ssl": {"ca": "certificado.pem"},
  # "ssl_mode": "VERIFY_IDENTITY"
}
mysql = MySQL(app)

@app.route('/patients', methods=["GET"])
@cross_origin(origin="*")
def getPatients():
    limitFrom = int(request.args.get('from', 0))
    limitTo = int(request.args.get('to', PAGE_SIZE))

    cursor = mysql.connection.cursor()
    cursor.execute("SHOW SESSION VARIABLES LIKE 'character\_set\_%'")
    print(cursor.fetchall())
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

@app.route('/auth/login', methods=['POST'])
@cross_origin()
def authLogin():
    # email = request.json.get("email", None)
    # password = request.json.get("password", None)

    cursor = mysql.connection.cursor()
    # cursor.execute('''SELECT id FROM user WHERE email = 'diegomzepeda11@gmail.com' AND password = '123455678';''')
    cursor.execute("SELECT JSON_OBJECT('id', id) FROM user WHERE email = %(email)s AND password = %(password)s LIMIT 1", request.json)
    queryResult = cursor.fetchone()

    if queryResult == None: 
          # el usuario no se encontró en la base de datos
        return jsonify({"msg": "Credenciales invalidas, verifique los datos introducidos."}), 401
    
    jsonResult = json.loads(queryResult[0])
    user = User.from_json(jsonResult)
    
    # crea un nuevo token con el id de usuario dentro
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token, user_id=user.id), 200



@app.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
@cross_origin()
def authRefresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200

