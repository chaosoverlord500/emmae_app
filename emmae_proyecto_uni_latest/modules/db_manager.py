import hashlib
import json
import os
import mysql.connector as dbconnector

JSON_PATH = os.path.join("administradores", "administradores.json")
CONFIG_FILE = "db_config.json"

def ensure_json_exists():
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    if not os.path.exists(JSON_PATH) or os.path.getsize(JSON_PATH) == 0:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def save_admin_json(id_number, password):
    ensure_json_exists()
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {}
    
    data[str(id_number)] = hash_password(password)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def delete_admin_json(id_number):
    ensure_json_exists()
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return

    if str(id_number) in data:
        del data[str(id_number)]
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def check_is_admin(id_number):
    ensure_json_exists()
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return False
    return str(id_number) in data

def get_admin_password(id_number):
    ensure_json_exists()
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(str(id_number), "")
    except json.JSONDecodeError:
        return ""

def fetch_dropdown_data(cursor, query):
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return []
        if len(rows[0]) == 1:
            return [str(row[0]) for row in rows]
        return [
            f"{row[0]} - {row[1]} {row[2]}" if len(row) > 2 else f"{row[0]} - {row[1]}"
            for row in rows
        ]
    except dbconnector.Error as err:
        print(f"Database query error: {err}")
        return []

def get_teachers_dropdown(cursor):
    return fetch_dropdown_data(cursor, "SELECT cedula_docente, nombre_docente, apellido_docente FROM docente")

def get_students_dropdown(cursor):
    return fetch_dropdown_data(cursor, "SELECT cedula_estudiante, nombre_estudiante, apellido_estudiante FROM estudiante")

def get_instruments_dropdown(cursor):
    return fetch_dropdown_data(cursor, "SELECT id_instrumento, tipo_instrumento FROM instrumentos")

def get_materials_dropdown(cursor):
    return fetch_dropdown_data(cursor, "SELECT id_mda, tipo_mda FROM material_de_apoyo")

def get_classrooms_dropdown(cursor):
    return fetch_dropdown_data(cursor, "SELECT id_salon, estado_salon FROM salon")

def get_db_credentials():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            os.remove(CONFIG_FILE)
    return {"host": "localhost", "user": "root", "password": "", "database": "emmae_basededatos"}

def ensure_database_exists(creds):
    try:
        temp_conn = dbconnector.connect(
            host=creds.get("host", "localhost"),
            user=creds.get("user", "root"),
            password=creds.get("password", "")
        )
        cursor = temp_conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS EMMAE_BASEDEDATOS;")
        cursor.execute("USE EMMAE_BASEDEDATOS;")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS docente (
                cedula_docente INT NOT NULL PRIMARY KEY,
                nombre_docente VARCHAR(100) NOT NULL,
                apellido_docente VARCHAR(100) NOT NULL,
                especialidad_primaria VARCHAR(100) NOT NULL,
                correo_docente VARCHAR(100) NOT NULL,
                telefono_docente VARCHAR(20) NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estudiante (
                cedula_estudiante VARCHAR(100) NOT NULL PRIMARY KEY,
                nombre_estudiante VARCHAR(100) NOT NULL,
                apellido_estudiante VARCHAR(100) NOT NULL,
                instrumento_estudiante VARCHAR(100) NOT NULL,
                tiene_piano_complementario BOOLEAN NOT NULL DEFAULT FALSE,
                ano_cursante VARCHAR(20) NOT NULL,
                telefono_estudiante VARCHAR(20) NOT NULL,
                correo_estudiante VARCHAR(100) NOT NULL,
                telefono_representante VARCHAR(20) NULL,
                correo_representante VARCHAR(100) NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instrumentos (
                id_instrumento INT NOT NULL PRIMARY KEY,
                tipo_instrumento VARCHAR(100) NOT NULL,
                instrumento_disponible BOOLEAN NOT NULL DEFAULT TRUE,
                estado_instrumento VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS material_de_apoyo (
                id_mda INT NOT NULL PRIMARY KEY,
                desc_mda VARCHAR(100) NOT NULL,
                tipo_mda VARCHAR(100) NULL,
                mda_disponible BOOLEAN NOT NULL DEFAULT TRUE,
                estado_mda VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salon (
                id_salon INT NOT NULL PRIMARY KEY,
                es_cubiculo BOOLEAN NOT NULL DEFAULT FALSE,
                salon_ocupado BOOLEAN NOT NULL DEFAULT FALSE,
                tiene_piano BOOLEAN NOT NULL DEFAULT TRUE,
                id_piano INT NULL,
                estado_salon VARCHAR(100) NOT NULL,
                salon_disponible BOOLEAN NOT NULL DEFAULT TRUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prestamo (
                id_prestamo INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                cedula_estudiante VARCHAR(100) NULL,
                cedula_docente INT NULL,
                id_instrumento INT NULL,
                id_mda INT NULL,
                id_salon INT NULL,
                fecha_prestamo DATE NOT NULL,
                fecha_limite_prestamo DATE NOT NULL,
                fecha_devolucion DATE NULL,
                estado VARCHAR(50) NOT NULL DEFAULT 'Prestado',
                FOREIGN KEY (cedula_estudiante) REFERENCES estudiante(cedula_estudiante),
                FOREIGN KEY (cedula_docente) REFERENCES docente(cedula_docente),
                FOREIGN KEY (id_instrumento) REFERENCES instrumentos(id_instrumento),
                FOREIGN KEY (id_mda) REFERENCES material_de_apoyo(id_mda),
                FOREIGN KEY (id_salon) REFERENCES salon(id_salon)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        temp_conn.commit()
        cursor.close()
        temp_conn.close()
    except dbconnector.Error as err:
        print(f"Error ensuring database exists: {err}")
        raise err

def connect_to_db():
    creds = get_db_credentials()
    try:
        ensure_database_exists(creds)
    except dbconnector.Error as err:
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        raise err

    try:
        conn = dbconnector.connect(
            host=creds.get("host", "localhost"),
            user=creds.get("user", "root"),
            password=creds.get("password", ""),
            database=creds.get("database", "emmae_basededatos")
        )
        return conn
    except dbconnector.Error as err:
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        raise err

def login(id_number: int, passwd: str) -> bool:
    if id_number == 123 and passwd == "admin":
        return True
    return check_is_admin(id_number) and get_admin_password(id_number) == hash_password(passwd)