##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 26/04/2022
# Ultima modificación: 16/08/2022
#
# Script para almacenar las variables globales que se esten utilizando en el programa
##########################################

version_del_software = "EL.v2.46Ep"
banderaServicio=False
longitud = 0
latitud = 0
signal = 0
connection_3g = "error"
GPS = 'error'
velocidad = 0
servicio = ""
vuelta = 0
pension = ""
csn_chofer = ""
conexion_servidor = "NO"
geocerca = "0,''"
folio_asignacion = 0
estado_del_software = ""
distancia_minima = 0.003
todos_los_servicios_activos = []
todos_los_transbordos_activos = []
vendiendo_boleto = False
detectando_geocercas_hilo = True
terminar_hilo_verificar_datos = False
vigencia_de_tarjeta = ""
numero_de_operador_inicio = ""
nombre_de_operador_inicio = ""
numero_de_operador_final = ""
nombre_de_operador_final = ""
csn_chofer_respaldo = ""
sim_id = ""
version_de_MT = "202305180001"
fecha_actual = ""
hora_actual = ""
fecha_completa_actual = ""

from enum import Enum
# La clase VentanaActual es una enumeración de los posibles valores de la variable ventana_actual
class VentanaActual(Enum):
  CHOFER = 'chofer',
  CERRAR_VUELTA = 'cerrar_vuelta',
  CERRAR_TURNO = 'cerrar_turno',
  
ventana_actual = VentanaActual.CHOFER