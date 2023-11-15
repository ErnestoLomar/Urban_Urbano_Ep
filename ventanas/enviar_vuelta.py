##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 16/08/2022
#
# Script de la ventana enviar vuelta.
#
##########################################

#Librerías externas
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import logging
import time

#Librerías propias
import variables_globales
from variables_globales import VentanaActual
from VerificarDatos import VerificarDatosWorker
class EnviarVuelta(QWidget):
    def __init__(self, close_signal):
        super().__init__()
        try:
            #Creamos nuestras variable para el control de la ventana enviar vuelta.
            self.close_signal = close_signal

            #Realizamos configuración de la ventana turno.
            uic.loadUi("/home/pi/Urban_Urbano/ui/enviar_vuelta.ui", self)
            self.setGeometry(0, 0 , 800, 440)
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.close_signal.connect(self.close_me)
            variables_globales.ventana_actual = VentanaActual.CERRAR_TURNO
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            self.settings.setValue('ventana_actual', "enviar_vuelta")
            variables_globales.terminar_hilo_verificar_datos = False
            self.terminar_hilo_verificar_datos = VerificarDatosWorker()
            self.runVerificarDatos()
        except Exception as e:
            print(e)
            logging.info(e)
            
    def runVerificarDatos(self):
        try:
            self.datosThread = QThread()
            self.datosWorker = self.terminar_hilo_verificar_datos
            self.datosWorker.moveToThread(self.datosThread)
            self.datosThread.started.connect(self.datosWorker.run)
            self.datosWorker.finished.connect(self.datosThread.quit)
            self.datosWorker.finished.connect(self.datosWorker.deleteLater)
            self.datosThread.finished.connect(self.datosThread.deleteLater)
            self.datosWorker.progress.connect(self.verificar_datos)
            self.datosThread.start()
        except Exception as e:
            print(e)
            logging.info(e)

    def verificar_datos(self, cantidad: dict):
        try:
            cantidad_de_datos_no_enviados = cantidad["cantidad_total_de_datos_no_enviados"]
            if cantidad_de_datos_no_enviados == 0:
                from abrir_ventanas import AbrirVentanas
                self.label_datos_faltantes.hide()
                self.label_no_apagar.setStyleSheet('font: 18pt "MS Shell Dlg 2"; color: rgb(55, 147, 72);')
                self.label_puntos.setStyleSheet('font: 18pt "MS Shell Dlg 2"; color: rgb(55, 147, 72);')
                self.label_no_apagar.setText(f"Datos ya enviados del viaje con servicio:")
                self.label_puntos.setText(f"{self.settings.value('servicio')[6:]}.")
                if str(self.settings.value('ventana_actual')) == str("enviar_vuelta"):
                    logging.info('Se abrirá Ventana de Cerrar Turno')
                    print("Abriendo ventana de cerrar turno en enviar_vuelta")
                    AbrirVentanas.cerrar_turno.cargar_datos()
                    AbrirVentanas.cerrar_turno.show()
            else:
                self.label_puntos.setText(f"con servicio: {self.settings.value('servicio')[6:]}.")
                self.label_datos_faltantes.setText(f"Faltan {str(cantidad_de_datos_no_enviados)} datos por enviar.")
        except Exception as e:
            print(e)
            logging.info(e)
    
    #Función para cerrar la ventana enviar vuelta.
    def close_me(self):
        try:
            variables_globales.terminar_hilo_verificar_datos = True
            self.close()
        except Exception as e:
            print(e)
            logging.info(e)