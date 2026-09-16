import datetime
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

from modules import db_manager as db_q
from modules import validator as validator

INSTRUMENTS = ["Piano", "Violin", "Viola", "Chelo", "Bajo", "Guitarra", "Cuatro", "Trompeta", "Trombon", "Percusion", "Flauta Dulce", "Flauta Transversa"]
STUDENT_INSTRUMENTS = INSTRUMENTS + ["Canto"]
MDA_ITEMS = ["Pupitre", "Silla", "Atril", "Libro"]

validator.check_service_status("MySQL80")    

try:
    conn = db_q.connect_to_db()
    cursor = conn.cursor()
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit(1)

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
            if db_q.login(int(id_str), password):
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
                label_text="Instrumento", dropdown_func=db_q.get_instruments_dropdown, items_source=INSTRUMENTS, allow_custom_id=True, has_availability=True, avail_mod_only=True
            ),
            "m.d.a": lambda: self.render_mda_operations(),
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
            cb_specialty = ttk.Combobox(form, values=INSTRUMENTS, state="readonly", width=38)
            cb_specialty.current(0)
            cb_specialty.pack(anchor="w", pady=(0, 10))

            var_is_admin = tk.BooleanVar(value=False)
            admin_pass_container = ttk.Frame(form)
            
            ttk.Label(admin_pass_container, text="Contraseña del Administrador:", bootstyle="inverse-light").pack(anchor="w", pady=(2, 2))
            entry_admin_pass = ttk.Entry(admin_pass_container, width=40, show="*")
            entry_admin_pass.pack(anchor="w", pady=(0, 5))

            def toggle_admin_pass():
                if var_is_admin.get():
                    admin_pass_container.pack(after=chk_admin, anchor="w", pady=5, fill="x")
                else:
                    entry_admin_pass.delete(0, tk.END)
                    admin_pass_container.pack_forget()

            chk_admin = ttk.Checkbutton(
                form, text="Administrador", variable=var_is_admin, 
                bootstyle="square-toggle", command=toggle_admin_pass
            )
            chk_admin.pack(anchor="w", pady=5)

            entry_email = self.create_labeled_entry(form, "Correo Electrónico:")
            cb_prefix, entry_phone_rest = self.create_phone_input(form, validator.validate_phone_rest)

            btn_save = ttk.Button(form, text=("Modificar" if is_mod else "Guardar Registro"), bootstyle=("primary" if is_mod else "success"))

            if is_mod:
                def load_teacher_data(event):
                    selected = cb_search.get()
                    if selected:
                        self.selected_id = selected.split(" - ")[0]
                        cursor.execute("SELECT nombre_docente, apellido_docente, especialidad_primaria, correo_docente, telefono_docente FROM docente WHERE cedula_docente = %s", (self.selected_id,))
                        row = cursor.fetchone()
                        if row:
                            entry_first_name.delete(0, tk.END); entry_first_name.insert(0, row[0])
                            entry_last_name.delete(0, tk.END); entry_last_name.insert(0, row[1])
                            cb_specialty.set(row[2])
                            entry_email.delete(0, tk.END); entry_email.insert(0, row[3])
                            
                            phone = row[4] or ""
                            valid_prefixes = ["0424", "0414", "0276", "0416", "0426", "0212", "0412"]
                            if len(phone) >= 4 and phone[:4] in valid_prefixes:
                                cb_prefix.set(phone[:4])
                                entry_phone_rest.delete(0, tk.END); entry_phone_rest.insert(0, phone[4:])
                            else:
                                cb_prefix.current(0)
                                entry_phone_rest.delete(0, tk.END); entry_phone_rest.insert(0, phone)

                            if db_q.check_is_admin(self.selected_id):
                                var_is_admin.set(True)
                                admin_pass_container.pack(after=chk_admin, anchor="w", pady=5, fill="x")
                                entry_admin_pass.delete(0, tk.END); entry_admin_pass.insert(0, db_q.get_admin_password(self.selected_id))
                            else:
                                var_is_admin.set(False)
                                entry_admin_pass.delete(0, tk.END)
                                admin_pass_container.pack_forget()

                cb_search.bind("<<ComboboxSelected>>", load_teacher_data)

            def save_teacher():
                teacher_id = self.selected_id if is_mod else entry_id.get().strip()
                first_name = entry_first_name.get().strip()
                last_name = entry_last_name.get().strip()
                specialty = cb_specialty.get()
                email = entry_email.get().strip()
                phone_digits = entry_phone_rest.get().strip()
                phone = f"{cb_prefix.get()}{phone_digits}"
                is_admin = var_is_admin.get()
                admin_pass = entry_admin_pass.get().strip()

                if not teacher_id.isdigit():
                    return messagebox.showerror("Error de Validación", "La cédula debe ser un valor numérico.")
                if not first_name or not last_name:
                    return messagebox.showerror("Error de Validación", "El nombre y apellido son obligatorios.")
                if not validator.validate_name_text(first_name) or not validator.validate_name_text(last_name):
                    return messagebox.showerror("Error de Validación", "Los nombres y apellidos no deben contener números.")
                if is_admin and not admin_pass:
                    return messagebox.showerror("Error de Validación", "La contraseña es obligatoria para el administrador.")
                if not validator.validate_email(email):
                    return messagebox.showerror("Error de Validación", "El formato del correo electrónico es inválido.")
                if len(phone_digits) < 7:
                    return messagebox.showerror("Error de Validación", "El número de teléfono tiene caracteres insuficientes.")

                try:
                    if is_mod:
                        query = """UPDATE docente SET nombre_docente=%s, apellido_docente=%s, especialidad_primaria=%s, correo_docente=%s, telefono_docente=%s WHERE cedula_docente=%s"""
                        cursor.execute(query, (first_name, last_name, specialty, email, phone, teacher_id))
                    else:
                        query = """INSERT INTO docente (cedula_docente, nombre_docente, apellido_docente, especialidad_primaria, correo_docente, telefono_docente) VALUES (%s, %s, %s, %s, %s, %s)"""
                        cursor.execute(query, (int(teacher_id), first_name, last_name, specialty, email, phone))

                    conn.commit()

                    if is_admin:
                        db_q.save_admin_json(teacher_id, admin_pass)
                    else:
                        db_q.delete_admin_json(teacher_id)

                    messagebox.showinfo("Éxito", f"Docente {'actualizado' if is_mod else 'registrado'} correctamente.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Database Error", f"Error al guardar: {ex}")

            btn_save.config(command=save_teacher)
            btn_save.pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            entry_filter = self.create_labeled_entry(self.content_area, "Filtrar Docente:")
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)

            def search_teachers(*args):
                for w in scroll.winfo_children():
                    w.destroy()
                term = f"%{entry_filter.get().strip()}%"
                try:
                    cursor.execute("SELECT cedula_docente, nombre_docente, apellido_docente, telefono_docente, correo_docente, especialidad_primaria FROM docente WHERE nombre_docente LIKE %s OR cedula_docente LIKE %s", (term, term))
                    for r in cursor.fetchall():
                        ttk.Label(scroll, text=f"Cédula: {r[0]} | Docente: {r[1]} {r[2]} | Teléfono: {r[3]} | Email: {r[4]} | Especialidad: {r[5]}", font=("Courier", 10)).pack(anchor="w", padx=10, pady=4)
                except Exception as ex:
                    print(ex)

            entry_filter.bind("<KeyRelease>", search_teachers)
            search_teachers()

    def render_student_operations(self):
        if self.current_action in ["Añadir", "Modificar"]:
            is_mod = self.current_action == "Modificar"
            
            if is_mod:
                ttk.Label(self.content_area, text="Seleccione Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                cb_search = ttk.Combobox(self.content_area, values=db_q.get_students_dropdown(cursor), state="readonly", width=40)
                cb_search.pack(anchor="w", pady=(0, 15))

            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            entry_first_name = self.create_labeled_entry(form, "Nombre Estudiante:")
            entry_last_name = self.create_labeled_entry(form, "Apellido Estudiante:")
            entry_age = self.create_labeled_entry(form, "Edad:", validate_type=validator.validate_simple_number)

            var_has_id = tk.BooleanVar(value=True)
            id_container = ttk.Frame(form)
            entry_id = self.create_labeled_entry(id_container, "Cédula Estudiante:")

            def update_id_state():
                try:
                    age_val = int(entry_age.get().strip()) if entry_age.get().strip().isdigit() else 0
                except ValueError:
                    age_val = 0

                if age_val < 9 or age_val > 120:
                    var_has_id.set(False)
                    id_container.pack_forget()
                else:
                    if var_has_id.get():
                        id_container.pack(after=chk_id, anchor="w", fill="x", pady=5)
                    else:
                        id_container.pack_forget()

            def toggle_id_checkbox():
                if var_has_id.get():
                    id_container.pack(after=chk_id, anchor="w", fill="x", pady=5)
                else:
                    id_container.pack_forget()

            chk_id = ttk.Checkbutton(form, text="Tiene Cédula", variable=var_has_id, bootstyle="square-toggle", command=toggle_id_checkbox)
            chk_id.pack(anchor="w", pady=5)
            id_container.pack(after=chk_id, anchor="w", fill="x", pady=5)

            entry_age.bind("<KeyRelease>", lambda e: update_id_state())

            ttk.Label(form, text="Instrumento Principal:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            cb_instrument = ttk.Combobox(form, values=STUDENT_INSTRUMENTS, state="readonly", width=38)
            cb_instrument.current(0)
            cb_instrument.pack(anchor="w", pady=(0, 10))

            var_piano = tk.BooleanVar(value=False)
            ttk.Checkbutton(form, text="Piano Complementario", variable=var_piano, bootstyle="square-toggle").pack(anchor="w", pady=5)

            entry_year = self.create_labeled_entry(form, "Año Cursante:")
            entry_email = self.create_labeled_entry(form, "Correo Estudiante:")
            cb_prefix, entry_phone_rest = self.create_phone_input(form, validator.validate_phone_rest)
            entry_rep_phone = self.create_labeled_entry(form, "Teléfono Representante (Opcional):")
            entry_rep_email = self.create_labeled_entry(form, "Correo Representante (Opcional):")

            if is_mod:
                def load_student_data(event):
                    selected = cb_search.get()
                    if selected:
                        self.selected_id = selected.split(" - ")[0]
                        cursor.execute("SELECT nombre_estudiante, apellido_estudiante, instrumento_estudiante, tiene_piano_complementario, ano_cursante, telefono_estudiante, correo_estudiante, telefono_representante, correo_representante FROM estudiante WHERE cedula_estudiante=%s", (self.selected_id,))
                        row = cursor.fetchone()
                        if row:
                            entry_first_name.delete(0, tk.END); entry_first_name.insert(0, row[0])
                            entry_last_name.delete(0, tk.END); entry_last_name.insert(0, row[1])
                            cb_instrument.set(row[2])
                            var_piano.set(bool(row[3]))
                            entry_year.delete(0, tk.END); entry_year.insert(0, row[4])
                            
                            phone = row[5] or ""
                            valid_prefixes = ["0424", "0414", "0276", "0416", "0426", "0212", "0412"]
                            if len(phone) >= 4 and phone[:4] in valid_prefixes:
                                cb_prefix.set(phone[:4])
                                entry_phone_rest.delete(0, tk.END); entry_phone_rest.insert(0, phone[4:])
                            else:
                                cb_prefix.current(0)
                                entry_phone_rest.delete(0, tk.END); entry_phone_rest.insert(0, phone)

                            entry_email.delete(0, tk.END); entry_email.insert(0, row[6])
                            entry_rep_phone.delete(0, tk.END); entry_rep_phone.insert(0, row[7] or "")
                            entry_rep_email.delete(0, tk.END); entry_rep_email.insert(0, row[8] or "")
                            
                            entry_age.delete(0, tk.END)
                            entry_age.insert(0, "10")
                            var_has_id.set(True)
                            id_container.pack(after=chk_id, anchor="w", fill="x", pady=5)
                            entry_id.delete(0, tk.END); entry_id.insert(0, str(self.selected_id))

                cb_search.bind("<<ComboboxSelected>>", load_student_data)

            def save_student():
                first_name = entry_first_name.get().strip()
                last_name = entry_last_name.get().strip()
                age_str = entry_age.get().strip()
                email = entry_email.get().strip()
                phone_digits = entry_phone_rest.get().strip()

                if not first_name or not last_name:
                    return messagebox.showerror("Error", "Nombre y apellido son obligatorios.")
                if not validator.validate_name_text(first_name) or not validator.validate_name_text(last_name):
                    return messagebox.showerror("Error", "Los nombres y apellidos no deben contener números.")
                if not is_mod and (not age_str.isdigit() or int(age_str) <= 0 or int(age_str) > 120):
                    return messagebox.showerror("Error", "Por favor ingrese una edad válida y real (positiva).")
                if not validator.validate_email(email):
                    return messagebox.showerror("Error", "El correo electrónico del estudiante no es válido.")
                if len(phone_digits) < 7:
                    return messagebox.showerror("Error", "El número de teléfono tiene caracteres insuficientes.")

                if is_mod:
                    student_id = self.selected_id
                else:
                    if var_has_id.get():
                        student_id = entry_id.get().strip()
                        if not student_id.isdigit():
                            return messagebox.showerror("Error", "La cédula debe ser numérica.")
                    else:
                        try:
                            cursor.execute("SELECT COUNT(*) FROM estudiante WHERE cedula_estudiante LIKE 'E%'")
                            count = cursor.fetchone()[0] + 1
                        except Exception:
                            count = 1
                        student_id = f"E{count}"

                try:
                    if is_mod:
                        query = """UPDATE estudiante SET nombre_estudiante=%s, apellido_estudiante=%s, instrumento_estudiante=%s, tiene_piano_complementario=%s, ano_cursante=%s, telefono_estudiante=%s, correo_estudiante=%s, telefono_representante=%s, correo_representante=%s WHERE cedula_estudiante=%s"""
                        cursor.execute(query, (first_name, last_name, cb_instrument.get(), var_piano.get(), entry_year.get(), f"{cb_prefix.get()}{entry_phone_rest.get()}", email, entry_rep_phone.get(), entry_rep_email.get(), str(student_id)))
                    else:
                        query = """INSERT INTO estudiante (cedula_estudiante, nombre_estudiante, apellido_estudiante, instrumento_estudiante, tiene_piano_complementario, ano_cursante, telefono_estudiante, correo_estudiante, telefono_representante, correo_representante) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        cursor.execute(query, (str(student_id), first_name, last_name, cb_instrument.get(), var_piano.get(), entry_year.get(), f"{cb_prefix.get()}{entry_phone_rest.get()}", email, entry_rep_phone.get(), entry_rep_email.get()))
                    
                    conn.commit()
                    messagebox.showinfo("Éxito", f"Estudiante con ID: {student_id} guardado correctamente.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            btn_text = "Modificar Estudiante" if is_mod else "Guardar Estudiante"
            btn_style = "primary" if is_mod else "success"
            ttk.Button(form, text=btn_text, bootstyle=btn_style, command=save_student).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            entry_filter = self.create_labeled_entry(self.content_area, "Filtrar por cédula o nombre:")
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)

            def search_students(*args):
                for w in scroll.winfo_children():
                    w.destroy()
                term = f"%{entry_filter.get().strip()}%"
                cursor.execute("SELECT cedula_estudiante, nombre_estudiante, apellido_estudiante, instrumento_estudiante FROM estudiante WHERE nombre_estudiante LIKE %s OR cedula_estudiante LIKE %s", (term, term))
                for r in cursor.fetchall():
                    ttk.Label(scroll, text=f"ID/Cédula: {r[0]} | Estudiante: {r[1]} {r[2]} | Instrumento: {r[3]}", font=("Courier", 10)).pack(anchor="w", padx=10, pady=4)

            entry_filter.bind("<KeyRelease>", search_students)
            search_students()

    def render_mda_operations(self):
        if self.current_action in ["Añadir", "Modificar"]:
            is_mod = self.current_action == "Modificar"

            if is_mod:
                ttk.Label(self.content_area, text="Seleccione Material (MDA) a Modificar:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                cursor.execute("SELECT id_mda, tipo_mda, desc_mda FROM material_de_apoyo")
                mda_rows = cursor.fetchall()
                mda_dropdown_values = []
                for r in mda_rows:
                    mda_id = r[0]
                    tipo = r[1]
                    desc = r[2]
                    if desc and desc.strip():
                        mda_dropdown_values.append(f'{mda_id} - {tipo} "{desc}"')
                    else:
                        mda_dropdown_values.append(f'{mda_id} - {tipo}')

                cb_search = ttk.Combobox(self.content_area, values=mda_dropdown_values, state="readonly", width=40)
                cb_search.pack(anchor="w", pady=(0, 15))

            ttk.Label(self.content_area, text="ID del Material (MDA):", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            entry_id = ttk.Entry(self.content_area, width=38)
            entry_id.pack(anchor="w", pady=(0, 10))

            ttk.Label(self.content_area, text="Tipo de Material (MDA):", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            entry_type = ttk.Combobox(self.content_area, values=MDA_ITEMS, state="readonly", width=38)
            entry_type.current(0)
            entry_type.pack(anchor="w", pady=(0, 10))

            entry_desc = self.create_labeled_entry(self.content_area, "Descripción:")
            entry_status = self.create_labeled_entry(self.content_area, "Estado del Material:")

            show_availability = is_mod
            var_available = tk.BooleanVar(value=True)
            if show_availability:
                ttk.Checkbutton(self.content_area, text="Disponible", variable=var_available, bootstyle="square-toggle").pack(anchor="w", pady=10)

            if is_mod:
                def load_item(event):
                    selected = cb_search.get()
                    if selected:
                        self.selected_id = selected.split(" - ")[0]
                        entry_id.delete(0, tk.END)
                        entry_id.insert(0, str(self.selected_id))
                        
                        cursor.execute("SELECT tipo_mda, desc_mda, estado_mda, mda_disponible FROM material_de_apoyo WHERE id_mda=%s", (self.selected_id,))
                        row = cursor.fetchone()
                        if row:
                            entry_type.set(row[0])
                            entry_desc.delete(0, tk.END)
                            if row[1]:
                                entry_desc.insert(0, row[1])
                            entry_status.delete(0, tk.END)
                            if row[2]:
                                entry_status.insert(0, row[2])
                            var_available.set(bool(row[3]))

                cb_search.bind("<<ComboboxSelected>>", load_item)
            else:
                try:
                    cursor.execute("SELECT MAX(id_mda) FROM material_de_apoyo")
                    res = cursor.fetchone()[0]
                    next_val = (res + 1) if res else 1
                    entry_id.insert(0, str(next_val))
                except Exception:
                    entry_id.insert(0, "1")

            def save_item():
                mat_type = entry_type.get()
                desc_val = entry_desc.get().strip()
                status = entry_status.get().strip()
                available = var_available.get() if show_availability else True
                custom_id = entry_id.get().strip()

                if not custom_id.isdigit():
                    return messagebox.showerror("Error", "El ID debe ser numérico.")
                item_id_val = int(custom_id)

                try:
                    if is_mod:
                        if not self.selected_id:
                            return
                        cursor.execute(
                            "UPDATE material_de_apoyo SET id_mda=%s, desc_mda=%s, tipo_mda=%s, estado_mda=%s, mda_disponible=%s WHERE id_mda=%s", 
                            (item_id_val, desc_val, mat_type, status, available, self.selected_id)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO material_de_apoyo (id_mda, desc_mda, tipo_mda, estado_mda, mda_disponible) VALUES (%s, %s, %s, %s, %s)", 
                            (item_id_val, desc_val, mat_type, status, available)
                        )

                    conn.commit()
                    messagebox.showinfo("Éxito", f"Material (MDA) {'modificado' if is_mod else 'añadido'}.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            btn_text = "Modificar" if is_mod else "Guardar"
            btn_style = "primary" if is_mod else "success"
            ttk.Button(self.content_area, text=btn_text, bootstyle=btn_style, command=save_item).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            cursor.execute("SELECT id_mda, desc_mda, tipo_mda, estado_mda, mda_disponible FROM material_de_apoyo")
            for r in cursor.fetchall():
                desc_str = f' | Desc: "{r[1]}"' if r[1] and r[1].strip() else ""
                ttk.Label(scroll, text=f"ID: {r[0]}{desc_str} | Tipo: {r[2]} | Estado: {r[3]} | ¿Disponible?: {'Sí' if r[4] else 'No'}", font=("Courier", 10)).pack(anchor="w", pady=4)

    def render_generic_resource_operations(self, table, id_col, type_col, status_col, avail_col, label_text, dropdown_func, items_source, allow_custom_id=False, has_availability=True, avail_mod_only=False):
        if self.current_action in ["Añadir", "Modificar"]:
            is_mod = self.current_action == "Modificar"

            if is_mod:
                ttk.Label(self.content_area, text=f"Seleccione {label_text} a Modificar:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                cb_search = ttk.Combobox(self.content_area, values=dropdown_func(cursor), state="readonly", width=40)
                cb_search.pack(anchor="w", pady=(0, 15))

            entry_id = None
            if allow_custom_id:
                ttk.Label(self.content_area, text=f"ID del {label_text}:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
                entry_id = ttk.Entry(self.content_area, width=38)
                entry_id.pack(anchor="w", pady=(0, 10))

            ttk.Label(self.content_area, text=f"Tipo de {label_text}:", bootstyle="inverse-light").pack(anchor="w", pady=(5, 2))
            entry_type = ttk.Combobox(self.content_area, values=items_source, state="readonly", width=38)
            entry_type.current(0)
            entry_type.pack(anchor="w", pady=(0, 10))

            entry_status = self.create_labeled_entry(self.content_area, f"Estado del {label_text}:")

            show_availability = has_availability and (not avail_mod_only or is_mod)
            var_available = tk.BooleanVar(value=True)
            if show_availability:
                ttk.Checkbutton(self.content_area, text="Disponible", variable=var_available, bootstyle="square-toggle").pack(anchor="w", pady=10)

            if is_mod:
                def load_item(event):
                    selected = cb_search.get()
                    if selected:
                        self.selected_id = selected.split(" - ")[0]
                        if entry_id:
                            entry_id.delete(0, tk.END)
                            entry_id.insert(0, str(self.selected_id))
                        
                        query_cols = f"{type_col}, {status_col}"
                        if has_availability:
                            query_cols += f", {avail_col}"
                        cursor.execute(f"SELECT {query_cols} FROM {table} WHERE {id_col}=%s", (self.selected_id,))
                        row = cursor.fetchone()
                        if row:
                            entry_type.set(row[0])
                            entry_status.delete(0, tk.END)
                            if row[1] is not None:
                                entry_status.insert(0, row[1])
                            if has_availability:
                                var_available.set(bool(row[2]))

                cb_search.bind("<<ComboboxSelected>>", load_item)
            elif allow_custom_id and entry_id:
                try:
                    cursor.execute(f"SELECT MAX({id_col}) FROM {table}")
                    res = cursor.fetchone()[0]
                    next_val = (res + 1) if res else 1
                    entry_id.insert(0, str(next_val))
                except Exception:
                    entry_id.insert(0, "1")

            def save_item():
                mat_type = entry_type.get()
                status = entry_status.get().strip()
                available = var_available.get() if show_availability else True
                custom_id = entry_id.get().strip() if entry_id else None

                if allow_custom_id and custom_id:
                    if not custom_id.isdigit():
                        return messagebox.showerror("Error", "El ID debe ser numérico.")
                    item_id_val = int(custom_id)
                else:
                    item_id_val = None

                try:
                    if is_mod:
                        if not self.selected_id:
                            return
                        if has_availability:
                            if allow_custom_id and item_id_val is not None and item_id_val != int(self.selected_id):
                                cursor.execute(f"UPDATE {table} SET {id_col}=%s, {type_col}=%s, {status_col}=%s, {avail_col}=%s WHERE {id_col}=%s", (item_id_val, mat_type, status, available, self.selected_id))
                            else:
                                cursor.execute(f"UPDATE {table} SET {type_col}=%s, {status_col}=%s, {avail_col}=%s WHERE {id_col}=%s", (mat_type, status, available, self.selected_id))
                        else:
                            if allow_custom_id and item_id_val is not None and item_id_val != int(self.selected_id):
                                cursor.execute(f"UPDATE {table} SET {id_col}=%s, {type_col}=%s, {status_col}=%s WHERE {id_col}=%s", (item_id_val, mat_type, status, self.selected_id))
                            else:
                                cursor.execute(f"UPDATE {table} SET {type_col}=%s, {status_col}=%s WHERE {id_col}=%s", (mat_type, status, self.selected_id))
                    else:
                        if has_availability:
                            if allow_custom_id and item_id_val is not None:
                                cursor.execute(f"INSERT INTO {table} ({id_col}, {type_col}, {status_col}, {avail_col}) VALUES (%s, %s, %s, %s)", (item_id_val, mat_type, status, available))
                            else:
                                cursor.execute(f"INSERT INTO {table} ({type_col}, {status_col}, {avail_col}) VALUES (%s, %s, %s)", (mat_type, status, available))
                        else:
                            if allow_custom_id and item_id_val is not None:
                                cursor.execute(f"INSERT INTO {table} ({id_col}, {type_col}, {status_col}) VALUES (%s, %s, %s)", (item_id_val, mat_type, status))
                            else:
                                cursor.execute(f"INSERT INTO {table} ({type_col}, {status_col}) VALUES (%s, %s)", (mat_type, status))

                    conn.commit()
                    messagebox.showinfo("Éxito", f"{label_text} {'modificado' if is_mod else 'añadido'}.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            btn_text = "Modificar" if is_mod else "Guardar"
            btn_style = "primary" if is_mod else "success"
            ttk.Button(self.content_area, text=btn_text, bootstyle=btn_style, command=save_item).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            if has_availability:
                cursor.execute(f"SELECT {id_col}, {type_col}, {status_col}, {avail_col} FROM {table}")
                for r in cursor.fetchall():
                    ttk.Label(scroll, text=f"ID: {r[0]} | Tipo: {r[1]} | Estado: {r[2]} | ¿Disponible?: {'Sí' if r[3] else 'No'}", font=("Courier", 10)).pack(anchor="w", pady=4)
            else:
                cursor.execute(f"SELECT {id_col}, {type_col}, {status_col} FROM {table}")
                for r in cursor.fetchall():
                    ttk.Label(scroll, text=f"ID: {r[0]} | Tipo: {r[1]} | Estado: {r[2]}", font=("Courier", 10)).pack(anchor="w", pady=4)

    def render_classroom_operations(self):
        if self.current_action in ["Añadir", "Modificar"]:
            is_mod = self.current_action == "Modificar"

            if is_mod:
                ttk.Label(self.content_area, text="Seleccione Salón a Modificar:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                cb_search = ttk.Combobox(self.content_area, values=db_q.get_classrooms_dropdown(cursor), state="readonly", width=40)
                cb_search.pack(anchor="w", pady=(0, 15))

            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            id_display_frame = ttk.Frame(form)
            id_display_frame.pack(anchor="w", pady=5, fill="x")
            ttk.Label(id_display_frame, text="Número Identificador:", bootstyle="inverse-light").pack(anchor="w", pady=(2, 2))
            entry_auto_id = ttk.Entry(id_display_frame, width=38, state="readonly")
            entry_auto_id.pack(anchor="w", pady=(0, 5))

            var_cubiculo = tk.BooleanVar(value=False)
            
            def calculate_next_id(*args):
                try:
                    if var_cubiculo.get():
                        cursor.execute("SELECT MAX(id_salon) FROM salon WHERE id_salon >= 1000")
                        res = cursor.fetchone()[0]
                        seq = (res - 1000 + 1) if res and res >= 1000 else 1
                    else:
                        cursor.execute("SELECT MAX(id_salon) FROM salon WHERE id_salon < 1000")
                        res = cursor.fetchone()[0]
                        seq = (res + 1) if res and res < 1000 else 1
                except Exception:
                    seq = 1

                entry_auto_id.config(state="normal")
                entry_auto_id.delete(0, tk.END)
                entry_auto_id.insert(0, str(seq))
                entry_auto_id.config(state="readonly")

            chk_cubiculo = ttk.Checkbutton(
                form, text="Es Cubículo", variable=var_cubiculo, 
                bootstyle="square-toggle", command=calculate_next_id
            )
            chk_cubiculo.pack(anchor="w", pady=5)

            if not is_mod:
                calculate_next_id()

            ttk.Label(form, text="Estado General del Salón:", bootstyle="inverse-light").pack(anchor="w")
            cb_status = ttk.Combobox(form, values=["Ok", "Dañado"], state="readonly", width=38)
            cb_status.current(0)
            cb_status.pack(anchor="w", pady=10)

            var_occupied = tk.BooleanVar(value=False)
            var_available = tk.BooleanVar(value=True)

            if is_mod:
                ttk.Checkbutton(form, text="Salón Ocupado", variable=var_occupied, bootstyle="square-toggle").pack(anchor="w", pady=5)
                ttk.Checkbutton(form, text="Salón Disponible", variable=var_available, bootstyle="square-toggle").pack(anchor="w", pady=5)

            var_piano_salon = tk.BooleanVar(value=True)
            ttk.Checkbutton(form, text="Tiene Piano", variable=var_piano_salon, bootstyle="square-toggle").pack(anchor="w", pady=5)

            ttk.Label(form, text="ID Piano (Opcional):", bootstyle="inverse-light").pack(anchor="w")
            cb_piano = ttk.Combobox(form, values=["Ninguno"] + db_q.get_instruments_dropdown(cursor), state="readonly", width=38)
            cb_piano.current(0)
            cb_piano.pack(anchor="w", pady=10)

            if is_mod:
                def load_classroom(event):
                    selected = cb_search.get()
                    if selected:
                        self.selected_id = selected.split(" - ")[0]
                        cursor.execute("SELECT estado_salon, salon_ocupado, salon_disponible, id_piano, es_cubiculo, tiene_piano FROM salon WHERE id_salon=%s", (self.selected_id,))
                        row = cursor.fetchone()
                        if row:
                            cb_status.set(row[0])
                            var_occupied.set(bool(row[1]))
                            var_available.set(bool(row[2]))
                            is_cub = bool(row[4])
                            var_cubiculo.set(is_cub)
                            var_piano_salon.set(bool(row[5]))
                            if row[3]:
                                cb_piano.set(str(row[3]))
                            
                            seq_val = (int(self.selected_id) - 1000) if is_cub and int(self.selected_id) >= 1000 else int(self.selected_id)
                            entry_auto_id.config(state="normal")
                            entry_auto_id.delete(0, tk.END)
                            entry_auto_id.insert(0, str(seq_val))
                            entry_auto_id.config(state="readonly")

                cb_search.bind("<<ComboboxSelected>>", load_classroom)

            def save_classroom():
                piano_val = cb_piano.get().split(" - ")[0] if cb_piano.get() != "Ninguno" else None
                seq_val = int(entry_auto_id.get())
                
                if var_cubiculo.get():
                    salon_id = 1000 + seq_val
                else:
                    salon_id = seq_val

                try:
                    if is_mod:
                        cursor.execute(
                            "UPDATE salon SET id_salon=%s, estado_salon=%s, salon_ocupado=%s, salon_disponible=%s, id_piano=%s, es_cubiculo=%s, tiene_piano=%s WHERE id_salon=%s", 
                            (salon_id, cb_status.get(), var_occupied.get(), var_available.get(), piano_val, var_cubiculo.get(), var_piano_salon.get(), self.selected_id)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO salon (id_salon, es_cubiculo, salon_ocupado, tiene_piano, id_piano, estado_salon, salon_disponible) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                            (salon_id, var_cubiculo.get(), False, var_piano_salon.get(), piano_val, cb_status.get(), True)
                        )
                    
                    conn.commit()
                    messagebox.showinfo("Éxito", f"Salón {'modificado' if is_mod else 'añadido'} correctamente.")
                    self.render_form_view()
                except Exception as ex:
                    messagebox.showerror("Error", str(ex))

            btn_text = "Modificar" if is_mod else "Guardar"
            btn_style = "primary" if is_mod else "success"
            ttk.Button(form, text=btn_text, bootstyle=btn_style, command=save_classroom).pack(anchor="w", pady=10)

        elif self.current_action == "Buscar":
            scroll = ScrolledFrame(self.content_area, bootstyle="round")
            scroll.pack(fill="both", expand=True)
            cursor.execute("SELECT id_salon, estado_salon, salon_ocupado, salon_disponible, id_piano, es_cubiculo FROM salon")
            for r in cursor.fetchall():
                is_cub = r[5]
                tipo = "Cubículo" if is_cub else "Salón"
                display_id = (r[0] - 1000) if is_cub and r[0] >= 1000 else r[0]
                ttk.Label(scroll, text=f"{tipo} Nro: {display_id} | Estado: {r[1]} | ¿Ocupado?: {'Sí' if r[2] else 'No'} | ¿Disponible?: {'Sí' if r[3] else 'No'} | Piano ID: {r[4] or 'Ninguno'}", font=("Courier", 10)).pack(anchor="w", pady=4)

    def render_loans_operations(self):
        ttk.Label(
            self.content_area, 
            text=f"{self.current_action} Préstamo - Módulo {self.display_name}", 
            font=("Arial", 16, "bold"), bootstyle="inverse-light"
        ).pack(anchor="w", pady=(0, 15))

        target_map = {
            "instrumentos": ("instrumentos", "id_instrumento", "tipo_instrumento", "instrumento_disponible", "Instrumento"),
            "m.d.a": ("material_de_apoyo", "id_mda", "tipo_mda", "mda_disponible", "Material (MDA)"),
            "salones": ("salon", "id_salon", "id_salon", "salon_disponible", "Salón")
        }

        if self.name not in target_map:
            return

        table_name, id_col, type_col, available_col, label_name = target_map[self.name]
        item_fk_column = id_col

        if self.current_action == "Añadir":
            form = ScrolledFrame(self.content_area, bootstyle="round")
            form.pack(fill="both", expand=True)

            try:
                if self.name == "instrumentos":
                    cursor.execute(f"SELECT {id_col}, {type_col} FROM {table_name} WHERE {available_col} = 1")
                    available_items = [f"{r[1]} - {r[0]}" for r in cursor.fetchall()]
                elif self.name == "m.d.a":
                    cursor.execute("SELECT id_mda, tipo_mda, desc_mda FROM material_de_apoyo WHERE mda_disponible = 1")
                    available_items = []
                    for r in cursor.fetchall():
                        mda_id = r[0]
                        tipo = r[1]
                        desc = r[2]
                        if desc and desc.strip():
                            available_items.append(f'{tipo} "{desc}" (ID: {mda_id})')
                        else:
                            available_items.append(f'{tipo} (ID: {mda_id})')
                elif self.name == "salones":
                    cursor.execute(f"SELECT {id_col}, es_cubiculo FROM {table_name} WHERE {available_col} = 1")
                    available_items = []
                    for r in cursor.fetchall():
                        salon_id = r[0]
                        es_cub = r[1]
                        if es_cub or salon_id >= 1000:
                            cubiculo_num = salon_id - 1000 if salon_id >= 1000 else salon_id
                            available_items.append(f"Cubiculo {cubiculo_num} - {salon_id}")
                        else:
                            available_items.append(f"Salon {salon_id}")
                else:
                    cursor.execute(f"SELECT {id_col} FROM {table_name} WHERE {available_col} = 1")
                    available_items = [str(r[0]) for r in cursor.fetchall()]
            except Exception:
                available_items = []

            ttk.Label(form, text=f"Seleccione {label_name} disponible:", bootstyle="inverse-light").pack(anchor="w", pady=2)
            cb_item = ttk.Combobox(form, values=available_items, state="readonly", width=38)
            cb_item.pack(anchor="w", pady=(0, 10))

            var_is_student_loan = tk.BooleanVar(value=True)
            assign_container = ttk.Frame(form)

            def update_loan_target():
                for w in assign_container.winfo_children():
                    w.destroy()
                if var_is_student_loan.get():
                    ttk.Label(assign_container, text="Asignar a Estudiante:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                    nonlocal cb_target_student
                    cb_target_student = ttk.Combobox(assign_container, values=db_q.get_students_dropdown(cursor), state="readonly", width=38)
                    cb_target_student.pack(anchor="w", pady=(0, 10))
                else:
                    ttk.Label(assign_container, text="Asignar a Docente:", bootstyle="inverse-light").pack(anchor="w", pady=2)
                    nonlocal cb_target_teacher
                    cb_target_teacher = ttk.Combobox(assign_container, values=db_q.get_teachers_dropdown(cursor), state="readonly", width=38)
                    cb_target_teacher.pack(anchor="w", pady=(0, 10))

            cb_target_student = None
            cb_target_teacher = None

            ttk.Checkbutton(
                form, text="Prestamo para Estudiante", variable=var_is_student_loan, 
                bootstyle="square-toggle", command=update_loan_target
            ).pack(anchor="w", pady=5)
            
            assign_container.pack(anchor="w", fill="x", pady=5)
            update_loan_target()

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
                selection_text = cb_item.get()
                if not selection_text:
                    return messagebox.showerror("Error", "Seleccione un recurso.")

                if self.name == "instrumentos" and " - " in selection_text:
                    item_id = selection_text.split(" - ")[-1]
                elif self.name == "m.d.a":
                    item_id = selection_text.split("ID: ")[1].replace(")", "")
                elif self.name == "salones":
                    if " - " in selection_text:
                        item_id = selection_text.split(" - ")[-1]
                    else:
                        item_id = selection_text.replace("Salon ", "")
                else:
                    item_id = selection_text

                student_id = None
                teacher_id = None

                if var_is_student_loan.get():
                    sel = cb_target_student.get()
                    if not sel:
                        return messagebox.showerror("Error", "Seleccione un estudiante.")
                    student_id = sel.split(" - ")[0]
                else:
                    sel = cb_target_teacher.get()
                    if not sel:
                        return messagebox.showerror("Error", "Seleccione un docente.")
                    teacher_id = int(sel.split(" - ")[0])

                current_year = datetime.datetime.now().year
                start_date = f"{current_year}-{cb_month_start.get()}-{int(sp_day_start.get()):02d}"
                end_date = f"{current_year}-{cb_month_end.get()}-{int(sp_day_end.get()):02d}"

                try:
                    query = f"""INSERT INTO prestamo (cedula_estudiante, cedula_docente, {item_fk_column}, fecha_prestamo, fecha_limite_prestamo, estado) VALUES (%s, %s, %s, %s, %s, 'Prestado')"""
                    cursor.execute(query, (student_id, teacher_id, int(item_id), start_date, end_date))

                    cursor.execute(f"UPDATE {table_name} SET {available_col} = 0 WHERE {id_col} = %s", (int(item_id),))
                    if self.name == "salones":
                        cursor.execute("UPDATE salon SET salon_ocupado = 1 WHERE id_salon = %s", (int(item_id),))

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
                    if self.name == "salones":
                        cursor.execute("UPDATE salon SET salon_ocupado = 0 WHERE id_salon = %s", (item_id,))

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
