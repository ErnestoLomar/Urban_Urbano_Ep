import sqlite3
from time import strftime
from datetime import datetime
import variables_globales
URI = "/home/pi/Urban_Urbano/db/rutas.db"
#URI = "rutas.db"

# Creando una tabla llamada chofer
tabla_chofer = '''CREATE TABLE IF NOT EXISTS chofer (
        chofer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100),
        foto VARCHAR(100),
        uuid VARCHAR(100)
)'''

tabla_pasajero = '''CREATE TABLE IF NOT EXISTS pasajero (
        pasajero_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100),
        foto VARCHAR(100),
        uuid VARCHAR(100)
)'''

tabla_asistencia = '''CREATE TABLE IF NOT EXISTS asistencia (
        asistencia_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pasajero_id INTEGER,
        fecha DATE,
        hora TIME,
        velocidad FLOAT,
        check_servidor VARCHAR(100) default 'NO',
        longitud float,
        latitud float,
        entrada INTEGER,
        folio INTEGER,
        folio_viaje VARCHAR(100),
        FOREIGN KEY (pasajero_id) REFERENCES pasajero(pasajero_id)
)'''

# Creando una tabla llamada ruta
tabla_rutas = '''CREATE TABLE IF NOT EXISTS rutas (
        ruta_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100),
        mapa VARCHAR(100),
        xi INTEGER,
        xf INTEGER,
        yi INTEGER,
        yf INTEGER,
        longitudi float,
        longitudf float,
        latitudi float,
        latitudf float
) '''

# Creación de una tabla llamada geocercas.
tabla_geocercas = '''CREATE TABLE IF NOT EXISTS geocercas (
        geocerca_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100),
        longitud float,
        latitud float,
        retraso_esperado Hour, 
        ruta_id INTEGER NOT NULL,
        FOREIGN KEY (ruta_id) REFERENCES rutas (ruta_id)
) '''

tabla_geocercas_historico = '''CREATE TABLE IF NOT EXISTS geocercas_historico (
        geocerca_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(100),
        longitud float,
        latitud float,
        retraso_esperado Hour,
        timepo_real Hour,
        ruta_id INTEGER NOT NULL,
)'''

tabla_cerrar_vuelta_chofer = '''CREATE TABLE IF NOT EXISTS cerrar_vuelta_chofer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chofer_id INTEGER,
        uid VARCHAR(100),
        folio_viaje VARCHAR(100),
        id_unidad INTEGER,
        check_servidor VARCHAR(100) default 'NO'
)'''

def crear_tabla_cerrar_vuelta_chofer():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_cerrar_vuelta_chofer)
    except Exception as e:
        print(e)

def guardar_cerrar_vuelta_chofer(chofer_id, uid, folio_viaje, id_unidad):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("INSERT INTO cerrar_vuelta_chofer (chofer_id, uid, folio_viaje, id_unidad) VALUES (?,?,?,?)", (chofer_id, uid, folio_viaje, id_unidad))
        con.commit()
    except Exception as e:
        print(e)

def obtener_cerrar_vuelta_chofer_no_enviados():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM cerrar_vuelta_chofer WHERE check_servidor = 'NO' LIMIT 10")
        return cur.fetchall()
    except Exception as e:
        print(e)

def actualizar_cerrar_vuelta_chofer_enviada(id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE cerrar_vuelta_chofer SET check_servidor = 'OK' WHERE id = ?", (id,))
        con.commit()
    except Exception as e:
        print(e)

def crear_tabla_chofer():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_chofer)
    except Exception as e:
        print(e)


def crear_tabla_rutas():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_rutas)
    except Exception as e:
        print(e)


def crear_tabla_geocercas():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        cur.execute(tabla_geocercas)
    except Exception as e:
        print(e)


def crear_tabla_pasajero():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_pasajero)
    except Exception as e:
        print(e)


def crear_tabla_asistencia():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_asistencia)
    except Exception as e:
        print(e)


crear_tabla_chofer()
crear_tabla_rutas()
crear_tabla_geocercas()
crear_tabla_pasajero()
crear_tabla_asistencia()


def guardar_chofer(nombre, foto, uuid):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO chofer (nombre, foto, uuid) VALUES (?, ?, ?)", (nombre, foto, uuid))
        con.commit()
    except Exception as e:
        print(e)


def guardar_ruta(nombre, mapa, xi, xf, yi, yf, longitudi, longitudf, latitudi, latitudf):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO rutas (nombre, mapa, xi, xf, yi, yf, longitudi, longitudf, latitudi, latitudf) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (nombre, mapa, xi, xf, yi, yf, longitudi, longitudf, latitudi, latitudf))
        con.commit()
    except Exception as e:
        print(e)


