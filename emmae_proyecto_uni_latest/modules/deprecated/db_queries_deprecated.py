import os
import json

JSON_PATH = os.path.join("administradores", "administradores.json")

def ensure_json_exists():
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    if not os.path.exists(JSON_PATH) or os.path.getsize(JSON_PATH) == 0:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)

def save_admin_json(id_number, password):
    ensure_json_exists()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    data[str(id_number)] = password
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def delete_admin_json(id_number):
    ensure_json_exists()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if str(id_number) in data:
        del data[str(id_number)]
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def check_is_admin(id_number):
    ensure_json_exists()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return str(id_number) in data

def get_admin_password(id_number):
    ensure_json_exists()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(str(id_number), "")

def fetch_dropdown_data(cursor, query):
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return []
        if len(rows[0]) == 1:
            return [str(row[0]) for row in rows]
        return [f"{row[0]} - {row[1]} {row[2]}" if len(row) > 2 else f"{row[0]} - {row[1]}" for row in rows]
    except Exception:
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