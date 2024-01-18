##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 10/05/2023
# Ultima modificación: 10/05/2023
#
# Script principal para iniciar el sistema
#
##########################################

#Librerías externas
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import logging
import time
import subprocess

sys.path.insert(1, '/home/pi/Urban_Urbano/utils')

import variables_globales as vg
from quectelWorker import QuectelWorker

'''
from asignaciones_queries import eliminar_auto_asignaciones_antiguas, eliminar_fin_de_viaje_antiguos
from tickets_usados import eliminar_tickets_antiguos
from ventas_queries import eliminar_ventas_antiguas
'''

class Configuraciones(QWidget):
    
    def __init__(self):
        super(Configuraciones, self).__init__()
        try:
            self.setGeometry(0, 0 , 800, 480)
            self.setWindowFlags(Qt.FramelessWindowHint)
            uic.loadUi("/home/pi/Urban_Urbano/ui/actualizacion_mt.ui", self)
            self.runQuectel()

        except Exception as e:
            logging.info(e)
            print("Ocurrio un problema al iniciar el 'init' de la ventana de encender_quectel")
            
    def reportProgressQuectel(self, res: bool):
        try:
            if res:
                self.close()
                subprocess.run("sudo python3 /home/pi/Urban_Urbano/ventanas/inicio.py",shell=True)
        except Exception as e:
            print("Error en el hilo del QuectelWorker: "+str(e))

    def runQuectel(self):
        try:
            self.minicomThread = QThread()
            self.minicomWorker = QuectelWorker()
            self.minicomWorker.moveToThread(self.minicomThread)
            self.minicomThread.started.connect(self.minicomWorker.run)
            self.minicomWorker.finished.connect(self.minicomThread.quit)
            self.minicomWorker.finished.connect(self.minicomWorker.deleteLater)
            self.minicomThread.finished.connect(self.minicomThread.deleteLater)
            self.minicomWorker.progress.connect(self.reportProgressQuectel)
            self.minicomThread.start()
        except Exception as e:
            logging.info("Error al iniciar el hilo de quectel: " + str(e))
            print("Error al iniciar el hilo de quectel: " + str(e))
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = Configuraciones()
    GUI.show()
    sys.exit(app.exec())