##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 26/08/2022
# Ultima modificación: 26/08/2022
#
# Script para administrar las geocercas en la base de datos.
#
##########################################

#Importamos librerías externas
import sqlite3

URI = "/home/pi/Urban_Urbano/db/geocercas.db"

#Creando una tabla llamada geocercas_servicios.
tabla_geocercas_servicios = '''CREATE TABLE geocercas_servicios ( 
    id_geocerca INTEGER PRIMARY KEY AUTOINCREMENT, 
    nombre_geocerca VARCHAR(100),
    latitud VARCHAR(100),
    longitud VARCHAR(100)
)'''

def crear_tabla_geocercas_servicios():
    try:
        #Establecemos la conexión con la base de datos
        con = sqlite3.connect(URI)
        cur = con.cursor()
        #Ejecutando la sentencia SQL en la variable `tabla_geocercas_servicios`.
        cur.execute(tabla_geocercas_servicios)
        con.close()
    except Exception as e:
        print(e)

#Función para insertar una geocerca.
def insertar_geocerca(nombre_geocerca, latitud, longitud):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO geocercas_servicios(nombre_geocerca, latitud, longitud) VALUES ('{nombre_geocerca}', '{latitud}', '{longitud}')''')
    con.commit()
    con.close()

#Función para obtener todas los servicios por pensión.
def obtener_geocerca_de_servicio(nombre_de_geocerca):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicios = f''' SELECT * FROM geocercas_servicios WHERE nombre_geocerca = "{nombre_de_geocerca}"'''
    cur.execute(select_servicios)
    resultado = cur.fetchone()
    con.close()
    return resultado