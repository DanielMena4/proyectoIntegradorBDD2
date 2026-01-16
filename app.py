from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from bson.objectid import ObjectId
import logging
import config
from db_helpers import get_collection

app = Flask(__name__)
app.config.from_object('config')
app.logger.setLevel(logging.DEBUG)

# ---------- RUTAS ----------

@app.route('/')
def index():
    return render_template('index.html')

# -------- CATEQUIZANDOS --------

@app.route('/catequizando')
def lista_catequizandos():
    catequizandos = list(get_collection("catequizandos").find())
    return render_template(
        "catequizando_list.html",
        catequizandos=catequizandos
    )

@app.route('/catequizando/nuevo', methods=['GET', 'POST'])
def nuevo_catequizando():
    col = get_collection("catequizandos")

    if request.method == 'POST':
        nombre = request.form.get("nombreCatequizando")
        apellido = request.form.get("apellidoCatequizando")

        if not nombre or not apellido:
            flash("Nombre y apellido son obligatorios", "warning")
            return redirect(url_for("nuevo_catequizando"))

        # 🔹 Generar catequizandoId incremental
        ultimo = col.find_one(sort=[("catequizandoId", -1)])
        nuevo_id = (ultimo["catequizandoId"] + 1) if ultimo and "catequizandoId" in ultimo else 1

        doc = {
            "catequizandoId": nuevo_id,
            "nombreCatequizando": nombre,
            "apellidoCatequizando": apellido,
            "fechaNacimientoCatequizando": request.form.get("fechaNacimientoCatequizando"),
            "genero": request.form.get("genero"),
            "emailCatequizando": request.form.get("emailCatequizando"),
            "telefonoCatequizando": request.form.get("telefonoCatequizando"),
            "direccionCatequizando": request.form.get("direccionCatequizando"),
            "nombrePadre": request.form.get("nombrePadre"),
            "nombreMadre": request.form.get("nombreMadre"),
            "estado": request.form.get("estado", "Activo"),
            "created_at": datetime.utcnow()
        }

        col.insert_one(doc)
        flash("Catequizando registrado correctamente", "success")
        return redirect(url_for("lista_catequizandos"))

    return render_template("catequizando_form.html", c=None)

# Editar catequizando
@app.route('/catequizando/editar/<id>', methods=['GET', 'POST'])
def editar_catequizando(id):
    col = get_collection("catequizandos")
    try:
        obj = col.find_one({"_id": ObjectId(id)})
    except:
        flash("ID inválido", "danger")
        return redirect(url_for("lista_catequizandos"))

    if request.method == 'POST':
        col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nombreCatequizando": request.form.get("nombreCatequizando"),
                "apellidoCatequizando": request.form.get("apellidoCatequizando"),
                "fechaNacimientoCatequizando": request.form.get("fechaNacimientoCatequizando"),
                "genero": request.form.get("genero"),
                "direccionCatequizando": request.form.get("direccionCatequizando"),
                "telefonoCatequizando": request.form.get("telefonoCatequizando"),
                "emailCatequizando": request.form.get("emailCatequizando"),
                "nombrePadre": request.form.get("nombrePadre"),
                "nombreMadre": request.form.get("nombreMadre"),
                "estado": request.form.get("estado")
            }}
        )
        flash("Catequizando actualizado", "success")
        return redirect(url_for("lista_catequizandos"))

    return render_template("catequizando_form.html", c=obj)


# Borrar catequizando
@app.route('/catequizando/borrar/<id>', methods=['POST'])
def borrar_catequizando(id):
    col = get_collection("catequizandos")
    col.delete_one({"_id": ObjectId(id)})
    flash("Catequizando eliminado", "success")
    return redirect(url_for("lista_catequizandos"))

# -------- CATEQUISTAS --------

@app.route('/catequista')
def lista_catequistas():
    col = get_collection("catequistas")
    col_usuarios = get_collection("usuarios")

    # Traemos todos los catequistas y usuarios
    catequistas = list(col.find())
    usuarios = {u["usuarioId"]: u for u in col_usuarios.find()}

    # Añadimos info de usuario si existe
    for c in catequistas:
        u = usuarios.get(c.get("Usuario_usuarioId"))
        if u:
            c["nombre"] = c.get("nombre") or u.get("nombreUsu")
            c["apellido"] = c.get("apellido") or u.get("apellidoUsu")

    return render_template("catequista_list.html", catequistas=catequistas)


@app.route('/catequista/nuevo', methods=['GET', 'POST'])
def nuevo_catequista():
    col_catequistas = get_collection("catequistas")
    col_usuarios = get_collection("usuarios")

    if request.method == 'POST':
        usuario_id = request.form.get("Usuario_usuarioId")
        usuario_id = int(usuario_id) if usuario_id else None

        # Generar catequistaId incremental
        ultimo = col_catequistas.find_one(sort=[("catequistaId", -1)])
        nuevo_id = (ultimo["catequistaId"] + 1) if ultimo else 1

        doc = {
            "catequistaId": nuevo_id,
            "nombre": request.form.get("nombre") or None,
            "apellido": request.form.get("apellido") or None,
            "telefonoCatequista": request.form.get("telefonoCatequista"),
            "Usuario_usuarioId": usuario_id
        }

        col_catequistas.insert_one(doc)
        flash("Catequista registrado correctamente", "success")
        return redirect(url_for("lista_catequistas"))

    usuarios = list(col_usuarios.find())
    return render_template("catequista_form.html", usuarios=usuarios, c=None)


