import mysql.connector as dbconnector
#from customtkinter import *
from tkinter import *
from tkinter import messagebox

def connect_db():
    try:
        conn = dbconnector.connect(
            host="localhost",
            user="root",
            password="252505",
            database="emmae_db"
        )
        messagebox.showinfo("Status - Exitoso", "Base de datos conectada")
        return conn
    except dbconnector.Error as err:
        messagebox.showerror("Status - Error", f"No se pudo conectar: {err}")

conn = connect_db()
cursor = conn.cursor()

#create database if one doesnt exist already
def create_db():
    if not messagebox.askyesno("DEBUG - DELETE DB", "Borrar base de datos actual si existe"):
        return None
        

    cursor.execute("DROP DATABASE IF EXISTS emmae_basededatos;")
    conn.commit()

    cursor.execute("CREATE DATABASE IF NOT EXISTS EMMAE_BASEDEDATOS;")
    cursor.execute("USE EMMAE_BASEDEDATOS;")

    query= """
    CREATE TABLE docente (
        id_docente INT AUTO_INCREMENT PRIMARY KEY,
        cedula INT NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cursor.execute(query)
    query= """
    CREATE TABLE estudiantes (
        id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
        cedula INT,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL,
        instrumento VARCHAR(100) NOT NULL,
        piano_complementario BOOLEAN NOT NULL DEFAULT FALSE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cursor.execute(query)
    conn.commit()
    messagebox.showinfo("Status - Exitoso", "Base de datos creada")

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
    create_db()

    test = TRUE
    while test:
        terminal_input = input(">")
        if terminal_input == "addstudent":
            gui_student()
        elif terminal_input == "addteacher":
            gui_teacher()
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
            print_students()
        elif terminal_input == "printteachers":
            cursor.execute("SELECT * FROM docente")
            
            rows = cursor.fetchall()

            print(" --- LISTA DE DOCENTES --- ")
            for row in rows:
                print(f"ID: {row[0]} | Nombre: {row[2]} {row[3]}")
        else:
            print("ERROR: Command not found")

def print_students():
    cursor.execute("SELECT * FROM estudiantes")
            
    rows = cursor.fetchall()

    print(" --- LISTA DE ESTUDIANTES --- ")
    for row in rows:
        print(f"ID: {row[0]} | Nombre: {row[2]} {row[3]} | Instrumento: {row[4]} | Piano: {row[5]}")

def print_teachers():
    cursor.execute("SELECT * FROM docente")
            
    rows = cursor.fetchall()

    print(" --- LISTA DE DOCENTES --- ")
    for row in rows:
        print(f"ID: {row[0]} | Nombre: {row[2]} {row[3]}")

#GUI
def gui_start():
    root = Tk()
    root.title="EMMAE APP"
    main(root)
    root.mainloop()
    

def main(root):
    for widget in root.winfo_children():
        widget.destroy()
    
    label = Label(text="Anadir usuarios")
    label.pack()

    teacher_button = Button(text="Anadir Profesor", command=lambda: gui_teacher(root))
    teacher_button.pack()

    student_button = Button(text="Anadir Estudiante", command=lambda: gui_student(root))
    student_button.pack()

    loadstudents_button = Button(text="Ver Estudiantes", command=print_students)
    loadstudents_button.pack()

    loadteachers_button = Button(text="Ver Docentes", command=print_teachers)
    loadteachers_button.pack()


def gui_teacher(root):
    for widget in root.winfo_children():
        widget.destroy()

    label = Label(text="Agregar docente")
    label.pack()

    label = Label(text="Cedula")
    label.pack()
    entryC = Entry(root)
    entryC.pack()

    label = Label(text="Nombre")
    label.pack()

    entryA = Entry(root)
    entryA.pack()

    label = Label(text="Apellido")
    label.pack()

    entryB = Entry(root)
    entryB.pack()

    button = Button(root, text="Agregar docente", command=lambda: add_teacher(entryC.get(), entryA.get(), entryB.get()))
    button.pack()

    buttonReturn = Button(root, text="Volver", command=lambda: main(root))
    buttonReturn.pack()

def gui_student(root):
    for widget in root.winfo_children():
        widget.destroy()

    label = Label(text="Agregar estudiante")
    label.pack()

    label = Label(text="Cedula")
    label.pack()
    entryC = Entry(root)
    entryC.pack()

    label = Label(text="Nombre")
    label.pack()

    entryA = Entry(root)
    entryA.pack()

    label = Label(text="Apellido")
    label.pack()

    entryB = Entry(root)
    entryB.pack()

    label = Label(text="Instrumento")
    label.pack()

    entryD = Entry(root)
    entryD.pack()

    piano_check = IntVar()
    checkbox = Checkbutton(root, text="piano complementario", variable=piano_check)
    checkbox.pack()

    button = Button(root, text="Agregar estudiante")#, command=add_student)
    button.pack()

    buttonReturn = Button(root, text="Volver", command=lambda: main(root))
    buttonReturn.pack()

gui_start()
#console_debug()


conn.close()
cursor.close()