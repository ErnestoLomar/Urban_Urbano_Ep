from datetime import datetime
import sqlite3
from time import strftime
import logging

from asignaciones_queries import obtener_ultimo_folio_asignaciones
from rutas_queries import obtener_ultimo_folio_asistencia
URI = "/home/pi/Urban_Urbano/db/folio.db"

tabla_folio = '''CREATE TABLE IF NOT EXISTS folio ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        folio Integer,
        fecha Date
)'''

tabla_folios_finales = '''CREATE TABLE IF NOT EXISTS folios_finales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio_geolo   INTEGER,
        folio_asignacion INTEGER,
        folio_asistencia INTEGER,
        check_servidor VARCHAR(100) default 'NO'
)'''


def crear_tabla_folios_finales():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_folios_finales)
    except Exception as e:
        print(e)
        logging.info(e)


def crear_tabla_folio():
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    cur.execute(tabla_folio)


def obtener_folios_finales_no_enviados():
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    select = f'''  SELECT * FROM folios_finales WHERE check_servidor = 'NO' LIMIT 10 '''
    cur.execute(select)
    resultado = cur.fetchall()
    return resultado


def actualizar_folio_final_check(id):
    conexion = sqlite3.connect(URI,check_same_thread=False)
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE folios_finales SET check_servidor = 'OK' WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    return True


def insertar_folio(folio: int, fecha):
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO folio(folio, fecha) VALUES ('{folio}', '{fecha}' )''')
    con.commit()


def actualizar_folio(id: int, folio: int,  fecha):
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    sql_update_query = f'''Update folio set folio = '{folio}', fecha = '{fecha}'  where id = {id}'''
    cur.execute(sql_update_query)
    con.commit()


def buscar_folio():
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    select = f'''  SELECT * FROM folio ORDER BY folio.folio DESC LIMIT 1 '''
    cur.execute(select)
    resultado = cur.fetchone()
    print(resultado)
    return resultado

# Si la fecha en la base de datos es la misma que la de hoy, devolver el número de folio actual. De lo
# contrario, actualice la base de datos con un nuevo número de folio y devuelva ese nuevo número


def cargarFolioActual():
    # Obtener datos de la base de datos.
    res = buscar_folio()
    id = res[0]
    folio_BD = res[1]
    fecha_BD = res[2]
    # obtener fecha actual
    fecha_actual = strftime("%m/%d/%Y")

    d1 = datetime.strptime(fecha_BD, "%m/%d/%Y")
    d2 = datetime.strptime(fecha_actual, "%m/%d/%Y")
    # diferencia entre las dos fechas
    delta = d2 - d1
    print("diferencia="+str(delta.days))
    if delta.days == 0:
        # return folio_BD
        return {
            'id': id,
            'folio': folio_BD
        }
    else:
        actualizar_folio(id, 1, fecha_actual)
        return {
            'id': id,
            'folio': 1
        }


def comparar_fecha():
    res = buscar_folio()
    id = res[0]
    fecha_actual = strftime("%m/%d/%Y")
    folio_BD = res[1]

    if fecha_actual == res[2]:
        return {
            'id': id,
            'folio': folio_BD
        }
    else:
        actualizar_folio(id, 1, fecha_actual)
        return {
            'id': id,
            'folio': 1
        }


def load_folio_actual():
    res = buscar_folio()
    id = res[0]
    fecha_actual = strftime("%d/%m/%Y")
    fecha_BD = res[2]
    fecha_BD = convert_date_format(fecha_BD)

    if compare_two_dates(fecha_actual, fecha_BD):
        return {
            'id': id,
            'folio': res[1]
        }
    else:
        actualizar_folio(id, 1, fecha_actual)
        return {
            'id': id,
            'folio': 1
        }


#  Toma dos fechas en formato "mm/dd/aaaa" y devuelve True si son la misma fecha y False si no lo son.
def compare_two_dates(date1, date2):
    d1 = datetime.strptime(date1, "%m/%d/%Y")
    d2 = datetime.strptime(date2, "%m/%d/%Y")
    delta = d2 - d1
    if delta.days == 0:
        return True
    else:
        return False

# convierte una fecha en formato dia/mes/año a mes/dia/año
def convert_date_format(date):
    return datetime.strptime(date, '%d/%m/%Y').strftime('%m/%d/%Y')

def guardar_folios_final():
    # obbtener folios finales y guardarlos en la base de datos
    folio_geolo = cargarFolioActual()['folio']
    folio_asignacion = obtener_ultimo_folio_asignaciones()['folio']
    folio_asistencia = obtener_ultimo_folio_asistencia()['folio']
    
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO folios_finales(folio_geolo, folio_asignacion, folio_asistencia) VALUES ('{folio_geolo}', '{folio_asignacion}', '{folio_asistencia}' )''')
    con.commit()

#guardar_folios_final()

crear_tabla_folio()
crear_tabla_folios_finales()

if buscar_folio() == None:
    fecha_actual = strftime("%m/%d/%Y")
    insertar_folio(1, fecha_actual)