@app.route('/catequista/editar/<int:id>', methods=['GET', 'POST'])
def editar_catequista(id):
    col_catequistas = get_collection("catequistas")
    col_usuarios = get_collection("usuarios")
    c = col_catequistas.find_one({"catequistaId": id})

    if not c:
        flash("Catequista no encontrado", "warning")
        return redirect(url_for("lista_catequistas"))

    if request.method == 'POST':
        usuario_id = request.form.get("Usuario_usuarioId")
        usuario_id = int(usuario_id) if usuario_id else None

        col_catequistas.update_one(
            {"catequistaId": id},
            {"$set": {
                "nombre": request.form.get("nombre") or None,
                "apellido": request.form.get("apellido") or None,
                "telefonoCatequista": request.form.get("telefonoCatequista"),
                "Usuario_usuarioId": usuario_id
            }}
        )
        flash("Catequista actualizado", "success")
        return redirect(url_for("lista_catequistas"))

    usuarios = list(col_usuarios.find())
    return render_template("catequista_form.html", usuarios=usuarios, c=c)


@app.route('/catequista/borrar/<int:id>', methods=['POST'])
def borrar_catequista(id):
    get_collection("catequistas").delete_one({"catequistaId": id})
    flash("Catequista eliminado", "success")
    return redirect(url_for("lista_catequistas"))

# -------- PARROQUIAS --------

@app.route('/parroquia')
def lista_parroquias():
    col = get_collection("parroquias")
    parroquias = list(col.find())
    return render_template("parroquia_list.html", parroquias=parroquias)


@app.route('/parroquia/nuevo', methods=['GET', 'POST'])
def nueva_parroquia():
    col = get_collection("parroquias")

    if request.method == 'POST':
        # Generar parroquiaID incremental
        ultimo = col.find_one(sort=[("parroquiaID", -1)])
        nuevo_id = (ultimo["parroquiaID"] + 1) if ultimo else 1

        doc = {
            "parroquiaID": nuevo_id,
            "nombreParro": request.form.get("nombreParro"),
            "direccionParro": request.form.get("direccionParro"),
            "telefonoParro": request.form.get("telefonoParro"),
            "emailParro": request.form.get("emailParro")
        }

        col.insert_one(doc)
        flash("Parroquia registrada correctamente", "success")
        return redirect(url_for("lista_parroquias"))

    return render_template("parroquia_form.html", p=None)


@app.route('/parroquia/editar/<int:id>', methods=['GET', 'POST'])
def editar_parroquia(id):
    col = get_collection("parroquias")
    p = col.find_one({"parroquiaID": id})

    if not p:
        flash("Parroquia no encontrada", "warning")
        return redirect(url_for("lista_parroquias"))

    if request.method == 'POST':
        col.update_one(
            {"parroquiaID": id},
            {"$set": {
                "nombreParro": request.form.get("nombreParro"),
                "direccionParro": request.form.get("direccionParro"),
                "telefonoParro": request.form.get("telefonoParro"),
                "emailParro": request.form.get("emailParro")
            }}
        )
        flash("Parroquia actualizada", "success")
        return redirect(url_for("lista_parroquias"))

    return render_template("parroquia_form.html", p=p)


@app.route('/parroquia/borrar/<int:id>', methods=['POST'])
def borrar_parroquia(id):
    get_collection("parroquias").delete_one({"parroquiaID": id})
    flash("Parroquia eliminada", "success")
    return redirect(url_for("lista_parroquias"))

# ---------- INSCRIPCIONES ----------
@app.route('/inscripcion')
def lista_inscripciones():
    col = get_collection("inscripciones")
    inscripciones = list(col.find())

    # Vamos a traer los datos relacionados para mostrar
    for i in inscripciones:
        # Catequizando
        c = get_collection("catequizandos").find_one({"catequizandoId": i["Catequizando_catequizandoId"]})
        i["catequizando"] = c

        # Parroquia
        p = get_collection("parroquias").find_one({"parroquiaID": i["Parroquia_parroquiaID"]})
        i["parroquia"] = p

        # Nivel
        n = get_collection("niveles").find_one({"nivelId": i["Nivel_nivelId"]})
        i["nivel"] = n

        # Catequista
        ct = get_collection("catequistas").find_one({"catequistaId": i["Catequista_catequistaId"]})
        if ct:
            u = get_collection("usuarios").find_one({"usuarioId": ct.get("Usuario_usuarioId")})
            ct["usuario"] = u
        i["catequista"] = ct

    return render_template("inscripcion_list.html", inscripciones=inscripciones)


