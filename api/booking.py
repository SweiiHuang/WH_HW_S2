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

booking_bp = Blueprint("booking_bp", __name__)

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


@booking_bp.route("/api/booking", methods=["GET", "POST", "DELETE"])
def booking_api():
    if request.method == "GET":
        currentToken = request.cookies.get("JWT_token")

        if currentToken == None:
            return {
                "error": True,
                "message": "未登入系統，拒絕存取"}, 403
        else:
            try:
                token_decode = jwt.decode(
                    currentToken, key, algorithms=["HS256"])
                memberId = token_decode["id"]

                connection = connection_pool.get_connection()
                cursor = connection.cursor()

                sql = '''SELECT 
                taipei_attractions.id,
                taipei_attractions.name,
                taipei_attractions.address,
                taipei_attractions.images,
                member.name,
                member.email,
                booking.memberId,
                booking.bookingDate,
                booking.bookingTime,
                booking.bookingPrice
                FROM
                booking
                INNER JOIN member ON member.id = booking.memberId 
                INNER JOIN taipei_attractions ON taipei_attractions.id = booking.attractionId
                WHERE booking.memberId = %s'''

                value = (memberId,)
                cursor.execute(sql, value,)
                result = cursor.fetchone()
                if result:
                    image = [result[3].split(",")][0]

                    attraction_dict = {
                        "id": result[0],
                        "name": result[1],
                        "address": result[2],
                        "image": image[0]
                    }

                    data_dict = {
                        "attraction": attraction_dict,
                        "date": result[7],
                        "time": result[8],
                        "price": result[9],
                        "memberName": result[4],
                        "memberEmail": result[5]
                    }
                    return {
                        "data": data_dict
                    }, 200

                else:
                    return {
                        "data": None
                    }, 200
            finally:
                cursor.close()
                connection.close()

    if request.method == "POST":
        trip = request.get_json()
        currentToken = request.cookies.get("JWT_token")

        if trip["attractionId"] == None or trip["date"] == None or trip["time"] == None or trip["price"] == None:
            return {"error": True,
                    "message": "建立失敗，輸入不正確或其他原因"}, 400
        elif currentToken == None:
            return {
                "error": True,
                "message": "未登入系統，拒絕存取"}, 403
        else:
            try:
                connection = connection_pool.get_connection()
                cursor = connection.cursor()

                token_decode = jwt.decode(
                    currentToken, key, algorithms=["HS256"])

                memberId = token_decode["id"]

                attraction_Id = trip["attractionId"]
                bookingDate = trip["date"]
                bookingTime = trip["time"]
                bookingPrice = trip["price"]

                sql_update = '''
                INSERT INTO booking (memberId, attractionId, bookingDate, bookingTime, bookingPrice)
                VALUES (%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE 
                memberId=%s, attractionId=%s, bookingDate=%s, bookingTime=%s, bookingPrice=%s;
                '''
                cursor.execute(sql_update,  (
                    memberId, attraction_Id,
                    bookingDate, bookingTime, bookingPrice,
                    memberId,
                    attraction_Id,
                    bookingDate, bookingTime, bookingPrice,
                ))
                connection.commit()

                return {"ok": True}, 200

            except:
                return {"error": True,
                        "message": "伺服器內部錯誤"}, 500
            finally:
                cursor.close()
                connection.close()

    if request.method == "DELETE":
        currentToken = request.cookies.get("JWT_token")
        if currentToken:
            token_decode = jwt.decode(currentToken, key, algorithms=["HS256"])
            memberId = token_decode["id"]
            try:
                connection = connection_pool.get_connection()
                cursor = connection.cursor()

                sql_delete = "DELETE FROM booking WHERE memberId=%s"
                booking_delete = (memberId,)
                cursor.execute(sql_delete, booking_delete)
                connection.commit()
                return {"ok": True}, 200
            except:
                return {"error": True, "message": "伺服器內部錯誤"}, 500
            finally:
                cursor.close()
                connection.close()
        else:
            return {"error": True,
                    "message": "未登入系統，拒絕存取"}, 403
