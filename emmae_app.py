import mysql.connector as dbconnector
from tkinter import *
from tkinter import messagebox

def connect_db():
    try:
        conn = dbconnector.connect(
            host="localhost",
            user="root",
            password="252505",
            database="emmae_basededatos"
        )
        messagebox.showinfo("Status - Exitoso", "Base de datos conectada")
        return conn
    except dbconnector.Error as err:
        messagebox.showerror("Status - Error", f"No se pudo conectar: {err}")
        return None

conn = connect_db()
cursor = conn.cursor()

#add_teacher(cedula, nombre, apellido)
def add_teacher(uid, name, surname):
    query = """
    INSERT INTO docente (cedula, nombre, apellido)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (uid, name, surname))
    conn.commit()
    messagebox.showinfo("Status - Exitoso", "Docente anadido")
    return query;

#add_student(cedula, nombre, apellido, instrumento, piano)
def add_student(uid, name, surname, instrument, piano):
    query = """
    INSERT INTO estudiantes (cedula, nombre, apellido, instrumento, piano_complementario) 
    VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(query, (uid, name, surname, instrument, piano))
    conn.commit()
    messagebox.showinfo("Status - Exitoso", "Estudiante anadido")
    return query;

#DEBUG FUNCTIONALITY
def delete_values():

    cursor.execute("DELETE FROM estudiantes")
    cursor.execute("DELETE FROM docente")
    conn.commit()
    messagebox.showinfo("Status - Exitoso", "Datos borrados")

def console_debug():
    test = TRUE
    while test:
        terminal_input = input(">")
        if terminal_input == "addstudent":
            cedula = input("cedula: ")
            nombre = input("nombre: ")
            apellido = input("apellido: ")
            instrumento = input("instrumento: ")
            piano = input("piano: ")
            add_student(cedula, nombre, apellido, instrumento, piano)
        elif terminal_input == "addteacher":
            cedula = input("cedula: ")
            nombre = input("nombre: ")
            apellido = input("apellido: ")
            add_teacher(cedula, nombre, apellido)
        elif terminal_input == "help":
            print("addteacher = anadir docente")
            print("addstudent = anadir estudiante")
            print("deletedb = borrar datos (DEBUG)")
            print("quit = cerrar consola")
            print("printstudents = mostrar datos de estudiantes")
            print("printteachers = mostrar datos de docentes")
        elif terminal_input == "deletedb":
            delete = messagebox.askyesno("DEBUG", "Desea borrar la base de datos?")
            if delete:
                delete_values()
            else:
                print("accion abortada")
        elif terminal_input == "quit":
            break
        elif terminal_input == "printstudents":
            cursor.execute("SELECT * FROM estudiantes")
            
            rows = cursor.fetchall()

            print(" --- LISTA DE ESTUDIANTES --- ")
            for row in rows:
                print(f"ID: {row[0]} | Nombre: {row[2]} {row[3]} | Instrumento: {row[4]} | Piano: {row[5]}")
        elif terminal_input == "printteachers":
            cursor.execute("SELECT * FROM docente")
            
            rows = cursor.fetchall()

            print(" --- LISTA DE DOCENTES --- ")
            for row in rows:
                print(f"ID: {row[0]} | Nombre: {row[2]} {row[3]}")
        else:
            print("ERROR: Command not found")


console_debug()

conn.close()
cursor.close()