# sistema.py
import json
import os

# ================================
# CLASE BASE USUARIO
# ================================
class Usuario:
    def __init__(self, usuario, contrasena, nombre, tipo):
        self.usuario = usuario
        self.contrasena = contrasena
        self.nombre = nombre
        self.tipo = tipo  # "estudiante" o "profesor"
        self.anuncios = []

# ================================
# ESTUDIANTE (hereda)
# ================================
class Estudiante(Usuario):
    def __init__(self, usuario, contrasena, nombre, grado):
        super().__init__(usuario, contrasena, nombre, "estudiante")
        self.grado = grado
        self.horario = []
        self.notas = []
    def calcular_promedio(self):
        """Calcula el promedio de las notas del estudiante"""
        if not self.notas:  # Si no hay notas
            return 0.0
        
        total = 0
        cantidad = 0
        
        for nota_str in self.notas:
            # Extraer el número de la cadena "Materia:nota"
            try:
                # Buscar el último ":" para separar materia y nota
                if ":" in nota_str:
                    # Dividir por ":" y tomar la última parte
                    partes = nota_str.split(":")
                    if len(partes) >= 2:
                        valor_str = partes[-1].strip()
                        # Intentar convertir a número
                        valor = float(valor_str)
                        total += valor
                        cantidad += 1
            except (ValueError, IndexError):
                # Si hay error, ignorar esa nota
                continue
        
        if cantidad == 0:
            return 0.0
        
        return round(total / cantidad, 2)  # Redondear a 2 decimales

# ================================
# PROFESOR (hereda)
# ================================
class Profesor(Usuario):
    def __init__(self, usuario, contrasena, nombre, curso):
        super().__init__(usuario, contrasena, nombre, "profesor")
        self.curso = curso

# ================================
# SISTEMA ACADEMICO
# ================================
class SistemaAcademico:
    def __init__(self, ruta_archivo="usuarios.json"):
        self.usuarios = []   # aquí guardamos objetos Usuario (Estudiante o Profesor)
        self.ruta_archivo = ruta_archivo
        self.cargar_json()

    # Carga el JSON y reconstruye objetos (Estudiante/Profesor)
    def cargar_json(self):
        if not os.path.exists(self.ruta_archivo):
            return

        with open(self.ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        self.usuarios = []

        for item in datos:
            tipo = item.get("tipo", "estudiante")

            if tipo == "profesor":
                obj = Profesor(
                    item["usuario"],
                    item["contrasena"],
                    item["nombre"],
                    item.get("curso", "")
                )
            else:
                obj = Estudiante(
                    item["usuario"],
                    item["contrasena"],
                    item["nombre"],
                    item.get("grado", "")
                )
                # asumimos ahora que todos los estudiantes tienen horario y notas (listas)
                obj.horario = item.get("horario", [])
                obj.notas = item.get("notas", [])

            obj.anuncios = item.get("anuncios", [])
            self.usuarios.append(obj)

    # Guarda la lista de objetos como lista de diccionarios en JSON
    def guardar_json(self):
        datos = []

        for u in self.usuarios:
            base = {
                "usuario": u.usuario,
                "contrasena": u.contrasena,
                "nombre": u.nombre,
                "tipo": u.tipo,
                "anuncios": u.anuncios
            }

            if u.tipo == "profesor":
                base["curso"] = u.curso
            else:
                # asumimos que todos los estudiantes tienen estos atributos
                base["grado"] = u.grado
                base["horario"] = u.horario
                base["notas"] = u.notas

            datos.append(base)

        with open(self.ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    # Registrar empacando el objeto (POO)
    def registrar(self, obj_usuario):
        self.usuarios.append(obj_usuario)
        self.guardar_json()

    # Login: devuelve el objeto Usuario o None
    def login(self, usuario, contrasena):
        for u in self.usuarios:
            if u.usuario == usuario and u.contrasena == contrasena:
                return u
        return None

    # Buscar por texto: devuelve lista de coincidencias (usuario o nombre, case-insensitive)
    def buscar(self, texto):
        texto = texto.lower()
        return [
            u for u in self.usuarios
            if texto in u.usuario.lower() or texto in u.nombre.lower()
        ]

    # Buscar por usuario exacto (devuelve un objeto o None)
    def buscar_por_usuario(self, username):
        return next((u for u in self.usuarios if u.usuario.lower() == username.lower()), None)