@app.route('/inscripcion/nueva', methods=['GET', 'POST'])
def nueva_inscripcion():
    col_catequizandos = get_collection("catequizandos")
    col_parroquias = get_collection("parroquias")
    col_niveles = get_collection("niveles")
    col_catequistas = get_collection("catequistas")
    col_usuarios = get_collection("usuarios")
    col_inscripciones = get_collection("inscripciones")

    catequizandos = list(col_catequizandos.find())
    parroquias = list(col_parroquias.find())
    niveles = list(col_niveles.find())
    catequistas = list(col_catequistas.find())
    usuarios = list(col_usuarios.find())

    if request.method == 'POST':
        doc = {
            "Catequizando_catequizandoId": int(request.form.get("catequizandoId")),
            "Parroquia_parroquiaID": int(request.form.get("parroquiaId")),
            "Nivel_nivelId": int(request.form.get("nivelId")),
            "Catequista_catequistaId": int(request.form.get("catequistaId")) if request.form.get("catequistaId") else None,
            "cicloInicio": request.form.get("cicloInicio"),
            "cicloFin": request.form.get("cicloFin"),
            "fechaInscripcion": request.form.get("fechaInscripcion"),
            "certificadoGenerado": "No",
            "created_at": datetime.utcnow()
        }

        col_inscripciones.insert_one(doc)
        flash("Inscripción creada correctamente", "success")
        return redirect(url_for("index"))

    return render_template(
        "inscripcion_form.html",
        catequizandos=catequizandos,
        parroquias=parroquias,
        niveles=niveles,
        catequistas=catequistas,
        usuarios=usuarios,
        inscripcion=None
    )


# Editar inscripcion
@app.route('/inscripcion/editar/<id>', methods=['GET', 'POST'])
def editar_inscripcion(id):
    col_inscripciones = get_collection("inscripciones")
    id = int(id)  # Usar inscripcionId

    ins = col_inscripciones.find_one({"inscripcionId": id})
    if not ins:
        flash("Inscripción no encontrada", "warning")
        return redirect(url_for("lista_inscripciones"))

    if request.method == 'POST':
        col_inscripciones.update_one(
            {"inscripcionId": id},
            {"$set": {
                "Catequizando_catequizandoId": int(request.form.get("catequizandoId")),
                "Parroquia_parroquiaID": int(request.form.get("parroquiaId")),
                "Nivel_nivelId": int(request.form.get("nivelId")),
                "Catequista_catequistaId": int(request.form.get("catequistaId")),
                "cicloInicio": request.form.get("cicloInicio"),
                "cicloFin": request.form.get("cicloFin"),
                "fechaInscripcion": request.form.get("fechaInscripcion"),
                "certificadoGenerado": request.form.get("certificadoGenerado") == "True"
            }}
        )
        flash("Inscripción actualizada", "success")
        return redirect(url_for("lista_inscripciones"))

    # Obtener listas para selects
    catequizandos = list(get_collection("catequizandos").find())
    parroquias = list(get_collection("parroquias").find())
    niveles = list(get_collection("niveles").find())
    catequistas = list(get_collection("catequistas").find())

    return render_template("inscripcion_form.html",
                        i=ins,
                        catequizandos=catequizandos,
                        parroquias=parroquias,
                        niveles=niveles,
                        catequistas=catequistas)


# Borrar inscripcion
@app.route('/inscripcion/borrar/<id>', methods=['POST'])
def borrar_inscripcion(id):
    col = get_collection("inscripciones")
    col.delete_one({"inscripcionId": int(id)})
    flash("Inscripción eliminada", "success")
    return redirect(url_for("lista_inscripciones"))


# -------- NIVELES --------

@app.route('/nivel')
def lista_niveles():
    col = get_collection("niveles")
    niveles = list(col.find())
    return render_template("nivel_list.html", niveles=niveles)


@app.route('/nivel/nuevo', methods=['GET', 'POST'])
def nuevo_nivel():
    col = get_collection("niveles")

    if request.method == 'POST':
        nombre = request.form.get("nombreNivel")
        descripcion = request.form.get("descripcion")

        if not nombre:
            flash("El nombre del nivel es obligatorio", "warning")
            return redirect(url_for("nuevo_nivel"))

        # Generar nivelId incremental
        ultimo = col.find_one(sort=[("nivelId", -1)])
        nuevo_id = (ultimo["nivelId"] + 1) if ultimo else 1

        doc = {
            "nivelId": nuevo_id,
            "nombreNivel": nombre,
            "descripcion": descripcion
        }

        col.insert_one(doc)
        flash("Nivel creado correctamente", "success")
        return redirect(url_for("lista_niveles"))

    return render_template("nivel_form.html", n=None)


