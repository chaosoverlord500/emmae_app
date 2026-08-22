import re

#valida el email
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

#valida el numero de telefono
def validate_phone_rest(text):
    return text == "" or (text.isdigit() and len(text) <= 7)

#valida que el texto sean numeros o texto
def validate_simple_number(text):
    return text == "" or text.isdigit()