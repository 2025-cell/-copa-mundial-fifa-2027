from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, date
import os
import certifi

app = Flask(__name__)
app.secret_key = "copa_mundial_fifa_2027_secret_key_cambia_esto"

# Contraseña del acceso rápido de administrador (botón oculto en login)
ADMIN_PASSWORD = "12345678"

# ================== CONEXIÓN A MONGODB ==================
# Reemplaza con tu URI de MongoDB Atlas
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://gueg091009hmczsla0_db_user:elviejo@cluster0.a7rdoev.mongodb.net/copa_mundial_fifa?retryWrites=true&w=majority&appName=Cluster0")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["copa_mundial_fifa"]

usuarios_col = db["usuarios"]
equipos_col = db["equipos"]
jugadores_col = db["jugadores"]
partidos_col = db["partidos"]
noticias_col = db["noticias"]
apuestas_col = db["apuestas"]
estadios_col = db["estadios"]
resultados_col = db["resultados"]
estadisticas_col = db["estadisticas"]
admins_col = db["administradores"]
patrocinadores_col = db["patrocinadores"]
boletos_col = db["boletos"]


# ================== FOTOS DE JUGADORES PARA EL LOGIN ==================
# Jugadores jóvenes destacados usados como fondo/carrusel decorativo en login
JUGADORES_LOGIN = [
    {"nombre": "Jude Bellingham", "pais": "Inglaterra", "img": "/static/img/imagen1.png"},
    {"nombre": "Lamine Yamal", "pais": "España", "img": "/static/img/imagen2.png"},
    {"nombre": "Jamal Musiala", "pais": "Alemania", "img": "/static/img/imagen3.png"},
    {"nombre": "Endrick", "pais": "Brasil", "img": "/static/img/imagen4.png"},
    {"nombre": "Pedri González", "pais": "España", "img": "/static/img/imagen5.png"},
]


# ================== CÓDIGOS ISO DE PAÍS POR EQUIPO (para banderas por imagen) ==================
CODIGOS_PAIS = {
    "Brasil": "br",
    "Argentina": "ar",
    "Uruguay": "uy",
    "Ecuador": "ec",
    "Francia": "fr",
    "Alemania": "de",
    "España": "es",
    "Inglaterra": "gb-eng",
    "Portugal": "pt",
    "Países Bajos": "nl",
    "Bélgica": "be",
    "Croacia": "hr",
    "Italia": "it",
    "Suiza": "ch",
    "Dinamarca": "dk",
    "Polonia": "pl",
    "México": "mx",
    "Estados Unidos": "us",
    "Canadá": "ca",
    "Costa Rica": "cr",
    "Japón": "jp",
    "Corea del Sur": "kr",
    "Australia": "au",
    "Arabia Saudita": "sa",
    "Marruecos": "ma",
    "Senegal": "sn",
    "Nigeria": "ng",
    "Ghana": "gh",
    "Colombia": "co",
    "Chile": "cl",
    "Paraguay": "py",
    "Perú": "pe",
}


def usuario_actual():
    if "usuario_id" in session:
        return usuarios_col.find_one({"_id": ObjectId(session["usuario_id"])})
    return None


def es_mayor_edad(fecha_nacimiento_str):
    try:
        y, m, d = map(int, fecha_nacimiento_str.split("-"))
        nacimiento = date(y, m, d)
        hoy = date.today()
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        return edad >= 18
    except Exception:
        return False


@app.context_processor
def inject_usuario():
    return {"usuario_actual": usuario_actual()}


# ================== AUTENTICACIÓN ==================

@app.route("/")
def index():
    if not usuario_actual():
        return redirect(url_for("login"))
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        contrasena = request.form.get("contrasena", "")

        usuario = usuarios_col.find_one({"correo": correo})
        if usuario and check_password_hash(usuario["contrasena"], contrasena):
            session["usuario_id"] = str(usuario["_id"])
            session["nombre"] = usuario["nombre"]
            flash(f"¡Bienvenido de nuevo, {usuario['nombre']}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Correo o contraseña incorrectos.", "error")

    return render_template("login.html", jugadores=JUGADORES_LOGIN)