@app.route('/nivel/editar/<int:id>', methods=['GET', 'POST'])
def editar_nivel(id):
    col = get_collection("niveles")
    nivel = col.find_one({"nivelId": id})

    if not nivel:
        flash("Nivel no encontrado", "warning")
        return redirect(url_for("lista_niveles"))

    if request.method == 'POST':
        col.update_one(
            {"nivelId": id},
            {"$set": {
                "nombreNivel": request.form.get("nombreNivel"),
                "descripcion": request.form.get("descripcion")
            }}
        )
        flash("Nivel actualizado correctamente", "success")
        return redirect(url_for("lista_niveles"))

    return render_template("nivel_form.html", n=nivel)


@app.route('/nivel/borrar/<int:id>', methods=['POST'])
def borrar_nivel(id):
    get_collection("niveles").delete_one({"nivelId": id})
    flash("Nivel eliminado correctamente", "success")
    return redirect(url_for("lista_niveles"))

# -------- USUARIOS --------

@app.route('/usuario')
def lista_usuarios():
    col = get_collection("usuarios")
    usuarios = list(col.find())

    # Obtener parroquias y roles para mostrar nombres
    parroquias_col = get_collection("parroquias")
    roles_col = get_collection("roles")

    parroquias = {p["parroquiaID"]: p["nombreParro"] for p in parroquias_col.find()}
    roles = {r["rolId"]: r["nombreRol"] for r in roles_col.find()}

    return render_template("usuario_list.html", usuarios=usuarios, parroquias=parroquias, roles=roles)


@app.route('/usuario/nuevo', methods=['GET', 'POST'])
def nuevo_usuario():
    parroquias = list(get_collection("parroquias").find())
    roles = list(get_collection("roles").find())

    if request.method == 'POST':
        nombre = request.form.get("nombreUsu")
        apellido = request.form.get("apellidoUsu")
        email = request.form.get("emailUsu")
        parroquiaId = int(request.form.get("Parroquia_parroquiaID"))
        rolId = int(request.form.get("Rol_rolId"))

        if not nombre or not apellido:
            flash("Nombre y apellido son obligatorios", "warning")
            return redirect(url_for("nuevo_usuario"))

        col = get_collection("usuarios")
        ultimo = col.find_one(sort=[("usuarioId", -1)])
        nuevo_id = (ultimo["usuarioId"] + 1) if ultimo else 1

        doc = {
            "usuarioId": nuevo_id,
            "nombreUsu": nombre,
            "apellidoUsu": apellido,
            "emailUsu": email,
            "Parroquia_parroquiaID": parroquiaId,
            "Rol_rolId": rolId
        }

        col.insert_one(doc)
        flash("Usuario creado correctamente", "success")
        return redirect(url_for("lista_usuarios"))

    return render_template("usuario_form.html", u=None, parroquias=parroquias, roles=roles)


