import os
import re
import json
import datetime
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# --- Conexión a Base de Datos ---
try:
    from modules import db_con as DB_con, user_management as User_Manager
    conn = DB_con.connect_to_db()
    cursor = conn.cursor()
except ImportError:
    print("Error al conectar a la base de datos")

JSON_PATH = os.path.join("administradores", "administradores.json")

def asegurar_json_existe():
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    if not os.path.exists(JSON_PATH) or os.path.getsize(JSON_PATH) == 0:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)

def guardar_en_json(cedula, contrasena):
    asegurar_json_existe()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        datos = json.load(f)
    datos[str(cedula)] = contrasena
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

def eliminar_de_json(cedula):
    asegurar_json_existe()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        datos = json.load(f)
    if str(cedula) in datos:
        del datos[str(cedula)]
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)

def verificar_es_admin(cedula):
    asegurar_json_existe()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        datos = json.load(f)
    return str(cedula) in datos

def obtener_contrasena_admin(cedula):
    asegurar_json_existe()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        datos = json.load(f)
    return datos.get(str(cedula), "")


# --- Validaciones ---
def validar_correo(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(patron, correo))

def validar_telefono_resto(texto):
    if texto == "" or (texto.isdigit() and len(texto) <= 7):
        return True
    return False

def validar_numero_simple(texto):
    if texto == "" or texto.isdigit():
        return True
    return False


# --- Helpers Dropdowns ---
def obtener_dropdown_docentes():
    try:
        cursor.execute("SELECT cedula_docente, nombre_docente, apellido_docente FROM docente")
        return [f"{row[0]} - {row[1]} {row[2]}" for row in cursor.fetchall()]
    except Exception:
        return []

def obtener_dropdown_estudiantes():
    try:
        cursor.execute("SELECT id_estudiante, nombre_estudiante, apellido_estudiante FROM estudiantes")
        return [f"{row[0]} - {row[1]} {row[2]}" for row in cursor.fetchall()]
    except Exception:
        return []

