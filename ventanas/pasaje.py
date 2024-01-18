##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 12/04/2022
#
# Script de la ventana pasaje.
#
##########################################

#Librerías externas
from unicodedata import decimal
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QSettings
import sys
from time import strftime
import logging
import time
import RPi.GPIO as GPIO
import subprocess
#import usb.core

sys.path.insert(1, '/home/pi/Urban_Urbano/db')

#Librerías propias
from ventas_queries import insertar_venta, insertar_item_venta, obtener_ultimo_folio_de_item_venta
from queries import obtener_datos_aforo, insertar_estadisticas_boletera
import variables_globales as vg
from emergentes import VentanaEmergente

try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
except Exception as e:
    print("No se pudo inicializar el zumbador: "+str(e))

##############################################################################################
# Clase Pasajero que representa los diferentes tipos de pasajeros que existen en el sistema
# Estudiantes, Niños, Personas normales, Personas Mayores
##############################################################################################
class Pasajero:
    def __init__(self, tipo: str, precio: decimal):

        #Creamos nuestras propiedades de la clase pasajero.
        self.tipo = tipo
        self.precio = precio
        self.total_pasajeros = 0

    #Función para obtener el subtotal de los pasajeros.
    def sub_total(self):
        try:
            return self.total_pasajeros * self.precio
        except Exception as e:
            logging.info(e)

    #Aumentamos en uno el numero de pasajeros
    def aumentar_pasajeros(self):
        try:
            self.total_pasajeros = self.total_pasajeros + 1
        except Exception as e:
            logging.info(e)


