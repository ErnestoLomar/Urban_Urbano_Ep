import sqlite3

URI = "/home/pi/Urban_Urbano/db/horarios.db"

#Creando una tabla llamada geocercas_servicios.
tabla_de_horas = '''CREATE TABLE horas (
    hora_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hora TIME,
    check_hecho TEXT(10) default 'NO'
)'''

def crear_tabla_de_horas():
    try:
        #Establecemos la conexion con la base de datos
        con = sqlite3.connect(URI)
        cur = con.cursor()
        #Ejecutando la sentencia SQL en la variable `tabla_geocercas_servicios`.
        cur.execute(tabla_de_horas)
        con.close()
    except Exception as e:
        print("No se pudo crear la tabla de horas alttus: " + str(e))

def obtener_estado_de_todas_las_horas_no_hechas():
    try:
        conexion = sqlite3.connect(URI)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM horas WHERE check_hecho = 'NO'")
        resultado = cursor.fetchall()
        conexion.close()
        return resultado
    except Exception as e:
        print("Fallo al obtener todas las horas: " + str(e))
        
def obtener_ultima_hora_no_hecha():
    try:
        conexion = sqlite3.connect(URI)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM horas WHERE check_hecho = 'NO' ORDER BY hora_id ASC LIMIT 1")
        resultado = cursor.fetchone()
        conexion.close()
        return resultado
    except Exception as e:
        print("Fallo al obtener la ultima hora: " + str(e))

def actualizar_estado_hora_check_hecho(estado, id):
    try:
        conexion = sqlite3.connect(URI)
        cursor = conexion.cursor()
        cursor.execute("UPDATE horas SET check_hecho = ? WHERE hora_id = ?", (estado,id))
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("Fallo al actualizar check_hecho de horas: " + str(e))
        return False
    
def actualizar_estado_hora_por_defecto():
    try:
        conexion = sqlite3.connect(URI)
        cursor = conexion.cursor()
        cursor.execute("UPDATE horas SET check_hecho = 'NO'")
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        print("Fallo al actualizar check_hecho de horas: " + str(e))
        return False