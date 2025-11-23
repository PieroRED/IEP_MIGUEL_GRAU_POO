import json
import os

# ================================
#   CLASES DEL SISTEMA
# ================================

class Usuario:
    def __init__(self, usuario, contrasena):
        self.usuario = usuario
        self.contrasena = contrasena


class Estudiante(Usuario):
    def __init__(self, usuario, contrasena, nombre, grado):
        super().__init__(usuario, contrasena)
        self.nombre = nombre
        self.grado = grado
        self.horario = []
        self.notas = []
        self.anuncios = []

    def mostrar_info(self):
        print("\n=== Información del Estudiante ===")
        print("Nombre:", self.nombre)
        print("Grado:", self.grado)

        print("\nHorario:")
        if self.horario:
            for clase in self.horario:
                print(" -", clase)
        else:
            print(" (Vacío)")

        print("\nNotas:")
        if self.notas:
            for nota in self.notas:
                print(" -", nota)
        else:
            print(" (Vacío)")

        print("\nAnuncios:")
        if self.anuncios:
            for a in self.anuncios:
                print(" -", a)
        else:
            print(" (Vacío)")


# ============================================
#   SISTEMA (maneja login, registro, JSON)
# ============================================

class SistemaAcademico:
    def __init__(self):
        self.estudiantes = []

        if os.path.exists("estudiantes.json"):
            with open("estudiantes.json", "r", encoding="utf-8") as f:
                datos = json.load(f)

            for e in datos:
                est = Estudiante(
                    e["usuario"],
                    e["contrasena"],
                    e["nombre"],
                    e["grado"]
                )
                est.horario = e["horario"]
                est.notas = e["notas"]
                est.anuncios = e["anuncios"]
                self.estudiantes.append(est)
        else:
            self.estudiantes = []

    def login(self, usuario, contrasena):
        for est in self.estudiantes:
            if est.usuario == usuario and est.contrasena == contrasena:
                return est
        return None

    def registrar(self):

        while True:
            usuario = input("Nuevo usuario: ").strip()
            if usuario == "":
                print("El usuario no puede estar vacío.")
            elif " " in usuario:
                print("El usuario no debe contener espacios.")
            elif len(usuario) < 5:
                print("El usuario debe tener al menos 5 caracteres.")
            elif any(e.usuario == usuario for e in self.estudiantes):
                print("Ese usuario ya existe.")
            else:
                break

        while True:
            contrasena = input("Nueva contraseña: ").strip()
            if len(contrasena) < 4:
                print("La contraseña debe tener al menos 4 caracteres.")
            elif " " in contrasena:
                print("La contraseña no debe contener espacios.")
            elif not any(c.isdigit() for c in contrasena):
                print("La contraseña debe tener al menos un número.")
            elif not any(c.isalpha() for c in contrasena):
                print("La contraseña debe tener al menos una letra.")
            else:
                break

        nombre = input("Nombre completo: ")
        grado = input("Grado: ")

        nuevo = Estudiante(usuario, contrasena, nombre, grado)

        print("\nIngresa el horario (vacío para terminar):")
        while True:
            materia = input("Clase: ").strip()
            if materia == "":
                break
            nuevo.horario.append(materia)

        print("\nIngresa notas (ejemplo: Matemáticas:18). Vacío para terminar:")
        while True:
            nota = input("Nota: ").strip()
            if nota == "":
                break
            nuevo.notas.append(nota)

        print("\nIngresa anuncios (vacío para terminar):")
        while True:
            an = input("Anuncio: ").strip()
            if an == "":
                break
            nuevo.anuncios.append(an)

        self.estudiantes.append(nuevo)

        datos = []
        for e in self.estudiantes:
            datos.append({
                "usuario": e.usuario,
                "contrasena": e.contrasena,
                "nombre": e.nombre,
                "grado": e.grado,
                "horario": e.horario,
                "notas": e.notas,
                "anuncios": e.anuncios
            })

        with open("estudiantes.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

        print("\nRegistro exitoso.")
        nuevo.mostrar_info()


# ================================
#   MÉTODO MAIN
# ================================

def main():
    sistema = SistemaAcademico()

    print("1. Iniciar sesión")
    print("2. Registrar nuevo estudiante")
    op = input("Opción: ")

    if op == "1":
        intentos = 3
        while intentos > 0:
            u = input("Usuario: ")
            c = input("Contraseña: ")
            est = sistema.login(u, c)

            if est:
                est.mostrar_info()
                break
            else:
                intentos -= 1
                print("Datos incorrectos. Intentos restantes:", intentos)

        if intentos == 0:
            print("Demasiados intentos. Intenta más tarde.")

    elif op == "2":
        sistema.registrar()
    else:
        print("Opción no válida.")


# Ejecutar main
if __name__ == "__main__":
    main()
