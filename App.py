from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Carpeta principal y base de datos
UPLOAD_FOLDER = "repositorio_imagenes"
DATABASE = "imagenes.db"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Categorías disponibles. Puedes modificar esta lista según tus necesidades.
CATEGORIAS = [
    "Eventos",
    "Parque de Sabaneta",
    "Sitios",
    "Fiestas",
    "Años",
    "Tejidos",
    "Otros",
]

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Carpeta para imágenes propias del diseño de la página, como logo o banner.
STATIC_FOLDER = "static"
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Valida si el archivo tiene una extensión permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    """Crea la conexión con SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea la tabla si no existe."""
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS imagenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            palabras_clave TEXT NOT NULL,
            filename TEXT NOT NULL,
            fecha_carga TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repositorio de Imágenes</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f4f6f8;
            color: #222;
        }
        header {
            background: #1f2937;
            color: white;
            padding: 28px 24px;
            text-align: center;
        }
        .header-logo {
            max-width: 180px;
            width: 100%;
            height: auto;
            margin-bottom: 14px;
        }
        .hero-image {
            width: 100%;
            max-height: 280px;
            object-fit: cover;
            border-radius: 18px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        main {
            max-width: 1100px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .card {
            background: white;
            padding: 22px;
            border-radius: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 12px;
        }
        input[type="text"], input[type="file"], select {
            width: 100%;
            padding: 11px;
            margin-top: 6px;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-sizing: border-box;
        }
        button {
            margin-top: 16px;
            background: #2563eb;
            color: white;
            border: none;
            padding: 12px 18px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #1d4ed8;
        }
        .search-row {
            display: grid;
            grid-template-columns: 1fr 240px auto;
            gap: 10px;
            align-items: end;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 18px;
        }
        .image-card {
            background: white;
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .image-card img {
            width: 100%;
            height: 190px;
            object-fit: cover;
        }
        .image-info {
            padding: 14px;
        }
        .category {
            display: inline-block;
            background: #dbeafe;
            color: #1e40af;
            padding: 6px 10px;
            margin-bottom: 8px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: bold;
        }
        .tag {
            display: inline-block;
            background: #e5e7eb;
            color: #374151;
            padding: 5px 9px;
            margin: 3px;
            border-radius: 999px;
            font-size: 12px;
        }
        .empty {
            text-align: center;
            padding: 30px;
            color: #666;
        }
        @media (max-width: 750px) {
            .search-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <img src="{{ url_for('static', filename='logo_sabaneta.png') }}" alt="Subdirección de Cultura - Municipio de Sabaneta" class="header-logo">
        <h1>Repositorio de Imágenes</h1>
        <p>Subdirección de Cultura - Municipio de Sabaneta</p>
        <p>Guarda imágenes, clasifícalas por categoría y encuéntralas por palabras clave</p>
    </header>

    <main>
        <img src="{{ url_for('static', filename='cultura_sabaneta.jpg') }}" alt="Imagen representativa de cultura en Sabaneta" class="hero-image">

        <section class="card">
            <h2>Cargar nueva imagen</h2>
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <label>Título de la imagen</label>
                <input type="text" name="titulo" placeholder="Ejemplo: Logo empresa, producto decorativo, diseño cliente" required>

                <label>Categoría / Carpeta</label>
                <select name="categoria" required>
                    {% for categoria in categorias %}
                        <option value="{{ categoria }}">{{ categoria }}</option>
                    {% endfor %}
                </select>

                <label>Palabras clave</label>
                <input type="text" name="palabras_clave" placeholder="Ejemplo: logo, dorado, bordado, cliente" required>

                <label>Seleccionar imagen</label>
                <input type="file" name="imagen" accept="image/*" required>

                <button type="submit">Guardar imagen</button>
            </form>
        </section>

        <section class="card">
            <h2>Buscar imágenes</h2>
            <form method="GET" action="/" class="search-row">
                <div>
                    <label>Palabra clave</label>
                    <input type="text" name="q" value="{{ query }}" placeholder="Buscar por título o palabra clave">
                </div>

                <div>
                    <label>Categoría</label>
                    <select name="categoria">
                        <option value="">Todas</option>
                        {% for categoria in categorias %}
                            <option value="{{ categoria }}" {% if categoria == categoria_filtro %}selected{% endif %}>{{ categoria }}</option>
                        {% endfor %}
                    </select>
                </div>

                <button type="submit">Buscar</button>
            </form>
        </section>

        <section>
            <h2>Resultados</h2>

            {% if imagenes %}
                <div class="gallery">
                    {% for imagen in imagenes %}
                        <article class="image-card">
                            <img src="{{ url_for('uploaded_file', categoria=imagen['categoria'], filename=imagen['filename']) }}" alt="{{ imagen['titulo'] }}">
                            <div class="image-info">
                                <span class="category">{{ imagen['categoria'] }}</span>
                                <h3>{{ imagen['titulo'] }}</h3>
                                <p><strong>Fecha:</strong> {{ imagen['fecha_carga'] }}</p>
                                <div>
                                    {% for palabra in imagen['palabras_clave'].split(',') %}
                                        <span class="tag">{{ palabra.strip() }}</span>
                                    {% endfor %}
                                </div>
                            </div>
                        </article>
                    {% endfor %}
                </div>
            {% else %}
                <div class="card empty">
                    No hay imágenes para mostrar.
                </div>
            {% endif %}
        </section>
    </main>
</body>
</html>
"""


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    categoria_filtro = request.args.get("categoria", "").strip()

    conn = get_db_connection()

    sql = "SELECT * FROM imagenes WHERE 1=1"
    params = []

    if query:
        search_pattern = f"%{query}%"
        sql += " AND (titulo LIKE ? OR palabras_clave LIKE ?)"
        params.extend([search_pattern, search_pattern])

    if categoria_filtro:
        sql += " AND categoria = ?"
        params.append(categoria_filtro)

    sql += " ORDER BY id DESC"

    imagenes = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template_string(
        HTML_TEMPLATE,
        imagenes=imagenes,
        query=query,
        categorias=CATEGORIAS,
        categoria_filtro=categoria_filtro,
    )


@app.route("/upload", methods=["POST"])
def upload_image():
    titulo = request.form.get("titulo", "").strip()
    categoria = request.form.get("categoria", "").strip()
    palabras_clave = request.form.get("palabras_clave", "").strip()
    file = request.files.get("imagen")

    if not titulo or not categoria or not palabras_clave or not file:
        return "Faltan datos para guardar la imagen", 400

    if categoria not in CATEGORIAS:
        return "La categoría seleccionada no es válida", 400

    if file.filename == "":
        return "No seleccionaste ninguna imagen", 400

    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{original_filename}"

        # Crea una carpeta física por categoría
        categoria_segura = secure_filename(categoria)
        category_folder = os.path.join(app.config["UPLOAD_FOLDER"], categoria_segura)
        os.makedirs(category_folder, exist_ok=True)

        filepath = os.path.join(category_folder, filename)
        file.save(filepath)

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO imagenes (titulo, categoria, palabras_clave, filename, fecha_carga)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                titulo,
                categoria_segura,
                palabras_clave,
                filename,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return "Formato de imagen no permitido", 400


@app.route("/repositorio_imagenes/<categoria>/<filename>")
def uploaded_file(categoria, filename):
    return send_from_directory(os.path.join(app.config["UPLOAD_FOLDER"], categoria), filename)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
