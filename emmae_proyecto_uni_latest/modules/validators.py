import re
import subprocess
import sys
import tkinter as tk

def validate_name_text(text):
    return bool(re.match("^[a-zA-ZáéíóúÁÉÍÓÚñÑ\\s]*$", text))

def validate_phone_rest(text):
    return text == "" or (text.isdigit() and len(text) <= 7)

def validate_simple_number(text):
    return text == "" or text.isdigit()

def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def show_service_error_dialog(message):
    root = tk.Tk()
    root.withdraw()
    
    dialog = tk.Toplevel(root)
    dialog.title("Error de Servicio MySQL")
    dialog.geometry("420x190")
    dialog.grab_set()
    
    tk.Label(dialog, text="Advertencia de Servicio", font=("Arial", 12, "bold"), fg="red").pack(pady=10)
    tk.Label(dialog, text=message, wraplength=390, justify="center").pack(padx=10, pady=5)
    
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=15)
    
    ignored = [False]
    
    def on_ignore():
        ignored[0] = True
        dialog.destroy()
        root.destroy()
        
    def on_exit():
        dialog.destroy()
        root.destroy()
        sys.exit()
        
    tk.Button(btn_frame, text="Ignorar", command=on_ignore, width=12, bg="orange", fg="black").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Salir", command=on_exit, width=12, bg="red", fg="white").pack(side="left", padx=10)
    
    root.wait_window(dialog)
    return ignored[0]

def check_service_status(service_name):
    cmd = ['sc', 'query', service_name]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    except Exception:
        if show_service_error_dialog(f"No se pudo ejecutar el comando de verificación para el servicio '{service_name}'."):
            return
        else:
            sys.exit()
    
    if 'STATE' not in result.stdout:
        if show_service_error_dialog(f"El servicio '{service_name}' no esta instalado."):
            return
        else:
            sys.exit()
    
    for line in result.stdout.splitlines():
        if 'STATE' in line:
            if not 'RUNNING' in line:
                if show_service_error_dialog(f"El servicio '{service_name}' esta instalado pero no esta encendido. Detalles: {line.strip()}"):
                    return
                else:
                    sys.exit()
