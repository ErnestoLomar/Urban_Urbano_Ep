from PyQt5.QtCore import QObject, pyqtSignal
import time
import logging

from ventas_queries import obtener_estado_de_todass_las_ventas_no_enviadas
from asignaciones_queries import obtener_todass_las_asignaciones_no_enviadas, obtener_estado_de_todos_los_viajes_no_enviados

class VerificarDatosWorker(QObject):
    
    try:
        finished = pyqtSignal()
        progress = pyqtSignal(dict)
    except Exception as e:
        print(e)
        logging.info(e)

    def run(self):
        try:
            while True:
                import variables_globales
                self.total_de_ventas_no_enviadas = obtener_estado_de_todass_las_ventas_no_enviadas()
                self.total_de_asignaciones_no_enviadas = obtener_todass_las_asignaciones_no_enviadas()
                self.total_de_viajes_no_enviados = obtener_estado_de_todos_los_viajes_no_enviados()
                print("Faltan enviar {} ventas, {} inicio_de_viaje y {} fin_de_viaje".format(len(self.total_de_ventas_no_enviadas), len(self.total_de_asignaciones_no_enviadas), len(self.total_de_viajes_no_enviados)))
                self.cantidad_total_de_datos_no_enviados = len(self.total_de_ventas_no_enviadas) + len(self.total_de_asignaciones_no_enviadas) + len(self.total_de_viajes_no_enviados)
                self.progress.emit({"cantidad_total_de_datos_no_enviados":self.cantidad_total_de_datos_no_enviados})
                self.continuar_o_no = variables_globales.terminar_hilo_verificar_datos
                #print("Continua o no: {}".format(self.continuar_o_no))
                if self.cantidad_total_de_datos_no_enviados == 0 or self.continuar_o_no:
                    print("Terminando hilo de verificar datos")
                    self.finished.emit()
                    break
                time.sleep(5)
        except Exception as e:
            print(e)
            logging.info(e)