@app.route('/usuario/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    col = get_collection("usuarios")
    usuario = col.find_one({"usuarioId": id})

    if not usuario:
        flash("Usuario no encontrado", "warning")
        return redirect(url_for("lista_usuarios"))

    parroquias = list(get_collection("parroquias").find())
    roles = list(get_collection("roles").find())

    if request.method == 'POST':
        col.update_one(
            {"usuarioId": id},
            {"$set": {
                "nombreUsu": request.form.get("nombreUsu"),
                "apellidoUsu": request.form.get("apellidoUsu"),
                "emailUsu": request.form.get("emailUsu"),
                "Parroquia_parroquiaID": int(request.form.get("Parroquia_parroquiaID")),
                "Rol_rolId": int(request.form.get("Rol_rolId"))
            }}
        )
        flash("Usuario actualizado correctamente", "success")
        return redirect(url_for("lista_usuarios"))

    return render_template("usuario_form.html", u=usuario, parroquias=parroquias, roles=roles)


@app.route('/usuario/borrar/<int:id>', methods=['POST'])
def borrar_usuario(id):
    get_collection("usuarios").delete_one({"usuarioId": id})
    flash("Usuario eliminado correctamente", "success")
    return redirect(url_for("lista_usuarios"))

# -------- ROLES --------

@app.route('/rol')
def lista_roles():
    col = get_collection("roles")
    roles = list(col.find())
    return render_template("rol_list.html", roles=roles)


@app.route('/rol/nuevo', methods=['GET', 'POST'])
def nuevo_rol():
    if request.method == 'POST':
        nombreRol = request.form.get("nombreRol")
        if not nombreRol:
            flash("El nombre del rol es obligatorio", "warning")
            return redirect(url_for("nuevo_rol"))

        col = get_collection("roles")
        ultimo = col.find_one(sort=[("rolId", -1)])
        nuevo_id = (ultimo["rolId"] + 1) if ultimo else 1

        col.insert_one({
            "rolId": nuevo_id,
            "nombreRol": nombreRol
        })
        flash("Rol creado correctamente", "success")
        return redirect(url_for("lista_roles"))

    return render_template("rol_form.html", r=None)


@app.route('/rol/editar/<int:id>', methods=['GET', 'POST'])
def editar_rol(id):
    col = get_collection("roles")
    rol = col.find_one({"rolId": id})

    if not rol:
        flash("Rol no encontrado", "warning")
        return redirect(url_for("lista_roles"))

    if request.method == 'POST':
        col.update_one(
            {"rolId": id},
            {"$set": {"nombreRol": request.form.get("nombreRol")}}
        )
        flash("Rol actualizado correctamente", "success")
        return redirect(url_for("lista_roles"))

    return render_template("rol_form.html", r=rol)


@app.route('/rol/borrar/<int:id>', methods=['POST'])
def borrar_rol(id):
    get_collection("roles").delete_one({"rolId": id})
    flash("Rol eliminado correctamente", "success")
    return redirect(url_for("lista_roles"))

# ---------- EVALUACIONES ----------

@app.route('/evaluacion')
def lista_evaluaciones():
    col = get_collection("evaluaciones")
    evaluaciones = list(col.find())
    return render_template("evaluacion_list.html", evaluaciones=evaluaciones)


@app.route('/evaluacion/nueva', methods=['GET', 'POST'])
def nueva_evaluacion():
    col_catequizandos = get_collection("catequizandos")
    col_niveles = get_collection("niveles")
    catequizandos = list(col_catequizandos.find())
    niveles = list(col_niveles.find())

    if request.method == 'POST':
        doc = {
            "evaluacionId": int(request.form.get("evaluacionId")),
            "catequizandoId": ObjectId(request.form.get("catequizandoId")),
            "nivelId": ObjectId(request.form.get("nivelId")),
            "fechaEvaluacion": request.form.get("fechaEvaluacion"),
            "nota": float(request.form.get("nota")),
            "observaciones": request.form.get("observaciones"),
            "created_at": datetime.utcnow()
        }
        get_collection("evaluaciones").insert_one(doc)
        flash("Evaluación registrada correctamente", "success")
        return redirect(url_for("lista_evaluaciones"))

    return render_template("evaluacion_form.html", e=None, catequizandos=catequizandos, niveles=niveles)


@app.route('/evaluacion/editar/<id>', methods=['GET', 'POST'])
def editar_evaluacion(id):
    col = get_collection("evaluaciones")
    col_catequizandos = get_collection("catequizandos")
    col_niveles = get_collection("niveles")

    try:
        e = col.find_one({"_id": ObjectId(id)})
    except:
        flash("ID inválido", "danger")
        return redirect(url_for("lista_evaluaciones"))

    catequizandos = list(col_catequizandos.find())
    niveles = list(col_niveles.find())

    if request.method == 'POST':
        col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "catequizandoId": ObjectId(request.form.get("catequizandoId")),
                "nivelId": ObjectId(request.form.get("nivelId")),
                "fechaEvaluacion": request.form.get("fechaEvaluacion"),
                "nota": float(request.form.get("nota")),
                "observaciones": request.form.get("observaciones")
            }}
        )
        flash("Evaluación actualizada", "success")
        return redirect(url_for("lista_evaluaciones"))

    return render_template("evaluacion_form.html", e=e, catequizandos=catequizandos, niveles=niveles)


@app.route('/evaluacion/borrar/<id>', methods=['POST'])
def borrar_evaluacion(id):
    col = get_collection("evaluaciones")
    col.delete_one({"_id": ObjectId(id)})
    flash("Evaluación eliminada", "success")
    return redirect(url_for("lista_evaluaciones"))

# ---------- ASISTENCIA ----------

@app.route('/asistencia')
def lista_asistencias():
    col = get_collection("asistencias")
    asistencias = list(col.find())
    return render_template("asistencia_list.html", asistencias=asistencias)


@app.route('/asistencia/nueva', methods=['GET', 'POST'])
def nueva_asistencia():
    col_catequizandos = get_collection("catequizandos")
    col_niveles = get_collection("niveles")
    catequizandos = list(col_catequizandos.find())
    niveles = list(col_niveles.find())

    if request.method == 'POST':
        doc = {
            "asistenciaId": int(request.form.get("asistenciaId")),
            "catequizandoId": ObjectId(request.form.get("catequizandoId")),
            "nivelId": ObjectId(request.form.get("nivelId")),
            "fecha": request.form.get("fecha"),
            "presente": request.form.get("presente") == "on",
            "observaciones": request.form.get("observaciones"),
            "created_at": datetime.utcnow()
        }
        get_collection("asistencias").insert_one(doc)
        flash("Asistencia registrada correctamente", "success")
        return redirect(url_for("lista_asistencias"))

    return render_template("asistencia_form.html", a=None, catequizandos=catequizandos, niveles=niveles)