def obtener_dropdown_instrumentos():
    try:
        cursor.execute("SELECT id_instrumento, tipo_instrumento FROM instrumentos")
        return [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
    except Exception:
        return []

def obtener_dropdown_material():
    try:
        cursor.execute("SELECT id_m_a, tipo_material FROM material")
        return [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
    except Exception:
        return []

def obtener_dropdown_salones():
    try:
        cursor.execute("SELECT id_salon FROM salones")
        return [f"{row[0]}" for row in cursor.fetchall()]
    except Exception:
        return []


# --- Vistas de la Aplicación ---
class LoginScreen(ttk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master, padding=30)
        self.on_login = on_login

        card = ttk.Frame(self, bootstyle="secondary", padding=30)
        card.pack(expand=True)

        ttk.Label(card, text="¡Bienvenido!", font=("Arial", 22, "bold")).pack(pady=(10, 5))
        ttk.Label(card, text="Inicie sesión en su cuenta", font=("Arial", 11), bootstyle="muted").pack(pady=(0, 20))

        self.uid_textbox = ttk.Entry(card, width=30, font=("Arial", 11))
        self.uid_textbox.insert(0, "Cédula")
        self.uid_textbox.bind("<FocusIn>", lambda e: self.clear_placeholder(self.uid_textbox, "Cédula"))
        self.uid_textbox.bind("<FocusOut>", lambda e: self.set_placeholder(self.uid_textbox, "Cédula"))
        self.uid_textbox.pack(pady=10)

        self.textbox = ttk.Entry(card, width=30, font=("Arial", 11))
        self.textbox.insert(0, "Contraseña")
        self.textbox.bind("<FocusIn>", lambda e: self.clear_placeholder(self.textbox, "Contraseña", show="*"))
        self.textbox.bind("<FocusOut>", lambda e: self.set_placeholder(self.textbox, "Contraseña"))
        self.textbox.pack(pady=10)

        ttk.Button(
            card, text="Iniciar Sesión", bootstyle="primary", width=28,
            command=lambda: self.check_credentials(self.uid_textbox.get(), self.textbox.get())
        ).pack(pady=(20, 10))

    def clear_placeholder(self, entry, text, show=""):
        if entry.get() == text:
            entry.delete(0, tk.END)
            if show:
                entry.config(show=show)

    def set_placeholder(self, entry, text):
        if not entry.get():
            entry.config(show="")
            entry.insert(0, text)

    def check_credentials(self, id_str, pswd):
        if id_str in ["Cédula", ""] or pswd in ["Contraseña", ""]:
            return messagebox.showerror("Error", "Por favor complete todos los campos")
        try:
            if User_Manager.login(int(id_str), pswd):
                self.on_login()
            else:
                messagebox.showerror("Error", "Datos Incorrectos")
        except ValueError:
            messagebox.showerror("Error", "No ingrese letras en el campo de Cédula")


class TopNavBar(ttk.Frame):
    def __init__(self, master, active_callback, logout_callback):
        super().__init__(master, bootstyle="dark", padding=5)
        
        modules = ["Profesor", "Estudiante", "Instrumentos", "M.D.A", "Salones"]
        for idx in range(len(modules) + 1):
            self.grid_columnconfigure(idx, weight=1)

        for idx, mod in enumerate(modules):
            btn = ttk.Button(
                self, text=mod, bootstyle="dark-link",
                command=lambda m=mod: active_callback(m.lower())
            )
            btn.grid(row=0, column=idx, padx=5, pady=5, sticky="ew")
            
        ttk.Button(
            self, text="Salir", bootstyle="danger-outline", width=10, command=logout_callback
        ).grid(row=0, column=len(modules), padx=15, pady=5, sticky="e")


class LeftSubMenu(ttk.Frame):
    def __init__(self, master, action_callback, mode_callback, show_toggle=False):
        super().__init__(master, bootstyle="dark", padding=15)
        self.action_callback = action_callback
        self.mode_callback = mode_callback
        
        if show_toggle:
            toggle_frame = ttk.Frame(self, bootstyle="dark")
            toggle_frame.pack(side="top", pady=(0, 15), fill="x")
            
            self.mode_var = tk.StringVar(value="A")
            btn_a = ttk.Radiobutton(
                toggle_frame, text="A", value="A", variable=self.mode_var, 
                bootstyle="toolbutton", width=5, command=self.on_toggle_change
            )
            btn_p = ttk.Radiobutton(
                toggle_frame, text="P", value="P", variable=self.mode_var, 
                bootstyle="toolbutton", width=5, command=self.on_toggle_change
            )
            btn_a.pack(side="left", expand=True, fill="x", padx=(0, 2))
            btn_p.pack(side="left", expand=True, fill="x", padx=(2, 0))
            
        self.buttons_frame = ttk.Frame(self, bootstyle="dark")
        self.buttons_frame.pack(side="top", fill="both", expand=True)
        
        actions = ["Añadir", "Modificar", "Buscar"]
        for act in actions:
            ttk.Button(
                self.buttons_frame, text=act, bootstyle="secondary-link", width=12,
                command=lambda a=act: self.action_callback(a)
            ).pack(side="top", pady=5, fill="x")

    def on_toggle_change(self):
        self.mode_callback(self.mode_var.get())


class InteractiveWorkspace(ttk.Frame):
    def __init__(self, master, name, include_loans=False):
        super().__init__(master)
        self.name = name.lower()
        self.display_name = name.title() if name != "m.d.a" else "M.D.A (Material de Apoyo)"
        self.include_loans = include_loans
        self.current_mode = "A"
        self.current_action = "Añadir"
        
        self.sidebar = LeftSubMenu(
            self, 
            action_callback=self.handle_action_change, 
            mode_callback=self.handle_mode_change, 
            show_toggle=include_loans
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 15))
        
        self.content_area = ttk.Frame(self, padding=20, bootstyle="light")
        self.content_area.pack(side="right", fill="both", expand=True)
        
        self.render_form_view()

    def handle_mode_change(self, mode):
        self.current_mode = mode
        self.render_form_view()

    def handle_action_change(self, action_type):
        self.current_action = action_type
        self.render_form_view()

    def render_form_view(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        if self.include_loans and self.current_mode == "P":
            self.render_prestamos_generic_operations()
            return

        ttk.Label(
            self.content_area, 
            text=f"{self.current_action} - Gestión de {self.display_name}", 
            font=("Arial", 16, "bold"), bootstyle="inverse-light"
        ).pack(anchor="w", pady=(0, 15))
        
        if self.name == "profesor":
            self.render_profesor_operations()
        elif self.name == "estudiante":
            self.render_estudiante_operations()
        elif self.name == "instrumentos":
            self.render_instrumentos_base_operations()
        elif self.name == "m.d.a":
            self.render_mda_base_operations()
        elif self.name == "salones":
            self.render_salones_base_operations()

    # =========================================================================
    # LÓGICA: DOCENTES 
    # =========================================================================
    def render_profesor_operations(self):
        vcmd = (self.register(validar_telefono_resto), '%P')

        if self.current_action == "Añadir":
            form_container = ScrolledFrame(self.content_area, bootstyle="round")
            form_container.pack(fill="both", expand=True)

            ttk.Label(form_container, text="Cédula:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_cedula = ttk.Entry(form_container, width=40)
            ent_cedula.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Nombre:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_nombre = ttk.Entry(form_container, width=40)
            ent_nombre.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Apellido:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_apellido = ttk.Entry(form_container, width=40)
            ent_apellido.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Especialidad:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            cb_especialidad = ttk.Combobox(form_container, values=["Canto", "Piano", "Guitarra", "Violín"], state="readonly", width=38)
            cb_especialidad.current(0)
            cb_especialidad.pack(anchor="w", pady=(0, 10))

            var_prestamo = tk.BooleanVar(value=False)
            chk_prestamo = ttk.Checkbutton(form_container, text="Tiene Préstamo", variable=var_prestamo, bootstyle="square-toggle")
            chk_prestamo.pack(anchor="w", pady=10)

            var_admin = tk.BooleanVar(value=False)
            chk_admin = ttk.Checkbutton(form_container, text="Administrador", variable=var_admin, bootstyle="square-toggle",
                                        command=lambda: toggle_pass_input(var_admin, ent_contrasena))
            chk_admin.pack(anchor="w", pady=5)

            ttk.Label(form_container, text="Contraseña del Administrador:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_contrasena = ttk.Entry(form_container, width=40, state="disabled", show="*")
            ent_contrasena.pack(anchor="w", pady=(0, 10))

            def toggle_pass_input(v_admin, e_pass):
                if v_admin.get():
                    e_pass.config(state="normal")
                else:
                    e_pass.delete(0, tk.END)
                    e_pass.config(state="disabled")

            ttk.Label(form_container, text="Correo Electrónico:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_correo = ttk.Entry(form_container, width=40)
            ent_correo.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Teléfono:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            tel_frame = ttk.Frame(form_container, bootstyle="light")
            tel_frame.pack(anchor="w", pady=(0, 15))
            
            cb_prefijo = ttk.Combobox(tel_frame, values=["0424", "0414", "0276", "0416", "0426", "0212", "0412"], state="readonly", width=8)
            cb_prefijo.current(0)
            cb_prefijo.pack(side="left", padx=(0, 5))
            
            ent_tel_resto = ttk.Entry(tel_frame, width=28, validate="key", validatecommand=vcmd)
            ent_tel_resto.pack(side="left")

            def ejecutar_guardado():
                ced = ent_cedula.get().strip()
                nom = ent_nombre.get().strip()
                ape = ent_apellido.get().strip()
                esp = cb_especialidad.get()
                pres = var_prestamo.get()
                corr = ent_correo.get().strip()
                pref = cb_prefijo.get()
                rest = ent_tel_resto.get().strip()
                tel_completo = f"{pref}{rest}"
                es_admin = var_admin.get()
                contra = ent_contrasena.get().strip()

                if not ced.isdigit():
                    return messagebox.showerror("Error de Validación", "La cédula debe ser un valor numérico.")
                if not nom or not ape:
                    return messagebox.showerror("Error de Validación", "El nombre y apellido son obligatorios.")
                if es_admin and not contra:
                    return messagebox.showerror("Error de Validación", "La contraseña es obligatoria para el administrador.")
                if not validar_correo(corr):
                    return messagebox.showerror("Error de Validación", "El formato del correo electrónico es inválido.")

                try:
                    query = """INSERT INTO docente (cedula_docente, nombre_docente, apellido_docente, especialidad, tiene_prestamo, correo, telefono) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query, (int(ced), nom, ape, esp, pres, corr, tel_completo))
                    conn.commit()
                    if es_admin:
                        guardar_en_json(ced, contra)
                    messagebox.showinfo("Éxito", "Docente registrado correctamente.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Database Error", f"No se pudo guardar el registro: {ex}")

            ttk.Button(form_container, text="Guardar Registro", bootstyle="success", command=ejecutar_guardado).pack(anchor="w", pady=10)

        elif self.current_action == "Modificar":
            ttk.Label(self.content_area, text="Buscar Docente por Cédula:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            search_frame = ttk.Frame(self.content_area, bootstyle="light")
            search_frame.pack(anchor="w", fill="x", pady=(0, 15))

            opciones_cb = obtener_dropdown_docentes()
            cb_busqueda = ttk.Combobox(search_frame, values=opciones_cb, state="readonly", width=40)
            cb_busqueda.pack(side="left", padx=(0, 10))

            form_edit = ScrolledFrame(self.content_area, bootstyle="round")
            form_edit.pack(fill="both", expand=True)

            ttk.Label(form_edit, text="Nombre:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_nombre = ttk.Entry(form_edit, width=40)
            ent_nombre.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_edit, text="Apellido:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_apellido = ttk.Entry(form_edit, width=40)
            ent_apellido.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_edit, text="Especialidad:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            cb_especialidad = ttk.Combobox(form_edit, values=["Canto", "Piano", "Guitarra", "Violín"], state="readonly", width=38)
            cb_especialidad.pack(anchor="w", pady=(0, 10))

            var_prestamo = tk.BooleanVar(value=False)
            chk_prestamo = ttk.Checkbutton(form_edit, text="Tiene Préstamo", variable=var_prestamo, bootstyle="square-toggle")
            chk_prestamo.pack(anchor="w", pady=10)

            var_admin = tk.BooleanVar(value=False)
            chk_admin = ttk.Checkbutton(form_edit, text="Administrador", variable=var_admin, bootstyle="square-toggle",
                                        command=lambda: toggle_pass_input(var_admin, ent_contrasena))
            chk_admin.pack(anchor="w", pady=5)

            ttk.Label(form_edit, text="Contraseña del Administrador:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_contrasena = ttk.Entry(form_edit, width=40, state="disabled", show="*")
            ent_contrasena.pack(anchor="w", pady=(0, 10))

            def toggle_pass_input(v_admin, e_pass):
                if v_admin.get():
                    e_pass.config(state="normal")
                else:
                    e_pass.delete(0, tk.END)
                    e_pass.config(state="disabled")

            ttk.Label(form_edit, text="Correo Electrónico:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_correo = ttk.Entry(form_edit, width=40)
            ent_correo.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_edit, text="Teléfono:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            tel_frame = ttk.Frame(form_edit, bootstyle="light")
            tel_frame.pack(anchor="w", pady=(0, 15))
            
            cb_prefijo = ttk.Combobox(tel_frame, values=["0424", "0414", "0276", "0416", "0426", "0212", "0412"], state="readonly", width=8)
            cb_prefijo.pack(side="left", padx=(0, 5))
            
            ent_tel_resto = ttk.Entry(tel_frame, width=28, validate="key", validatecommand=vcmd)
            ent_tel_resto.pack(side="left")

            self.cedula_seleccionada = None

            def cargar_datos_docente(event):
                seleccion = cb_busqueda.get()
                if seleccion:
                    self.cedula_seleccionada = seleccion.split(" - ")[0]
                    try:
                        cursor.execute("SELECT nombre_docente, apellido_docente, especialidad, tiene_prestamo, correo, telefono FROM docente WHERE cedula_docente = %s", (self.cedula_seleccionada,))
                        doc = cursor.fetchone()
                        if doc:
                            ent_nombre.delete(0, tk.END); ent_nombre.insert(0, doc[0])
                            ent_apellido.delete(0, tk.END); ent_apellido.insert(0, doc[1])
                            cb_especialidad.set(doc[2])
                            var_prestamo.set(bool(doc[3]))
                            ent_correo.delete(0, tk.END); ent_correo.insert(0, doc[4])
                            
                            tel_db = doc[5] if doc[5] else ""
                            if len(tel_db) >= 4 and tel_db[:4] in ["0424", "0414", "0276", "0416", "0426", "0212", "0412"]:
                                cb_prefijo.set(tel_db[:4])
                                ent_tel_resto.delete(0, tk.END); ent_tel_resto.insert(0, tel_db[4:])
                            else:
                                cb_prefijo.current(0)
                                ent_tel_resto.delete(0, tk.END); ent_tel_resto.insert(0, tel_db)

                            if verificar_es_admin(self.cedula_seleccionada):
                                var_admin.set(True)
                                ent_contrasena.config(state="normal")
                                ent_contrasena.delete(0, tk.END); ent_contrasena.insert(0, obtener_contrasena_admin(self.cedula_seleccionada))
                            else:
                                var_admin.set(False)
                                ent_contrasena.delete(0, tk.END); ent_contrasena.config(state="disabled")
                    except Exception as ex:
                        messagebox.showerror("Error", f"Fallo al recuperar información: {ex}")

            cb_busqueda.bind("<<ComboboxSelected>>", cargar_datos_docente)

            def ejecutar_actualizacion():
                if not self.cedula_seleccionada: return
                nom = ent_nombre.get().strip()
                ape = ent_apellido.get().strip()
                esp = cb_especialidad.get()
                pres = var_prestamo.get()
                corr = ent_correo.get().strip()
                pref = cb_prefijo.get()
                rest = ent_tel_resto.get().strip()
                tel_completo = f"{pref}{rest}"
                es_admin = var_admin.get()
                contra = ent_contrasena.get().strip()

                try:
                    cursor.execute("""UPDATE docente SET nombre_docente=%s, apellido_docente=%s, especialidad=%s, tiene_prestamo=%s, correo=%s, telefono=%s 
                                      WHERE cedula_docente=%s""", (nom, ape, esp, pres, corr, tel_completo, self.cedula_seleccionada))
                    conn.commit()
                    if es_admin: guardar_en_json(self.cedula_seleccionada, contra)
                    else: eliminar_de_json(self.cedula_seleccionada)
                    messagebox.showinfo("Éxito", "Docente actualizado.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            ttk.Button(form_edit, text="Modificar", bootstyle="primary", command=ejecutar_actualizacion).pack(anchor="w", pady=15)

        elif self.current_action == "Buscar":
            ttk.Label(self.content_area, text="Filtrar Docente:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            ent_filtro = ttk.Entry(self.content_area, width=40)
            ent_filtro.pack(anchor="w", pady=(0, 10))

            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)

            def refrescar_busqueda(*args):
                for w in scroll.winfo_children(): w.destroy()
                termino = f"%{ent_filtro.get().strip()}%"
                try:
                    cursor.execute("SELECT cedula_docente, nombre_docente, apellido_docente, telefono, correo, especialidad, tiene_prestamo FROM docente WHERE nombre_docente LIKE %s OR cedula_docente LIKE %s", (termino, termino))
                    for r in cursor.fetchall():
                        ttk.Label(scroll, text=f"Cédula: {r[0]} | Docente: {r[1]} {r[2]} | Teléfono: {r[3]} | Email: {r[4]} | Especialidad: {r[5]} | ¿En Préstamo?: {'Sí' if r[6] else 'No'}", font=("Courier", 10)).pack(anchor="w", padx=10, pady=4)
                except Exception as ex: print(ex)

            ent_filtro.bind("<KeyRelease>", refrescar_busqueda)
            refrescar_busqueda()

    # =========================================================================
    # LÓGICA: ESTUDIANTES
    # =========================================================================
    def render_estudiante_operations(self):
        vcmd_tel = (self.register(validar_telefono_resto), '%P')
        vcmd_num = (self.register(validar_numero_simple), '%P')

        if self.current_action == "Añadir":
            form_container = ScrolledFrame(self.content_area, bootstyle="round")
            form_container.pack(fill="both", expand=True)

            ttk.Label(form_container, text="Cédula Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_cedula = ttk.Entry(form_container, width=40, validate="key", validatecommand=vcmd_num)
            ent_cedula.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Nombre Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_nombre = ttk.Entry(form_container, width=40)
            ent_nombre.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Apellido Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_apellido = ttk.Entry(form_container, width=40)
            ent_apellido.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Instrumento Principal:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_instrumento = ttk.Entry(form_container, width=40)
            ent_instrumento.pack(anchor="w", pady=(0, 10))

            var_piano = tk.BooleanVar(value=False)
            ttk.Checkbutton(form_container, text="Piano Complementario", variable=var_piano, bootstyle="square-toggle").pack(anchor="w", pady=5)

            var_prestamo = tk.BooleanVar(value=False)
            ttk.Checkbutton(form_container, text="Tiene Préstamo", variable=var_prestamo, bootstyle="square-toggle").pack(anchor="w", pady=5)

            ttk.Label(form_container, text="Año Cursante:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_ano = ttk.Entry(form_container, width=40)
            ent_ano.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Correo Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_correo = ttk.Entry(form_container, width=40)
            ent_correo.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Teléfono Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            tel_frame = ttk.Frame(form_container, bootstyle="light")
            tel_frame.pack(anchor="w", pady=(0, 10))
            cb_prefijo = ttk.Combobox(tel_frame, values=["0424", "0414", "0276", "0416", "0426", "0212", "0412"], state="readonly", width=8)
            cb_prefijo.current(0)
            cb_prefijo.pack(side="left", padx=(0, 5))
            ent_tel_resto = ttk.Entry(tel_frame, width=28, validate="key", validatecommand=vcmd_tel)
            ent_tel_resto.pack(side="left")

            ttk.Label(form_container, text="Teléfono Representante (Opcional):", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_tel_rep = ttk.Entry(form_container, width=40)
            ent_tel_rep.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_container, text="Correo Representante (Opcional):", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_corr_rep = ttk.Entry(form_container, width=40)
            ent_corr_rep.pack(anchor="w", pady=(0, 15))

            def ejecutar_guardado_est():
                ced = ent_cedula.get().strip()
                nom = ent_nombre.get().strip()
                ape = ent_apellido.get().strip()
                if not ced.isdigit() or not nom or not ape:
                    return messagebox.showerror("Error", "Campos obligatorios incorrectos.")
                try:
                    query = """INSERT INTO estudiantes (cedula_estudiante, nombre_estudiante, apellido_estudiante, instrumento, piano_comp, tiene_prestamo, ano_cursante, telefono_est, correo_est, telefono_rep, correo_rep) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query, (int(ced), nom, ape, ent_instrumento.get(), var_piano.get(), var_prestamo.get(), ent_ano.get(), f"{cb_prefijo.get()}{ent_tel_resto.get()}", ent_correo.get(), ent_tel_rep.get(), ent_corr_rep.get()))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Estudiante guardado.")
                    self.render_form_view()
                except Exception as ex: messagebox.showerror("Error", str(ex))

            ttk.Button(form_container, text="Guardar Estudiante", bootstyle="success", command=ejecutar_guardado_est).pack(anchor="w", pady=10)

        elif self.current_action == "Modificar":
            ttk.Label(self.content_area, text="Seleccione Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_busqueda = ttk.Combobox(self.content_area, values=obtener_dropdown_estudiantes(), state="readonly", width=40)
            cb_busqueda.pack(anchor="w", pady=(0, 15))

            form_edit = ScrolledFrame(self.content_area, bootstyle="round")
            form_edit.pack(fill="both", expand=True)

            ttk.Label(form_edit, text="Nombre:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_nombre = ttk.Entry(form_edit, width=40)
            ent_nombre.pack(anchor="w", pady=(0, 10))

            ttk.Label(form_edit, text="Apellido:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            ent_apellido = ttk.Entry(form_edit, width=40)
            ent_apellido.pack(anchor="w", pady=(0, 10))

            self.id_est_seleccionado = None

            def cargar_est(event):
                sel = cb_busqueda.get()
                if sel:
                    self.id_est_seleccionado = sel.split(" - ")[0]
                    cursor.execute("SELECT nombre_estudiante, apellido_estudiante FROM estudiantes WHERE id_estudiante=%s", (self.id_est_seleccionado,))
                    res = cursor.fetchone()
                    if res:
                        ent_nombre.delete(0, tk.END); ent_nombre.insert(0, res[0])
                        ent_apellido.delete(0, tk.END); ent_apellido.insert(0, res[1])

            cb_busqueda.bind("<<ComboboxSelected>>", cargar_est)

            def mod_est():
                if not self.id_est_seleccionado: return
                cursor.execute("UPDATE estudiantes SET nombre_estudiante=%s, apellido_estudiante=%s WHERE id_estudiante=%s", (ent_nombre.get(), ent_apellido.get(), self.id_est_seleccionado))
                conn.commit()
                messagebox.showinfo("Éxito", "Estudiante modificado.")
                self.render_form_view()

            ttk.Button(form_edit, text="Modificar", bootstyle="primary", command=mod_est).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            ttk.Label(self.content_area, text="Filtrar por cédula o nombre:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            ent_filtro = ttk.Entry(self.content_area, width=40)
            ent_filtro.pack(anchor="w", pady=(0, 10))

            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)

            def buscar_est_rec(*args):
                for w in scroll.winfo_children(): w.destroy()
                term = f"%{ent_filtro.get().strip()}%"
                cursor.execute("SELECT id_estudiante, nombre_estudiante, apellido_estudiante, instrumento, tiene_prestamo FROM estudiantes WHERE nombre_estudiante LIKE %s OR cedula_estudiante LIKE %s", (term, term))
                for r in cursor.fetchall():
                    ttk.Label(scroll, text=f"ID: {r[0]} | Estudiante: {r[1]} {r[2]} | Instrumento: {r[3]} | ¿En Préstamo?: {'Sí' if r[4] else 'No'}", font=("Courier", 10)).pack(anchor="w", padx=10, pady=4)

            ent_filtro.bind("<KeyRelease>", buscar_est_rec)
            buscar_est_rec()

    # =========================================================================
    # LÓGICA BASE: INSTRUMENTOS
    # =========================================================================
    def render_instrumentos_base_operations(self):
        if self.current_action == "Añadir":
            ttk.Label(self.content_area, text="Tipo de Instrumento:", bootstyle="inverse-light").pack(anchor="w")
            ent_tipo = ttk.Entry(self.content_area, width=40)
            ent_tipo.pack(anchor="w", pady=10)

            ttk.Label(self.content_area, text="Estado del Instrumento:", bootstyle="inverse-light").pack(anchor="w")
            cb_estado = ttk.Combobox(self.content_area, values=["Ok", "Danado"], state="readonly", width=38)
            cb_estado.current(0)
            cb_estado.pack(anchor="w", pady=10)

            var_en_uso = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.content_area, text="Está en Uso / En Préstamo", variable=var_en_uso, bootstyle="square-toggle").pack(anchor="w", pady=10)

            def guardar():
                cursor.execute("INSERT INTO instrumentos (tipo_instrumento, estado, instrumento_en_prest) VALUES (%s, %s, %s)", (ent_tipo.get().strip(), cb_estado.get(), var_en_uso.get()))
                conn.commit()
                messagebox.showinfo("Éxito", "Instrumento añadido.")
                self.render_form_view()

            ttk.Button(self.content_area, text="Guardar", bootstyle="success", command=guardar).pack(anchor="w")
            
        elif self.current_action == "Modificar":
            ttk.Label(self.content_area, text="Seleccione Instrumento a Modificar:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_busqueda = ttk.Combobox(self.content_area, values=obtener_dropdown_instrumentos(), state="readonly", width=40)
            cb_busqueda.pack(anchor="w", pady=(0, 15))

            ttk.Label(self.content_area, text="Tipo de Instrumento:", bootstyle="inverse-light").pack(anchor="w")
            ent_tipo = ttk.Entry(self.content_area, width=40)
            ent_tipo.pack(anchor="w", pady=10)

            ttk.Label(self.content_area, text="Estado:", bootstyle="inverse-light").pack(anchor="w")
            cb_estado = ttk.Combobox(self.content_area, values=["Ok", "Danado"], state="readonly", width=38)
            cb_estado.pack(anchor="w", pady=10)

            var_en_uso = tk.BooleanVar(value=False)
            chk_en_uso = ttk.Checkbutton(self.content_area, text="Está en Uso / En Préstamo", variable=var_en_uso, bootstyle="square-toggle")
            chk_en_uso.pack(anchor="w", pady=10)

            self.id_ins_seleccionado = None

            def cargar_ins(event):
                sel = cb_busqueda.get()
                if sel:
                    self.id_ins_seleccionado = sel.split(" - ")[0]
                    cursor.execute("SELECT tipo_instrumento, estado, instrumento_en_prest FROM instrumentos WHERE id_instrumento=%s", (self.id_ins_seleccionado,))
                    res = cursor.fetchone()
                    if res:
                        ent_tipo.delete(0, tk.END); ent_tipo.insert(0, res[0])
                        cb_estado.set(res[1])
                        var_en_uso.set(bool(res[2]))

            cb_busqueda.bind("<<ComboboxSelected>>", cargar_ins)

            def mod_ins():
                if not self.id_ins_seleccionado: return
                cursor.execute("UPDATE instrumentos SET tipo_instrumento=%s, estado=%s, instrumento_en_prest=%s WHERE id_instrumento=%s", (ent_tipo.get().strip(), cb_estado.get(), var_en_uso.get(), self.id_ins_seleccionado))
                conn.commit()
                messagebox.showinfo("Éxito", "Instrumento modificado.")
                self.render_form_view()

            ttk.Button(self.content_area, text="Modificar", bootstyle="primary", command=mod_ins).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            cursor.execute("SELECT id_instrumento, tipo_instrumento, estado, instrumento_en_prest FROM instrumentos")
            for r in cursor.fetchall():
                ttk.Label(scroll, text=f"ID: {r[0]} | Tipo: {r[1]} | Estado: {r[2]} | ¿Está en uso/Préstamo?: {'Sí' if r[3] else 'No'}", font=("Courier", 10)).pack(anchor="w", pady=4)


    # =========================================================================
    # LÓGICA BASE: MDA (Material de Apoyo)
    # =========================================================================
    def render_mda_base_operations(self):
        if self.current_action == "Añadir":
            ttk.Label(self.content_area, text="Tipo de Material:", bootstyle="inverse-light").pack(anchor="w")
            cb_tipo = ttk.Combobox(self.content_area, values=["A", "B", "C"], state="readonly", width=38)
            cb_tipo.current(0)
            cb_tipo.pack(anchor="w", pady=10)

            ttk.Label(self.content_area, text="Estado del Material:", bootstyle="inverse-light").pack(anchor="w")
            cb_estado = ttk.Combobox(self.content_area, values=["Ok", "Danado"], state="readonly", width=38)
            cb_estado.current(0)
            cb_estado.pack(anchor="w", pady=10)

            var_en_uso = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.content_area, text="Está en Uso / En Préstamo", variable=var_en_uso, bootstyle="square-toggle").pack(anchor="w", pady=10)

            def guardar():
                cursor.execute("INSERT INTO material (tipo_material, estado_material, material_en_prest) VALUES (%s, %s, %s)", (cb_tipo.get(), cb_estado.get(), var_en_uso.get()))
                conn.commit()
                messagebox.showinfo("Éxito", "Material añadido.")
                self.render_form_view()

            ttk.Button(self.content_area, text="Guardar", bootstyle="success", command=guardar).pack(anchor="w")

        elif self.current_action == "Modificar":
            ttk.Label(self.content_area, text="Seleccione Material a Modificar:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_busqueda = ttk.Combobox(self.content_area, values=obtener_dropdown_material(), state="readonly", width=40)
            cb_busqueda.pack(anchor="w", pady=(0, 15))

            ttk.Label(self.content_area, text="Tipo de Material:", bootstyle="inverse-light").pack(anchor="w")
            cb_tipo = ttk.Combobox(self.content_area, values=["A", "B", "C"], state="readonly", width=38)
            cb_tipo.pack(anchor="w", pady=10)

            ttk.Label(self.content_area, text="Estado del Material:", bootstyle="inverse-light").pack(anchor="w")
            cb_estado = ttk.Combobox(self.content_area, values=["Ok", "Danado"], state="readonly", width=38)
            cb_estado.pack(anchor="w", pady=10)

            var_en_uso = tk.BooleanVar(value=False)
            chk_en_uso = ttk.Checkbutton(self.content_area, text="Está en Uso / En Préstamo", variable=var_en_uso, bootstyle="square-toggle")
            chk_en_uso.pack(anchor="w", pady=10)

            self.id_mat_seleccionado = None

            def cargar_mat(event):
                sel = cb_busqueda.get()
                if sel:
                    self.id_mat_seleccionado = sel.split(" - ")[0]
                    cursor.execute("SELECT tipo_material, estado_material, material_en_prest FROM material WHERE id_m_a=%s", (self.id_mat_seleccionado,))
                    res = cursor.fetchone()
                    if res:
                        cb_tipo.set(res[0])
                        cb_estado.set(res[1])
                        var_en_uso.set(bool(res[2]))

            cb_busqueda.bind("<<ComboboxSelected>>", cargar_mat)

            def mod_mat():
                if not self.id_mat_seleccionado: return
                cursor.execute("UPDATE material SET tipo_material=%s, estado_material=%s, material_en_prest=%s WHERE id_m_a=%s", (cb_tipo.get(), cb_estado.get(), var_en_uso.get(), self.id_mat_seleccionado))
                conn.commit()
                messagebox.showinfo("Éxito", "Material modificado.")
                self.render_form_view()

            ttk.Button(self.content_area, text="Modificar", bootstyle="primary", command=mod_mat).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            cursor.execute("SELECT id_m_a, tipo_material, estado_material, material_en_prest FROM material")
            for r in cursor.fetchall():
                ttk.Label(scroll, text=f"ID: {r[0]} | Tipo: {r[1]} | Estado: {r[2]} | ¿Está en uso/Préstamo?: {'Sí' if r[3] else 'No'}", font=("Courier", 10)).pack(anchor="w", pady=4)


    # =========================================================================
    # LÓGICA BASE: SALONES
    # =========================================================================
    def render_salones_base_operations(self):
        vcmd_num = (self.register(validar_numero_simple), '%P')

        if self.current_action == "Añadir":
            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            ttk.Label(form, text="ID de Salón (Número):", bootstyle="inverse-light").pack(anchor="w")
            ent_id = ttk.Entry(form, width=40, validate="key", validatecommand=vcmd_num)
            ent_id.pack(anchor="w", pady=10)

            ttk.Label(form, text="Estado General del Salón:", bootstyle="inverse-light").pack(anchor="w")
            cb_estado = ttk.Combobox(form, values=["Ok", "Danado"], state="readonly", width=38)
            cb_estado.current(0)
            cb_estado.pack(anchor="w", pady=10)

            var_ocupado = tk.BooleanVar(value=False)
            ttk.Checkbutton(form, text="Salón Ocupado", variable=var_ocupado, bootstyle="square-toggle").pack(anchor="w", pady=5)

            var_tiene_piano = tk.BooleanVar(value=False)
            ttk.Checkbutton(form, text="Tiene Piano", variable=var_tiene_piano, bootstyle="square-toggle").pack(anchor="w", pady=5)

            ttk.Label(form, text="Estado del Piano (Opcional):", bootstyle="inverse-light").pack(anchor="w")
            cb_estado_piano = ttk.Combobox(form, values=["Ninguno", "Ok", "Danado"], state="readonly", width=38)
            cb_estado_piano.current(0)
            cb_estado_piano.pack(anchor="w", pady=10)

            def guardar():
                id_s = ent_id.get().strip()
                if not id_s: return messagebox.showerror("Error", "Ingrese un número de salón.")
                est_p = cb_estado_piano.get() if cb_estado_piano.get() != "Ninguno" else None
                try:
                    cursor.execute("INSERT INTO salones (id_salon, estado, salon_ocupado, tiene_piano, estado_piano) VALUES (%s, %s, %s, %s, %s)", 
                                   (int(id_s), cb_estado.get(), var_ocupado.get(), var_tiene_piano.get(), est_p))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Salón añadido.")
                    self.render_form_view()
                except Exception as ex: messagebox.showerror("Error", str(ex))

            ttk.Button(form, text="Guardar", bootstyle="success", command=guardar).pack(anchor="w", pady=10)

        elif self.current_action == "Modificar":
            ttk.Label(self.content_area, text="Seleccione Salón a Modificar:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_busqueda = ttk.Combobox(self.content_area, values=obtener_dropdown_salones(), state="readonly", width=40)
            cb_busqueda.pack(anchor="w", pady=(0, 15))

            form_edit = ScrolledFrame(self.content_area, bootstyle="round")
            form_edit.pack(fill="both", expand=True)

            ttk.Label(form_edit, text="Estado General del Salón:", bootstyle="inverse-light").pack(anchor="w")
            cb_estado = ttk.Combobox(form_edit, values=["Ok", "Danado"], state="readonly", width=38)
            cb_estado.pack(anchor="w", pady=10)

            var_ocupado = tk.BooleanVar(value=False)
            ttk.Checkbutton(form_edit, text="Salón Ocupado", variable=var_ocupado, bootstyle="square-toggle").pack(anchor="w", pady=5)

            var_tiene_piano = tk.BooleanVar(value=False)
            ttk.Checkbutton(form_edit, text="Tiene Piano", variable=var_tiene_piano, bootstyle="square-toggle").pack(anchor="w", pady=5)

            ttk.Label(form_edit, text="Estado del Piano:", bootstyle="inverse-light").pack(anchor="w")
            cb_estado_piano = ttk.Combobox(form_edit, values=["Ninguno", "Ok", "Danado"], state="readonly", width=38)
            cb_estado_piano.pack(anchor="w", pady=10)

            self.id_sal_seleccionado = None

            def cargar_sal(event):
                self.id_sal_seleccionado = cb_busqueda.get()
                if self.id_sal_seleccionado:
                    cursor.execute("SELECT estado, salon_ocupado, tiene_piano, estado_piano FROM salones WHERE id_salon=%s", (self.id_sal_seleccionado,))
                    res = cursor.fetchone()
                    if res:
                        cb_estado.set(res[0])
                        var_ocupado.set(bool(res[1]))
                        var_tiene_piano.set(bool(res[2]))
                        cb_estado_piano.set(res[3] if res[3] else "Ninguno")

            cb_busqueda.bind("<<ComboboxSelected>>", cargar_sal)

            def mod_sal():
                if not self.id_sal_seleccionado: return
                est_p = cb_estado_piano.get() if cb_estado_piano.get() != "Ninguno" else None
                cursor.execute("UPDATE salones SET estado=%s, salon_ocupado=%s, tiene_piano=%s, estado_piano=%s WHERE id_salon=%s", 
                               (cb_estado.get(), var_ocupado.get(), var_tiene_piano.get(), est_p, self.id_sal_seleccionado))
                conn.commit()
                messagebox.showinfo("Éxito", "Salón modificado.")
                self.render_form_view()

            ttk.Button(form_edit, text="Modificar", bootstyle="primary", command=mod_sal).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            cursor.execute("SELECT id_salon, estado, salon_ocupado, tiene_piano, ya_en_prest FROM salones")
            for r in cursor.fetchall():
                ttk.Label(scroll, text=f"Salón Nro: {r[0]} | Estado: {r[1]} | ¿Ocupado?: {'Sí' if r[2] else 'No'} | ¿Tiene Piano?: {'Sí' if r[3] else 'No'} | ¿En Préstamo?: {'Sí' if r[4] else 'No'}", font=("Courier", 10)).pack(anchor="w", pady=4)


    # =========================================================================
    # MENÚ "P" (PRÉSTAMOS con Spinboxes para Fecha/Hora)
    # =========================================================================
    def render_prestamos_generic_operations(self):
        ttk.Label(
            self.content_area, 
            text=f"{self.current_action} Préstamo - Módulo {self.display_name}", 
            font=("Arial", 16, "bold"), bootstyle="inverse-light"
        ).pack(anchor="w", pady=(0, 15))

        if self.name == "instrumentos":
            tabla, id_col, prest_bool, t_id = "instrumentos", "id_instrumento", "instrumento_en_prest", "Instrumento"
        elif self.name == "m.d.a":
            tabla, id_col, prest_bool, t_id = "material", "id_m_a", "material_en_prest", "Material (MDA)"
        elif self.name == "salones":
            tabla, id_col, prest_bool, t_id = "salones", "id_salon", "ya_en_prest", "Salón"
        else:
            return

        if self.current_action == "Añadir":
            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            try:
                cursor.execute(f"SELECT {id_col} FROM {tabla} WHERE {prest_bool} = 0")
                items_disponibles = [str(r[0]) for r in cursor.fetchall()]
            except Exception: items_disponibles = []

            ttk.Label(form, text=f"Seleccione {t_id} disponible:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_item = ttk.Combobox(form, values=items_disponibles, state="readonly", width=38)
            cb_item.pack(anchor="w", pady=(0, 10))

            ttk.Label(form, text="Asignar a Cédula de Docente (Opcional):", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_docente = ttk.Combobox(form, values=["Ninguno"] + obtener_dropdown_docentes(), state="readonly", width=38)
            cb_docente.current(0)
            cb_docente.pack(anchor="w", pady=(0, 10))

            ttk.Label(form, text="Asignar a ID de Estudiante (Opcional):", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_estudiante = ttk.Combobox(form, values=["Ninguno"] + obtener_dropdown_estudiantes(), state="readonly", width=38)
            cb_estudiante.current(0)
            cb_estudiante.pack(anchor="w", pady=(0, 10))

            meses_valores = [f"{i:02d}" for i in range(1, 13)]

            # --- FECHA Y HORA DE PRÉSTAMO ---
            ttk.Label(form, text="Fecha Préstamo:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            f_prest_frame = ttk.Frame(form, bootstyle="light")
            f_prest_frame.pack(anchor="w", pady=(0, 10))
            
            ttk.Label(f_prest_frame, text="Día: ", bootstyle="inverse-light").pack(side="left")
            sp_dia_p = ttk.Spinbox(f_prest_frame, from_=1, to=31, width=5, format="%02.0f")
            sp_dia_p.pack(side="left", padx=(0, 10))
            
            ttk.Label(f_prest_frame, text="Mes: ", bootstyle="inverse-light").pack(side="left")
            cb_mes_p = ttk.Combobox(f_prest_frame, values=meses_valores, state="readonly", width=5)
            cb_mes_p.current(0)
            cb_mes_p.pack(side="left")

            ttk.Label(form, text="Hora Préstamo (HH:MM):", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            h_prest_frame = ttk.Frame(form, bootstyle="light")
            h_prest_frame.pack(anchor="w", pady=(0, 10))
            
            sp_hora_p = ttk.Spinbox(h_prest_frame, from_=0, to=23, width=5, format="%02.0f")
            sp_hora_p.pack(side="left")
            ttk.Label(h_prest_frame, text=" : ", bootstyle="inverse-light").pack(side="left")
            sp_min_p = ttk.Spinbox(h_prest_frame, from_=0, to=59, width=5, format="%02.0f")
            sp_min_p.pack(side="left")

            # --- FECHA Y HORA LÍMITE ---
            ttk.Label(form, text="Fecha Límite:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            f_lim_frame = ttk.Frame(form, bootstyle="light")
            f_lim_frame.pack(anchor="w", pady=(0, 10))
            
            ttk.Label(f_lim_frame, text="Día: ", bootstyle="inverse-light").pack(side="left")
            sp_dia_l = ttk.Spinbox(f_lim_frame, from_=1, to=31, width=5, format="%02.0f")
            sp_dia_l.pack(side="left", padx=(0, 10))
            
            ttk.Label(f_lim_frame, text="Mes: ", bootstyle="inverse-light").pack(side="left")
            cb_mes_l = ttk.Combobox(f_lim_frame, values=meses_valores, state="readonly", width=5)
            cb_mes_l.current(0)
            cb_mes_l.pack(side="left")

            ttk.Label(form, text="Hora Límite (HH:MM):", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            h_lim_frame = ttk.Frame(form, bootstyle="light")
            h_lim_frame.pack(anchor="w", pady=(0, 10))
            
            sp_hora_l = ttk.Spinbox(h_lim_frame, from_=0, to=23, width=5, format="%02.0f")
            sp_hora_l.pack(side="left")
            ttk.Label(h_lim_frame, text=" : ", bootstyle="inverse-light").pack(side="left")
            sp_min_l = ttk.Spinbox(h_lim_frame, from_=0, to=59, width=5, format="%02.0f")
            sp_min_l.pack(side="left")

            def registrar_prestamo():
                item_id = cb_item.get()
                if not item_id: return messagebox.showerror("Error", "Seleccione un recurso.")

                doc_sel = cb_docente.get()
                est_sel = cb_estudiante.get()
                ced_doc = int(doc_sel.split(" - ")[0]) if doc_sel != "Ninguno" else None
                id_est = int(est_sel.split(" - ")[0]) if est_sel != "Ninguno" else None

                anio_actual = datetime.datetime.now().year
                fecha_p = f"{anio_actual}-{cb_mes_p.get()}-{int(sp_dia_p.get()):02d}"
                hora_p = f"{int(sp_hora_p.get()):02d}:{int(sp_min_p.get()):02d}:00"
                fecha_l = f"{anio_actual}-{cb_mes_l.get()}-{int(sp_dia_l.get()):02d}"
                hora_l = f"{int(sp_hora_l.get()):02d}:{int(sp_min_l.get()):02d}:00"

                try:
                    if self.name == "instrumentos":
                        q = """UPDATE instrumentos SET instrumento_en_prest=1, fecha_prest_instrumetnto=%s, hora_prest_instrumetnto=%s, 
                               fecha_limite_instrumetnto=%s, hora_limite_instrumetnto=%s, id_estudiante=%s, cedula_docente=%s WHERE id_instrumento=%s"""
                    elif self.name == "m.d.a":
                        q = """UPDATE material SET material_en_prest=1, fecha_prest_m_a=%s, hora_prest_m_a=%s, 
                               fecha_limite_m_a=%s, hora_limite_m_a=%s, id_estudiante=%s, cedula_docente=%s WHERE id_m_a=%s"""
                    elif self.name == "salones":
                        q = """UPDATE salones SET ya_en_prest=1, fecha_prest=%s, hora_prest=%s, 
                               fecha_limite_prest=%s, hora_limite_prest=%s, id_estudiante_ocu=%s, cedula_docente_ocupante=%s WHERE id_salon=%s"""
                    
                    cursor.execute(q, (fecha_p, hora_p, fecha_l, hora_l, id_est, ced_doc, int(item_id)))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Préstamo registrado.")
                    self.render_form_view()
                except Exception as ex: messagebox.showerror("Error", str(ex))

            ttk.Button(form, text="Registrar Préstamo", bootstyle="success", command=registrar_prestamo).pack(anchor="w", pady=15)

        elif self.current_action == "Modificar":
            ttk.Label(self.content_area, text="Devolución / Liberación de recurso prestado:", bootstyle="inverse-light").pack(anchor="w")
            try:
                cursor.execute(f"SELECT {id_col} FROM {tabla} WHERE {prest_bool} = 1")
                items_prestados = [str(r[0]) for r in cursor.fetchall()]
            except Exception: items_prestados = []

            cb_dev = ttk.Combobox(self.content_area, values=items_prestados, state="readonly", width=40)
            cb_dev.pack(anchor="w", pady=10)

            def liberar_prestamo():
                it = cb_dev.get()
                if not it: return
                try:
                    if self.name == "instrumentos":
                        q = "UPDATE instrumentos SET instrumento_en_prest=0, id_estudiante=NULL, cedula_docente=NULL, fecha_prest_instrumetnto=NULL, hora_prest_instrumetnto=NULL, fecha_limite_instrumetnto=NULL, hora_limite_instrumetnto=NULL WHERE id_instrumento=%s"
                    elif self.name == "m.d.a":
                        q = "UPDATE material SET material_en_prest=0, id_estudiante=NULL, cedula_docente=NULL, fecha_prest_m_a=NULL, hora_prest_m_a=NULL, fecha_limite_m_a=NULL, hora_limite_m_a=NULL WHERE id_m_a=%s"
                    elif self.name == "salones":
                        q = "UPDATE salones SET ya_en_prest=0, id_estudiante_ocu=NULL, cedula_docente_ocupante=NULL, fecha_prest=NULL, hora_prest=NULL, fecha_limite_prest=NULL, hora_limite_prest=NULL WHERE id_salon=%s"
                    cursor.execute(q, (int(it),))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Recurso liberado.")
                    self.render_form_view()
                except Exception as ex: messagebox.showerror("Error", str(ex))

            ttk.Button(self.content_area, text="Concluir Préstamo (Devolución)", bootstyle="danger", command=liberar_prestamo).pack(anchor="w")

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            try:
                if self.name == "instrumentos":
                    cursor.execute("SELECT id_instrumento, tipo_instrumento, id_estudiante, cedula_docente, fecha_prest_instrumetnto, hora_prest_instrumetnto FROM instrumentos WHERE instrumento_en_prest=1")
                elif self.name == "m.d.a":
                    cursor.execute("SELECT id_m_a, tipo_material, id_estudiante, cedula_docente, fecha_prest_m_a, hora_prest_m_a FROM material WHERE material_en_prest=1")
                elif self.name == "salones":
                    cursor.execute("SELECT id_salon, estado, id_estudiante_ocu, cedula_docente_ocupante, fecha_prest, hora_prest FROM salones WHERE ya_en_prest=1")
                
                for r in cursor.fetchall():
                    ttk.Label(scroll, text=f"ID Recurso: {r[0]} | Descr: {r[1]} | Estudiante: {r[2]} | Docente: {r[3]} | Prestado: {r[4]} a las {r[5]}", font=("Courier", 10)).pack(anchor="w", pady=4)
            except Exception as ex: print(ex)


class UpdateDataScreen(ttk.Frame):
    def __init__(self, master, on_logout):
        super().__init__(master, padding=15)
        self.on_logout = on_logout
        
        self.top_nav = TopNavBar(self, active_callback=self.switch_workspace, logout_callback=self.on_logout)
        self.top_nav.pack(side="top", fill="x", pady=(0, 15)) 
        
        self.workspace_container = ttk.Frame(self)
        self.workspace_container.pack(side="bottom", fill="both", expand=True)
        
        self.active_workspace = None
        self.switch_workspace("profesor")

    def switch_workspace(self, target_view):
        if self.active_workspace:
            self.active_workspace.destroy()
        
        has_loans = target_view in ["instrumentos", "m.d.a", "salones"]
        self.active_workspace = InteractiveWorkspace(self.workspace_container, name=target_view, include_loans=has_loans)
        self.active_workspace.pack(fill="both", expand=True)


class App(ttk.Window):
    def __init__(self):
        super().__init__(title="EMMAE - Sistema Escolar v2.6", themename="flatly", size=(1080, 700))
        self.current_screen = None
        self.load_login_screen()
    
    def load_login_screen(self):
        if self.current_screen: self.current_screen.destroy()
        self.current_screen = LoginScreen(self, on_login=self.load_admin_screen)
        self.current_screen.pack(expand=True, fill="both")

    def load_admin_screen(self):
        if self.current_screen: self.current_screen.destroy()
        self.current_screen = UpdateDataScreen(self, on_logout=self.load_login_screen)
        self.current_screen.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    try:
        app.mainloop()
    finally:
        try:
            cursor.close()
            conn.close()
        except NameError: pass