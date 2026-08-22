def add_student(id: int, name: str, surname: str, instrument: str, piano: bool, conn, cursor) -> bool:
    query = """
    INSERT INTO estudiantes (cedula, nombre, apellido, instrumento, piano_complementario) 
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (id, name, surname, instrument, piano))
    conn.commit()
    return True

def add_teacher(id: int, name: str, surname: str, admin: bool, specialty: str, conn, cursor):
    # Enforce lowercase column names to match your strict SQL script definition
    query = """
    INSERT INTO docente (cedula, nombre, apellido, especialidad) 
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (id, name, surname, specialty))
    conn.commit()
    print("Status - Exitoso", "Docente añadido")
    return query

def add_mda(tipo: str, en_prestamo: str, material: str, id_estudiante: int, id_docente, conn, cursor):
    # Fixed query targeting the correct table structure ('material') instead of 'docente'
    query = """
    INSERT INTO material (tipo_material, material_en_prestamo, estado_material, id_estudiante, id_docente) 
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (tipo, en_prestamo, material, id_estudiante, id_docente))
    conn.commit()
    return True

def add_instrument(tipo: str, en_prestamo: int, estado: str, id_estudiante: int, id_docente: int, conn, cursor) -> bool:
    query = """
    INSERT INTO instrumentos (tipo_instrumento, instrumento_en_prestamo, estado, id_estudiante, id_docente) 
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (tipo, en_prestamo, estado, id_estudiante, id_docente))
    conn.commit()
    return True

def login(id: int, passwd: str) -> bool:
    if id == 333 and passwd == "admin":
        return True
    return False