@app.route('/asistencia/editar/<id>', methods=['GET', 'POST'])
def editar_asistencia(id):
    col = get_collection("asistencias")
    col_catequizandos = get_collection("catequizandos")
    col_niveles = get_collection("niveles")

    try:
        a = col.find_one({"_id": ObjectId(id)})
    except:
        flash("ID inválido", "danger")
        return redirect(url_for("lista_asistencias"))

    catequizandos = list(col_catequizandos.find())
    niveles = list(col_niveles.find())

    if request.method == 'POST':
        col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "catequizandoId": ObjectId(request.form.get("catequizandoId")),
                "nivelId": ObjectId(request.form.get("nivelId")),
                "fecha": request.form.get("fecha"),
                "presente": request.form.get("presente") == "on",
                "observaciones": request.form.get("observaciones")
            }}
        )
        flash("Asistencia actualizada", "success")
        return redirect(url_for("lista_asistencias"))

    return render_template("asistencia_form.html", a=a, catequizandos=catequizandos, niveles=niveles)


@app.route('/asistencia/borrar/<id>', methods=['POST'])
def borrar_asistencia(id):
    col = get_collection("asistencias")
    col.delete_one({"_id": ObjectId(id)})
    flash("Asistencia eliminada", "success")
    return redirect(url_for("lista_asistencias"))


# ---------- SACRAMENTO ----------

@app.route('/sacramento')
def lista_sacramentos():
    col = get_collection("sacramentos")
    sacramentos = list(col.find())
    return render_template("sacramento_list.html", sacramentos=sacramentos)


@app.route('/sacramento/nuevo', methods=['GET', 'POST'])
def nuevo_sacramento():
    catequizandos = list(get_collection("catequizandos").find())

    if request.method == 'POST':
        doc = {
            "sacramentoId": int(request.form.get("sacramentoId")),
            "catequizandoId": ObjectId(request.form.get("catequizandoId")),
            "tipoSacramento": request.form.get("tipoSacramento"),
            "fecha": request.form.get("fecha"),
            "lugar": request.form.get("lugar"),
            "ministro": request.form.get("ministro"),
            "observaciones": request.form.get("observaciones"),
            "created_at": datetime.utcnow()
        }
        get_collection("sacramentos").insert_one(doc)
        flash("Sacramento registrado correctamente", "success")
        return redirect(url_for("lista_sacramentos"))

    return render_template("sacramento_form.html", s=None, catequizandos=catequizandos)


@app.route('/sacramento/editar/<id>', methods=['GET', 'POST'])
def editar_sacramento(id):
    col = get_collection("sacramentos")
    catequizandos = list(get_collection("catequizandos").find())

    try:
        s = col.find_one({"_id": ObjectId(id)})
    except:
        flash("ID inválido", "danger")
        return redirect(url_for("lista_sacramentos"))

    if request.method == 'POST':
        col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "catequizandoId": ObjectId(request.form.get("catequizandoId")),
                "tipoSacramento": request.form.get("tipoSacramento"),
                "fecha": request.form.get("fecha"),
                "lugar": request.form.get("lugar"),
                "ministro": request.form.get("ministro"),
                "observaciones": request.form.get("observaciones")
            }}
        )
        flash("Sacramento actualizado", "success")
        return redirect(url_for("lista_sacramentos"))

    return render_template("sacramento_form.html", s=s, catequizandos=catequizandos)


@app.route('/sacramento/borrar/<id>', methods=['POST'])
def borrar_sacramento(id):
    col = get_collection("sacramentos")
    col.delete_one({"_id": ObjectId(id)})
    flash("Sacramento eliminado", "success")
    return redirect(url_for("lista_sacramentos"))
 # ---------- TRASLADO ----------

@app.route('/traslado')
def lista_traslados():
    col = get_collection("traslados")
    traslados = list(col.find())
    return render_template("traslado_list.html", traslados=traslados)


@app.route('/traslado/nuevo', methods=['GET', 'POST'])
def nuevo_traslado():
    catequizandos = list(get_collection("catequizandos").find())

    if request.method == 'POST':
        doc = {
            "trasladoId": int(request.form.get("trasladoId")),
            "catequizandoId": ObjectId(request.form.get("catequizandoId")),
            "fecha": request.form.get("fecha"),
            "motivo": request.form.get("motivo"),
            "parroquiaOrigen": request.form.get("parroquiaOrigen"),
            "parroquiaDestino": request.form.get("parroquiaDestino"),
            "observaciones": request.form.get("observaciones"),
            "created_at": datetime.utcnow()
        }
        get_collection("traslados").insert_one(doc)
        flash("Traslado registrado correctamente", "success")
        return redirect(url_for("lista_traslados"))

    return render_template("traslado_form.html", t=None, catequizandos=catequizandos)


@app.route('/traslado/editar/<id>', methods=['GET', 'POST'])
def editar_traslado(id):
    col = get_collection("traslados")
    catequizandos = list(get_collection("catequizandos").find())

    try:
        t = col.find_one({"_id": ObjectId(id)})
    except:
        flash("ID inválido", "danger")
        return redirect(url_for("lista_traslados"))

    if request.method == 'POST':
        col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "catequizandoId": ObjectId(request.form.get("catequizandoId")),
                "fecha": request.form.get("fecha"),
                "motivo": request.form.get("motivo"),
                "parroquiaOrigen": request.form.get("parroquiaOrigen"),
                "parroquiaDestino": request.form.get("parroquiaDestino"),
                "observaciones": request.form.get("observaciones")
            }}
        )
        flash("Traslado actualizado", "success")
        return redirect(url_for("lista_traslados"))

    return render_template("traslado_form.html", t=t, catequizandos=catequizandos)


