import json
import os
import re
import mysql.connector
from mysql.connector import Error
from data.mySQL import MySQLPassword

# path = os.getcwd()  # 查詢當前路徑
# print(path)

try:  # 連接 MySQL 資料庫
    connection = mysql.connector.connect(
        host='localhost',
        database='attractions_db',
        user='root',
        password=MySQLPassword())

    cursor = connection.cursor()

    # Create table
    sql = "CREATE TABLE taipei_attractions(id BIGINT PRIMARY KEY AUTO_INCREMENT,taipeiId BIGINT, name VARCHAR(255) NOT NULL,category VARCHAR(255),description VARCHAR(4000),address VARCHAR(255),transport VARCHAR(4000),mrt VARCHAR(255),lat FLOAT,lng FLOAT,images VARCHAR(4000));"
    cursor.execute(sql)

    with open("/Users/WH_HW_S2/taipei-day-trip/data/taipei-attractions.json", mode="r", encoding="utf-8") as file:
        data = json.load(file)

        data_list = data['result']['results']
        spot_num = len(data_list)  # 58

        i = 0
        while i < spot_num:
            taipeiId = data_list[i]['_id']
            name = data_list[i]['name']
            category = data_list[i]['CAT']
            description = data_list[i]['description']
            address = data_list[i]['address']
            transport = data_list[i]['direction']
            mrt = data_list[i]['MRT']
            lat = data_list[i]['latitude']
            lng = data_list[i]['longitude']
            text = data_list[i]['file']
            image = re.findall(
                "(?:https\:)?\/\/.*\.(?:jpg|JPG|png|PNG)", text)
            images = image[0]

            sql_insert = "INSERT INTO taipei_attractions(taipeiId, name, category, description, address, transport, mrt, lat, lng, images) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            new_data = (taipeiId, name, category, description,
                        address, transport, mrt, lat, lng, images)
            cursor.execute(sql_insert, new_data)
            connection.commit()
            i += 1

except Error as e:
    print("資料庫連接失敗：", e)

finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("資料庫連線已關閉")
