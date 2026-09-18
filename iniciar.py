"""Arranque de la versión portátil (pincho USB).

Estructura de la carpeta portátil:
    Iniciar GHCT.bat
    python/        Python embebido con todas las librerías
    aplicacion/    backend (app/, migrations/) y este archivo
    web/           frontend ya compilado
    datos/         base de datos (ghct.db) y clave de sesión
    copias/        copias de seguridad automáticas

Al arrancar: copia de seguridad de la base de datos, la pone al día con las
migraciones (por si la aplicación es más nueva que los datos), busca un
puerto libre, abre el navegador y sirve la aplicación hasta cerrar la
ventana.

Con --copia solo hace una copia de seguridad y termina.
"""

import datetime
import glob
import os
import shutil
import socket
import sqlite3
import sys
import threading
import webbrowser

APLICACION = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(APLICACION)
DATOS = os.path.join(RAIZ, "datos")
WEB = os.path.join(RAIZ, "web")
COPIAS = os.path.join(RAIZ, "copias")
BD = os.path.join(DATOS, "ghct.db")
COPIAS_AUTOMATICAS_A_GUARDAR = 30

os.makedirs(DATOS, exist_ok=True)
os.makedirs(COPIAS, exist_ok=True)
os.environ["GHCT_DATOS"] = DATOS
os.environ["GHCT_WEB"] = WEB
sys.path.insert(0, APLICACION)


def copia_de_seguridad(etiqueta):
    """Copia consistente con la API de copias de SQLite (vale aunque la base
    de datos esté abierta)."""
    if not os.path.exists(BD):
        return None
    marca = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(COPIAS, f"ghct_{marca}_{etiqueta}.db")
    origen = sqlite3.connect(BD)
    copia = sqlite3.connect(destino)
    with copia:
        origen.backup(copia)
    copia.close()
    origen.close()
    return destino


def limpiar_copias_automaticas():
    automaticas = sorted(glob.glob(os.path.join(COPIAS, "ghct_*_al_arrancar.db")))
    for vieja in automaticas[:-COPIAS_AUTOMATICAS_A_GUARDAR]:
        os.remove(vieja)


def tiene_migraciones(ruta):
    if not os.path.exists(ruta):
        return False
    con = sqlite3.connect(ruta)
    try:
        return con.execute("SELECT name FROM sqlite_master WHERE name = 'alembic_version'").fetchone() is not None
    finally:
        con.close()


def puerto_libre(desde=5000, hasta=5020):
    for puerto in range(desde, hasta + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", puerto))
                return puerto
            except OSError:
                continue
    raise SystemExit("No hay ningún puerto libre entre 5000 y 5020. Cierra otras aplicaciones y vuelve a intentarlo.")


def main():
    if "--copia" in sys.argv:
        destino = copia_de_seguridad("manual")
        print(f"Copia guardada en {destino}" if destino else "Todavía no hay base de datos que copiar.")
        return

    print("GHCT - Generador de horarios")
    print("Preparando... (desde un pincho puede tardar un poco la primera vez)")

    datos_existentes = tiene_migraciones(BD)
    copia_de_seguridad("al_arrancar")
    limpiar_copias_automaticas()

    from flask_migrate import stamp, upgrade

    from app import create_app

    app = create_app()
    migraciones = os.path.join(APLICACION, "migrations")
    with app.app_context():
        if datos_existentes:
            upgrade(directory=migraciones)
        else:
            # Base de datos nueva: create_app ya creó todas las tablas.
            stamp(directory=migraciones)

    puerto = int(os.environ.get("GHCT_PUERTO") or puerto_libre())
    url = f"http://localhost:{puerto}"
    if not os.environ.get("GHCT_SIN_NAVEGADOR"):
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    print()
    print(f"  La aplicación está en {url}")
    print("  NO CIERRES ESTA VENTANA mientras trabajas.")
    print("  Para terminar, cierra el navegador y después esta ventana.")
    print()

    from werkzeug.serving import run_simple

    run_simple("127.0.0.1", puerto, app, threaded=True, use_reloader=False, use_debugger=False)


if __name__ == "__main__":
    main()