@app.route('/traslado/borrar/<id>', methods=['POST'])
def borrar_traslado(id):
    col = get_collection("traslados")
    col.delete_one({"_id": ObjectId(id)})
    flash("Traslado eliminado", "success")
    return redirect(url_for("lista_traslados"))

# ---------- NOTIFICACIONES ----------

@app.route('/notificacion')
def lista_notificaciones():
    notis = list(get_collection("notificaciones").find())
    return render_template("notificacion_list.html", notificaciones=notis)


@app.route('/notificacion/nuevo', methods=['GET', 'POST'])
def nueva_notificacion():
    usuarios = list(get_collection("usuarios").find())
    catequizandos = list(get_collection("catequizandos").find())
    catequistas = list(get_collection("catequistas").find())

    if request.method == 'POST':
        doc = {
            "notificacionId": int(request.form.get("notificacionId")),
            "titulo": request.form.get("titulo"),
            "mensaje": request.form.get("mensaje"),
            "fecha": request.form.get("fecha"),
            "usuarioId": ObjectId(request.form.get("usuarioId")) if request.form.get("usuarioId") else None,
            "catequizandoId": ObjectId(request.form.get("catequizandoId")) if request.form.get("catequizandoId") else None,
            "catequistaId": ObjectId(request.form.get("catequistaId")) if request.form.get("catequistaId") else None,
            "leida": False,
            "created_at": datetime.utcnow()
        }
        get_collection("notificaciones").insert_one(doc)
        flash("Notificación registrada", "success")
        return redirect(url_for("lista_notificaciones"))

    return render_template(
        "notificacion_form.html",
        n=None,
        usuarios=usuarios,
        catequizandos=catequizandos,
        catequistas=catequistas
    )


@app.route('/notificacion/editar/<id>', methods=['GET', 'POST'])
def editar_notificacion(id):
    col = get_collection("notificaciones")
    usuarios = list(get_collection("usuarios").find())
    catequizandos = list(get_collection("catequizandos").find())
    catequistas = list(get_collection("catequistas").find())

    try:
        n = col.find_one({"_id": ObjectId(id)})
    except:
        flash("ID inválido", "danger")
        return redirect(url_for("lista_notificaciones"))

    if request.method == 'POST':
        col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "titulo": request.form.get("titulo"),
                "mensaje": request.form.get("mensaje"),
                "fecha": request.form.get("fecha"),
                "usuarioId": ObjectId(request.form.get("usuarioId")) if request.form.get("usuarioId") else None,
                "catequizandoId": ObjectId(request.form.get("catequizandoId")) if request.form.get("catequizandoId") else None,
                "catequistaId": ObjectId(request.form.get("catequistaId")) if request.form.get("catequistaId") else None,
                "leida": request.form.get("leida") == "on"
            }}
        )
        flash("Notificación actualizada", "success")
        return redirect(url_for("lista_notificaciones"))

    return render_template(
        "notificacion_form.html",
        n=n,
        usuarios=usuarios,
        catequizandos=catequizandos,
        catequistas=catequistas
    )


@app.route('/notificacion/borrar/<id>', methods=['POST'])
def borrar_notificacion(id):
    col = get_collection("notificaciones")
    col.delete_one({"_id": ObjectId(id)})
    flash("Notificación eliminada", "success")
    return redirect(url_for("lista_notificaciones"))


# ---------- DOCUMENTOS ----------

@app.route('/documento')
def lista_documentos():
    docs = list(get_collection("documentos").find())
    return render_template("documento_list.html", documentos=docs)


@app.route('/documento/nuevo', methods=['GET', 'POST'])
def nuevo_documento():
    catequizandos = list(get_collection("catequizandos").find())
    catequistas = list(get_collection("catequistas").find())

    if request.method == 'POST':
        doc = {
            "documentoId": int(request.form.get("documentoId")),
            "nombre": request.form.get("nombre"),
            "tipo": request.form.get("tipo"),
            "fechaEmision": request.form.get("fechaEmision"),
            "catequizandoId": ObjectId(request.form.get("catequizandoId")) if request.form.get("catequizandoId") else None,
            "catequistaId": ObjectId(request.form.get("catequistaId")) if request.form.get("catequistaId") else None,
            "archivo": request.form.get("archivo"),
            "created_at": datetime.utcnow()
        }
        get_collection("documentos").insert_one(doc)
        flash("Documento registrado", "success")
        return redirect(url_for("lista_documentos"))

    return render_template(
        "documento_form.html",
        d=None,
        catequizandos=catequizandos,
        catequistas=catequistas
    )


