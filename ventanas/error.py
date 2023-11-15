##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 16/08/2022
#
# Script de la ventana error.
#
##########################################
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import logging

class VentanaError(QWidget):
    def __init__(self):
        super().__init__()
        try:
            #Realizamos configuración de la ventana error.
            self.setGeometry(0, 0 , 800, 440)
            self.setWindowFlags(Qt.FramelessWindowHint)
            uic.loadUi("/home/pi/Urban_Urbano/ui/error.ui", self)
        except Exception as e:
            logging.info(e)