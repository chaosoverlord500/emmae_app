import datetime
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from modules import db_con as DB_con, user_management as User_Manager
from modules.validators import validate_email, validate_phone_rest, validate_simple_number
from modules import db_queries as db_q

try:
    conn = DB_con.connect_to_db()
    cursor = conn.cursor()
except ImportError:
    print("Error connecting to the database")


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

    def check_credentials(self, id_str, password):
        if id_str in ["Cédula", ""] or password in ["Contraseña", ""]:
            return messagebox.showerror("Error", "Por favor complete todos los campos")
        try:
            if User_Manager.login(int(id_str), password):
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
        self.selected_id = None
        
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

    def create_labeled_entry(self, parent, label_text, width=40, show=None, validate_type=None):
        ttk.Label(parent, text=label_text, bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
        kwargs = {"width": width}
        if show:
            kwargs["show"] = show
        if validate_type:
            cmd = (self.register(validate_type), '%P')
            kwargs["validate"] = "key"
            kwargs["validatecommand"] = cmd
        entry = ttk.Entry(parent, **kwargs)
        entry.pack(anchor="w", pady=(0, 10))
        return entry

    def create_phone_input(self, parent, validate_cmd):
        ttk.Label(parent, text="Teléfono:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
        tel_frame = ttk.Frame(parent, bootstyle="light")
        tel_frame.pack(anchor="w", pady=(0, 15))
        
        prefixes = ["0424", "0414", "0276", "0416", "0426", "0212", "0412"]
        prefix_cb = ttk.Combobox(tel_frame, values=prefixes, state="readonly", width=8)
        prefix_cb.current(0)
        prefix_cb.pack(side="left", padx=(0, 5))
        
        phone_entry = ttk.Entry(tel_frame, width=28, validate="key", validatecommand=(self.register(validate_cmd), '%P'))
        phone_entry.pack(side="left")
        return prefix_cb, phone_entry

    def render_form_view(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        if self.include_loans and self.current_mode == "P":
            self.render_loans_operations()
            return

        ttk.Label(
            self.content_area, 
            text=f"{self.current_action} - Gestión de {self.display_name}", 
            font=("Arial", 16, "bold"), bootstyle="inverse-light"
        ).pack(anchor="w", pady=(0, 15))
        
        handlers = {
            "profesor": self.render_teacher_operations,
            "estudiante": self.render_student_operations,
            "instrumentos": lambda: self.render_generic_resource_operations(
                table="instrumentos", id_col="id_instrumento", type_col="tipo_instrumento", 
                status_col="estado_instrumento", avail_col="instrumento_disponible", 
                label_text="Instrumento", dropdown_func=db_q.get_instruments_dropdown
            ),
            "m.d.a": lambda: self.render_generic_resource_operations(
                table="material_de_apoyo", id_col="id_mda", type_col="tipo_mda", 
                status_col="estado_mda", avail_col="mda_disponible", 
                label_text="Material (MDA)", dropdown_func=db_q.get_materials_dropdown
            ),
            "salones": self.render_classroom_operations
        }
        
        if self.name in handlers:
            handlers[self.name]()

    def render_teacher_operations(self):
        if self.current_action in ["Añadir", "Modificar"]:
            is_mod = self.current_action == "Modificar"
            
            if is_mod:
                ttk.Label(self.content_area, text="Buscar Docente por Cédula:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                cb_search = ttk.Combobox(self.content_area, values=db_q.get_teachers_dropdown(cursor), state="readonly", width=40)
                cb_search.pack(anchor="w", pady=(0, 15))

            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            entry_id = None if is_mod else self.create_labeled_entry(form, "Cédula:")
            entry_first_name = self.create_labeled_entry(form, "Nombre:")
            entry_last_name = self.create_labeled_entry(form, "Apellido:")

            ttk.Label(form, text="Especialidad:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            cb_specialty = ttk.Combobox(form, values=["Canto", "Piano", "Guitarra", "Violín"], state="readonly", width=38)
            cb_specialty.current(0)
            cb_specialty.pack(anchor="w", pady=(0, 10))

            var_has_loan = tk.BooleanVar(value=False)
            ttk.Checkbutton(form, text="Tiene Préstamo", variable=var_has_loan, bootstyle="square-toggle").pack(anchor="w", pady=10)

            var_is_admin = tk.BooleanVar(value=False)
            entry_admin_pass = self.create_labeled_entry(form, "Contraseña del Administrador:", show="*")
            entry_admin_pass.config(state="disabled")

            def toggle_admin_pass():
                if var_is_admin.get():
                    entry_admin_pass.config(state="normal")
                else:
                    entry_admin_pass.delete(0, tk.END)
                    entry_admin_pass.config(state="disabled")

            ttk.Checkbutton(
                form, text="Administrador", variable=var_is_admin, 
                bootstyle="square-toggle", command=toggle_admin_pass
            ).pack(anchor="w", pady=5)

            entry_email = self.create_labeled_entry(form, "Correo Electrónico:")
            cb_prefix, entry_phone_rest = self.create_phone_input(form, validate_phone_rest)

            if is_mod:
                def load_teacher_data(event):
                    selected = cb_search.get()
                    if selected:
                        self.selected_id = selected.split(" - ")[0]
                        cursor.execute("SELECT nombre_docente, apellido_docente, especialidad_primaria, docente_tiene_prestamo, correo_docente, telefono_docente FROM docente WHERE cedula_docente = %s", (self.selected_id,))
                        row = cursor.fetchone()
                        if row:
                            entry_first_name.delete(0, tk.END); entry_first_name.insert(0, row[0])
                            entry_last_name.delete(0, tk.END); entry_last_name.insert(0, row[1])
                            cb_specialty.set(row[2])
                            var_has_loan.set(bool(row[3]))
                            entry_email.delete(0, tk.END); entry_email.insert(0, row[4])
                            
                            phone = row[5] or ""
                            valid_prefixes = ["0424", "0414", "0276", "0416", "0426", "0212", "0412"]
                            if len(phone) >= 4 and phone[:4] in valid_prefixes:
                                cb_prefix.set(phone[:4])
                                entry_phone_rest.delete(0, tk.END); entry_phone_rest.insert(0, phone[4:])
                            else:
                                cb_prefix.current(0)
                                entry_phone_rest.delete(0, tk.END); entry_phone_rest.insert(0, phone)

                            if db_q.check_is_admin(self.selected_id):
                                var_is_admin.set(True)
                                entry_admin_pass.config(state="normal")
                                entry_admin_pass.delete(0, tk.END); entry_admin_pass.insert(0, db_q.get_admin_password(self.selected_id))
                            else:
                                var_is_admin.set(False)
                                entry_admin_pass.delete(0, tk.END); entry_admin_pass.config(state="disabled")

                cb_search.bind("<<ComboboxSelected>>", load_teacher_data)

            def save_teacher():
                teacher_id = self.selected_id if is_mod else entry_id.get().strip()
                first_name = entry_first_name.get().strip()
                last_name = entry_last_name.get().strip()
                specialty = cb_specialty.get()
                has_loan = var_has_loan.get()
                email = entry_email.get().strip()
                phone = f"{cb_prefix.get()}{entry_phone_rest.get().strip()}"
                is_admin = var_is_admin.get()
                admin_pass = entry_admin_pass.get().strip()

                if not teacher_id.isdigit():
                    return messagebox.showerror("Error de Validación", "La cédula debe ser un valor numérico.")
                if not first_name or not last_name:
                    return messagebox.showerror("Error de Validación", "El nombre y apellido son obligatorios.")
                if is_admin and not admin_pass:
                    return messagebox.showerror("Error de Validación", "La contraseña es obligatoria para el administrador.")
                if not validate_email(email):
                    return messagebox.showerror("Error de Validación", "El formato del correo electrónico es inválido.")

                try:
                    if is_mod:
                        query = """UPDATE docente SET nombre_docente=%s, apellido_docente=%s, especialidad_primaria=%s, docente_tiene_prestamo=%s, correo_docente=%s, telefono_docente=%s WHERE cedula_docente=%s"""
                        cursor.execute(query, (first_name, last_name, specialty, has_loan, email, phone, teacher_id))
                    else:
                        query = """INSERT INTO docente (cedula_docente, nombre_docente, apellido_docente, especialidad_primaria, docente_tiene_prestamo, correo_docente, telefono_docente) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                        cursor.execute(query, (int(teacher_id), first_name, last_name, specialty, has_loan, email, phone))

                    conn.commit()

                    if is_admin:
                        db_q.save_admin_json(teacher_id, admin_pass)
                    else:
                        db_q.delete_admin_json(teacher_id)

                    messagebox.showinfo("Éxito", f"Docente {'actualizado' if is_mod else 'registrado'} correctamente.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Database Error", f"Error al guardar: {ex}")

            btn_text = "Modificar" if is_mod else "Guardar Registro"
            btn_style = "primary" if is_mod else "success"
            ttk.Button(form, text=btn_text, bootstyle=btn_style, command=save_teacher).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            entry_filter = self.create_labeled_entry(self.content_area, "Filtrar Docente:")
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)

            def search_teachers(*args):
                for w in scroll.winfo_children():
                    w.destroy()
                term = f"%{entry_filter.get().strip()}%"
                try:
                    cursor.execute("SELECT cedula_docente, nombre_docente, apellido_docente, telefono_docente, correo_docente, especialidad_primaria, docente_tiene_prestamo FROM docente WHERE nombre_docente LIKE %s OR cedula_docente LIKE %s", (term, term))
                    for r in cursor.fetchall():
                        ttk.Label(scroll, text=f"Cédula: {r[0]} | Docente: {r[1]} {r[2]} | Teléfono: {r[3]} | Email: {r[4]} | Especialidad: {r[5]} | ¿En Préstamo?: {'Sí' if r[6] else 'No'}", font=("Courier", 10)).pack(anchor="w", padx=10, pady=4)
                except Exception as ex:
                    print(ex)

            entry_filter.bind("<KeyRelease>", search_teachers)
            search_teachers()

    def render_student_operations(self):
        if self.current_action == "Añadir":
            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            entry_id = self.create_labeled_entry(form, "Cédula Estudiante:", validate_type=validate_simple_number)
            entry_first_name = self.create_labeled_entry(form, "Nombre Estudiante:")
            entry_last_name = self.create_labeled_entry(form, "Apellido Estudiante:")
            entry_instrument = self.create_labeled_entry(form, "Instrumento Principal:")

            var_piano = tk.BooleanVar(value=False)
            ttk.Checkbutton(form, text="Piano Complementario", variable=var_piano, bootstyle="square-toggle").pack(anchor="w", pady=5)

            var_has_loan = tk.BooleanVar(value=False)
            ttk.Checkbutton(form, text="Tiene Préstamo", variable=var_has_loan, bootstyle="square-toggle").pack(anchor="w", pady=5)

            entry_year = self.create_labeled_entry(form, "Año Cursante:")
            entry_email = self.create_labeled_entry(form, "Correo Estudiante:")
            cb_prefix, entry_phone_rest = self.create_phone_input(form, validate_phone_rest)
            entry_rep_phone = self.create_labeled_entry(form, "Teléfono Representante (Opcional):")
            entry_rep_email = self.create_labeled_entry(form, "Correo Representante (Opcional):")

            def save_student():
                student_id = entry_id.get().strip()
                first_name = entry_first_name.get().strip()
                last_name = entry_last_name.get().strip()
                if not student_id.isdigit() or not first_name or not last_name:
                    return messagebox.showerror("Error", "Campos obligatorios incorrectos.")
                try:
                    query = """INSERT INTO estudiante (cedula_estudiante, nombre_estudiante, apellido_estudiante, instrumento_estudiante, tiene_piano_complementario, estudiante_tiene_prestamo, ano_cursante, telefono_estudiante, correo_estudiante, telefono_representante, correo_representante) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query, (int(student_id), first_name, last_name, entry_instrument.get(), var_piano.get(), var_has_loan.get(), entry_year.get(), f"{cb_prefix.get()}{entry_phone_rest.get()}", entry_email.get(), entry_rep_phone.get(), entry_rep_email.get()))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Estudiante guardado.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            ttk.Button(form, text="Guardar Estudiante", bootstyle="success", command=save_student).pack(anchor="w", pady=10)

        elif self.current_action == "Modificar":
            ttk.Label(self.content_area, text="Seleccione Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_search = ttk.Combobox(self.content_area, values=db_q.get_students_dropdown(cursor), state="readonly", width=40)
            cb_search.pack(anchor="w", pady=(0, 15))

            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            entry_first_name = self.create_labeled_entry(form, "Nombre:")
            entry_last_name = self.create_labeled_entry(form, "Apellido:")

            def load_student_data(event):
                selected = cb_search.get()
                if selected:
                    self.selected_id = selected.split(" - ")[0]
                    cursor.execute("SELECT nombre_estudiante, apellido_estudiante FROM estudiante WHERE cedula_estudiante=%s", (self.selected_id,))
                    row = cursor.fetchone()
                    if row:
                        entry_first_name.delete(0, tk.END); entry_first_name.insert(0, row[0])
                        entry_last_name.delete(0, tk.END); entry_last_name.insert(0, row[1])

            cb_search.bind("<<ComboboxSelected>>", load_student_data)

            def update_student():
                if not self.selected_id:
                    return
                cursor.execute("UPDATE estudiante SET nombre_estudiante=%s, apellido_estudiante=%s WHERE cedula_estudiante=%s", (entry_first_name.get(), entry_last_name.get(), self.selected_id))
                conn.commit()
                messagebox.showinfo("Éxito", "Estudiante modificado.")
                self.render_form_view()

            ttk.Button(form, text="Modificar", bootstyle="primary", command=update_student).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            entry_filter = self.create_labeled_entry(self.content_area, "Filtrar por cédula o nombre:")
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)

            def search_students(*args):
                for w in scroll.winfo_children():
                    w.destroy()
                term = f"%{entry_filter.get().strip()}%"
                cursor.execute("SELECT cedula_estudiante, nombre_estudiante, apellido_estudiante, instrumento_estudiante, estudiante_tiene_prestamo FROM estudiante WHERE nombre_estudiante LIKE %s OR cedula_estudiante LIKE %s", (term, term))
                for r in cursor.fetchall():
                    ttk.Label(scroll, text=f"Cédula: {r[0]} | Estudiante: {r[1]} {r[2]} | Instrumento: {r[3]} | ¿En Préstamo?: {'Sí' if r[4] else 'No'}", font=("Courier", 10)).pack(anchor="w", padx=10, pady=4)

            entry_filter.bind("<KeyRelease>", search_students)
            search_students()

    def render_generic_resource_operations(self, table, id_col, type_col, status_col, avail_col, label_text, dropdown_func):
        if self.current_action in ["Añadir", "Modificar"]:
            is_mod = self.current_action == "Modificar"

            if is_mod:
                ttk.Label(self.content_area, text=f"Seleccione {label_text} a Modificar:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                cb_search = ttk.Combobox(self.content_area, values=dropdown_func(cursor), state="readonly", width=40)
                cb_search.pack(anchor="w", pady=(0, 15))

            entry_type = self.create_labeled_entry(self.content_area, f"Tipo de {label_text}:")

            ttk.Label(self.content_area, text=f"Estado del {label_text}:", bootstyle="inverse-light").pack(anchor="w")
            cb_status = ttk.Combobox(self.content_area, values=["Ok", "Dañado"], state="readonly", width=38)
            cb_status.current(0)
            cb_status.pack(anchor="w", pady=10)

            var_available = tk.BooleanVar(value=True)
            ttk.Checkbutton(self.content_area, text="Disponible", variable=var_available, bootstyle="square-toggle").pack(anchor="w", pady=10)

            if is_mod:
                def load_item(event):
                    selected = cb_search.get()
                    if selected:
                        self.selected_id = selected.split(" - ")[0]
                        cursor.execute(f"SELECT {type_col}, {status_col}, {avail_col} FROM {table} WHERE {id_col}=%s", (self.selected_id,))
                        row = cursor.fetchone()
                        if row:
                            entry_type.delete(0, tk.END); entry_type.insert(0, row[0])
                            cb_status.set(row[1])
                            var_available.set(bool(row[2]))

                cb_search.bind("<<ComboboxSelected>>", load_item)

            def save_item():
                mat_type = entry_type.get().strip()
                status = cb_status.get()
                available = var_available.get()

                if is_mod:
                    if not self.selected_id:
                        return
                    cursor.execute(f"UPDATE {table} SET {type_col}=%s, {status_col}=%s, {avail_col}=%s WHERE {id_col}=%s", (mat_type, status, available, self.selected_id))
                else:
                    cursor.execute(f"INSERT INTO {table} ({type_col}, {status_col}, {avail_col}) VALUES (%s, %s, %s)", (mat_type, status, available))

                conn.commit()
                messagebox.showinfo("Éxito", f"{label_text} {'modificado' if is_mod else 'añadido'}.")
                self.render_form_view()

            btn_text = "Modificar" if is_mod else "Guardar"
            btn_style = "primary" if is_mod else "success"
            ttk.Button(self.content_area, text=btn_text, bootstyle=btn_style, command=save_item).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            cursor.execute(f"SELECT {id_col}, {type_col}, {status_col}, {avail_col} FROM {table}")
            for r in cursor.fetchall():
                ttk.Label(scroll, text=f"ID: {r[0]} | Tipo: {r[1]} | Estado: {r[2]} | ¿Disponible?: {'Sí' if r[3] else 'No'}", font=("Courier", 10)).pack(anchor="w", pady=4)

    def render_classroom_operations(self):
        if self.current_action in ["Añadir", "Modificar"]:
            is_mod = self.current_action == "Modificar"

            if is_mod:
                ttk.Label(self.content_area, text="Seleccione Salón a Modificar:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                cb_search = ttk.Combobox(self.content_area, values=db_q.get_classrooms_dropdown(cursor), state="readonly", width=40)
                cb_search.pack(anchor="w", pady=(0, 15))

            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            ttk.Label(form, text="Estado General del Salón:", bootstyle="inverse-light").pack(anchor="w")
            cb_status = ttk.Combobox(form, values=["Ok", "Dañado"], state="readonly", width=38)
            cb_status.current(0)
            cb_status.pack(anchor="w", pady=10)

            var_occupied = tk.BooleanVar(value=False)
            ttk.Checkbutton(form, text="Salón Ocupado", variable=var_occupied, bootstyle="square-toggle").pack(anchor="w", pady=5)

            var_available = tk.BooleanVar(value=True)
            ttk.Checkbutton(form, text="Salón Disponible", variable=var_available, bootstyle="square-toggle").pack(anchor="w", pady=5)

            ttk.Label(form, text="ID Piano (Opcional):", bootstyle="inverse-light").pack(anchor="w")
            cb_piano = ttk.Combobox(form, values=["Ninguno"] + db_q.get_instruments_dropdown(cursor), state="readonly", width=38)
            cb_piano.current(0)
            cb_piano.pack(anchor="w", pady=10)

            if is_mod:
                def load_classroom(event):
                    selected = cb_search.get()
                    if selected:
                        self.selected_id = selected.split(" - ")[0]
                        cursor.execute("SELECT estado_salon, salon_ocupado, salon_disponible, id_piano FROM salon WHERE id_salon=%s", (self.selected_id,))
                        row = cursor.fetchone()
                        if row:
                            cb_status.set(row[0])
                            var_occupied.set(bool(row[1]))
                            var_available.set(bool(row[2]))
                            if row[3]:
                                cb_piano.set(str(row[3]))

                cb_search.bind("<<ComboboxSelected>>", load_classroom)

            def save_classroom():
                piano_val = cb_piano.get().split(" - ")[0] if cb_piano.get() != "Ninguno" else None
                try:
                    if is_mod:
                        if not self.selected_id:
                            return
                        cursor.execute("UPDATE salon SET estado_salon=%s, salon_ocupado=%s, salon_disponible=%s, id_piano=%s WHERE id_salon=%s", 
                                       (cb_status.get(), var_occupied.get(), var_available.get(), piano_val, self.selected_id))
                    else:
                        cursor.execute("INSERT INTO salon (estado_salon, salon_ocupado, salon_disponible, id_piano) VALUES (%s, %s, %s, %s)", 
                                       (cb_status.get(), var_occupied.get(), var_available.get(), piano_val))
                    
                    conn.commit()
                    messagebox.showinfo("Éxito", f"Salón {'modificado' if is_mod else 'añadido'}.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            btn_text = "Modificar" if is_mod else "Guardar"
            btn_style = "primary" if is_mod else "success"
            ttk.Button(form, text=btn_text, bootstyle=btn_style, command=save_classroom).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            cursor.execute("SELECT id_salon, estado_salon, salon_ocupado, salon_disponible, id_piano FROM salon")
            for r in cursor.fetchall():
                ttk.Label(scroll, text=f"Salón Nro: {r[0]} | Estado: {r[1]} | ¿Ocupado?: {'Sí' if r[2] else 'No'} | ¿Disponible?: {'Sí' if r[3] else 'No'} | Piano ID: {r[4] or 'Ninguno'}", font=("Courier", 10)).pack(anchor="w", pady=4)

    def render_loans_operations(self):
        ttk.Label(
            self.content_area, 
            text=f"{self.current_action} Préstamo - Módulo {self.display_name}", 
            font=("Arial", 16, "bold"), bootstyle="inverse-light"
        ).pack(anchor="w", pady=(0, 15))

        target_map = {
            "instrumentos": ("instrumentos", "id_instrumento", "instrumento_disponible", "Instrumento"),
            "m.d.a": ("material_de_apoyo", "id_mda", "mda_disponible", "Material (MDA)"),
            "salones": ("salon", "id_salon", "salon_disponible", "Salón")
        }

        if self.name not in target_map:
            return

        table_name, id_col, available_col, label_name = target_map[self.name]
        item_fk_column = id_col

        if self.current_action == "Añadir":
            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            try:
                cursor.execute(f"SELECT {id_col} FROM {table_name} WHERE {available_col} = 1")
                available_items = [str(r[0]) for r in cursor.fetchall()]
            except Exception:
                available_items = []

            ttk.Label(form, text=f"Seleccione {label_name} disponible:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_item = ttk.Combobox(form, values=available_items, state="readonly", width=38)
            cb_item.pack(anchor="w", pady=(0, 10))

            ttk.Label(form, text="Asignar a Cédula de Docente (Opcional):", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_teacher = ttk.Combobox(form, values=["Ninguno"] + db_q.get_teachers_dropdown(cursor), state="readonly", width=38)
            cb_teacher.current(0)
            cb_teacher.pack(anchor="w", pady=(0, 10))

            ttk.Label(form, text="Asignar a Cédula de Estudiante (Opcional):", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_student = ttk.Combobox(form, values=["Ninguno"] + db_q.get_students_dropdown(cursor), state="readonly", width=38)
            cb_student.current(0)
            cb_student.pack(anchor="w", pady=(0, 10))

            months_values = [f"{i:02d}" for i in range(1, 13)]

            def create_date_picker(parent_frame, label_prefix):
                ttk.Label(parent_frame, text=f"Fecha {label_prefix}:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
                date_frame = ttk.Frame(parent_frame, bootstyle="light")
                date_frame.pack(anchor="w", pady=(0, 10))
                
                ttk.Label(date_frame, text="Día: ", bootstyle="inverse-light").pack(side="left")
                sp_day = ttk.Spinbox(date_frame, from_=1, to=31, width=5, format="%02.0f")
                sp_day.pack(side="left", padx=(0, 10))
                
                ttk.Label(date_frame, text="Mes: ", bootstyle="inverse-light").pack(side="left")
                cb_month = ttk.Combobox(date_frame, values=months_values, state="readonly", width=5)
                cb_month.current(0)
                cb_month.pack(side="left")

                return sp_day, cb_month

            sp_day_start, cb_month_start = create_date_picker(form, "Préstamo")
            sp_day_end, cb_month_end = create_date_picker(form, "Límite")

            def register_loan():
                item_id = cb_item.get()
                if not item_id:
                    return messagebox.showerror("Error", "Seleccione un recurso.")

                teacher_sel = cb_teacher.get()
                student_sel = cb_student.get()
                teacher_id = int(teacher_sel.split(" - ")[0]) if teacher_sel != "Ninguno" else None
                student_id = int(student_sel.split(" - ")[0]) if student_sel != "Ninguno" else None

                current_year = datetime.datetime.now().year
                start_date = f"{current_year}-{cb_month_start.get()}-{int(sp_day_start.get()):02d}"
                end_date = f"{current_year}-{cb_month_end.get()}-{int(sp_day_end.get()):02d}"

                try:
                    query = f"""INSERT INTO prestamo (cedula_estudiante, cedula_docente, {item_fk_column}, fecha_prestamo, fecha_limite_prestamo, estado) VALUES (%s, %s, %s, %s, %s, 'Prestado')"""
                    cursor.execute(query, (student_id, teacher_id, int(item_id), start_date, end_date))

                    cursor.execute(f"UPDATE {table_name} SET {available_col} = 0 WHERE {id_col} = %s", (int(item_id),))
                    conn.commit()

                    messagebox.showinfo("Éxito", "Préstamo registrado.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            ttk.Button(form, text="Registrar Préstamo", bootstyle="success", command=register_loan).pack(anchor="w", pady=15)

        elif self.current_action == "Modificar":
            ttk.Label(self.content_area, text="Devolución / Liberación de recurso prestado:", bootstyle="inverse-light").pack(anchor="w")

            try:
                cursor.execute(f"SELECT id_prestamo, {item_fk_column} FROM prestamo WHERE {item_fk_column} IS NOT NULL AND estado = 'Prestado'")
                borrowed_items = [f"{r[0]} - Recurso ID: {r[1]}" for r in cursor.fetchall()]
            except Exception:
                borrowed_items = []

            cb_return = ttk.Combobox(self.content_area, values=borrowed_items, state="readonly", width=40)
            cb_return.pack(anchor="w", pady=10)

            def release_loan():
                selection = cb_return.get()
                if not selection:
                    return
                loan_id = selection.split(" - ")[0]
                
                try:
                    cursor.execute(f"SELECT {item_fk_column} FROM prestamo WHERE id_prestamo = %s", (loan_id,))
                    item_id = cursor.fetchone()[0]

                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    cursor.execute("UPDATE prestamo SET estado = 'Devuelto', fecha_devolucion = %s WHERE id_prestamo = %s", (today, loan_id))
                    
                    cursor.execute(f"UPDATE {table_name} SET {available_col} = 1 WHERE {id_col} = %s", (item_id,))
                    conn.commit()

                    messagebox.showinfo("Éxito", "Recurso devuelto correctamente.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            ttk.Button(self.content_area, text="Concluir Préstamo (Devolución)", bootstyle="danger", command=release_loan).pack(anchor="w")

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            try:
                query = f"SELECT id_prestamo, {item_fk_column}, cedula_estudiante, cedula_docente, fecha_prestamo, fecha_limite_prestamo, estado FROM prestamo WHERE {item_fk_column} IS NOT NULL"
                cursor.execute(query)
                for r in cursor.fetchall():
                    ttk.Label(scroll, text=f"Préstamo ID: {r[0]} | Recurso ID: {r[1]} | Estudiante: {r[2]} | Docente: {r[3]} | Desde: {r[4]} | Hasta: {r[5]} | Estado: {r[6]}", font=("Courier", 10)).pack(anchor="w", pady=4)
            except Exception as ex:
                print(ex)


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
        if self.current_screen:
            self.current_screen.destroy()
        self.current_screen = LoginScreen(self, on_login=self.load_admin_screen)
        self.current_screen.pack(expand=True, fill="both")

    def load_admin_screen(self):
        if self.current_screen:
            self.current_screen.destroy()
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
        except NameError:
            pass