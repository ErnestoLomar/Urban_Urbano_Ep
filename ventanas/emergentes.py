from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class VentanaEmergente(QWidget):
    def __init__(self, tipo_imagen, parametro):
        super().__init__()
        # cargamos el archivo de ui
        self.setGeometry(20, 25, 761, 411)
        self.setWindowFlags(Qt.FramelessWindowHint)
        uic.loadUi("/home/pi/Urban_Urbano/ui/emergentes.ui", self)
        try:
            if tipo_imagen == "ACEPTADO":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/Aceptado.png"))
                self.label_texto.setText(str(parametro))
            elif tipo_imagen == "NODESTINO":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/NoDestino.png"))
                self.label_texto.setText(str(parametro))
            elif tipo_imagen == "EQUIVOCADO":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/Equivocado.png"))
                self.label_texto.setText(str(parametro).replace("{", "").replace("}","").replace("'", ""))
            elif tipo_imagen == "CADUCO":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/Caducado.png"))
                self.label_texto.setText(str(parametro))
            elif tipo_imagen == "UTILIZADO":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/Utilizado.png"))
                self.label_texto.setText(str(parametro))
            elif tipo_imagen == "INVALIDO":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/Invalido.png"))
                self.label_texto.setText(str(parametro))
            elif tipo_imagen == "IMPRESORA":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/problema_impresora.png"))
                self.label_texto.setText(str(parametro))
            elif tipo_imagen == "TARJETAINVALIDA":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/001.jpg"))
                self.label_texto.setText(str(parametro))
            elif tipo_imagen == "NOCORTE":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/nocorte.jpg"))
                self.label_texto.setText(str(parametro))
            elif tipo_imagen == "FUERADEVIGENCIA":
                self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/fuera_de_vigencia.jpg"))
                self.label_texto.setText(str(parametro))
        except Exception as e:
            self.label_fondo.setPixmap(QPixmap("/home/pi/Urban_Urbano/Imagenes/no.png"))
            self.label_texto.setText("")
            print("emergentes.py, linea 25: "+str(e))