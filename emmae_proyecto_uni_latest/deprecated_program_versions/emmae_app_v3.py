import os
import customtkinter as ctk
from tkinter import messagebox

try:
    from modules import db_con as DB_con, user_management as User_Manager
    conn = DB_con.connect_to_db()
    cursor = conn.cursor()
except ImportError:
    class Mock:
        def cursor(self): return self
        def close(self): pass
        @staticmethod
        def login(uid, pswd): return True
    conn = cursor = User_Manager = Mock()

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login):
        super().__init__(master, fg_color="#FFFFFF", corner_radius=15, width=350, height=400)
        self.pack_propagate(False)
        self.on_login = on_login

        ctk.CTkLabel(self, text="Bienvenido!", font=("Arial", 24, "bold"), text_color="#0A1118").pack(pady=(40, 5))
        ctk.CTkLabel(self, text="Inicie sesión en su cuenta", font=("Arial", 13), text_color="#6B7280").pack(pady=(0, 25))

        self.uid_textbox = ctk.CTkEntry(self, width=260, height=40, corner_radius=8, placeholder_text="Cédula")
        self.uid_textbox.pack(pady=10)

        self.textbox = ctk.CTkEntry(self, width=260, height=40, corner_radius=8, placeholder_text="Contraseña", show="*")
        self.textbox.pack(pady=10)

        ctk.CTkButton(
            self, text="Iniciar Sesión", width=260, height=40, corner_radius=8, font=("Arial", 13, "bold"),
            command=lambda: self.check_credentials(self.uid_textbox.get(), self.textbox.get())
        ).pack(pady=(20, 10))

        ctk.CTkButton(
            self, text="Olvidé mi contraseña", fg_color="transparent", text_color="#9CA3AF", hover_color="#F3F4F6", font=("Arial", 11),
            command=lambda: messagebox.showinfo("EMMAE APP", "Comuníquese con el administrador para cambiar su contraseña")
        ).pack(pady=5)

    def check_credentials(self, id_str, pswd):
        if not id_str or not pswd:
            return messagebox.showerror("Error", "Por favor complete todos los campos")
        try:
            if User_Manager.login(int(id_str), pswd):
                self.on_login()
            else:
                messagebox.showerror("Error", "Datos Incorrectos")
        except ValueError:
            messagebox.showerror("Error", "No ingrese letras en el campo de Cédula")


class TopNavBar(ctk.CTkFrame):
    def __init__(self, master, active_callback, logout_callback):
        super().__init__(master, fg_color="#0A1118", corner_radius=25, height=50, width=720)
        self.grid_propagate(False)
        
        modules = ["Profesor", "Estudiante", "Instrumentos", "M.D.A", "Salones"]
        for idx in range(len(modules) + 1):
            self.grid_columnconfigure(idx, weight=1)

        for idx, mod in enumerate(modules):
            btn = ctk.CTkButton(
                self, text=mod, fg_color="transparent", hover_color="#1F2937", text_color="#FFFFFF",
                width=110, height=36, corner_radius=18, font=("Arial", 12, "bold"),
                command=lambda m=mod: active_callback(m.lower())
            )
            btn.grid(row=0, column=idx, padx=4, pady=7, sticky="nsew")
            
        ctk.CTkButton(
            self, text="Salir", fg_color="transparent", hover_color="#1F2937", text_color="#FFFFFF",
            width=80, height=36, corner_radius=18, font=("Arial", 12, "bold"), command=logout_callback
        ).grid(row=0, column=len(modules), padx=10, pady=7, sticky="e")


class LeftSubMenu(ctk.CTkFrame):
    def __init__(self, master, action_callback, mode_callback, show_toggle=False):
        super().__init__(master, fg_color="#0A1118", width=130, corner_radius=20)
        self.action_callback = action_callback
        self.buttons_frame = None
        
        if show_toggle:
            self.toggle = ctk.CTkSegmentedButton(
                self, values=["A", "P"], command=mode_callback,
                font=("Arial", 12, "bold"), fg_color="#1F2937", 
                selected_color="#3B82F6"
            )
            self.toggle.set("A")
            self.toggle.pack(side="top", pady=(15, 5), padx=10, fill="x")
            
        self.refresh_actions()

    def refresh_actions(self):
        if self.buttons_frame:
            self.buttons_frame.destroy()
            
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(side="top", fill="both", expand=True, pady=(5, 15))
        
        actions = ["Añadir", "Modificar", "Buscar", "Eliminar"]
        for act in actions:
            ctk.CTkButton(
                self.buttons_frame, text=act, fg_color="transparent", hover_color="#1F2937", text_color="#FFFFFF",
                height=32, width=110, corner_radius=16, font=("Arial", 11),
                command=lambda a=act: self.action_callback(a)
            ).pack(side="top", pady=6, padx=10)


