##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 16/08/2022
#
# Script para actualizar los iconos de la ventana de inicio.
#
##########################################

#Librerías externas
from PyQt5.QtCore import QObject, pyqtSignal
import time
import logging

from ventas_queries import obtener_estado_de_todass_las_ventas_no_enviadas
from asignaciones_queries import obtener_todass_las_asignaciones_no_enviadas, obtener_estado_de_todos_los_viajes_no_enviados

#Librerias propias
import variables_globales

#Es un QObject que emite una señal cuando está hecho.
class ActualizarIconosWorker(QObject):
    try:
        finished = pyqtSignal()
        #Creando una señal que se emitirá cuando el worker haya terminado.
        progress = pyqtSignal(dict)
    except Exception as e:
        print(e)
        logging.info(e)
    
    #Crea un nuevo hilo, y en ese hilo ejecuta una función que emite una señal cada segundo
    def run(self):
        try:
            while True:
                res = {}
                #Leer informacion
                res['longitud'] = variables_globales.longitud
                res['latitud'] = variables_globales.latitud
                res['signal_3g'] = variables_globales.signal
                res['connection_3g'] = variables_globales.connection_3g
                res["gps"] = variables_globales.GPS
                res['velocidad'] = variables_globales.velocidad
                res['servidor'] = variables_globales.conexion_servidor
                self.total_de_ventas_no_enviadas = obtener_estado_de_todass_las_ventas_no_enviadas()
                self.total_de_asignaciones_no_enviadas = obtener_todass_las_asignaciones_no_enviadas()
                self.total_de_viajes_no_enviados = obtener_estado_de_todos_los_viajes_no_enviados()
                self.cantidad_total_de_datos_no_enviados = len(self.total_de_ventas_no_enviadas) + len(self.total_de_asignaciones_no_enviadas) + len(self.total_de_viajes_no_enviados)
                res['datos_pendientes'] = self.cantidad_total_de_datos_no_enviados
                self.progress.emit(res)
                time.sleep(1)
        except Exception as e:
            print(e)
            logging.info(e)
