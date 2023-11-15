import sqlite3

URI = "/home/pi/Urban_Urbano/db/tickets_usados.db"

#Creando una tabla llamada geocercas_servicios.
tabla_de_tickets_usados = '''CREATE TABLE tickets_usados ( 
    id_ticket INTEGER PRIMARY KEY AUTOINCREMENT,
    qr VARCHAR(100),
    fecha_de_ticket_usado VARCHAR(100) DEFAULT "NO",
    fecha_de_ticket_hecho VARCHAR(100) DEFAULT "NO",
    hora_de_ticket_usado VARCHAR(100) DEFAULT "NO",
    hora_de_ticket_hecho VARCHAR(100) DEFAULT "NO",
    tramo VARCHAR(100) DEFAULT "NO",
    tipo_de_pasajero VARCHAR(100) DEFAULT "NO",
    doble_transbordo_o_no VARCHAR(100) DEFAULT "NO"
)'''

def crear_tabla_de_tickets_usados():
    try:
        #Establecemos la conexión con la base de datos
        con = sqlite3.connect(URI)
        cur = con.cursor()
        #Ejecutando la sentencia SQL en la variable `tabla_geocercas_servicios`.
        cur.execute(tabla_de_tickets_usados)
        con.close()
    except Exception as e:
        print(e)

"""
#Función para insertar una ticket usado.
def insertar_ticket_usado(qr, fecha_de_ticket_usado, fecha_de_ticket_hecho, hora_de_ticket_usado, hora_de_ticket_hecho, tramo, tipo_de_pasajero, doble_transbordo_o_no):
    cur.execute(
        f'''INSERT INTO tickets_usados(qr, fecha_de_ticket_usado, fecha_de_ticket_hecho, hora_de_ticket_usado, hora_de_ticket_hecho, tramo, tipo_de_pasajero, doble_transbordo_o_no) VALUES ('{qr}, '{fecha_de_ticket_usado}', '{fecha_de_ticket_hecho}', '{hora_de_ticket_usado}', '{hora_de_ticket_hecho}', '{tramo}', '{tipo_de_pasajero}', '{doble_transbordo_o_no}')''')
    con.commit()"""
    
#Función para insertar una ticket usado.
def insertar_ticket_usado(qr):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    cur.execute(
        f'''INSERT INTO tickets_usados(qr) VALUES ('{qr}')''')
    con.commit()
    con.close()

#Función para verificar que el ticket no haya sido usado.
def verificar_ticket(fecha_de_ticket_usado, fecha_de_ticket_hecho, hora_de_ticket_usado, hora_de_ticket_hecho, tramo, tipo_de_pasajero, doble_transbordo_o_no):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicios = f''' SELECT * FROM tickets_usados WHERE fecha_de_ticket_usado = "{fecha_de_ticket_usado}, fecha_de_ticket_hecho = "{fecha_de_ticket_hecho}, hora_de_ticket_usado = "{hora_de_ticket_usado}, hora_de_ticket_hecho = "{hora_de_ticket_hecho}, tramo = "{tramo}, tipo_de_pasajero = "{tipo_de_pasajero}, doble_transbordo_o_no = "{doble_transbordo_o_no}"'''
    cur.execute(select_servicios)
    resultado = cur.fetchone()
    con.close()
    return resultado
    
#Función para verificar que el ticket no haya sido usado.
def verificar_ticket_completo(qr):
    #Establecemos la conexión con la base de datos
    con = sqlite3.connect(URI)
    cur = con.cursor()
    select_servicios = f''' SELECT * FROM tickets_usados WHERE qr = "{qr}" LIMIT 1'''
    cur.execute(select_servicios)
    resultado = cur.fetchone()
    con.close()
    return resultado

def obtener_primer_ticket():
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM tickets_usados ORDER BY id_ticket ASC LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        print(e)
        
def seleccionar_tickets_antiguos():
    try:
        conexion = sqlite3.connect(URI,check_same_thread=False)
        cursor = conexion.cursor()
        cursor.execute(f"SELECT id_ticket, qr FROM tickets_usados")
        resultado = cursor.fetchall()
        conexion.close()
        return resultado
    except Exception as e:
        print(e)
        return False

def eliminar_tickets_antiguos(id):
    try:
        con = sqlite3.connect(URI,check_same_thread=False)
        cur = con.cursor()
        cur.execute(f"DELETE FROM tickets_usados WHERE id_ticket == {id}")
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        return False
