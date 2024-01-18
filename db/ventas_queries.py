##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 26/04/2022
# Ultima modificación: 16/08/2022
#
# Script para administrar la base de datos de los queries de las ventas.
#
##########################################

#Importamos librerías externas
import sqlite3
from time import strftime

URI = "/home/pi/Urban_Urbano/db/ventas.db"

#Query para crear la tabla de ventas.
tabla_venta = '''CREATE TABLE IF NOT EXISTS venta ( 
        venta_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        fecha Datetime,
        origen VARCHAR(100),
        destino VARCHAR(100),
        total float
)'''

#Query para crear la tabla de items de venta.
tabla_item_venta = '''CREATE TABLE IF NOT EXISTS item_venta ( 
        item_venta_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        folio_venta INTEGER,
        folio_viaje VARCHAR(100),
        fecha date,
        hora time,
        id_del_servicio_o_transbordo INTEGER,
        id_geocerca INTEGER,
        id_tipo_de_pasajero INTEGER,
        transbordo_o_no VARCHAR(10),
        tipo_pasajero VARCHAR(30),
        nombre_de_pasajero VARCHAR(20),
        costo float,
        check_servidor VARCHAR(100) default 'NO'
)'''


#Función para crear la tabla de ventas.
def crear_tabla_venta():
    #Creamos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    cur.execute(tabla_venta)
    con.close()

#Función para crear la tabla de items de venta.
def crear_tabla_items_venta():
    #Creamos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    cur.execute(tabla_item_venta)
    con.close()

#Función para crear las tablas de la base de datos.
def crear_tablas():
    crear_tabla_venta()
    crear_tabla_items_venta()


#Función para insertar una venta.
def insertar_venta(fecha: str, origen: str, destino: str,  total: float):
    #Creamos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO venta( fecha, origen, destino,  total) VALUES ('{fecha}' , '{origen}', '{destino}', '{total}' )''')
    con.commit()
    con.close()

#Función para insertar un item de venta.
def insertar_item_venta(folio_venta, folio_de_viaje, fecha, hora, id_de_serivio_o_transbordo, id_geocerca, id_tipo_de_pasajero, transbordo_o_no, tipo_pasajero, nombre_de_pasajero, costo):
    #Creamos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO item_venta(folio_venta, folio_viaje, fecha, hora, id_del_servicio_o_transbordo, id_geocerca, id_tipo_de_pasajero, transbordo_o_no, tipo_pasajero, nombre_de_pasajero, costo) VALUES ('{folio_venta}' , '{folio_de_viaje}', '{fecha}', '{hora}', '{id_de_serivio_o_transbordo}' , '{id_geocerca}' , '{id_tipo_de_pasajero}' , '{transbordo_o_no}' , '{tipo_pasajero}' , '{nombre_de_pasajero}' , '{costo}') ''')
    con.commit()
    con.close()

#Función para buscar la ultima venta.
def buscar_ultima_venta():
    #Creamos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select = f''' SELECT * FROM venta ORDER BY venta.venta_id DESC LIMIT 1 '''
    cur.execute(select)
    resultado = cur.fetchone()
    con.close()
    return resultado

#Función para buscar items de venta.
def buscar_items_venta(venta_id: int):
    #Creamos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select = f''' SELECT * FROM item_venta WHERE item_venta.venta_id = "{venta_id}" '''
    cur.execute(select)
    resultado = cur.fetchmany()
    con.close()
    return resultado

def obtener_ultimo_folio_de_item_venta():
    #Creamos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select = f''' SELECT * FROM item_venta ORDER BY item_venta.item_venta_id DESC LIMIT 1 '''
    cur.execute(select)
    resultado = cur.fetchone()
    con.close()
    return resultado

def obtener_primer_folio_de_item_venta():
    #Creamos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select = f''' SELECT * FROM item_venta ORDER BY item_venta.item_venta_id ASC LIMIT 1 '''
    cur.execute(select)
    resultado = cur.fetchone()
    con.close()
    return resultado

def obtener_estado_de_ventas_no_enviadas():
    conexion = sqlite3.connect(URI)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM item_venta WHERE check_servidor = 'NO' LIMIT 1")
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_total_de_ventas_por_folioviaje_y_fecha(folio_viaje,fecha):
    conexion = sqlite3.connect(URI)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM item_venta WHERE folio_viaje = ? AND fecha = ?", (folio_viaje,fecha,))
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_total_de_efectivo_por_folioviaje(folio_viaje):
    conexion = sqlite3.connect(URI)
    cursor = conexion.cursor()

    # Selecciona la suma de los costos para el folio_viaje y fecha dados
    cursor.execute("SELECT SUM(costo) FROM item_venta WHERE folio_viaje = ?", (folio_viaje,))
    
    # Recupera el resultado (será un solo valor, la suma de costos)
    resultado = cursor.fetchone()[0]

    # Si no hay ventas para el folio_viaje y fecha dados, establece el resultado en 0
    if resultado is None:
        resultado = 0

    conexion.close()
    return resultado

def obtener_total_de_ventas_por_folioviaje(folio_viaje):
    conexion = sqlite3.connect(URI)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM item_venta WHERE folio_viaje = ?", (folio_viaje,))
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_estado_de_todas_las_ventas_no_enviadas():
    conexion = sqlite3.connect(URI)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM item_venta WHERE check_servidor = 'NO' LIMIT 1")
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def obtener_estado_de_todass_las_ventas_no_enviadas():
    conexion = sqlite3.connect(URI)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM item_venta WHERE check_servidor = 'NO'")
    resultado = cursor.fetchall()
    conexion.close()
    return resultado

def actualizar_estado_venta_check_servidor(estado, id):
    conexion = sqlite3.connect(URI)
    cursor = conexion.cursor()
    cursor.execute("UPDATE item_venta SET check_servidor = ? WHERE item_venta_id = ?", (estado,id))
    conexion.commit()
    conexion.close()
    return True

def obtener_venta_por_folio_y_foliodeviaje(folio_venta, folio_de_viaje):
    conexion = sqlite3.connect(URI)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM item_venta WHERE folio_venta = ? AND folio_viaje = ? LIMIT 1", (folio_venta, folio_de_viaje))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

def seleccionar_ventas_antiguas():
    try:
        conexion = sqlite3.connect(URI,check_same_thread=False)
        cursor = conexion.cursor()
        cursor.execute(f"SELECT item_venta_id, fecha FROM item_venta")
        resultado = cursor.fetchall()
        conexion.close()
        return resultado
    except Exception as e:
        print(e)
        return False

def eliminar_ventas_antiguas(id):
    try:
        conexion = sqlite3.connect(URI)
        cursor = conexion.cursor()
        cursor.execute(f"DELETE FROM item_venta WHERE item_venta_id == {id}")
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(e)
        return False

#crear_tablas()