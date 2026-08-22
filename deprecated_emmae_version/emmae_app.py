import customtkinter
from customtkinter import *
from tkinter import messagebox

# Placeholder module mock-ups based on user file requirements
from modules import db_con as DB_con
from modules import user_management as User_Manager

conn = DB_con.connect_to_db()
cursor = conn.cursor()

set_appearance_mode("light")
set_default_color_theme("blue")

class LoginScreen(CTkFrame):
    def __init__(self, master, on_login):
        super().__init__(master)

        self.on_login = on_login

        welcome_label = CTkLabel(
            self,
            text="Bienvenido!",
            fg_color="transparent"
        )
        welcome_label.grid(
            row=0,
            column=0,
            padx=0,
            pady=10,
            columnspan=2
        )

        login_label = CTkLabel(
            self,
            text="Inicie sesion en su cuenta",
            fg_color="transparent"
        )
        login_label.grid(
            row=1,
            column=0,
            padx=0,
            pady=10,
            columnspan=2
        )

        self.uid_textbox = CTkEntry(master=self, height=30, placeholder_text="Cedula")
        self.uid_textbox.grid(row=2, column=0, pady=5)

        self.textbox = CTkEntry(master=self, height=30, placeholder_text="Contrasena", show="*")
        self.textbox.grid(row=3, column=0, pady=5)

        self.login_button = CTkButton(
            self,
            text="Iniciar Sesion",
            command=lambda: self.check_credentials(self.uid_textbox.get(), self.textbox.get()),
        )
        self.login_button.grid(
            row=4,
            column=0,
            padx=20,
            pady=10,
            columnspan=2
        )

        self.forgot_pass_button = CTkButton(
            self,
            text="Olvide mi contrasena",
            fg_color="transparent",
            text_color="gray",
            command=lambda: messagebox.showinfo("EMMAE APP", "Comuniquese con el administrador del sistema para cambiar su contrasena")
        )
        self.forgot_pass_button.grid(
            row=5,
            column=0,
            padx=20,
            pady=10,
            columnspan=2
        )

    def check_credentials(self, id: str, pswd: str):
        try:
            if User_Manager.login(int(id), pswd):
                self.on_login()
            else:
                messagebox.showerror("EMMAE APP - Error", "Datos Incorrectos")
        except ValueError:
            messagebox.showerror("EMMAE APP - Error", "No ingrese letras en el campo de Cedula")


class AdminPanel(CTkFrame):
    def __init__(self, master, on_logout, show_profesor_form, show_estudiante_form, show_instrumentos_form, show_mda_form, show_salones_form):
        super().__init__(master, fg_color="transparent") 

        self.on_logout = on_logout

        for i in range(1, 8):
            self.grid_columnconfigure(i, weight=1)

        self.btn_profesor = CTkButton(
            self, text="Profesor", height=40, font=("Arial", 13, "bold"),
            command=show_profesor_form
        )
        self.btn_profesor.grid(row=0, column=1, padx=5, pady=15, sticky="ew")

        self.btn_estudiante = CTkButton(
            self, text="Estudiante", height=40, font=("Arial", 13, "bold"),
            command=show_estudiante_form
        )
        self.btn_estudiante.grid(row=0, column=2, padx=5, pady=15, sticky="ew")

        self.btn_instrumentos = CTkButton(
            self, text="Instrumentos", height=40, font=("Arial", 13, "bold"),
            command=show_instrumentos_form
        )
        self.btn_instrumentos.grid(row=0, column=3, padx=5, pady=15, sticky="ew")

        self.btn_mda = CTkButton(
            self, text="M.D.A", height=40, font=("Arial", 13, "bold"),
            command=show_mda_form
        )
        self.btn_mda.grid(row=0, column=4, padx=5, pady=15, sticky="ew")

        self.btn_salones = CTkButton(
            self, text="Salones", height=40, font=("Arial", 13, "bold"),
            command=show_salones_form
        )
        self.btn_salones.grid(row=0, column=6, padx=5, pady=15, sticky="ew")

        self.btn_logout = CTkButton(
            self, 
            text="Logout", 
            command=on_logout, 
            height=40,
            fg_color="#A30000", 
            hover_color="#7A0000",
            font=("Arial", 13, "bold")
        )
        self.btn_logout.grid(row=0, column=7, padx=(20, 5), pady=15, sticky="ew")


