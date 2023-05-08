from api.attraction import attraction_bp
from api.order import order_bp
from api.booking import booking_bp
from api.auth import auth_bp
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


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["JSON_SORT_KEYS"] = False

app.register_blueprint(attraction_bp)
app.register_blueprint(order_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(auth_bp)

CORS(app)
bcrypt = Bcrypt(app)
key = os.getenv("JWT_KEY")
dbPASSWORD = os.getenv("DB_PASSWORD")
partnerKEY = os.getenv("PARTNER_KEY")
merchantID = os.getenv("MERCHANT_ID")


# MySQL configurations
dbconfig = {
    "host": "localhost",
    "database": "attractions_db",
    "user": "root",
    "password": dbPASSWORD,
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

@app.route("/member")
def member():
    return render_template("member.html")


app.run(host='0.0.0.0', port=3000, debug=True)
