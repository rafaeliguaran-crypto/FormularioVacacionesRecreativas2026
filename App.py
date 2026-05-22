from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

HORARIOS = [
    "Martes 16 de Junio entre las 9:00 a. m. y 12:00 p. m.",
    "Martes 16 de Junio entre las 2:00 p. m. y 5:00 p. m.",
    "Miércoles 17 de Junio entre las 9:00 a. m. y 12:00 p. m.",
    "Miércoles 17 de Junio entre las 2:00 p. m. y 5:00 p. m.",
    "Jueves 18 de Junio entre las 9:00 a. m. y 12:00 p. m.",
    "Jueves 18 de Junio entre las 2:00 p. m. y 5:00 p. m.",
    "Viernes 19 de Junio entre las 9:00 a. m. y 12:00 p. m.",
    "Viernes 19 de Junio entre las 2:00 p. m. y 5:00 p. m."
]

def conectar_db():
    return sqlite3.connect("vacaciones_recreativas.db")

def crear_tabla():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autorizacion_datos TEXT NOT NULL,
            autorizacion_imagenes TEXT NOT NULL,
            tipo_documento TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            celular TEXT NOT NULL,
            correo TEXT NOT NULL,
            comunidad TEXT NOT NULL,
            espacio_adecuado TEXT NOT NULL,
            horario TEXT NOT NULL UNIQUE
        )
    """)

    conn.commit()
    conn.close()

def obtener_horarios_disponibles():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT horario FROM inscripciones")
    horarios_ocupados = [fila[0] for fila in cursor.fetchall()]

    conn.close()

    return [h for h in HORARIOS if h not in horarios_ocupados]

@app.route("/", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        datos = (
            request.form.get("autorizacion_datos"),
            request.form.get("autorizacion_imagenes"),
            request.form.get("tipo_documento"),
            request.form.get("numero_documento"),
            request.form.get("nombre_completo"),
            request.form.get("celular"),
            request.form.get("correo"),
            request.form.get("comunidad"),
            request.form.get("espacio_adecuado"),
            request.form.get("horario")
        )

        try:
            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO inscripciones (
                    autorizacion_datos,
                    autorizacion_imagenes,
                    tipo_documento,
                    numero_documento,
                    nombre_completo,
                    celular,
                    correo,
                    comunidad,
                    espacio_adecuado,
                    horario
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, datos)

            conn.commit()
            conn.close()

            return redirect(url_for("gracias"))

        except sqlite3.IntegrityError:
            return "Ese horario ya fue seleccionado por otra persona. Por favor vuelve al formulario y escoge otro horario disponible."

    horarios_disponibles = obtener_horarios_disponibles()
    return render_template("index.html", horarios=horarios_disponibles)

@app.route("/gracias")
def gracias():
    return render_template("gracias.html")

@app.route("/registros")
def registros():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inscripciones")
    datos = cursor.fetchall()

    conn.close()

    return render_template("registros.html", datos=datos)

if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)