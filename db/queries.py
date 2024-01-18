##########################################
# Autor:
# Fecha de creación: 26/04/2022
# Ultima modificación: 27/06/2022
#
# Script para administrar la base de datos local
##########################################
import sqlite3
URI = "/home/pi/Urban_Urbano/db/aforo.db"

# cambiar altitud a latitud
tabla_gps = '''CREATE TABLE IF NOT EXISTS gps ( 
    idMuestreo INTEGER PRIMARY KEY AUTOINCREMENT, 
    fechaGPS DATE, 
    horaGPS Time, 
    errorGPS VARCHAR(100) ,  
    longitudGPS REAL, 
    altitudGPS Real,  
    velocidadGPS REAL, 
    geocerca varchar, 
    folio INTEGER , 
    check_servidor varchar,
    folio_viaje VARCHAR(100)
)'''

tabla_aforo = ''' CREATE TABLE IF NOT EXISTS parametros (
    idTransportista int(4), 
    idUnidad int(5),
    puertoSocket int(10),
    intervaloGPS Real, 
    enableGPS boolean, 
    kmActual Real,
    inicio_folio int(10)
) '''

tabla_temp = ''' CREATE TABLE IF NOT EXISTS temp (
    idMuestreo int(4), 
    fechaElegida DATE, 
    horaElegida TIME, 
    origenFechaHora VARCHAR(100), 
    errorTempCPU VARCHAR(100), 
    errorTempGPU VARCHAR(100), 
    tempCPU Real, 
    tempGPU Real
) '''

tabla_tablillas = ''' CREATE TABLE IF NOT EXISTS tablillas (
    idTablilla INTEGER PRIMARY KEY AUTOINCREMENT,
    num_tablilla VARCHAR(20),
    socket VARCHAR(20)
) '''

tabla_estadisticas = ''' CREATE TABLE IF NOT EXISTS estadisticas (
    idMuestreo INTEGER PRIMARY KEY AUTOINCREMENT,
    idUnidad VARCHAR(10),
    fecha date,
    hora time,
    columna_db VARCHAR(30),
    valor_columna VARCHAR(50),
    check_servidor VARCHAR(20) default 'NO'
) '''

def crear_tabla_gps():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_gps)
    except Exception as e:
        print("Problema al crear tabla del gps: ", e)


def crear_tabla_aforo():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_aforo)
    except Exception as e:
        print("Problema al crear tabla aforo: ", e)


def crear_tabla_temp():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_temp)
    except Exception as e:
        print("Problema al crear tabla de la temperatura: ", e)
        
def crear_tabla_estadisticas():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_estadisticas)
    except Exception as e:
        print("Problema al crear tabla de la estadisticas: ", e)
        
def crear_tabla_tablillas():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(tabla_tablillas)
    except Exception as e:
        print("Problema al crear tabla de las tablillas: ", e)


def insertar_gps(fechaGPS, horaGPS, errorGPS, longitud, latitud, velocidadGPS, geocerca, folio, check_servidor, folio_viaje):
    # BD GPS
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            f"INSERT INTO gps(fechaGPS, horaGPS, errorGPS,  longitudGPS, altitudGPS , velocidadGPS, geocerca, folio, check_servidor, folio_viaje ) VALUES ('{fechaGPS}', '{horaGPS}', '{errorGPS}' , '{longitud}','{latitud}','{velocidadGPS}','{geocerca}','{folio}','{check_servidor}', '{folio_viaje}' )")
        con.commit()
    except Exception as e:
        print(e)


def insertar_aforo(idTransportista, idUnidad, puertoSocket, intervaloGPS, enableGPS, kmActual, inicio_folio):
    # BD aforo
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    cur.execute(
        f"INSERT INTO parametros VALUES (' {idTransportista}','{idUnidad}','{puertoSocket}', '{intervaloGPS}', '{enableGPS}' , '{kmActual}', '{inicio_folio}')")
    con.commit()
    con.close()