@app.route("/admin-login", methods=["POST"])
def admin_login():
    contrasena = request.form.get("contrasena_admin", "")

    if contrasena != ADMIN_PASSWORD:
        flash("Contraseña de administrador incorrecta.", "error")
        return redirect(url_for("login"))

    admin_user = usuarios_col.find_one({"rol": "admin"})
    if not admin_user:
        flash("Aún no existe una cuenta admin. Visita /setup-admin primero.", "error")
        return redirect(url_for("login"))

    session["usuario_id"] = str(admin_user["_id"])
    session["nombre"] = admin_user["nombre"]
    flash("Acceso de administrador concedido.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        contrasena = request.form.get("contrasena", "")
        edad_nacimiento = request.form.get("fecha_nacimiento", "")

        if usuarios_col.find_one({"correo": correo}):
            flash("Ya existe una cuenta con ese correo.", "error")
            return redirect(url_for("registro"))

        confirmar_contrasena = request.form.get("confirmar_contrasena", "")
        if contrasena != confirmar_contrasena:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for("registro"))

        nuevo_usuario = {
            "nombre": nombre,
            "correo": correo,
            "contrasena": generate_password_hash(contrasena),
            "fecha_nacimiento": edad_nacimiento,
            "es_mayor_edad": es_mayor_edad(edad_nacimiento),
            "comprobante_identidad": request.form.get("comprobante_identidad", "").strip(),
            "fecha_registro": datetime.utcnow(),
            "rol": "usuario",
        }
        resultado = usuarios_col.insert_one(nuevo_usuario)
        session["usuario_id"] = str(resultado.inserted_id)
        session["nombre"] = nombre
        flash("Registro exitoso. ¡Bienvenido!", "success")
        return redirect(url_for("home"))

    return render_template("registro.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("login"))


def login_requerido(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not usuario_actual():
            flash("Debes iniciar sesión para continuar.", "error")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


# ================== PÁGINA PRINCIPAL ==================

@app.route("/home")
@login_requerido
def home():
    ultimas_noticias = list(noticias_col.find().sort("fecha_publicacion", -1).limit(3))
    proximos_partidos = list(partidos_col.find().sort("fecha", 1).limit(3))
    return render_template("home.html", noticias=ultimas_noticias, partidos=proximos_partidos)


# ================== NOTICIAS ==================

@app.route("/noticias")
@login_requerido
def noticias():
    todas = list(noticias_col.find().sort("fecha_publicacion", -1))
    return render_template("noticias.html", noticias=todas)


# ================== PARTIDOS ==================

@app.route("/partidos")
@login_requerido
def partidos():
    lista_partidos = list(partidos_col.find().sort("fecha", 1))
    for p in lista_partidos:
        p["equipo_local_info"] = equipos_col.find_one({"_id": p.get("id_equipo_local")})
        p["equipo_visitante_info"] = equipos_col.find_one({"_id": p.get("id_equipo_visitante")})
        p["resultado"] = resultados_col.find_one({"id_partido": p["_id"]})
    return render_template("partidos.html", partidos=lista_partidos)


# ================== EQUIPOS ==================

@app.route("/equipos")
@login_requerido
def equipos():
    grupo = request.args.get("grupo")
    filtro = {"grupo": grupo} if grupo else {}
    lista_equipos = list(equipos_col.find(filtro))
    for e in lista_equipos:
        e["codigo_pais"] = CODIGOS_PAIS.get(e.get("nombre_equipo"), "un")
    return render_template("equipos.html", equipos=lista_equipos, grupo_actual=grupo)


@app.route("/equipos/<equipo_id>")
@login_requerido
def detalle_equipo(equipo_id):
    equipo = equipos_col.find_one({"_id": ObjectId(equipo_id)})
    if equipo:
        equipo["codigo_pais"] = CODIGOS_PAIS.get(equipo.get("nombre_equipo"), "un")
    jugadores = list(jugadores_col.find({"id_equipo": ObjectId(equipo_id)}))
    estadistica = estadisticas_col.find_one({"id_equipo": ObjectId(equipo_id)})
    return render_template("detalle_equipo.html", equipo=equipo, jugadores=jugadores, estadistica=estadistica)


# ================== ELIMINATORIAS ==================

@app.route("/eliminatorias")
@login_requerido
def eliminatorias():
    fases = ["Octavos de final", "Cuartos de final", "Semifinal", "Final"]
    bracket = {}
    for fase in fases:
        partidos_fase = list(partidos_col.find({"fase": fase}).sort("fecha", 1))
        for p in partidos_fase:
            p["equipo_local_info"] = equipos_col.find_one({"_id": p.get("id_equipo_local")})
            p["equipo_visitante_info"] = equipos_col.find_one({"_id": p.get("id_equipo_visitante")})
            p["resultado"] = resultados_col.find_one({"id_partido": p["_id"]})
        bracket[fase] = partidos_fase
    return render_template("eliminatorias.html", bracket=bracket, fases=fases)


# ================== PATROCINADORES ==================

@app.route("/patrocinadores")
@login_requerido
def patrocinadores():
    lista = list(patrocinadores_col.find())
    return render_template("patrocinadores.html", patrocinadores=lista)


# ================== BOLETOS ==================

@app.route("/boletos", methods=["GET", "POST"])
@login_requerido
def boletos():
    usuario = usuario_actual()

    if request.method == "POST":
        id_partido = request.form.get("id_partido")
        tipo_boleto = request.form.get("tipo_boleto")
        cantidad = int(request.form.get("cantidad", 1))

        precios = {"General": 800, "Preferente": 1500, "VIP": 3500}
        boletos_col.insert_one({
            "id_usuario": usuario["_id"],
            "id_partido": ObjectId(id_partido),
            "tipo_boleto": tipo_boleto,
            "cantidad": cantidad,
            "precio_unitario": precios.get(tipo_boleto, 800),
            "total": precios.get(tipo_boleto, 800) * cantidad,
            "fecha_compra": datetime.utcnow(),
        })
        flash("Boletos comprados correctamente.", "success")
        return redirect(url_for("boletos"))

    partidos_disponibles = list(partidos_col.find())
    for p in partidos_disponibles:
        p["equipo_local_info"] = equipos_col.find_one({"_id": p.get("id_equipo_local")})
        p["equipo_visitante_info"] = equipos_col.find_one({"_id": p.get("id_equipo_visitante")})

    mis_boletos = list(boletos_col.find({"id_usuario": usuario["_id"]}).sort("fecha_compra", -1))
    for b in mis_boletos:
        partido = partidos_col.find_one({"_id": b.get("id_partido")})
        b["partido_info"] = partido

    return render_template("boletos.html", partidos=partidos_disponibles, mis_boletos=mis_boletos)


# ================== ASISTENTE IA ==================

RESPUESTAS_IA = {
    "horario": "Puedes consultar todos los horarios de partidos en el apartado 'Partidos'. Se actualizan en tiempo real conforme el administrador los programa.",
    "boleto": "Los boletos se compran desde el apartado 'Boletos'. Elige el partido, el tipo (General, Preferente o VIP) y la cantidad.",
    "apuesta": "El apartado de apuestas está disponible solo para mayores de 18 años. Ahí puedes elegir el partido, el tipo de apuesta y tu predicción.",
    "equipo": "Puedes ver la información de cada equipo (plantilla, entrenador, grupo y estadísticas) en el apartado 'Equipos'.",
    "default": "Soy el asistente de la Copa Mundial FIFA 2027. Puedo ayudarte con dudas sobre horarios, boletos, apuestas o equipos. ¿Sobre qué tema quieres preguntar?",
}


@app.route("/asistente", methods=["GET", "POST"])
@login_requerido
def asistente():
    respuesta = None
    pregunta = None
    if request.method == "POST":
        pregunta = request.form.get("pregunta", "").lower()
        respuesta = RESPUESTAS_IA["default"]
        for clave in RESPUESTAS_IA:
            if clave in pregunta:
                respuesta = RESPUESTAS_IA[clave]
                break
    return render_template("asistente.html", respuesta=respuesta, pregunta=pregunta)


# ================== ESTADÍSTICAS ==================

@app.route("/estadisticas")
@login_requerido
def estadisticas():
    tabla = list(estadisticas_col.find())
    for fila in tabla:
        equipo = equipos_col.find_one({"_id": fila.get("id_equipo")})
        fila["nombre_equipo"] = equipo["nombre_equipo"] if equipo else "Desconocido"
        fila["codigo_pais"] = CODIGOS_PAIS.get(equipo["nombre_equipo"], "un") if equipo else "un"
        fila["puntos"] = fila.get("victorias", 0) * 3 + fila.get("empates", 0)
    tabla.sort(key=lambda x: x.get("puntos", 0), reverse=True)
    return render_template("estadisticas.html", tabla=tabla)


# ================== APUESTAS ==================

@app.route("/apuestas", methods=["GET", "POST"])
@login_requerido
def apuestas():
    usuario = usuario_actual()

    # Paso 1: si todavía no verificó su CURP, se le pide antes de dejarlo apostar
    if not usuario.get("curp_verificado"):
        if request.method == "POST" and request.form.get("accion") == "verificar_curp":
            curp = request.form.get("curp", "").strip().upper()
            declara_mayor = request.form.get("declara_mayor_edad") == "on"

            if len(curp) != 18:
                flash("El CURP debe tener 18 caracteres.", "error")
                return redirect(url_for("apuestas"))
            if not declara_mayor:
                flash("Debes declarar que eres mayor de edad para continuar.", "error")
                return redirect(url_for("apuestas"))

            usuarios_col.update_one(
                {"_id": usuario["_id"]},
                {"$set": {
                    "curp": curp,
                    "curp_verificado": True,
                    "es_mayor_edad": True,
                }},
            )
            flash("Verificación completada. Ya puedes apostar.", "success")
            return redirect(url_for("apuestas"))

        return render_template("apuestas_verificacion.html")

    # Paso 2: ya verificado, puede apostar normalmente
    if request.method == "POST" and request.form.get("accion") == "apostar":
        id_partido = request.form.get("id_partido")
        tipo_apuesta = request.form.get("tipo_apuesta")
        prediccion = request.form.get("prediccion")
        cantidad = float(request.form.get("cantidad", 0))

        nueva_apuesta = {
            "id_usuario": usuario["_id"],
            "id_partido": ObjectId(id_partido),
            "tipo_apuesta": tipo_apuesta,
            "prediccion": prediccion,
            "cantidad": cantidad,
            "fecha_apuesta": datetime.utcnow(),
        }
        apuestas_col.insert_one(nueva_apuesta)
        flash("Apuesta registrada correctamente.", "success")
        return redirect(url_for("apuestas"))

    partidos_disponibles = list(partidos_col.find().sort("fecha", 1))
    for p in partidos_disponibles:
        p["equipo_local_info"] = equipos_col.find_one({"_id": p.get("id_equipo_local")})
        p["equipo_visitante_info"] = equipos_col.find_one({"_id": p.get("id_equipo_visitante")})

    mis_apuestas = list(apuestas_col.find({"id_usuario": usuario["_id"]}).sort("fecha_apuesta", -1))
    for a in mis_apuestas:
        partido = partidos_col.find_one({"_id": a.get("id_partido")})
        if partido:
            partido["equipo_local_info"] = equipos_col.find_one({"_id": partido.get("id_equipo_local")})
            partido["equipo_visitante_info"] = equipos_col.find_one({"_id": partido.get("id_equipo_visitante")})
        a["partido_info"] = partido

    return render_template("apuestas.html", partidos=partidos_disponibles, mis_apuestas=mis_apuestas)


# ================== PERFIL ==================

@app.route("/perfil", methods=["GET", "POST"])
@login_requerido
def perfil():
    usuario = usuario_actual()

    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre", "").strip()
        nuevo_correo = request.form.get("correo", "").strip().lower()
        nueva_contrasena = request.form.get("nueva_contrasena", "")
        confirmar_contrasena = request.form.get("confirmar_contrasena", "")

        if nuevo_correo != usuario["correo"] and usuarios_col.find_one({"correo": nuevo_correo}):
            flash("Ese correo ya está en uso por otra cuenta.", "error")
            return redirect(url_for("perfil"))

        cambios = {
            "nombre": nuevo_nombre,
            "correo": nuevo_correo,
        }

        if nueva_contrasena:
            if nueva_contrasena != confirmar_contrasena:
                flash("Las contraseñas nuevas no coinciden.", "error")
                return redirect(url_for("perfil"))
            cambios["contrasena"] = generate_password_hash(nueva_contrasena)

        usuarios_col.update_one({"_id": usuario["_id"]}, {"$set": cambios})
        session["nombre"] = nuevo_nombre
        flash("Perfil actualizado.", "success")
        return redirect(url_for("perfil"))

    return render_template("perfil.html", usuario=usuario)


# ================== ADMINISTRACIÓN ==================

def admin_requerido(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        usuario = usuario_actual()
        if not usuario or usuario.get("rol") != "admin":
            flash("Acceso restringido a administradores.", "error")
            return redirect(url_for("home"))
        return func(*args, **kwargs)

    return wrapper


@app.route("/admin")
@admin_requerido
def admin_dashboard():
    total_usuarios = usuarios_col.count_documents({})
    total_noticias = noticias_col.count_documents({})
    total_partidos = partidos_col.count_documents({})
    total_apuestas = apuestas_col.count_documents({})
    return render_template(
        "admin_dashboard.html",
        total_usuarios=total_usuarios,
        total_noticias=total_noticias,
        total_partidos=total_partidos,
        total_apuestas=total_apuestas,
    )


@app.route("/admin/noticias", methods=["GET", "POST"])
@admin_requerido
def admin_noticias():
    if request.method == "POST":
        noticias_col.insert_one({
            "titulo": request.form.get("titulo"),
            "descripcion": request.form.get("descripcion"),
            "fecha_publicacion": datetime.utcnow(),
            "id_admin": usuario_actual()["_id"],
        })
        flash("Noticia publicada.", "success")
        return redirect(url_for("admin_noticias"))

    todas = list(noticias_col.find().sort("fecha_publicacion", -1))
    return render_template("admin_noticias.html", noticias=todas)


@app.route("/admin/noticias/eliminar/<noticia_id>")
@admin_requerido
def admin_eliminar_noticia(noticia_id):
    noticias_col.delete_one({"_id": ObjectId(noticia_id)})
    flash("Noticia eliminada.", "success")
    return redirect(url_for("admin_noticias"))


@app.route("/admin/equipos", methods=["GET", "POST"])
@admin_requerido
def admin_equipos():
    if request.method == "POST":
        equipos_col.insert_one({
            "nombre_equipo": request.form.get("nombre_equipo"),
            "pais": request.form.get("pais"),
            "entrenador": request.form.get("entrenador"),
            "grupo": request.form.get("grupo"),
        })
        flash("Equipo agregado.", "success")
        return redirect(url_for("admin_equipos"))

    todos = list(equipos_col.find())
    return render_template("admin_equipos.html", equipos=todos)


@app.route("/admin/equipos/editar/<equipo_id>", methods=["GET", "POST"])
@admin_requerido
def admin_editar_equipo(equipo_id):
    equipo = equipos_col.find_one({"_id": ObjectId(equipo_id)})
    if request.method == "POST":
        equipos_col.update_one({"_id": ObjectId(equipo_id)}, {"$set": {
            "nombre_equipo": request.form.get("nombre_equipo"),
            "pais": request.form.get("pais"),
            "entrenador": request.form.get("entrenador"),
            "grupo": request.form.get("grupo"),
        }})
        flash("Equipo actualizado.", "success")
        return redirect(url_for("admin_equipos"))
    return render_template("admin_editar_equipo.html", equipo=equipo)


@app.route("/admin/equipos/eliminar/<equipo_id>")
@admin_requerido
def admin_eliminar_equipo(equipo_id):
    equipos_col.delete_one({"_id": ObjectId(equipo_id)})
    flash("Equipo eliminado.", "success")
    return redirect(url_for("admin_equipos"))


@app.route("/admin/jugadores", methods=["GET", "POST"])
@admin_requerido
def admin_jugadores():
    equipos_lista = list(equipos_col.find())

    if request.method == "POST":
        jugadores_col.insert_one({
            "id_equipo": ObjectId(request.form.get("id_equipo")),
            "nombre": request.form.get("nombre"),
            "posicion": request.form.get("posicion"),
            "numero_camiseta": int(request.form.get("numero_camiseta", 0)),
            "fecha_nacimiento": request.form.get("fecha_nacimiento"),
        })
        flash("Jugador agregado.", "success")
        return redirect(url_for("admin_jugadores"))

    todos = list(jugadores_col.find())
    for j in todos:
        j["equipo_info"] = equipos_col.find_one({"_id": j.get("id_equipo")})
    return render_template("admin_jugadores.html", jugadores=todos, equipos=equipos_lista)


@app.route("/admin/jugadores/eliminar/<jugador_id>")
@admin_requerido
def admin_eliminar_jugador(jugador_id):
    jugadores_col.delete_one({"_id": ObjectId(jugador_id)})
    flash("Jugador eliminado.", "success")
    return redirect(url_for("admin_jugadores"))


@app.route("/admin/patrocinadores", methods=["GET", "POST"])
@admin_requerido
def admin_patrocinadores():
    if request.method == "POST":
        patrocinadores_col.insert_one({
            "nombre": request.form.get("nombre"),
            "categoria": request.form.get("categoria"),
            "sitio_web": request.form.get("sitio_web"),
        })
        flash("Patrocinador agregado.", "success")
        return redirect(url_for("admin_patrocinadores"))

    todos = list(patrocinadores_col.find())
    return render_template("admin_patrocinadores.html", patrocinadores=todos)


@app.route("/admin/patrocinadores/eliminar/<patrocinador_id>")
@admin_requerido
def admin_eliminar_patrocinador(patrocinador_id):
    patrocinadores_col.delete_one({"_id": ObjectId(patrocinador_id)})
    flash("Patrocinador eliminado.", "success")
    return redirect(url_for("admin_patrocinadores"))


@app.route("/admin/partidos", methods=["GET", "POST"])
@admin_requerido
def admin_partidos():
    equipos_lista = list(equipos_col.find())
    estadios_lista = list(estadios_col.find())

    if request.method == "POST":
        partidos_col.insert_one({
            "fecha": request.form.get("fecha"),
            "hora": request.form.get("hora"),
            "fase": request.form.get("fase"),
            "id_equipo_local": ObjectId(request.form.get("id_equipo_local")),
            "id_equipo_visitante": ObjectId(request.form.get("id_equipo_visitante")),
            "id_estadio": ObjectId(request.form.get("id_estadio")) if request.form.get("id_estadio") else None,
        })
        flash("Partido programado.", "success")
        return redirect(url_for("admin_partidos"))

    todos = list(partidos_col.find().sort("fecha", 1))
    for p in todos:
        p["equipo_local_info"] = equipos_col.find_one({"_id": p.get("id_equipo_local")})
        p["equipo_visitante_info"] = equipos_col.find_one({"_id": p.get("id_equipo_visitante")})

    return render_template("admin_partidos.html", partidos=todos, equipos=equipos_lista, estadios=estadios_lista)


@app.route("/admin/partidos/resultado/<partido_id>", methods=["POST"])
@admin_requerido
def admin_actualizar_resultado(partido_id):
    goles_local = int(request.form.get("goles_local", 0))
    goles_visitante = int(request.form.get("goles_visitante", 0))

    resultados_col.update_one(
        {"id_partido": ObjectId(partido_id)},
        {"$set": {
            "id_partido": ObjectId(partido_id),
            "goles_local": goles_local,
            "goles_visitante": goles_visitante,
        }},
        upsert=True,
    )
    flash("Resultado actualizado.", "success")
    return redirect(url_for("admin_partidos"))


@app.route("/admin/partidos/eliminar/<partido_id>")
@admin_requerido
def admin_eliminar_partido(partido_id):
    partidos_col.delete_one({"_id": ObjectId(partido_id)})
    resultados_col.delete_one({"id_partido": ObjectId(partido_id)})
    flash("Partido eliminado.", "success")
    return redirect(url_for("admin_partidos"))


@app.route("/admin/usuarios")
@admin_requerido
def admin_usuarios():
    todos = list(usuarios_col.find())
    return render_template("admin_usuarios.html", usuarios=todos)


# ================== INICIALIZACIÓN ==================

@app.route("/setup-admin")
def setup_admin():
    """Ruta de un solo uso para crear el primer administrador. Elimínala en producción."""
    if usuarios_col.find_one({"correo": "admin@copamundial.com"}):
        return "El administrador ya existe."

    usuarios_col.insert_one({
        "nombre": "Administrador",
        "correo": "admin@copamundial.com",
        "contrasena": generate_password_hash("admin123"),
        "fecha_nacimiento": "1990-01-01",
        "es_mayor_edad": True,
        "fecha_registro": datetime.utcnow(),
        "rol": "admin",
    })
    return "Administrador creado: admin@copamundial.com / admin123"


if __name__ == "__main__":
    app.run(debug=True)