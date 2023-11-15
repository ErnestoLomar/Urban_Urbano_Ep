import sqlite3

URI = "/home/pi/Urban_Urbano/db/operadores.db"

#Creando una tabla llamada geocercas_servicios.
tabla_de_operadores = '''CREATE TABLE informacion ( 
    UID INTEGER PRIMARY KEY,
    numero_de_operador INT,
    nombre VARCHAR(100)
)'''

def crear_tabla_de_operadores():
    try:
        #Establecemos la conexión con la base de datos
        con = sqlite3.connect(URI)
        cur = con.cursor()
        #Ejecutando la sentencia SQL en la variable `tabla_geocercas_servicios`.
        cur.execute(tabla_de_operadores)
        con.close()
    except Exception as e:
        print(e)
        
def obtener_operador_por_UID(UID):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM informacion WHERE UID = ? LIMIT 1", (UID,))
        operador = cur.fetchone()
        con.close()
        return operador
    except Exception as e:
        print(e)