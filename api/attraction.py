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


attraction_bp = Blueprint("attraction_BP", __name__)


dbPASSWORD = os.getenv("DB_PASSWORD")

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


@attraction_bp.route("/api/attractions", methods=["GET"])
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


@attraction_bp.route("/api/attraction/<attractionId>", methods=["GET"])
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


@attraction_bp.route("/api/categories", methods=["GET"])
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
