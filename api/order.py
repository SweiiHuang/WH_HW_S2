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

order_bp = Blueprint("order_BP", __name__)

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


@order_bp.route("/api/orders", methods=["POST","GET"])
def order_api():
    if request.method == "POST":
        currentToken = request.cookies.get("JWT_token")
        
        if currentToken == None:
            return {
                "error": True,
                "message": "未登入系統，請重新登入"}, 403
        else:
            order = request.get_json()
            prime = order["prime"]
            price = order["order"]["price"]
            tripId = order["order"]["trip"]["attraction"]["id"]
            date = order["order"]["trip"]["date"]
            time = order["order"]["trip"]["time"]
            name = order["order"]["contact"]["name"]
            email = order["order"]["contact"]["email"]
            phone = order["order"]["contact"]["phone"]

            if name == None or email == None or phone == None:
                return {
                    "error": True,
                    "message": "請填入完整訂購資訊"}, 400
            else:
                try:
                    token_decode = jwt.decode(
                        currentToken, key, algorithms=["HS256"])

                    memberId = token_decode["id"]
                    order_number = datetime.now().strftime("%Y%m%d%H%M%S")
                    status = "未付款"

                    connection = connection_pool.get_connection()
                    cursor = connection.cursor()

                    sql_update = '''
                    INSERT INTO order_list(
                        orderId,
                        orderNumber,
                        paymentStatus,
                        orderMemberId,
                        orderMemberName,
                        orderMemberEmail,
                        orderMemberPhone,
                        orderAttractionId,
                        orderDate,
                        orderTime,
                        orderPrice,
                        createTime)
                    VALUE
                    (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP)
                    '''
                    order_update = (order_number, status,
                                    memberId, name, email, phone, tripId, date, time, price)
                    cursor.execute(sql_update, order_update)

                    sql_delete = '''DELETE FROM booking WHERE memberId=%s'''
                    booking_delete = (memberId,)
                    cursor.execute(sql_delete, booking_delete)

                    connection.commit()
                    cursor.close()
                    connection.close()

                    headers = {"Content-Type": "application/json",
                            "x-api-key": partnerKEY}

                    order_data = {
                        "prime": prime,
                        "partner_key": partnerKEY,
                        "merchant_id": merchantID,
                        "order_number": order_number,
                        "details": name+"的訂單",
                        "amount": price,
                        "cardholder": {
                            "phone_number": phone,
                            "name": name,
                            "email": email,
                        },
                    }

                    # Pay by Prime (Server to TapPayServer)
                    response = requests.post("https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime", headers=headers,
                                            json=order_data).json()
                    status_code = response["status"]

                    if status_code == 0:
                        status = "已付款"
                        connection = connection_pool.get_connection()
                        cursor = connection.cursor()
                        sql_update = '''
                        UPDATE order_list
                        SET paymentStatus=%s
                        WHERE orderNumber=%s'''

                        order_update = (status, order_number)
                        cursor.execute(sql_update, order_update)
                        connection.commit()

                        cursor.close()
                        connection.close()

                        return {

                            "data": {
                                "number": order_number,
                                "payment": {
                                    "status": status_code,
                                    "message": "付款成功"
                                }
                            }}, 200
                    else:
                        return {
                            "data": {
                                "number": order_number,
                                "payment": {
                                    "status": status_code,
                                    "message": "付款失敗"
                                }
                            }}, 200

                except:
                    return {
                        "error": True,
                        "message": "伺服器內部錯誤"
                    }, 500

    if request.method == "GET":
        currentToken = request.cookies.get("JWT_token")
        if currentToken == None:
            return {
                "error": True,
                "message": "未登入系統，請重新登入"}, 403
        else:
            try:
                token_decode = jwt.decode(
                currentToken, key, algorithms=["HS256"])
                memberId = token_decode["id"]

                connection = connection_pool.get_connection()
                cursor = connection.cursor()

                sql_old_order = '''
                SELECT * FROM order_list WHERE orderMemberId =%s
                '''
                value = (memberId,)

                cursor.execute(sql_old_order,value)
                result = cursor.fetchall()
                if len(result) > 0:
                    outcome =[]
                    for i in range(len(result)):
                        order_dict = {
                            "ordernumber":result[i][1],
                            "orderdate":result[i][11],
                            "paymentstatus":result[i][2],
                            "orderprice":result[i][10],
                        }
                        outcome.append(order_dict)

                    return {"data":outcome },200
                else:
                    return{
                        "data":None,
                        "message":"查無歷史訂單資料"
                    },200

                    
            except:
                return {"error": True, "message": "伺服器內部錯誤"}, 500
                  
            finally:
                cursor.close()
                connection.close()


@order_bp.route("/api/order/<orderNumber>", methods=["GET"])
def oderNumber_api(orderNumber):
    currentToken = request.cookies.get("JWT_token")
    if currentToken == None:
        return {
            "error": True,
            "message": "未登入系統，請重新登入"}, 403
    else:
        try:
            connection = connection_pool.get_connection()
            cursor = connection.cursor()
            
            sql_search = '''
            SELECT * 
            FROM order_list 
            INNER JOIN taipei_attractions  
            ON order_list.orderAttractionId = taipei_attractions.id 
            WHERE orderNumber = %s'''

            value = (orderNumber,)

            cursor.execute(sql_search,value)
            result = cursor.fetchone()
            
            return{
                    "data": {
                        "number": result[1],
                        "price": result[10],
                        "trip": {
                            "attraction": {
                            "id": result[7],
                            "name": result[14],
                            "address": result[17],
                            "image": result[22].split(",")[0]
                            },
                        "date": result[8],
                        "time": result[9]
                            },
                        "contact": {
                                "name": result[4],
                                "email": result[5],
                                "phone": result[6]
                                },
                        "status": result[2]
                                }
                                },200
        except:
            return{
                "data":None
            },200

        finally:
            cursor.close()
            connection.close()



