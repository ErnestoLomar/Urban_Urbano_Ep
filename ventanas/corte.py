##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 16/08/2022
#
# Script de la ventana corte.
#
##########################################

#Librerías externas
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from time import strftime
import logging
import time
import RPi.GPIO as GPIO

#Librerías propias
import variables_globales as variables_globales
from variables_globales import VentanaActual
from enviar_vuelta import EnviarVuelta
from queries import obtener_datos_aforo
from asignaciones_queries import guardar_estado_del_viaje
from ventas_queries import obtener_ultimo_folio_de_item_venta, obtener_total_de_ventas_por_folioviaje_y_fecha

try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
except Exception as e:
    print("No se pudo inicializar el zumbador: "+str(e))

class corte(QWidget):

    close_signal = pyqtSignal()
    close_signal_pasaje = pyqtSignal()
    
    def __init__(self,close_signal_para_enviar_vuelta):
        super().__init__()
        try:
            uic.loadUi("/home/pi/Urban_Urbano//ui/corte.ui", self)

            #Creamos nuestras variables para el control del corte.
            self.close_signal_vuelta = close_signal_para_enviar_vuelta

            #Realizamos configuración de la ventana corte.
            self.setGeometry(0, 0, 800, 440)
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.close_signal_vuelta.connect(self.close_me)
            self.idUnidad = str(obtener_datos_aforo()[1])
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            self.inicializar()
        except Exception as e:
            logging.info(f"Error en la ventana corte: {e}")

    #Función para inicializar la ventana corte.
    def inicializar(self):
        try:
            self.label_fin.mousePressEvent = lambda event: self.terminar_vuelta(event, True)
            self.label_cancel.mousePressEvent = self.cancelar
        except Exception as e:
            logging.info(f"Error en la ventana corte: {e}")

    def cargar_datos(self):
        try:
            self.settings.setValue('ventana_actual', "corte")
            #variables_globales.ventana_actual = "corte"
            self.label_head.setText(f"{self.idUnidad} {str(self.settings.value('servicio')[6:])}") # Obneter todos los datos del servicio, etc, desde el archivo de settings.
            self.label_vuelta.setText(f"Vuelta {str(self.settings.value('vuelta'))}")
            
            self.label_cantidad_boletos_estud.setText(f"{str(self.settings.value('info_estudiantes')).split(',')[0]}  $")
            self.label_total_cobro_estud.setText(f"{str(self.settings.value('info_estudiantes')).split(',')[1]}")

            self.label_cantidad_boletos_normal.setText(f"{str(self.settings.value('info_normales')).split(',')[0]}  $")
            self.label_total_cobro_normal.setText(f"{str(self.settings.value('info_normales')).split(',')[1]}")

            self.label_cantidad_boletos_ninio.setText(f"{str(self.settings.value('info_chicos')).split(',')[0]}  $")
            self.label_total_cobro_ninio.setText(f"{str(self.settings.value('info_chicos')).split(',')[1]}")

            self.label_cantidad_boletos_admayor.setText(f"{str(self.settings.value('info_ad_mayores')).split(',')[0]}  $")
            self.label_total_cobro_admayor.setText(f"{str(self.settings.value('info_ad_mayores')).split(',')[1]}")
            
            self.label_total_a_liquidar.setText(self.settings.value('total_a_liquidar'))
        except Exception as e:
            logging.info(f"Error en la ventana corte: {e}")

    #Función para cerrar la ventana de corte.
    def terminar_vuelta(self, event, imprimir):
        try:
            print("El imprimir mandado es: ", imprimir)
            self.close()
            try:
                from impresora import imprimir_ticket_de_corte
            except Exception as e:
                print("No se importaron las librerias de impresora")
            
            hecho = imprimir_ticket_de_corte(self.idUnidad, imprimir)
            hora = variables_globales.hora_actual
            fecha = str(variables_globales.fecha_actual).replace('/', '-')
            csn_init = str(self.settings.value('csn_chofer'))
            self.settings.setValue('respaldo_csn_chofer', csn_init)
            total_de_boletos_db = ""
            
            if hecho:
                
                ultima_venta_bd = obtener_ultimo_folio_de_item_venta()
                print("Ultima venta en la base de datos es: "+str(ultima_venta_bd))
                logging.info(f"Ultima venta en la base de datos es: {ultima_venta_bd}")
                
                if (len(self.settings.value('folio_de_viaje')) != 0):
                    total_de_boletos_db = obtener_total_de_ventas_por_folioviaje_y_fecha(self.settings.value('folio_de_viaje'), fecha)
                elif (len(variables_globales.folio_asignacion) != 0):
                    total_de_boletos_db = obtener_total_de_ventas_por_folioviaje_y_fecha(variables_globales.folio_asignacion, fecha)
                    
                print("El total de boletos en la base de datos es: "+str(len(total_de_boletos_db)))
                logging.info(f"El total de boletos en la base de datos es: {len(total_de_boletos_db)}")
                
                total_de_folio_aforo_efectivo = int(self.settings.value('info_estudiantes').split(',')[0]) + int(self.settings.value('info_normales').split(',')[0]) + int(self.settings.value('info_chicos').split(',')[0]) + int(self.settings.value('info_ad_mayores').split(',')[0])
                print("El total de boletos en el aforo es: "+str(total_de_folio_aforo_efectivo))
                logging.info(f"El total de boletos en el aforo es: {total_de_folio_aforo_efectivo}")
                
                if ultima_venta_bd != None:
                    print("Ultima folio de venta en la bd: "+str(ultima_venta_bd[1]))
                    logging.info(f"Ultima folio de venta en la bd: {ultima_venta_bd[1]}")
                    
                    if len(total_de_boletos_db) != total_de_folio_aforo_efectivo:
                        print("La cantidad de boletos en la base de datos no coincide con la cantidad de boletos en el aforo.")
                        logging.info(f"La cantidad de boletos en la base de datos no coincide con la cantidad de boletos en el aforo.")
                        
                        '''
                        if len(total_de_boletos_db) != ultima_venta_bd[1]:
                            print("La cantidad de boletos en la base de datos no coincide con el folio de la ultima venta en la base de datos.")
                            logging.info(f"La cantidad de boletos en la base de datos no coincide con el folio de la ultima venta en la base de datos.")
                            total_de_folio_aforo_efectivo = ultima_venta_bd[1]
                            print("Se ha actualizado el total de boletos en el aforo a: "+str(total_de_folio_aforo_efectivo))
                            logging.info(f"Se ha actualizado el total de boletos en el aforo a: {total_de_folio_aforo_efectivo}")'''
                            
                        total_de_folio_aforo_efectivo = len(total_de_boletos_db)
                        print("Se ha actualizado el total de boletos en el aforo a: "+str(total_de_folio_aforo_efectivo))
                        logging.info(f"Se ha actualizado el total de boletos en el aforo a: {total_de_folio_aforo_efectivo}")
                if self.settings.value('csn_chofer_dos') == "":
                    guardar_estado_del_viaje(csn_init,f"{self.settings.value('servicio')},{self.settings.value('pension')}", fecha, hora,total_de_folio_aforo_efectivo,0,str(self.settings.value('folio_de_viaje')))
                else:
                    guardar_estado_del_viaje(str(self.settings.value('csn_chofer_dos')),f"{self.settings.value('servicio')},{self.settings.value('pension')}", fecha, hora,total_de_folio_aforo_efectivo,0,str(self.settings.value('folio_de_viaje')))
                self.close_signal.emit()
                self.close_signal_pasaje.emit()
                variables_globales.ventana_actual = VentanaActual.CERRAR_TURNO
                variables_globales.folio_asignacion = 0
                if variables_globales.folio_asignacion != 0:
                    print*("El folio de asignacion no se reinicia")
                    logging.info("El folio de asignacion no se reinicia")
                    variables_globales.folio_asignacion = 0
                self.settings.setValue('origen_actual', "")
                self.settings.setValue('folio_de_viaje', "")
                self.settings.setValue('pension', "")
                self.settings.setValue('turno', "")
                self.settings.setValue('vuelta', 1)
                self.settings.setValue('info_estudiantes', "0,0.0")
                self.settings.setValue('info_normales', "0,0.0")
                self.settings.setValue('info_chicos', "0,0.0")
                self.settings.setValue('info_ad_mayores', "0,0.0")
                self.settings.setValue('reiniciar_folios', 1)
                self.settings.setValue('total_a_liquidar', "0.0")
                self.settings.setValue('total_de_folios', 0)
                self.settings.setValue('csn_chofer_dos', "")
                self.enviar_vualta = EnviarVuelta(self.close_signal_vuelta)
                self.enviar_vualta.show()
            else:
                self.settings.setValue('csn_chofer_dos', "")
                self.settings.setValue('ventana_actual', "servicios_transbordos")
                for i in range(5):
                    GPIO.output(12, True)
                    time.sleep(0.055)
                    GPIO.output(12, False)
                    time.sleep(0.055)
                time.sleep(.5)
        except Exception as e:
            print(f"Error en la ventana corte: {e}")
            logging.info(f"Error en la ventana corte: {e}")
            for i in range(5):
                GPIO.output(12, True)
                time.sleep(0.055)
                GPIO.output(12, False)
                time.sleep(0.055)
            time.sleep(.5)

    #Función para cancelar el corte.
    def cancelar(self, event):
        try:
            self.settings.setValue('csn_chofer_dos', "")
            self.settings.setValue('ventana_actual', "servicios_transbordos")
            variables_globales.numero_de_operador_final = ""
            variables_globales.nombre_de_operador_final = ""
            self.settings.setValue('numero_de_operador_final', "")
            self.settings.setValue('nombre_de_operador_final', "")
            self.close()
        except Exception as e:
            logging.info(f"Error en la ventana corte: {e}")
    
    #Función para cerrar la ventana de corte.
    def close_me(self):
        try:
            self.close()
        except Exception as e:
            logging.info(f"Error en la ventana corte: {e}")