def guardar_geocerca(nombre, longitud, latitud, retraso_esperado, ruta_id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        cur.execute(
            "INSERT INTO geocercas (nombre, longitud, latitud, retraso_esperado, ruta_id) VALUES (?, ?, ?, ?, ?)", (nombre, longitud, latitud, retraso_esperado, ruta_id))
        con.commit()
    except Exception as e:
        print(e)


def obtener_geocerca_por_ruta(ruta_id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM geocercas WHERE ruta_id = ?", (ruta_id,))
        return cur.fetchall()
    except Exception as e:
        print(e)


def obtener_rutas():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM rutas")
        return cur.fetchall()
    except Exception as e:
        print(e)


def obtener_ruta_por_id(ruta_id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM rutas WHERE ruta_id = ?", (ruta_id,))
        return cur.fetchone()
    except Exception as e:
        print(e)

def obtener_ruta_por_nombre(ruta_nombre):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM rutas WHERE nombre = ?", (ruta_nombre,))
        return cur.fetchone()
    except Exception as e:
        print(e)


def obtener_chofer_por_id(chofer_id: str):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM chofer WHERE chofer_id = ?", (chofer_id,))
        return cur.fetchone()
    except Exception as e:
        print(e)


def obtener_chofer_por_uuid(uuid):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM chofer WHERE uuid = ?", (uuid,))
        return cur.fetchone()
    except Exception as e:
        print(e)


def obtener_pasajero_por_id(pasajero_id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM pasajero WHERE pasajero_id = ?",
                    (pasajero_id,))
        return cur.fetchone()
    except Exception as e:
        print(e)


def guardar_pasajero(nombre, foto, uuid):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO pasajero (nombre, foto, uuid) VALUES (?, ?, ?)", (nombre, foto, uuid))
        con.commit()
    except Exception as e:
        print(e)


def guardar_asistencia(pasajero_id, fecha, hora, velocidad, longitud, latitud, entrada, folio, folio_viaje):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO asistencia (pasajero_id, fecha, hora, velocidad, longitud, latitud, entrada, folio, folio_viaje ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (pasajero_id, fecha, hora, velocidad, longitud, latitud, entrada, folio, folio_viaje))
        con.commit()
    except Exception as e:
        print(e)

def guardar_asistencia_de_usuario_pendiente(pasajero_id, fecha, hora, velocidad, longitud, latitud, entrada, folio, folio_viaje):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO asistencia_usuarios_pendientes (pasajero_id, fecha, hora, velocidad, longitud, latitud, entrada, folio, folio_viaje ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (pasajero_id, fecha, hora, velocidad, longitud, latitud, entrada, folio, folio_viaje))
        con.commit()
    except Exception as e:
        print(e)


def obtener_pasajero_por_uuid(uuid):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM pasajero WHERE uuid = ?", (uuid,))
        return cur.fetchone()
    except Exception as e:
        print(e)


def obtener_asistencias_por_check_servidor():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM asistencia WHERE check_servidor = 'no' ")
        return cur.fetchall()
    except Exception as e:
        print(e)


def checar_pasajero_por_fecha_y_uuid(fecha, uuid):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM pasajero WHERE fecha = ? AND uuid = ?", (fecha, uuid))
        return cur.fetchone()
    except Exception as e:
        print(e)


def obtener_ultima_asistencia():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM asistencia ORDER BY asistencia_id DESC LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        print(e)


def obtener_asistencias_no_enviadas():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM asistencia WHERE check_servidor = 'NO' ")
        return cur.fetchall()
    except Exception as e:
        print(e)

def obtener_asistencias_de_usuarios_pendientes_no_enviadas():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM asistencia_usuarios_pendientes WHERE check_servidor = 'NO' ")
        return cur.fetchall()
    except Exception as e:
        print(e)


def actualizar_asistencia_check_servidor(asistencia_id):
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    try:
        cur.execute(
            "UPDATE asistencia SET check_servidor = 'OK' WHERE asistencia_id = ?", (asistencia_id,))
        con.commit()
    except Exception as e:
        print(e)

def actualizar_asistencia_usuarios_pendientes_check_servidor(asistencia_id):
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    try:
        cur.execute(
            "UPDATE asistencia_usuarios_pendientes SET check_servidor = 'OK' WHERE asistencia_id = ?", (asistencia_id,))
        con.commit()
    except Exception as e:
        print(e)


def obtener_ultima_asistencia_de_hoy_por_pasajero(pasajero_id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM asistencia WHERE pasajero_id = ? AND fecha = ? ORDER BY asistencia_id DESC LIMIT 1", (pasajero_id, datetime.now().strftime("%d/%m/%Y")))
        return cur.fetchone()
    except Exception as e:
        print(e)

def obtener_ultima_asistencia_de_hoy_por_pasajero_pendiente(pasajero_id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM asistencia_usuarios_pendientes WHERE pasajero_id = ? AND fecha = ? ORDER BY asistencia_id DESC LIMIT 1", (pasajero_id, datetime.now().strftime("%d/%m/%Y")))
        return cur.fetchone()
    except Exception as e:
        print(e)


# se obtiene el siguiente folio si es un dia nuevo se reinicia el folio
def obtener_ultimo_folio_asistencia():
    asistencia = obtener_ultima_asistencia()
    if asistencia is None:
        return {
            'folio': 1
        }
    folio = asistencia[9]
    fecha_db = asistencia[2]
    fecha_actual = strftime("%d/%m/%Y")

    if compare_two_dates(fecha_actual, fecha_db):
        return {
            'folio': folio + 1
        }
    else:
        return {
            'folio': 1
        }

#  Toma dos fechas en formato "mm/dd/aaaa" y devuelve True si son la misma fecha y False si no lo son.


def compare_two_dates(date1, date2):
    d1 = datetime.strptime(date1, "%d/%m/%Y")
    d2 = datetime.strptime(date2, "%d/%m/%Y")
    delta = d2 - d1
    if delta.days == 0:
        return True
    else:
        return False


def marcar_asistencia(pasajero):

    folio_actual = obtener_ultimo_folio_asistencia()['folio']
    fecha = strftime("%d/%m/%Y")
    hora = strftime("%H:%M:%S")

    if len(pasajero) != 8:

        asistencia = obtener_ultima_asistencia_de_hoy_por_pasajero(pasajero[0])

        if asistencia is None:
            # no se ha subido en todo el dia, subida
            guardar_asistencia(pasajero[0], fecha, hora, variables_globales.velocidad, variables_globales.longitud, variables_globales.latitud, 1, folio_actual, variables_globales.folio_asignacion)
            print("##############################")
            print("INGRESADO EN ASISTENCIA IS NONE")
            print("##############################")
        else:
            if asistencia[8] == 1:
                # bajada
                print("##############################")
                print("INGRESADO EN ASISTENCIA BAJADA")
                print("##############################")
                guardar_asistencia(pasajero[0], fecha, hora, variables_globales.velocidad, variables_globales.longitud, variables_globales.latitud, 0, folio_actual, variables_globales.folio_asignacion)
            else:
                # subida
                print("##############################")
                print("INGRESADO EN ASISTENCIA SUBIDA")
                print("##############################")
                guardar_asistencia(pasajero[0], fecha, hora, variables_globales.velocidad, variables_globales.longitud, variables_globales.latitud, 1, folio_actual, variables_globales.folio_asignacion)
        folio_actual = folio_actual + 1
    else:

        asistencia_usuario_pendiente = obtener_ultima_asistencia_de_hoy_por_pasajero_pendiente(pasajero)

        if asistencia_usuario_pendiente is None:
            # no se ha subido en todo el dia, subida
            guardar_asistencia_de_usuario_pendiente(pasajero, fecha, hora, variables_globales.velocidad, variables_globales.longitud, variables_globales.latitud, 1, folio_actual, variables_globales.folio_asignacion)
            print("##############################")
            print("INGRESADO EN ASISTENCIA IS NONE")
            print("##############################")
        else:
            if asistencia_usuario_pendiente[8] == 1:
                # bajada
                print("##############################")
                print("INGRESADO EN ASISTENCIA BAJADA")
                print("##############################")
                guardar_asistencia_de_usuario_pendiente(pasajero, fecha, hora, variables_globales.velocidad, variables_globales.longitud, variables_globales.latitud, 0, folio_actual, variables_globales.folio_asignacion)
            else:
                # subida
                print("##############################")
                print("INGRESADO EN ASISTENCIA SUBIDA")
                print("##############################")
                guardar_asistencia_de_usuario_pendiente(pasajero, fecha, hora, variables_globales.velocidad, variables_globales.longitud, variables_globales.latitud, 1, folio_actual, variables_globales.folio_asignacion)
        folio_actual = folio_actual + 1