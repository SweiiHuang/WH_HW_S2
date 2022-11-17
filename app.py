from flask import *
import json
import os
import re
import mysql.connector
import mysql.connector.pooling
from mysql.connector import Error
from mySQL import MySQLPassword

# Original-------------------
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Original-------------------
app.config["JSON_SORT_KEYS"] = False

# MySQL configurations
dbconfig = {
    "host": "localhost",
    "database": "attractions_db",
    "user": "root",
    "password": MySQLPassword()
}
# create connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
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


# Pages-------------------------------------


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


@app.route("/api/attractions", methods=["GET"])
def attractions_api():
    # Parameter
    page = request.args.get("page", 0)
    page = int(page)
    keyword = request.args.get("keyword", "")

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

    else:
        return {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }, 500  # 伺服器內部錯誤


@app.route("/api/attraction/<attractionId>", methods=["GET"])
def attractionsId_api(attractionId):

    cursor = connection.cursor()
    sql = "SELECT * FROM taipei_attractions WHERE id = %s"
    value = (attractionId,)
    cursor.execute(sql, value)
    result = cursor.fetchone()

    try:
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
                "images": [result[10]]
            }
            data = {"data": data_dict}
            return (data), 200
        else:
            return {
                "error": True,
                "message": "請按照情境提供對應的錯誤訊息"
            }, 400  # 景點編號不正確
    except:
        return {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }, 500  # 伺服器內部錯誤


@app.route("/api/categories", methods=["GET"])
def categories_api():
    cursor = connection.cursor()
    sql = "SELECT DISTINCT category FROM taipei_attractions"
    cursor.execute(sql)
    result = [item[0] for item in cursor.fetchall()]

    if result:
        return {
            "data": result
        }, 200  # 正常運作

    else:
        return {
            "error": True,
            "message": "請按照情境提供對應的錯誤訊息"
        }, 500  # 伺服器內部錯誤


app.run(host='0.0.0.0', port=3000, debug=True)
