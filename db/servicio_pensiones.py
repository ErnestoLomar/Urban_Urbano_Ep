##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 26/04/2022
# Ultima modificación: 27/08/2022
#
# Script para administrar la base de datos de los servicios.
#
##########################################

#Importamos librerías externas
import sqlite3

URI = "/home/pi/Urban_Urbano/db/servicios_pensiones.db"

#Creando una tabla llamada ruta.
tabla_pension = '''CREATE TABLE pension (
    pension_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    nombre VARCHAR(100)
)'''

tabla_servicios_de_pension = '''CREATE TABLE servicio_de_pension (
    numero_de_servicio INTEGER PRIMARY KEY,
    inicio_servicio VARCHAR(100),
    final_servicio VARCHAR(100),
    comienzo VARCHAR(100),
    nombre_pension VARCHAR(100)
)'''

tabla_transbordos_de_servicios = '''CREATE TABLE transbordos_de_servicios (
    inicio_transbordo VARCHAR(100),
    final_transbordo VARCHAR(100),
    numero_de_servicio_asociado VARCHAR(100)
)'''

def crear_tabla_pension():
    try:
        #Establecemos la conexión con la base de datos
        con = sqlite3.connect(URI)
        cur = con.cursor()
        #Ejecutando la sentencia SQL en la variable `tabla_pension`.
        cur.execute(tabla_pension)
        con.close()
    except Exception as e:
        print(e)

#Función para crear la tabla de rutas de pension.
def crear_tabla_servicios_de_pension():
    try:
        #Establecemos la conexión con la base de datos
        con = sqlite3.connect(URI)
        cur = con.cursor()
        # Ejecutando la sentencia SQL en la variable `tabla_rutas_de_pension`.
        cur.execute(tabla_servicios_de_pension)
        con.close()
    except Exception as e:
        print(e)

#Función para insertar una pension.
def insertar_pension(nombre_de_pension):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO pension(nombre) VALUES ('{nombre_de_pension}')''')
    con.commit()
    con.close()

#Función para insertar una ruta.
def insertar_servicio(numero_de_servicio, inicio_servicio, fin_servicio, comienzo, nombre_pension):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO servicio_de_pension(numero_de_servicio, inicio_servicio, final_servicio, comienzo, nombre_pension) VALUES ('{numero_de_servicio}', '{inicio_servicio}', '{fin_servicio}', '{comienzo}', '{nombre_pension}' )''')
    con.commit()
    con.close()

#Función para obtener todas los servicios por pensión.
def obtener_servicios_de_pension(nombre_de_pension):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicios = f''' SELECT * FROM servicio_de_pension WHERE nombre_pension = "{nombre_de_pension}" '''
    cur.execute(select_servicios)
    resultado = cur.fetchall()
    con.close()
    return resultado

def obtener_pensiones():
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicios = f''' SELECT * FROM pension'''
    cur.execute(select_servicios)
    resultado = cur.fetchall()
    con.close()
    return resultado

def obtener_servicio_por_numero_servicio(numero_de_servicio):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicios = f''' SELECT * FROM servicio_de_pension WHERE numero_de_servicio = "{numero_de_servicio}" '''
    cur.execute(select_servicios)
    resultado = cur.fetchall()
    con.close()
    return resultado

def obtener_transbordo_por_numero_servicio(numero_de_servicio):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicios = f''' SELECT * FROM transbordos_de_servicios WHERE numero_de_servicio = "{numero_de_servicio}" '''
    cur.execute(select_servicios)
    resultado = cur.fetchall()
    con.close()
    return resultado

def obtener_origen_por_numero_de_servicio(numero_de_servicio):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicios = f''' SELECT * FROM servicio_de_pension WHERE numero_de_servicio = "{numero_de_servicio}" '''
    cur.execute(select_servicios)
    resultado = cur.fetchone()
    con.close()
    return resultado