class InteractiveWorkspace(ctk.CTkFrame):
    def __init__(self, master, name, include_loans=False):
        super().__init__(master, fg_color="transparent")
        self.name = name.title()
        self.include_loans = include_loans
        self.current_mode = "A"
        self.current_action = "Añadir"
        
        self.sidebar = LeftSubMenu(
            self, 
            action_callback=self.handle_action_change, 
            mode_callback=self.handle_mode_change, 
            show_toggle=include_loans
        )
        self.sidebar.pack(side="left", anchor="c", padx=(5, 15), pady=5)
        
        self.content_area = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=15)
        self.content_area.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
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
        
        # If in Préstamos mode (P), all screens show up empty
        if self.include_loans and self.current_mode == "P":
            ctk.CTkLabel(
                self.content_area, 
                text=f"{self.current_action} - Préstamos de {self.name}", 
                text_color="#111827", font=("Arial", 16, "bold")
            ).pack(anchor="w", padx=25, pady=(20, 15))
            
            ctk.CTkLabel(
                self.content_area, 
                text="Vacío por el momento", 
                text_color="#9CA3AF", font=("Arial", 14, "italic")
            ).pack(pady=60, expand=True)
            return

        # Default Mode A (Asset Management) Layouts
        ctk.CTkLabel(self.content_area, text=f"{self.current_action} - Gestión de {self.name}", text_color="#111827", font=("Arial", 16, "bold")).pack(anchor="w", padx=25, pady=(20, 15))
        
        if self.current_action == "Añadir":
            ctk.CTkLabel(self.content_area, text="Ingrese el valor correspondiente:", text_color="#4B5563").pack(anchor="w", padx=25, pady=2)
            ctk.CTkEntry(self.content_area, width=300, height=35, placeholder_text=f"Nombre del {self.name}").pack(anchor="w", padx=25, pady=10)
            ctk.CTkButton(self.content_area, text="Guardar Registro", width=120, height=32).pack(anchor="w", padx=25, pady=10)
            
        elif self.current_action in ["Modificar", "Eliminar"]:
            ctk.CTkLabel(self.content_area, text="Seleccione el elemento:", text_color="#4B5563").pack(anchor="w", padx=25, pady=2)
            ctk.CTkOptionMenu(self.content_area, values=[f"{self.name} A", f"{self.name} B"], width=300, height=35, fg_color="#FFFFFF", text_color="#000000", button_color="#0A1118").pack(anchor="w", padx=25, pady=10)
            ctk.CTkButton(self.content_area, text="Actualizar" if self.current_action == "Modificar" else "Eliminar", width=120, height=32).pack(anchor="w", padx=25, pady=10)
            
        elif self.current_action == "Buscar":
            ctk.CTkLabel(self.content_area, text="Registros encontrados:", text_color="#4B5563").pack(anchor="w", padx=25, pady=2)
            scroll = ctk.CTkScrollableFrame(self.content_area, fg_color="#FFFFFF", corner_radius=8)
            scroll.pack(anchor="w", padx=25, pady=10, fill="both", expand=True)
            for i in range(1, 6):
                ctk.CTkLabel(scroll, text=f"ID: 00{i} | Ejemplo {self.name} {i}", text_color="#374151").pack(anchor="w", padx=10, pady=3)


class UpdateDataScreen(ctk.CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master, fg_color="transparent")
        self.on_logout = on_logout
        
        self.top_nav = TopNavBar(self, active_callback=self.switch_workspace, logout_callback=self.on_logout)
        self.top_nav.pack(side="top", anchor="center", pady=(5, 15)) 
        
        self.workspace_container = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_container.pack(side="bottom", fill="both", expand=True)
        
        self.active_workspace = None
        self.switch_workspace("profesor")

    def switch_workspace(self, target_view):
        if self.active_workspace:
            self.active_workspace.destroy()
        
        has_loans = target_view in ["instrumentos", "m.d.a", "salones"]
        self.active_workspace = InteractiveWorkspace(self.workspace_container, name=target_view, include_loans=has_loans)
        self.active_workspace.pack(fill="both", expand=True)


# --- Main Application Window ---

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EMMAE - Menú de Administrador v2.0")
        self.geometry("1000x650") 
        self.current_screen = None
        self.load_login_screen()
    
    def load_login_screen(self):
        if self.current_screen: 
            self.current_screen.destroy()
        self.current_screen = LoginScreen(self, on_login=self.load_admin_screen)
        self.current_screen.pack(expand=True)

    def load_admin_screen(self):
        if self.current_screen: 
            self.current_screen.destroy()
        self.current_screen = UpdateDataScreen(self, on_logout=self.load_login_screen)
        self.current_screen.pack(fill="both", expand=True, padx=15, pady=15)


if __name__ == "__main__":
    app = App()
    try:
        app.mainloop()
    finally:
        try:
            cursor.close()
            conn.close()
        except AttributeError:
            pass