import mysql.connector as dbconnector

def connect_to_db():
    try:
        conn = dbconnector.connect(
            host="localhost",
            user="root",
            password="252505",
            database="emmae_db"
        )
        print("Status - Exitoso", "Base de datos conectada")
        return conn
    except dbconnector.Error as err:
        print("Status - Error", f"No se pudo conectar: {err}")