def insertar_temp(idMuestreo, fechaElegida, horaElegida, origenFechaHora, errorTempCPU, errorTempGPU, tempCPU, tempGPU):
    # BD temp
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    cur.execute(
        f"INSERT INTO temp VALUES (' {idMuestreo}','{fechaElegida}', '{horaElegida}', '{origenFechaHora}' , '{errorTempCPU}','{errorTempGPU}','{tempCPU}','{tempGPU}' )")
    con.commit()
    con.close()
    
def insertar_estadisticas_boletera(unidad, fecha, hora, columna, valor):
    # BD temp
    try:
        con = sqlite3.connect(URI, check_same_thread=False)
        cur = con.cursor()
        cur.execute("INSERT INTO estadisticas(idUnidad, fecha, hora, columna_db, valor_columna) VALUES (?, ?, ?, ?, ?)", (unidad, fecha, hora, columna, valor))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        return False

def insertar_tablilla(num_tablilla, socket):
    # BD temp
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    cur.execute(f"INSERT INTO tablillas(num_tablilla, socket) VALUES ('{num_tablilla}','{socket}')")
    con.commit()
    con.close()

def obtener_datos_no_enviados():
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    select_rutas = f''' SELECT * FROM gps where check_servidor = 'error' ORDER BY idMuestreo ASC LIMIT 20'''
    cur.execute(select_rutas)
    resultado = cur.fetchall()
    return resultado


def actualizar_registro_gps(id):
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    sql_update_query = f'''Update gps set check_servidor = 'OK' where idMuestreo = {id}'''
    cur.execute(sql_update_query)
    con.commit()
    con.close()

def obtener_datos_aforo():
    con = sqlite3.connect(URI,check_same_thread=False)
    cur = con.cursor()
    select_rutas = f''' SELECT * FROM parametros ORDER BY idTransportista DESC LIMIT 1'''
    cur.execute(select_rutas)
    resultado = cur.fetchone()
    return resultado

def obtener_estadisticas_no_enviadas():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        select_estadisticas = f''' SELECT * FROM estadisticas WHERE check_servidor = 'NO' LIMIT 1 '''
        cur.execute(select_estadisticas)
        resultado = cur.fetchall()
        con.close()
        return resultado
    except Exception as e:
        print(e)
        
def actualizar_estado_estadistica_check_servidor(estado, id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE estadisticas SET check_servidor = ? WHERE idMuestreo = ?", (estado,id))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        return False
    
def actualizar_socket(socket):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE parametros SET puertoSocket = ? WHERE idTransportista = 1", (socket,))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        return False
    
def obtener_ultima_ACT():
    try:
        conexion = sqlite3.connect(URI,check_same_thread=False)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM estadisticas WHERE columna_db = 'ACT' ORDER BY idMuestreo DESC LIMIT 1")
        resultado = cursor.fetchall()
        conexion.close()
        return resultado
    except Exception as e:
        print("Fallo al obtener ultima estadistica ACT: " + str(e))
        
def eliminar_todas_las_estadisticas_ACT_no_hechas():
    try:
        conexion = sqlite3.connect(URI)
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM estadisticas WHERE columna_db = 'ACT' AND check_servidor = 'NO'")
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("Fallo al eliminar estadisticas ACT: " + str(e))
        return False
    
def seleccionar_estadistias_antiguas():
    try:
        conexion = sqlite3.connect(URI,check_same_thread=False)
        cursor = conexion.cursor()
        cursor.execute(f"SELECT idMuestreo, fecha FROM estadisticas")
        resultado = cursor.fetchall()
        conexion.close()
        return resultado
    except Exception as e:
        print(e)
        return False
    
def eliminar_estadisticas_antiguas(id):
    try:
        conexion = sqlite3.connect(URI)
        cursor = conexion.cursor()
        cursor.execute(f"DELETE FROM estadisticas WHERE idMuestreo == {id}")
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print(e)
        return False

#Función para crear las tablas de las bases de datos
def crear_tablas():
    crear_tabla_aforo()
    crear_tabla_temp()
    crear_tabla_gps()
    crear_tabla_estadisticas()
    crear_tabla_tablillas()
    
#insertar_aforo(1,21000,8150,0.0,0,0.0,51)