@app.route('/documento/editar/<id>', methods=['GET', 'POST'])
def editar_documento(id):
    col = get_collection("documentos")
    catequizandos = list(get_collection("catequizandos").find())
    catequistas = list(get_collection("catequistas").find())

    try:
        d = col.find_one({"_id": ObjectId(id)})
    except:
        flash("ID inválido", "danger")
        return redirect(url_for("lista_documentos"))

    if request.method == 'POST':
        col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nombre": request.form.get("nombre"),
                "tipo": request.form.get("tipo"),
                "fechaEmision": request.form.get("fechaEmision"),
                "catequizandoId": ObjectId(request.form.get("catequizandoId")) if request.form.get("catequizandoId") else None,
                "catequistaId": ObjectId(request.form.get("catequistaId")) if request.form.get("catequistaId") else None,
                "archivo": request.form.get("archivo")
            }}
        )
        flash("Documento actualizado", "success")
        return redirect(url_for("lista_documentos"))

    return render_template(
        "documento_form.html",
        d=d,
        catequizandos=catequizandos,
        catequistas=catequistas
    )


@app.route('/documento/borrar/<id>', methods=['POST'])
def borrar_documento(id):
    col = get_collection("documentos")
    col.delete_one({"_id": ObjectId(id)})
    flash("Documento eliminado", "success")
    return redirect(url_for("lista_documentos"))

# ---------- CERTIFICADOS ----------

@app.route('/certificado')
def lista_certificados():
    col_cert = get_collection("certificados")
    col_ins = get_collection("inscripciones")
    col_cateq = get_collection("catequizandos")
    col_niveles = get_collection("niveles")
    col_parroquias = get_collection("parroquias")

    certificados = list(col_cert.find())

    for c in certificados:
        # 1️⃣ Inscripción
        ins = col_ins.find_one({
            "inscripcionId": c.get("Inscripcion_inscripcionId")
        })

        c["inscripcion"] = ins

        if ins:
            # 2️⃣ Catequizando
            c["catequizando"] = col_cateq.find_one({
                "catequizandoId": ins.get("Catequizando_catequizandoId")
            })

            # 3️⃣ Nivel
            c["nivel"] = col_niveles.find_one({
                "nivelId": ins.get("Nivel_nivelId")
            })

            # 4️⃣ Parroquia
            c["parroquia"] = col_parroquias.find_one({
                "parroquiaID": ins.get("Parroquia_parroquiaID")
            })
        else:
            c["catequizando"] = None
            c["nivel"] = None
            c["parroquia"] = None

    return render_template(
        "certificado_list.html",
        certificados=certificados
    )


@app.route('/certificado/nuevo', methods=['GET', 'POST'])
def nuevo_certificado():
    catequizandos = list(get_collection("catequizandos").find())
    niveles = list(get_collection("niveles").find())
    parroquias = list(get_collection("parroquias").find())

    if request.method == 'POST':
        cert = {
            "certificadoId": int(request.form.get("certificadoId")),
            "catequizandoId": ObjectId(request.form.get("catequizandoId")),
            "nivelId": ObjectId(request.form.get("nivelId")),
            "parroquiaId": ObjectId(request.form.get("parroquiaId")),
            "fechaEmision": request.form.get("fechaEmision"),
            "firmadoPor": request.form.get("firmadoPor"),
            "archivo": request.form.get("archivo"),
            "created_at": datetime.utcnow()
        }
        get_collection("certificados").insert_one(cert)
        flash("Certificado registrado", "success")
        return redirect(url_for("lista_certificados"))

    return render_template(
        "certificado_form.html",
        c=None,
        catequizandos=catequizandos,
        niveles=niveles,
        parroquias=parroquias
    )


@app.route('/certificado/editar/<id>', methods=['GET', 'POST'])
def editar_certificado(id):
    col = get_collection("certificados")
    catequizandos = list(get_collection("catequizandos").find())
    niveles = list(get_collection("niveles").find())
    parroquias = list(get_collection("parroquias").find())

    try:
        c = col.find_one({"_id": ObjectId(id)})
    except:
        flash("ID inválido", "danger")
        return redirect(url_for("lista_certificados"))

    if request.method == 'POST':
        col.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "catequizandoId": ObjectId(request.form.get("catequizandoId")),
                "nivelId": ObjectId(request.form.get("nivelId")),
                "parroquiaId": ObjectId(request.form.get("parroquiaId")),
                "fechaEmision": request.form.get("fechaEmision"),
                "firmadoPor": request.form.get("firmadoPor"),
                "archivo": request.form.get("archivo")
            }}
        )
        flash("Certificado actualizado", "success")
        return redirect(url_for("lista_certificados"))

    return render_template(
        "certificado_form.html",
        c=c,
        catequizandos=catequizandos,
        niveles=niveles,
        parroquias=parroquias
    )


@app.route('/certificado/borrar/<id>', methods=['POST'])
def borrar_certificado(id):
    col = get_collection("certificados")
    col.delete_one({"_id": ObjectId(id)})
    flash("Certificado eliminado", "success")
    return redirect(url_for("lista_certificados"))


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
