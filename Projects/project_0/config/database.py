import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "root",
        database = "e_commerce_platform_db",
        autocommit = True
    )
    return connection