class VentanaPasaje(QWidget):
    def __init__(self, precio, de: str, hacia: str, precio_preferente, close_signal, servicio_o_transbordo: str, id_tabla, ruta, tramo, cerrar_ventana_servicios):
        super().__init__()
        try:
            uic.loadUi("/home/pi/Urban_Urbano/ui/pasaje.ui", self)

            #Creamos nuestras variables para la ventana pasaje.
            self.origen = de
            self.destino = hacia
            self.close_signal = close_signal
            self.cerrar_servicios = cerrar_ventana_servicios
            self.precio = precio
            self.precio_preferente = precio_preferente
            self.personas_normales = Pasajero("personas_normales", self.precio)
            self.estudiantes = Pasajero("estudiantes", self.precio_preferente)
            self.personas_mayores = Pasajero("personas_mayores", self.precio_preferente)
            self.chicos = Pasajero("chicos", self.precio_preferente)
            self.servicio_o_transbordo = servicio_o_transbordo.split(',')
            self.id_tabla = id_tabla
            self.ruta = ruta
            self.tramo = tramo
            #vg.vendiendo_boleto = True

            #Realizamos configuraciones de la ventana pasaje.
            self.close_signal.connect(self.close_me)
            self.inicializar_labels()
            self.label_de.setText("De: " + str(de.split("_")[0]))
            self.label_hacia.setText("A: "+ str(hacia.split("_")[0]))
            self.label_8.setText('$'+str(precio))
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            self.Unidad = str(obtener_datos_aforo()[1])
        except Exception as e:
            logging.info(e)
    
    #Función para cerrar la ventana pasaje.
    def close_me(self):
        try:
            vg.vendiendo_boleto = False
            self.close()
        except Exception as e:
            logging.info(e)

    #Inicializamos las señales de los labels al darles click
    def inicializar_labels(self):
        try:
            self.label_volver.mousePressEvent = self.handle_volver
            self.label_ninos.mousePressEvent = self.handle_ninos
            self.label_estudiantes.mousePressEvent = self.handle_estudiantes
            self.label_mayores_edad.mousePressEvent = self.handle_mayores_edad
            self.label_personas_normales.mousePressEvent = self.handle_personas_normales
            self.label_pagar.mousePressEvent = self.handle_pagar
        except Exception as e:
            logging.info(e)

    #Función para volver a la ventana pasada.
    def handle_volver(self, event):
        try:
            vg.vendiendo_boleto = False
            self.close()
        except Exception as e:
            logging.info(e)

    #Función para manejar el evento de darle click al label de los niños
    def handle_ninos(self, event):
        try:
            self.chicos.aumentar_pasajeros()
            self.label_ninos_total.setText(str(self.chicos.total_pasajeros))
            self.label_ninos_total_precio.setText("$ "+str(int(self.chicos.sub_total())))
            self.calcularTotal()
        except Exception as e:
            logging.info(e)

    #Función para manejar el evento de darle click al label de los estudiantes
    def handle_estudiantes(self, event):
        try:
            self.estudiantes.aumentar_pasajeros()
            self.label_estudiantes_total.setText(str(self.estudiantes.total_pasajeros))
            self.label_estudiantes_total_precio.setText("$ "+str(int(self.estudiantes.sub_total())))
            self.calcularTotal()
        except Exception as e:
            logging.info(e)

    #Función para manejar el evento de darle click al label de las personas mayores
    def handle_mayores_edad(self, event):
        try:
            self.personas_mayores.aumentar_pasajeros()
            self.label_mayores_total.setText(str(self.personas_mayores.total_pasajeros))
            self.label_mayores_total_precio.setText("$ "+str(int(self.personas_mayores.sub_total())))
            self.calcularTotal()
        except Exception as e:
            logging.info(e)

    #Función para manejar el evento de darle click al label de las personas normales
    def handle_personas_normales(self, event):
        try:
            self.personas_normales.aumentar_pasajeros()
            self.label_normales_total.setText(str(self.personas_normales.total_pasajeros))
            self.label_normales_total_precio.setText("$ "+str(int(self.personas_normales.sub_total())))
            self.calcularTotal()
        except Exception as e:
            logging.info(e)

    #Función para manejar el evento de darle click al label pagar
    def handle_pagar(self, event):
        try:
            
            if self.calcularTotal() == 0:
                return
            
            self.close_me()
            
            
            if len(vg.folio_asignacion) <= 1:
                
                self.ve = VentanaEmergente("VOID", "No existe viaje", 4.5)
                self.ve.show()
                for i in range(5):
                    GPIO.output(12, True)
                    time.sleep(0.055)
                    GPIO.output(12, False)
                    time.sleep(0.055)
                
                self.cerrar_servicios.emit()
                
                return
            
            try:
                from impresora import imprimir_boleto_normal_pasaje, imprimir_boleto_con_qr_pasaje
            except Exception as e:
                print("No se importaron las librerias de impresora")
            
            #self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(self.calcularTotal())}") #<--- Cambiar total a liquidar
            
            estudiantes = self.estudiantes
            normales = self.personas_normales
            chicos = self.chicos
            mayores = self.personas_mayores

            full_date = strftime("%Y/%m/%d %H:%M:%S")
            fecha = str(strftime('%d-%m-%Y')).replace('/', '-')
            
            fecha_estadistica = strftime('%Y/%m/%d').replace('/', '')[2:]
                
            # Procedemos a obtener la hora de la boletera
            fecha_actual_estadistica = str(subprocess.run("date", stdout=subprocess.PIPE, shell=True))
            indice = fecha_actual_estadistica.find(":")
            hora_estadistica = str(fecha_actual_estadistica[(int(indice) - 2):(int(indice) + 6)]).replace(":","")
            
            try:

                if self.servicio_o_transbordo[0] == 'SER':
                    
                    if estudiantes.total_pasajeros > 0:
                        folio = 0
                        for i in range(estudiantes.total_pasajeros):
                            
                            # Obtenemos el ultimo folio de venta de la base de datos.
                            ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                            
                            if ultimo_folio_de_venta != None:
                                folio = ultimo_folio_de_venta[1] + 1
                                if ultimo_folio_de_venta == folio:
                                    logging.info("Folio repetido por reiniciar_folios 0")
                                    folio = ultimo_folio_de_venta[1] + 1
                            else:
                                folio = 1
                            hora = strftime("%H:%M:%S")
                            hecho = imprimir_boleto_normal_pasaje(str(folio),str(fecha),str(hora),str(self.Unidad),'ESTUDIANTE',str(estudiantes.precio),str(self.ruta),str(self.tramo))
                            if hecho:
                                insertar_item_venta(folio, str(self.settings.value('folio_de_viaje')), fecha, hora, int(self.id_tabla), int(str(self.settings.value('geocerca')).split(",")[0]), 1, "n", "preferente", "estudiante", estudiantes.precio)
                                total_boletos_estudiantes = str(self.settings.value('info_estudiantes')).split(',')[0]
                                subtotal_estudiantes = str(self.settings.value('info_estudiantes')).split(',')[1]
                                total_boletos_estudiantes = int(total_boletos_estudiantes) + 1
                                subtotal_estudiantes = float(subtotal_estudiantes) + float(estudiantes.precio)
                                self.settings.setValue('info_estudiantes', f"{total_boletos_estudiantes},{subtotal_estudiantes}")
                                self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(estudiantes.precio)}")
                                self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                logging.info("Boleto de estudiante impreso")
                            else:
                                insertar_estadisticas_boletera(str(self.Unidad), fecha_estadistica, hora_estadistica, "BMI", f"SE")
                                logging.info("No se pudo imprimir el boleto, error al imprimir el boleto")
                                
                                self.ve = VentanaEmergente("IMPRESORA", "", 4.5)
                                self.ve.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)
                
                    if normales.total_pasajeros > 0:
                        for i in range(normales.total_pasajeros):
                            ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                            if ultimo_folio_de_venta != None:
                                folio = ultimo_folio_de_venta[1] + 1
                                if ultimo_folio_de_venta == folio:
                                    logging.info("Folio repetido por reiniciar_folios 0")
                                    folio = ultimo_folio_de_venta[1] + 1
                            else:
                                folio = 1
                            hora = strftime("%H:%M:%S")
                            hecho = imprimir_boleto_normal_pasaje(str(folio),str(fecha),str(hora),str(self.Unidad),'NORMAL',str(normales.precio),str(self.ruta),str(self.tramo))
                            if hecho:
                                insertar_item_venta(folio, str(self.settings.value('folio_de_viaje')), fecha, hora, int(self.id_tabla), int(str(self.settings.value('geocerca')).split(",")[0]), 2, "n", "normal", "normal", normales.precio)
                                total_boletos_normales = str(self.settings.value('info_normales')).split(',')[0]
                                subtotal_normales = str(self.settings.value('info_normales')).split(',')[1]
                                total_boletos_normales = int(total_boletos_normales) + 1
                                subtotal_normales = float(subtotal_normales) + float(normales.precio)
                                self.settings.setValue('info_normales', f"{total_boletos_normales},{subtotal_normales}")
                                self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(normales.precio)}")
                                self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                logging.info("Boleto normal impreso")
                            else:
                                insertar_estadisticas_boletera(str(self.Unidad), fecha_estadistica, hora_estadistica, "BMI", f"SN")
                                logging.info("No se pudo imprimir el boleto, error al imprimir el boleto")
                                
                                self.ve = VentanaEmergente("IMPRESORA", "", 4.5)
                                self.ve.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)

                    if chicos.total_pasajeros > 0:
                        for i in range(chicos.total_pasajeros):
                            ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                            if ultimo_folio_de_venta != None:
                                folio = ultimo_folio_de_venta[1] + 1
                                if ultimo_folio_de_venta == folio:
                                    logging.info("Folio repetido por reiniciar_folios 0")
                                    folio = ultimo_folio_de_venta[1] + 1
                            else:
                                folio = 1
                            hora = strftime("%H:%M:%S")
                            hecho = imprimir_boleto_normal_pasaje(str(folio),str(fecha),str(hora),str(self.Unidad),'MENOR',str(chicos.precio),str(self.ruta),str(self.tramo))
                            if hecho:
                                insertar_item_venta(folio, str(self.settings.value('folio_de_viaje')), fecha, hora, int(self.id_tabla), int(str(self.settings.value('geocerca')).split(",")[0]), 3, "n", "preferente", "chico", chicos.precio)
                                total_boletos_chicos = str(self.settings.value('info_chicos')).split(',')[0]
                                subtotal_chicos = str(self.settings.value('info_chicos')).split(',')[1]
                                total_boletos_chicos = int(total_boletos_chicos) + 1
                                subtotal_chicos = float(subtotal_chicos) + float(chicos.precio)
                                self.settings.setValue('info_chicos', f"{total_boletos_chicos},{subtotal_chicos}")
                                self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(chicos.precio)}")
                                self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                logging.info("Boleto chico impreso")
                            else:
                                insertar_estadisticas_boletera(str(self.Unidad), fecha_estadistica, hora_estadistica, "BMI", f"SM")
                                logging.info("No se pudo imprimir el boleto, error al imprimir el boleto")
                                
                                self.ve = VentanaEmergente("IMPRESORA", "", 4.5)
                                self.ve.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)
                    
                    if mayores.total_pasajeros > 0:
                        for i in range(mayores.total_pasajeros):
                            ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                            if ultimo_folio_de_venta != None:
                                folio = ultimo_folio_de_venta[1] + 1
                                if ultimo_folio_de_venta == folio:
                                    logging.info("Folio repetido por reiniciar_folios 0")
                                    folio = ultimo_folio_de_venta[1] + 1
                            else:
                                folio = 1
                            hora = strftime("%H:%M:%S")
                            hecho = imprimir_boleto_normal_pasaje(str(folio),str(fecha),str(hora),str(self.Unidad),'MAYOR',str(mayores.precio),str(self.ruta),str(self.tramo))
                            if hecho:
                                insertar_item_venta(folio, str(self.settings.value('folio_de_viaje')), fecha, hora, int(self.id_tabla), int(str(self.settings.value('geocerca')).split(",")[0]), 4, "n", "preferente", "mayor", mayores.precio)
                                total_boletos_mayores = str(self.settings.value('info_ad_mayores')).split(',')[0]
                                subtotal_mayores = str(self.settings.value('info_ad_mayores')).split(',')[1]
                                total_boletos_mayores = int(total_boletos_mayores) + 1
                                subtotal_mayores = float(subtotal_mayores) + float(mayores.precio)
                                self.settings.setValue('info_ad_mayores', f"{total_boletos_mayores},{subtotal_mayores}")
                                self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(mayores.precio)}")
                                self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                logging.info("Boleto adulto mayor impreso")
                            else:
                                insertar_estadisticas_boletera(str(self.Unidad), fecha_estadistica, hora_estadistica, "BMI", f"SA")
                                logging.info("No se pudo imprimir el boleto, error al imprimir el boleto")
                                
                                self.ve = VentanaEmergente("IMPRESORA", "", 4.5)
                                self.ve.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)

                else:
                    if estudiantes.total_pasajeros > 0:
                        folio = 0
                        for i in range(estudiantes.total_pasajeros):
                            ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                            if ultimo_folio_de_venta != None:
                                folio = ultimo_folio_de_venta[1] + 1
                                if ultimo_folio_de_venta == folio:
                                    logging.info("Folio repetido por reiniciar_folios 0")
                                    folio = ultimo_folio_de_venta[1] + 1
                            else:
                                folio = 1
                            hora = strftime("%H:%M:%S")
                            hecho = imprimir_boleto_con_qr_pasaje(str(folio),str(fecha),str(hora),str(self.Unidad),'ESTUDIANTE',str(estudiantes.precio),str(self.ruta),str(self.tramo),self.servicio_o_transbordo)
                            if hecho:
                                insertar_item_venta(folio, str(self.settings.value('folio_de_viaje')), fecha, hora, int(self.id_tabla), int(str(self.settings.value('geocerca')).split(",")[0]), 1, "t", "preferente", "estudiante", estudiantes.precio)
                                total_boletos_estudiantes = str(self.settings.value('info_estudiantes')).split(',')[0]
                                subtotal_estudiantes = str(self.settings.value('info_estudiantes')).split(',')[1]
                                total_boletos_estudiantes = int(total_boletos_estudiantes) + 1
                                subtotal_estudiantes = float(subtotal_estudiantes) + float(estudiantes.precio)
                                self.settings.setValue('info_estudiantes', f"{total_boletos_estudiantes},{subtotal_estudiantes}")
                                self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(estudiantes.precio)}")
                                self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                logging.info("Boleto con QR de estudiante impreso")
                            else:
                                insertar_estadisticas_boletera(str(self.Unidad), fecha_estadistica, hora_estadistica, "BMI", f"TE")
                                logging.info("No se pudo imprimir el boleto, error al imprimir el boleto")
                                
                                self.ve = VentanaEmergente("IMPRESORA", "", 4.5)
                                self.ve.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)
                
                    if normales.total_pasajeros > 0:
                        for i in range(normales.total_pasajeros):
                            ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                            if ultimo_folio_de_venta != None:
                                folio = ultimo_folio_de_venta[1] + 1
                                if ultimo_folio_de_venta == folio:
                                    logging.info("Folio repetido por reiniciar_folios 0")
                                    folio = ultimo_folio_de_venta[1] + 1
                            else:
                                folio = 1
                            hora = strftime("%H:%M:%S")
                            hecho = imprimir_boleto_con_qr_pasaje(str(folio),str(fecha),str(hora),str(self.Unidad),'NORMAL',str(normales.precio),str(self.ruta),str(self.tramo),self.servicio_o_transbordo)
                            if hecho:
                                insertar_item_venta(folio, str(self.settings.value('folio_de_viaje')), fecha, hora, int(self.id_tabla), int(str(self.settings.value('geocerca')).split(",")[0]), 2, "t", "normal", "normal", normales.precio)
                                total_boletos_normales = str(self.settings.value('info_normales')).split(',')[0]
                                subtotal_normales = str(self.settings.value('info_normales')).split(',')[1]
                                total_boletos_normales = int(total_boletos_normales) + 1
                                subtotal_normales = float(subtotal_normales) + float(normales.precio)
                                self.settings.setValue('info_normales', f"{total_boletos_normales},{subtotal_normales}")
                                self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(normales.precio)}")
                                self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                logging.info("Boleto con QR de normal impreso")
                            else:
                                insertar_estadisticas_boletera(str(self.Unidad), fecha_estadistica, hora_estadistica, "BMI", f"TN")
                                logging.info("No se pudo imprimir el boleto, error al imprimir el boleto")
                                
                                self.ve = VentanaEmergente("IMPRESORA", "", 4.5)
                                self.ve.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)

                    if chicos.total_pasajeros > 0:
                        for i in range(chicos.total_pasajeros):
                            ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                            if ultimo_folio_de_venta != None:
                                folio = ultimo_folio_de_venta[1] + 1
                                if ultimo_folio_de_venta == folio:
                                    logging.info("Folio repetido por reiniciar_folios 0")
                                    folio = ultimo_folio_de_venta[1] + 1
                            else:
                                folio = 1
                            hora = strftime("%H:%M:%S")
                            hecho = imprimir_boleto_con_qr_pasaje(str(folio),str(fecha),str(hora),str(self.Unidad),'MENOR',str(chicos.precio),str(self.ruta),str(self.tramo),self.servicio_o_transbordo)
                            if hecho:
                                insertar_item_venta(folio, str(self.settings.value('folio_de_viaje')), fecha, hora, int(self.id_tabla), int(str(self.settings.value('geocerca')).split(",")[0]), 3, "t", "preferente", "chico", chicos.precio)
                                total_boletos_chicos = str(self.settings.value('info_chicos')).split(',')[0]
                                subtotal_chicos = str(self.settings.value('info_chicos')).split(',')[1]
                                total_boletos_chicos = int(total_boletos_chicos) + 1
                                subtotal_chicos = float(subtotal_chicos) + float(chicos.precio)
                                self.settings.setValue('info_chicos', f"{total_boletos_chicos},{subtotal_chicos}")
                                self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(chicos.precio)}")
                                self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                logging.info("Boleto con QR de chico impreso")
                            else:
                                insertar_estadisticas_boletera(str(self.Unidad), fecha_estadistica, hora_estadistica, "BMI", f"TM")
                                logging.info("No se pudo imprimir el boleto, error al imprimir el boleto")
                                
                                self.ve = VentanaEmergente("IMPRESORA", "", 4.5)
                                self.ve.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)
                    
                    if mayores.total_pasajeros > 0:
                        for i in range(mayores.total_pasajeros):
                            ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                            if ultimo_folio_de_venta != None:
                                folio = ultimo_folio_de_venta[1] + 1
                                if ultimo_folio_de_venta == folio:
                                    logging.info("Folio repetido por reiniciar_folios 0")
                                    folio = ultimo_folio_de_venta[1] + 1
                            else:
                                folio = 1
                            hora = strftime("%H:%M:%S")
                            hecho = imprimir_boleto_con_qr_pasaje(str(folio),str(fecha),str(hora),str(self.Unidad),'MAYOR',str(mayores.precio),str(self.ruta),str(self.tramo),self.servicio_o_transbordo)
                            if hecho:
                                insertar_item_venta(folio, str(self.settings.value('folio_de_viaje')), fecha, hora, int(self.id_tabla), int(str(self.settings.value('geocerca')).split(",")[0]), 4, "t", "preferente", "mayor", mayores.precio)
                                total_boletos_mayores = str(self.settings.value('info_ad_mayores')).split(',')[0]
                                subtotal_mayores = str(self.settings.value('info_ad_mayores')).split(',')[1]
                                total_boletos_mayores = int(total_boletos_mayores) + 1
                                subtotal_mayores = float(subtotal_mayores) + float(mayores.precio)
                                self.settings.setValue('info_ad_mayores', f"{total_boletos_mayores},{subtotal_mayores}")
                                self.settings.setValue('total_a_liquidar', f"{float(self.settings.value('total_a_liquidar')) + float(mayores.precio)}")
                                self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                logging.info("Boleto con QR de mayor impreso")
                            else:
                                insertar_estadisticas_boletera(str(self.Unidad), fecha_estadistica, hora_estadistica, "BMI", f"TA")
                                logging.info("No se pudo imprimir el boleto, error al imprimir el boleto")
                                
                                self.ve = VentanaEmergente("IMPRESORA", "", 4.5)
                                self.ve.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)
            except Exception as e:
                print(e)
                for i in range(5):
                    GPIO.output(12, True)
                    time.sleep(0.055)
                    GPIO.output(12, False)
                    time.sleep(0.055)
                time.sleep(.5)
            insertar_venta(full_date, self.origen, self.destino, self.calcularTotal())
        except Exception as e:
            print(e)
            logging.info(e)

    #Función para calcular el total de todos los pasajeros
    def calcularTotal(self):
        try:
            totalPersonas = self.chicos.total_pasajeros + self.estudiantes.total_pasajeros + self.personas_mayores.total_pasajeros + self.personas_normales.total_pasajeros
            totalPrecio = self.chicos.sub_total() + self.estudiantes.sub_total() + self.personas_mayores.sub_total() + self.personas_normales.sub_total()
            self.label_personas_total.setText(str(totalPersonas))
            self.label_total_precio.setText("$ "+str(int(totalPrecio)))
            return totalPrecio
        except Exception as e:
            logging.info(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = VentanaPasaje(10, "calle #33", "calle #45")
    GUI.show()
    sys.exit(app.exec())