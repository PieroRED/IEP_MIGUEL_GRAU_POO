# .\venv\Scripts\Activate PARA EL ENTORNO VIRTUAL

# 1. IR A TU CARPETA DEL PROYECTO
# cd ruta/a/tu/proyecto

# 2. INICIAR CONTROL DE VERSIONES (solo primera vez)
# git init

# 3. PREPARAR TODOS LOS ARCHIVOS
# git add .

# 4. GUARDAR PRIMER VERSIÓN
# git commit -m "Primer commit: Sistema académico Miguel Grau"

# 5. CONECTAR CON GITHUB (solo primera vez) - CON TU ENLACE REAL
# git remote add origin https://github.com/PieroRED/IEP_MIGUEL_GRAU_POO.git

# 6. SUBIR A GITHUB
# git push -u origin main   # Si usas rama 'main'
# O si usas rama 'master':
# git push -u origin master

from flask import Flask, render_template, request, redirect, url_for, session
from sistema import SistemaAcademico, Estudiante, Profesor

app = Flask(__name__)
app.secret_key = "cambia_esta_clave_por_una_segura"

sistema = SistemaAcademico()  # instancia central del sistema POO

# RUTA RAIZ -> redirige a login
@app.route("/")
def index():
    return redirect(url_for("login"))

# LOGIN (GET muestra formulario, POST procesa)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()

        u = sistema.login(usuario, contrasena)
        if u:
            session["usuario"] = u.usuario
            # guardamos tipo como el nombre de la clase (Estudiante o Profesor)
            session["tipo"] = u.__class__.__name__
            # redirigir a perfil según tipo
            if isinstance(u, Profesor):
                return redirect(url_for("perfilP"))
            else:
                return redirect(url_for("perfilE"))

        # si fallo login, simplemente volver al login (sin flash por ahora)
        return redirect(url_for("login"))

    return render_template("login.html")

# PÁGINA DE SELECCIÓN: elegir tipo de registro
@app.route("/registro")
def registro():
    return render_template("registro.html")

# REGISTRO ESTUDIANTE (GET muestra form, POST registra)
@app.route("/registro_estudiante", methods=["GET", "POST"])
def registro_estudiante():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()
        nombre = request.form.get("nombre", "").strip()
        grado = request.form.get("grado", "").strip()

        # Validar campos vacíos
        if not all([usuario, contrasena, nombre, grado]):
            return "Todos los campos son obligatorios"

        # Validaciones mínimas (puedes ampliar)
        if any(u.usuario == usuario for u in sistema.usuarios):
            return "El usuario ya existe"

        try:
            obj = Estudiante(usuario, contrasena, nombre, grado)
            sistema.registrar(obj)
        except Exception as e:
            return f"Error al registrar: {e}"
        
        return redirect(url_for("login"))

    return render_template("registro_estudiante.html")

# REGISTRO PROFESOR
@app.route("/registro_profesor", methods=["GET", "POST"])
def registro_profesor():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()
        nombre = request.form.get("nombre", "").strip()
        curso = request.form.get("curso", "").strip()

        # Validar campos vacíos
        if not all([usuario, contrasena, nombre, curso]):
            return "Todos los campos son obligatorios"

        if any(u.usuario == usuario for u in sistema.usuarios):
            return "El usuario ya existe"

        try:
            obj = Profesor(usuario, contrasena, nombre, curso)
            sistema.registrar(obj)
        except Exception as e:
            return f"Error al registrar: {e}"
        
        return redirect(url_for("login"))

    return render_template("registro_profesor.html")

# PERFIL ESTUDIANTE (ruta perfilE)
@app.route("/perfilE")
def perfilE():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario = session["usuario"]
    u = sistema.buscar_por_usuario(usuario)
    if not u or not isinstance(u, Estudiante):
        return redirect(url_for("login"))
    return render_template("perfilE.html", estudiante=u)

# PERFIL PROFESOR (ruta perfilP)
@app.route("/perfilP")
def perfilP():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario = session["usuario"]
    u = sistema.buscar_por_usuario(usuario)
    if not u or not isinstance(u, Profesor):
        return redirect(url_for("login"))
    return render_template("perfilP.html", profesor=u)

# BUSCAR (solo profesores): GET muestra formulario, POST procesa
@app.route("/buscar", methods=["GET", "POST"])
def buscar():
    # controlar acceso: solo profesor puede usar
    if "tipo" not in session or session.get("tipo") != "Profesor":
        return redirect(url_for("login"))

    resultados = []  # ✅ CORREGIDO: lista vacía en lugar de None
    termino = ""     # ✅ CORREGIDO: string vacío en lugar de None

    if request.method == "POST":
        termino = request.form.get("termino", "").strip()
        if termino:  # ✅ Solo buscar si hay término
            resultados = sistema.buscar(termino)

    return render_template("buscar.html", resultados=resultados, termino=termino)

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# PROMEDIO DEL ESTUDIANTE (solo estudiantes)
@app.route("/promedio")
def promedio():
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    usuario = session["usuario"]
    u = sistema.buscar_por_usuario(usuario)
    
    # Verificar que sea estudiante
    if not u or not isinstance(u, Estudiante):
        return redirect(url_for("login"))
    
    # Calcular promedio
    promedio = u.calcular_promedio()
    
    return render_template("promedio.html", estudiante=u, promedio=promedio)

# AGREGAR NOTA A ESTUDIANTE (solo profesores)
@app.route("/agregar_nota", methods=["GET", "POST"])
def agregar_nota():
    # Verificar que sea profesor
    if "usuario" not in session or session.get("tipo") != "Profesor":
        return redirect(url_for("login"))
    
    if request.method == "POST":
        # Obtener datos del formulario
        usuario_estudiante = request.form.get("usuario_estudiante", "").strip()
        materia = request.form.get("materia", "").strip()
        nota = request.form.get("nota", "").strip()
        
        # Validar campos vacíos
        if not all([usuario_estudiante, materia, nota]):
            return "Todos los campos son obligatorios"
        
        # Validar que la nota sea un número válido
        try:
            nota_float = float(nota)
            if not (0 <= nota_float <= 20):
                return "La nota debe estar entre 0 y 20"
        except ValueError:
            return "La nota debe ser un número válido"
        
        # Buscar al estudiante
        estudiante = sistema.buscar_por_usuario(usuario_estudiante)
        
        if estudiante and isinstance(estudiante, Estudiante):
            # Agregar nota con formato "Materia: nota"
            nueva_nota = f"{materia}: {nota}"
            estudiante.notas.append(nueva_nota)
            
            try:
                sistema.guardar_json()  # Guardar en JSON
            except Exception as e:
                return f"Error al guardar la nota: {e}"
            
            return redirect(url_for("perfilP"))
        else:
            # Si no encuentra al estudiante
            return "Estudiante no encontrado"
    
    # GET: mostrar formulario
    return render_template("agregar_nota.html")

if __name__ == "__main__":
    app.run(debug=True)