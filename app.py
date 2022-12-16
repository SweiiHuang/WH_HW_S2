from flask import *
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
from datetime import datetime, timedelta

# Original-------------------
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Original-------------------
app.config["JSON_SORT_KEYS"] = False

CORS(app)
bcrypt = Bcrypt(app)

key = "thisissecret"


# MySQL configurations
dbconfig = {
    "host": "localhost",
    "database": "attractions_db",
    "user": "root",
    "password": "root20137aws",
}
# create connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=10,
    pool_reset_session=True,
    **dbconfig
)

try:
    connection = connection_pool.get_connection()
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("資料庫版本：", db_Info)  # 顯示資料庫版本

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("目前使用的資料庫：", record)  # 顯示目前使用的資料庫

except Error as e:
    print("資料庫連接失敗：", e)

finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("資料庫連線已關閉")


# Original Pages------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")


@app.route("/booking")
def booking():
    return render_template("booking.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")
# Pages End-----------------------------------
# 預定行程API-----------------------------------


@app.route("/api/booking", methods=["GET", "POST", "DELETE"])
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

# 會員相關API----------------------------------


@app.route("/api/user", methods=["POST"])  # 新會員註冊
def register_api():
    member = request.get_json()
    name = member["name"]
    email = member["email"]
    password = member["password"]
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

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


@app.route("/api/user/auth", methods=["GET", "PUT", "DELETE"])
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


# ----------------------------------------------
# 旅遊景點API


@app.route("/api/attractions", methods=["GET"])
def attractions_api():

    # Parameter
    page = request.args.get("page", 0)
    page = int(page)
    keyword = request.args.get("keyword", "")

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        sql = "SELECT * FROM taipei_attractions WHERE category =%s or name LIKE %s ORDER BY id LIMIT %s, %s"
        value = (keyword, ("%"+keyword+"%"), (page*12), 12)
        cursor.execute(sql, value)
        result = cursor.fetchall()
        if len(result) > 0:
            outcome = []
            for i in range(len(result)):
                data_dict = {
                    "id": result[i][0],
                    "name": result[i][2],
                    "category": result[i][3],
                    "description": result[i][4],
                    "address": result[i][5],
                    "transport": result[i][6],
                    "mrt": result[i][7],
                    "lat": result[i][8],
                    "lng": result[i][9],
                    "images": result[i][10].split(",")
                }
                outcome.append(data_dict)

        if len(result) == 12:
            page_add = (page+1)
        else:
            page_add = None

        data = {"nextPage": page_add, "data": outcome}
        return (data), 200  # 正常運作

    except:
        return {
            "error": True,
            "message": "伺服器內部錯誤"
        }, 500  # 伺服器內部錯誤

    finally:
        cursor.close()
        connection.close()


@app.route("/api/attraction/<attractionId>", methods=["GET"])
def attractionsId_api(attractionId):

    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        sql = "SELECT * FROM taipei_attractions WHERE id = %s"
        value = (attractionId,)
        cursor.execute(sql, value)
        result = cursor.fetchone()

        if result:
            data_dict = {
                "id": result[0],
                "name": result[2],
                "category": result[3],
                "description": result[4],
                "address": result[5],
                "transport": result[6],
                "mrt": result[7],
                "lat": result[8],
                "lng": result[9],
                "images": result[10].split(",")
            }
            data = {"data": data_dict}
            return (data), 200
        else:
            return {
                "error": True,
                "message": "景點編號不正確"
            }, 400  # 景點編號不正確
    except:
        return {
            "error": True,
            "message": "伺服器內部錯誤"
        }, 500  # 伺服器內部錯誤

    finally:
        cursor.close()
        connection.close()


@app.route("/api/categories", methods=["GET"])
def categories_api():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        sql = "SELECT DISTINCT category FROM taipei_attractions"
        cursor.execute(sql)
        result = [item[0] for item in cursor.fetchall()]

        if result:
            return {
                "data": result
            }, 200  # 正常運作

    except:
        return {
            "error": True,
            "message": "伺服器內部錯誤"
        }, 500  # 伺服器內部錯誤

    finally:
        cursor.close()
        connection.close()


app.run(host='0.0.0.0', port=3000, debug=True)