class DB_options(CTkFrame):
    def __init__(self, master, on_agregar_click):
        super().__init__(master, corner_radius=10)
        
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.btn_agregar = CTkButton(
            self,
            text="Agregar",
            command=on_agregar_click,
            height=45,
            font=("Arial", 12, "bold")
        )
        self.btn_agregar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.btn_modificar = CTkButton(
            self,
            text="Eliminar",
            height=45,
            state="disabled",
            font=("Arial", 12, "bold")
        )
        self.btn_modificar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_eliminar = CTkButton(
            self,
            text="Guardar",
            height=45,
            state="disabled",
            font=("Arial", 12, "bold")
        )
        self.btn_eliminar.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")


class DisplayDB(CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
        self.form_container = CTkFrame(self, fg_color="transparent")
        self.form_container.place(relx=0.5, rely=0.5, anchor="center")

    def clear_form(self):
        for widget in self.form_container.winfo_children():
            widget.destroy()

    def show_profesor_fields(self):
        self.clear_form()
        
        lbl_name = CTkLabel(self.form_container, text="Nombre:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_name.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.ent_name = CTkEntry(self.form_container, width=220, height=32)
        self.ent_name.grid(row=0, column=1, padx=10, pady=8)

        lbl_surname = CTkLabel(self.form_container, text="Apellido:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_surname.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_surname = CTkEntry(self.form_container, width=220, height=32)
        self.ent_surname.grid(row=1, column=1, padx=10, pady=8)

        lbl_id = CTkLabel(self.form_container, text="Cedula:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id.grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.ent_id = CTkEntry(self.form_container, width=220, height=32)
        self.ent_id.grid(row=2, column=1, padx=10, pady=8)

        lbl_especialidad = CTkLabel(self.form_container, text="Especialidad:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_especialidad.grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.ent_especialidad_doc = CTkEntry(self.form_container, width=220, height=32)
        self.ent_especialidad_doc.grid(row=3, column=1, padx=10, pady=8)

        self.chk_admin = CTkCheckBox(self.form_container, text="es administrador", text_color="#000000", font=("Arial", 12, "bold"))
        self.chk_admin.grid(row=4, column=0, columnspan=2, padx=10, pady=12, sticky="w")

    def show_estudiante_fields(self):
        self.clear_form()

        lbl_name = CTkLabel(self.form_container, text="Nombre:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_name.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.ent_name = CTkEntry(self.form_container, width=220, height=32)
        self.ent_name.grid(row=0, column=1, padx=10, pady=8)

        lbl_surname = CTkLabel(self.form_container, text="Apellido:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_surname.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_surname = CTkEntry(self.form_container, width=220, height=32)
        self.ent_surname.grid(row=1, column=1, padx=10, pady=8)

        lbl_id = CTkLabel(self.form_container, text="Cedula:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id.grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.ent_id = CTkEntry(self.form_container, width=220, height=32)
        self.ent_id.grid(row=2, column=1, padx=10, pady=8)

        lbl_instrumento = CTkLabel(self.form_container, text="Instrumento:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_instrumento.grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.ent_instrumento = CTkEntry(self.form_container, width=220, height=32)
        self.ent_instrumento.grid(row=3, column=1, padx=10, pady=8)

        self.chk_piano = CTkCheckBox(self.form_container, text="Piano Complementario", text_color="#000000", font=("Arial", 12, "bold"))
        self.chk_piano.grid(row=4, column=0, columnspan=2, padx=10, pady=12, sticky="w")

    def show_instrumentos_fields(self):
        self.clear_form()

        lbl_tipo = CTkLabel(self.form_container, text="Tipo Instrumento:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_tipo.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.ent_tipo_instrumento = CTkEntry(self.form_container, width=220, height=32)
        self.ent_tipo_instrumento.grid(row=0, column=1, padx=10, pady=8)

        lbl_estado = CTkLabel(self.form_container, text="Estado:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_estado.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_estado_instrumento = CTkEntry(self.form_container, width=220, height=32)
        self.ent_estado_instrumento.grid(row=1, column=1, padx=10, pady=8)

        lbl_id_est = CTkLabel(self.form_container, text="ID Estudiante:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id_est.grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.ent_id_estudiante = CTkEntry(self.form_container, width=220, height=32)
        self.ent_id_estudiante.grid(row=2, column=1, padx=10, pady=8)

        lbl_id_doc = CTkLabel(self.form_container, text="ID Docente:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id_doc.grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.ent_id_docente = CTkEntry(self.form_container, width=220, height=32)
        self.ent_id_docente.grid(row=3, column=1, padx=10, pady=8)

        self.chk_prestamo = CTkCheckBox(self.form_container, text="Instrumento en Prestamo", text_color="#000000", font=("Arial", 12, "bold"))
        self.chk_prestamo.grid(row=4, column=0, columnspan=2, padx=10, pady=12, sticky="w")

    def show_mda_fields(self):
        self.clear_form()

        lbl_tipo = CTkLabel(self.form_container, text="Tipo Material:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_tipo.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.ent_tipo_material = CTkEntry(self.form_container, width=220, height=32)
        self.ent_tipo_material.grid(row=0, column=1, padx=10, pady=8)

        lbl_estado = CTkLabel(self.form_container, text="Estado Material:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_estado.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_estado_material = CTkEntry(self.form_container, width=220, height=32)
        self.ent_estado_material.grid(row=1, column=1, padx=10, pady=8)

        lbl_id_est = CTkLabel(self.form_container, text="ID Estudiante:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id_est.grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.ent_id_estudiante_mda = CTkEntry(self.form_container, width=220, height=32)
        self.ent_id_estudiante_mda.grid(row=2, column=1, padx=10, pady=8)

        lbl_id_doc = CTkLabel(self.form_container, text="ID Docente:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id_doc.grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.ent_id_docente_mda = CTkEntry(self.form_container, width=220, height=32)
        self.ent_id_docente_mda.grid(row=3, column=1, padx=10, pady=8)

        self.chk_prestamo_mda = CTkCheckBox(self.form_container, text="Material en Prestamo", text_color="#000000", font=("Arial", 12, "bold"))
        self.chk_prestamo_mda.grid(row=4, column=0, columnspan=2, padx=10, pady=12, sticky="w")

    def show_salones_fields(self):
        self.clear_form()

        lbl_id_ocupante = CTkLabel(self.form_container, text="ID Estudiante Ocupante:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id_ocupante.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.ent_id_ocupante = CTkEntry(self.form_container, width=220, height=32)
        self.ent_id_ocupante.grid(row=0, column=1, padx=10, pady=8)

        lbl_especialidad = CTkLabel(self.form_container, text="Especialidad Docente:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_especialidad.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.ent_especialidad = CTkEntry(self.form_container, width=220, height=32)
        self.ent_especialidad.grid(row=1, column=1, padx=10, pady=8)

        self.chk_disponible = CTkCheckBox(self.form_container, text="Disponible / Libre", text_color="#000000", font=("Arial", 12, "bold"))
        self.chk_disponible.grid(row=2, column=0, columnspan=2, padx=10, pady=6, sticky="w")

        self.chk_piano_salon = CTkCheckBox(self.form_container, text="Tiene Piano", text_color="#000000", font=("Arial", 12, "bold"))
        self.chk_piano_salon.grid(row=3, column=0, columnspan=2, padx=10, pady=12, sticky="w")


class UpdateDataScreen(CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(0, weight=1)

        # Track which context view is currently rendering
        self.current_view = "profesor"

        self.db_display = DisplayDB(self)
        self.db_display.grid(row=1, column=1, padx=(10, 15), pady=15, sticky="nsew")
        self.db_display.show_profesor_fields()

        admin_panel = AdminPanel(
            self, 
            on_logout, 
            show_profesor_form=lambda: self.switch_view("profesor"), 
            show_estudiante_form=lambda: self.switch_view("estudiante"),
            show_instrumentos_form=lambda: self.switch_view("instrumentos"),
            show_mda_form=lambda: self.switch_view("mda"),
            show_salones_form=lambda: self.switch_view("salones")
        )
        admin_panel.grid(row=0, column=0, columnspan=2, padx=15, pady=(5, 0), sticky="ew")

        db_options = DB_options(self, on_agregar_click=self.add_active_record)
        db_options.grid(row=1, column=0, padx=(15, 10), pady=15, sticky="nsew")

    def switch_view(self, view_name):
        self.current_view = view_name
        if view_name == "profesor":
            self.db_display.show_profesor_fields()
        elif view_name == "estudiante":
            self.db_display.show_estudiante_fields()
        elif view_name == "instrumentos":
            self.db_display.show_instrumentos_fields()
        elif view_name == "mda":
            self.db_display.show_mda_fields()
        elif view_name == "salones":
            self.db_display.show_salones_fields()

    def add_active_record(self):
        try:
            if self.current_view == "profesor":
                id_val = int(self.db_display.ent_id.get())
                name_val = self.db_display.ent_name.get()
                surname_val = self.db_display.ent_surname.get()
                spec_val = self.db_display.ent_especialidad_doc.get()
                admin_val = bool(self.db_display.chk_admin.get())
                
                User_Manager.add_teacher(id_val, name_val, surname_val, admin_val, spec_val, conn, cursor)
                messagebox.showinfo("EMMAE DB", "Docente agregado exitosamente!")

            elif self.current_view == "estudiante":
                id_val = int(self.db_display.ent_id.get())
                name_val = self.db_display.ent_name.get()
                surname_val = self.db_display.ent_surname.get()
                inst_val = self.db_display.ent_instrumento.get()
                piano_val = bool(self.db_display.chk_piano.get())
                
                User_Manager.add_student(id_val, name_val, surname_val, inst_val, piano_val, conn, cursor)
                messagebox.showinfo("EMMAE DB", "Estudiante agregado exitosamente!")

            elif self.current_view == "instrumentos":
                tipo = self.db_display.ent_tipo_instrumento.get()
                estado = self.db_display.ent_estado_instrumento.get()
                id_est = self.db_display.ent_id_estudiante.get()
                id_doc = self.db_display.ent_id_docente.get()
                prestamo = int(self.db_display.chk_prestamo.get())
                
                # Handling empty input references gracefully to matching database definitions
                id_est = int(id_est) if id_est.strip() else None
                id_doc = int(id_doc) if id_doc.strip() else None

                User_Manager.add_instrument(tipo, prestamo, estado, id_est, id_doc, conn, cursor)
                messagebox.showinfo("EMMAE DB", "Instrumento agregado exitosamente!")

            elif self.current_view == "mda":
                tipo = self.db_display.ent_tipo_material.get()
                estado = self.db_display.ent_estado_material.get()
                id_est = self.db_display.ent_id_estudiante_mda.get()
                id_doc = self.db_display.ent_id_docente_mda.get()
                prestamo = "1" if self.db_display.chk_prestamo_mda.get() else "0"

                id_est = int(id_est) if id_est.strip() else None
                id_doc = int(id_doc) if id_doc.strip() else None

                User_Manager.add_mda(tipo, prestamo, estado, id_est, id_doc, conn, cursor)
                messagebox.showinfo("EMMAE DB", "Material de apoyo agregado exitosamente!")

            elif self.current_view == "salones":
                # Writing missing pipeline directly inside our safe context block
                id_est_ocupante = self.db_display.ent_id_ocupante.get()
                spec_docente = self.db_display.ent_especialidad.get()
                disponible = bool(self.db_display.chk_disponible.get())
                tiene_piano = bool(self.db_display.chk_piano_salon.get())

                id_est_ocupante = int(id_est_ocupante) if id_est_ocupante.strip() else None
                
                salon_query = """
                INSERT INTO salones (salon_ocupado, tiene_piano, estado, id_estudiante_ocupante, especialidad_docente)
                VALUES (%s, %s, %s, %s, %s)
                """
                estado_str = "Disponible" if disponible else "Ocupado"
                cursor.execute(salon_query, (not disponible, tiene_piano, estado_str, id_est_ocupante, spec_docente))
                conn.commit()
                messagebox.showinfo("EMMAE DB", "Salon registrado exitosamente!")

        except ValueError as e:
            messagebox.showerror("Error de Entrada", "Verifique los datos ingresados. Los IDs y Cedulas deben ser numéricos.")
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo guardar el registro:\n{str(e)}")


class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("EMMAE - Menu de Administrador v2.0")
        self.geometry("900x550") # Significantly increased canvas sizing for full clarity

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_screen = None
        self.load_login_screen()
    
    def load_login_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()

        self.current_screen = LoginScreen(self, on_login=self.load_admin_screen)
        self.current_screen.grid(row=0, column=0, padx=0, pady=0)

    def load_admin_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()

        self.current_screen = UpdateDataScreen(self, on_logout=self.load_login_screen)
        self.current_screen.pack(fill="both", expand=True, padx=10, pady=10)


if __name__ == "__main__":
    app = App()
    try:
        app.mainloop()
    finally:
        cursor.close()
        conn.close()