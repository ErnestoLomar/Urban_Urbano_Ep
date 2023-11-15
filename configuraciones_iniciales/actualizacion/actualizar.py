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
import time
import logging

#Se hacen las importaciones necesarias
from FTP import verificar_memoria_UFS, ConfigurarFTP

class Actualizar(QWidget):
    
    def __init__(self):
        super().__init__()
        try:
            self.setGeometry(0, 0 , 800, 440)
            self.setWindowFlags(Qt.FramelessWindowHint)
            uic.loadUi("/home/pi/Urban_Urbano/ui/actualizacion.ui", self)
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            self.label_porcentaje.hide()
        except Exception as e:
            logging.info(e)

    def actualizar_raspberrypi(self, tamanio_esperado, version_matriz):
        try:
            self.label_info.setStyleSheet('font: 18pt "MS Shell Dlg 2"; color: rgb(55, 147, 72);')
            self.label_info_2.setStyleSheet('font: 18pt "MS Shell Dlg 2"; color: rgb(55, 147, 72);')
            self.label_info.setText("Recibiendo actualizaciones...")
            self.label_info_2.setText("por favor, no use la boletera")
            hacer = verificar_memoria_UFS(version_matriz)
            if hacer:
                hacer = ConfigurarFTP("azure", tamanio_esperado, version_matriz)
                if hacer:
                    self.label_info.setStyleSheet('font: 18pt "MS Shell Dlg 2"; color: rgb(55, 147, 72);')
                    self.label_info_2.setText("")
                    self.label_info.setText("Actualización correcta, reiniciando...")
                else:
                    self.label_info.setStyleSheet('font: 18pt "MS Shell Dlg 2"; color: rgb(255, 0, 0);')
                    self.label_info_2.setText("")
                    self.label_info.setText("No se completo la configuración de FTP")
                    time.sleep(5)
                    self.close()
            else:
                    self.label_info.setStyleSheet('font: 18pt "MS Shell Dlg 2"; color: rgb(255, 0, 0);')
                    self.label_info_2.setText("")
                    self.label_info.setText("No se completo la verificación de la memoria UFS")
                    time.sleep(5)
                    self.close()
        except Exception as e:
            print(e)
            self.label_info.setStyleSheet('font: 18pt "MS Shell Dlg 2"; color: rgb(255, 0, 0);')
            self.label_info_2.setText("")
            self.label_info.setText("No se completo la actualizacion")
            logging.info(e)