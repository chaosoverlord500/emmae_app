class AdminPanel(CTkFrame):
    def __init__(self, master, on_logout, show_profesor_form, show_estudiante_form):
        super().__init__(master, fg_color="transparent") 

        self.on_logout = on_logout

        for i in range(1, 9):
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

        self.btn_prestamos = CTkButton(
            self, text="Préstamos", height=40, font=("Arial", 13, "bold")
        )
        self.btn_prestamos.grid(row=0, column=3, padx=5, pady=15, sticky="ew")

        self.btn_instrumentos = CTkButton(
            self, text="Instrumentos", height=40, font=("Arial", 13, "bold")
        )
        self.btn_instrumentos.grid(row=0, column=4, padx=5, pady=15, sticky="ew")

        self.btn_mda = CTkButton(
            self, text="M.D.A", height=40, font=("Arial", 13, "bold")
        )
        self.btn_mda.grid(row=0, column=5, padx=5, pady=15, sticky="ew")

        self.btn_salones = CTkButton(
            self, text="Salones", height=40, font=("Arial", 13, "bold")
        )
        self.btn_salones.grid(row=0, column=7, padx=5, pady=15, sticky="ew")

        self.btn_logout = CTkButton(
            self, 
            text="Logout", 
            command=on_logout, 
            height=40,
            fg_color="#A30000", 
            hover_color="#7A0000",
            font=("Arial", 13, "bold")
        )
        self.btn_logout.grid(row=0, column=8, padx=(20, 5), pady=15, sticky="ew")


class DB_options(CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=10)
        
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.btn_agregar = CTkButton(
            self,
            text="Agregar",
            command=lambda: self.check_credentials(self.uid_textbox.get(), self.textbox.get()),
            height=35,
            font=("Arial", 12, "bold")
        )
        self.btn_agregar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.btn_modificar = CTkButton(
            self,
            text="Eliminar",
            height=35,
            font=("Arial", 12, "bold")
        )
        self.btn_modificar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_eliminar = CTkButton(
            self,
            text="Guardar",
            height=35,
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
        lbl_name.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.ent_name = CTkEntry(self.form_container, width=160)
        self.ent_name.grid(row=0, column=1, padx=10, pady=5)

        lbl_surname = CTkLabel(self.form_container, text="Apellido:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_surname.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ent_surname = CTkEntry(self.form_container, width=160)
        self.ent_surname.grid(row=1, column=1, padx=10, pady=5)

        lbl_id = CTkLabel(self.form_container, text="Cedula:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.ent_id = CTkEntry(self.form_container, width=160)
        self.ent_id.grid(row=2, column=1, padx=10, pady=5)

        self.chk_admin = CTkCheckBox(self.form_container, text="es administrador", text_color="#000000", font=("Arial", 12, "bold"))
        self.chk_admin.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="w")

    def show_estudiante_fields(self):
        self.clear_form()

        lbl_name = CTkLabel(self.form_container, text="Nombre:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_name.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.ent_name = CTkEntry(self.form_container, width=160)
        self.ent_name.grid(row=0, column=1, padx=10, pady=5)

        lbl_surname = CTkLabel(self.form_container, text="Apellido:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_surname.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ent_surname = CTkEntry(self.form_container, width=160)
        self.ent_surname.grid(row=1, column=1, padx=10, pady=5)

        lbl_id = CTkLabel(self.form_container, text="Cedula:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_id.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.ent_id = CTkEntry(self.form_container, width=160)
        self.ent_id.grid(row=2, column=1, padx=10, pady=5)

        lbl_instrumento = CTkLabel(self.form_container, text="Instrumento:", text_color="#000000", font=("Arial", 12, "bold"))
        lbl_instrumento.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.ent_instrumento = CTkEntry(self.form_container, width=160)
        self.ent_instrumento.grid(row=3, column=1, padx=10, pady=5)

        self.chk_piano = CTkCheckBox(self.form_container, text="Piano Complementario", text_color="#000000", font=("Arial", 12, "bold"))
        self.chk_piano.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")


class UpdateDataScreen(CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        db_display = DisplayDB(self)
        db_display.grid(row=1, column=1, padx=(10, 15), pady=15, sticky="nsew")

        admin_panel = AdminPanel(
            self, 
            on_logout, 
            show_profesor_form=db_display.show_profesor_fields, 
            show_estudiante_form=db_display.show_estudiante_fields
        )
        admin_panel.grid(row=0, column=0, columnspan=2, padx=15, pady=(5, 0), sticky="ew")

        db_options = DB_options(self)
        db_options.grid(row=1, column=0, padx=(15, 10), pady=15, sticky="nsew")
