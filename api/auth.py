from flask import *
from flask import Flask
import requests
import json
import os
import re
import jwt
import mysql.connector
import mysql.connector.pooling

from mysql.connector import Error
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask import jsonify
from flask import Blueprint
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


auth_bp = Blueprint("auth_bp", __name__)


dbPASSWORD = os.getenv("DB_PASSWORD")
partnerKEY = os.getenv("PARTNER_KEY")
merchantID = os.getenv("MERCHANT_ID")
key = os.getenv("JWT_KEY")

dbconfig = {
    "host": "localhost",
    "database": "attractions_db",
    "user": "root",
    "password": dbPASSWORD,
}


connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=10,
    pool_reset_session=True,
    **dbconfig
)

bcrypt = Bcrypt()


@auth_bp.route("/api/user", methods=["POST"])  # 新會員註冊
def register_api():
    member = request.get_json()
    name = member["name"]
    email = member["email"]
    password = member["password"]
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    match = email_pattern.match(email)

    if match:
        try:
            connection = connection_pool.get_connection()
            cursor = connection.cursor()
            
            sql = "SELECT * FROM member WHERE email = %s"
            value = (email,)
            cursor.execute(sql, value)
            result = cursor.fetchall()
            
            if result:
                return {
                    "error": True,
                    "message": "Email已被註冊"
                    }, 400
            else:
                cursor = connection.cursor()
                sql_update = "INSERT INTO member VALUES (NULL,%s, %s, %s,CURRENT_TIMESTAMP)"
                member_update = (
                name, email, pw_hash,)
                cursor.execute(sql_update, member_update)
                
                connection.commit()
                
                return {
                    "ok": True
                    }, 200
        except:
            return {
                "error": True,
                "message": "伺服器內部錯誤"
                }, 500
        finally:
            cursor.close()
            connection.close()
    else:
        return {"error": True, "message": "無效的Email格式"}, 400
    


@auth_bp.route("/api/user/auth", methods=["GET", "PUT", "DELETE"])
def auth_api():
    if request.method == "GET":
        currentToken = request.cookies.get("JWT_token")
        if currentToken:
            try:
                connection = connection_pool.get_connection()
                cursor = connection.cursor()
                token_decode = jwt.decode(
                    currentToken, key, algorithms=["HS256"])
                sql = "SELECT * FROM member WHERE id = %s"
                value = (token_decode["id"],)
                cursor.execute(sql, value)
                result = cursor.fetchone()
                return make_response(jsonify({
                    "data": {
                        "id": result[0],
                        "name": result[1],
                        "email": result[2]
                    }
                }), 200)
            finally:
                cursor.close()
                connection.close()
        else:
            resp = make_response(jsonify({"data": None}), 200)
        return resp

    if request.method == "PUT":
        member = request.get_json()
        email = member["email"]
        password = member["password"]

        try:
            connection = connection_pool.get_connection()
            cursor = connection.cursor()

            sql = "SELECT * FROM member WHERE email = %s"
            value = (email,)
            cursor.execute(sql, value)
            result = cursor.fetchone()

            if result:
                if bcrypt.check_password_hash(result[3], password) == True:
                    token_encode = jwt.encode(
                        {"id": result[0], }, key, algorithm="HS256")
                    resp = make_response({"ok": True}, 200)
                    resp.set_cookie(key="JWT_token",
                                    value=token_encode, max_age=604800)
                    return resp
                else:
                    bcrypt.check_password_hash(result[3], password) == False
                    resp = make_response(
                        {"error": True, "message": "登入失敗，密碼錯誤"}, 400)
                return resp
            else:
                resp = make_response(
                    {"error": True, "message": "登入失敗，帳號錯誤"}, 400)
                return resp

        except:
            resp = make_response({"error": True, "message": "伺服器內部錯誤"}, 500)
            return resp

        finally:
            cursor.close()
            connection.close()

    if request.method == "DELETE":
        resp = make_response({"ok": True}, 200)
        resp.set_cookie(key="JWT_token", value="", max_age=-1)
    return resp
