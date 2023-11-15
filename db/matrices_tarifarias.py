##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 25/08/2022
# Ultima modificación: 25/08/2022
#
# Script para administrar las matrices tarifarias en la base de datos.
#
##########################################

#Importamos librerías externas
import sqlite3

URI = "/home/pi/Urban_Urbano/db/matrices_tarifarias.db"

#Creando una tabla llamada matriz_tarifaria_servicios.
tabla_matriz_tarifaria_servicios = '''CREATE TABLE matriz_tarifaria_servicios ( 
    matriz_t_s_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    origen VARCHAR(100),
    destino VARCHAR(100),
    precio_normal float,
    precio_preferente float,
    numero_de_servicio INTEGER
)'''

#Creando una tabla llamada matriz_tarifaria_transbordos .
tabla_matriz_tarifaria_transbordos = '''CREATE TABLE matriz_tarifaria_transbordos ( 
    matriz_t_t_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    origen VARCHAR(100),
    destino VARCHAR(100),
    precio_normal float,
    precio_preferente float,
    numero_de_servicio INTEGER,
    primer_transbordo VARCHAR(100),
    segundo_transbordo VARCHAR(100)
)'''

def crear_tabla_matriz_tarifaria_servicios():
    try:
        #Establecemos la conexión con la base de datos
        con = sqlite3.connect(URI)
        cur = con.cursor()
        #Ejecutando la sentencia SQL en la variable `tabla_pension`.
        cur.execute(tabla_matriz_tarifaria_servicios)
        con.close()
    except Exception as e:
        print(e)

def crear_tabla_matriz_tarifaria_transbordos():
    try:
        #Establecemos la conexión con la base de datos
        con = sqlite3.connect(URI)
        cur = con.cursor()
        #Ejecutando la sentencia SQL en la variable `tabla_pension`.
        cur.execute(tabla_matriz_tarifaria_transbordos)
        con.close()
    except Exception as e:
        print(e)

#Función para insertar matrices tarifaria de un servicio.
def insertar_matriz_tarifaria_servicios(origen, destino, precio_normal, precio_preferente, numero_de_servicio):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    insert_matriz_tarifaria = f'''INSERT INTO matriz_tarifaria_servicios (origen, destino, precio_normal, precio_preferente, numero_de_servicio) VALUES ('{origen}', '{destino}', {precio_normal}, {precio_preferente}, {numero_de_servicio})'''
    cur.execute(insert_matriz_tarifaria)
    con.commit()
    con.close()
    return True

#Función para insertar matrices tarifaria de un transbordo.
def insertar_matriz_tarifaria_transbordos(origen, destino, precio_normal, precio_preferente, numero_de_servicio, priemr_transbordo, segundo_transbordo):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    insert_matriz_tarifaria = f'''INSERT INTO matriz_tarifaria_transbordos (origen, destino, precio_normal, precio_preferente, numero_de_servicio, primer_transbordo, segundo_transbordo) VALUES ('{origen}', '{destino}', {precio_normal}, {precio_preferente}, {numero_de_servicio}, '{priemr_transbordo}', '{segundo_transbordo}')'''
    cur.execute(insert_matriz_tarifaria)
    con.commit()
    con.close()
    return True

def obtener_servicio_por_numero_de_servicio_y_origen(numero_de_servicio, origen):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicio = f'''SELECT * FROM matriz_tarifaria_servicios WHERE numero_de_servicio = {numero_de_servicio} AND origen = '{origen}' '''
    cur.execute(select_servicio)
    servicio = cur.fetchall()
    con.close()
    return servicio

def obtener_transbordos_por_origen_y_numero_de_servicio(numero_de_servicio, origen):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_transbordos = f'''SELECT * FROM matriz_tarifaria_transbordos WHERE numero_de_servicio = {numero_de_servicio} AND origen = '{origen}' '''
    cur.execute(select_transbordos)
    transbordos = cur.fetchall()
    con.close()
    return transbordos

def obtener_servicio_por_origen_y_destino(origen, destino):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicio = f'''SELECT * FROM matriz_tarifaria_servicios WHERE origen = '{origen}' AND destino = '{destino}' '''
    cur.execute(select_servicio)
    servicio = cur.fetchall()
    con.close()
    return servicio

def obtener_destino_de_servicios_directos(destino):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicio = f'''SELECT * FROM matriz_tarifaria_servicios WHERE destino = '{destino}' '''
    cur.execute(select_servicio)
    servicio = cur.fetchall()
    con.close()
    return servicio

def obtener_destino_de_transbordos(destino):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_transbordo = f'''SELECT * FROM matriz_tarifaria_transbordos WHERE destino = '{destino}' '''
    cur.execute(select_transbordo)
    servicio = cur.fetchall()
    con.close()
    return servicio