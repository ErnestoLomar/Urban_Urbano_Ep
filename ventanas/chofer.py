##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 11/04/2022
# Ultima modificación: 16/04/2022
#
# Script de la ventana chofer.
#
##########################################

#Librerías externas
import datetime
import subprocess
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QSettings
import sys
from servicios import Rutas
from time import strftime
import logging
import RPi.GPIO as GPIO
import time

#Librerías propias
from servicio_pensiones import obtener_servicios_de_pension, obtener_pensiones
import variables_globales as vg
from asignaciones_queries import guardar_auto_asignacion, obtener_ultima_asignacion, aniadir_folio_de_viaje_a_auto_asignacion, eliminar_auto_asignacion_por_folio, obtener_ultimo_folio_auto_asignacion, modificar_folio_auto_asignacion
from queries import obtener_datos_aforo
from matrices_tarifarias import obtener_servicio_por_numero_de_servicio_y_origen, obtener_transbordos_por_origen_y_numero_de_servicio
from servicio_pensiones import obtener_origen_por_numero_de_servicio

try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(33, GPIO.OUT)
except Exception as e:
    print("No se pudo inicializar el ventilador: "+str(e))

class VentanaChofer(QWidget):

    def __init__(self,close_signal, close_signal_pasaje):
        super().__init__()
        try:
            uic.loadUi("/home/pi/Urban_Urbano/ui/chofer.ui", self)

            #Realizamos configuración de la ventana chofer.
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            self.settings.setValue('ventana_actual', "chofer")
            #vg.ventana_actual = "chofer"
            if len(vg.csn_chofer) != 0:
                self.settings.setValue('csn_chofer', vg.csn_chofer)
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setGeometry(0,0,800, 480)
            self.inicializar_comboBox()
            self.inicializar_labels()
            #self.cargar_datos()
            self.spinBox_vuelta.valueChanged.connect(self.handle_spin)
            self.spinBox_vuelta.setMinimum(1)

            #Creamos nuestras variables para guardar los datos
            self.close_signal = close_signal
            self.close_signal_pasaje = close_signal_pasaje
            self.turno = ""
            self.pension = ""
            self.servicio = ""
            self.vuelta = 1
            self.pension_selec = ""
            self.idUnidad = str(obtener_datos_aforo()[1])
            self.intentos = 1
        except Exception as e:
            print(e)
            logging.info(e)

    #Inicializamos las señales de los labels al darles click
    def inicializar_labels(self):
        try:
            self.label_ok.mousePressEvent = self.handle_ok
            self.label_cancel.mousePressEvent = self.handle_cancel
        except Exception as e:
            print(e)
            logging.info(e)
    
    #Función para cargar los datos de las rutas de la base de datos.
    def cargar_pensiones_db(self):
        try:
            self.lista_pensiones = []
            self.lista_pensiones_db = obtener_pensiones()
            for p in self.lista_pensiones_db:
                pension = p[1]
                if pension != "AlttusTI":
                    self.lista_pensiones.append(pension)
        except Exception as e:
            print(e)
            logging.info(e)
        
    #Inicializamos el comboBox con los datos de los turnos y servicios
    def inicializar_comboBox(self):
        try:
            #Cargamos las pensiones de la base de datos
            self.cargar_pensiones_db()
            
            #ComboBox de turnos
            self.comboBox_turno.setStyleSheet('selection-background-color: gray; font: 18pt "Rockwell";')
            self.lista_turnos = {"Matutino": "Matutino", "Vespertino": "Vespertino"}
            self.comboBox_turno.addItems(self.lista_turnos)
            self.comboBox_turno.activated[str].connect(self.turno_seleccionado)

            #ComboBox de pensiones
            self.comboBox_pension.setStyleSheet('QComboBox { combobox-popup: 1; selection-background-color: gray; font: 18pt "Rockwell";}')
            self.comboBox_pension.setMaxVisibleItems(15)
            self.comboBox_pension.addItems(self.lista_pensiones)
            self.comboBox_pension.activated[str].connect(self.pension_seleccionada)
            self.comboBox_pension.setCurrentIndex(20)

            
            #ComboBox de servicios
            self.comboBox_servicio.setStyleSheet('QComboBox { combobox-popup: 1; selection-background-color: gray; font: 18pt "Rockwell";}')
            self.comboBox_servicio.setMaxVisibleItems(15)
            self.comboBox_servicio.activated[str].connect(self.servicio_seleccionado)
        except Exception as e:
            print(e)
            logging.info(e)


    #Función para manejar el evento del spin (Vuelta)
    def handle_spin(self):
        try:
            self.vuelta = self.spinBox_vuelta.value()
            vg.vuelta = self.vuelta
            self.settings.setValue('vuelta', self.vuelta)
        except Exception as e:
            print(e)
            logging.info(e)

    #Función para manejar el evento de darle click al label ok
    def handle_ok(self, event):
        try:
            # Si el servicio que se seleccionó esta vació quiere decir que escogieron la primer opción de la pensión, entonces lo buscamos manualmente 
            # si no escogemos el que seleccionaron.
            self.close()
            fecha_completa = strftime('%Y-%m-%d %H:%M:%S')
            hora = strftime('%H:%M:%S')
            
            # Obtenemos la fecha actual de la raspberry
            
            # Ejecutar el comando date y obtener la salida
            #result = subprocess.run(['date', '+%d/%m/%Y'], stdout=subprocess.PIPE)

            # Decodificar la salida en formato de cadena de caracteres
            #fecha = datetime.datetime.strptime(str(result.stdout.decode('utf-8').strip()), "%d/%m/%Y").strftime("%d/%m/%Y")
            
            fecha_vg = str(vg.fecha_actual).replace('/', '-')
            
            print("La fecha actual de la raspberry es: ", fecha_vg)

            if self.pension_selec != "":
                if self.servicio != "":
                    origen = obtener_origen_por_numero_de_servicio(int(self.servicio.split(" - ")[0]))
                    total_de_servicios = obtener_servicio_por_numero_de_servicio_y_origen(int(self.servicio.split(" - ")[0]), str(origen[3]).replace("(", "").replace(")", "").replace(",", "").replace("'", ""))
                    if len(total_de_servicios) != 0:
                        # Obtenemos el ultimo folio de auto_asignacion en la base de datos
                        ultima_asignacion = obtener_ultima_asignacion()
                        print("La ultima asignacion es: ", ultima_asignacion)
                        
                        self.settings.setValue('servicio', self.servicio)
                        self.settings.setValue('pension', self.pension_selec)
                        self.settings.setValue('turno', self.comboBox_turno.currentText())
                        guardar_auto_asignacion(self.settings.value('csn_chofer'), f"{self.settings.value('servicio')},{self.settings.value('pension')}", fecha_vg, hora)
                        folio = self.crear_folio()
                        
                        # Revisamos que el folio se haya incrementado.
                        if ultima_asignacion != None:
                            if ultima_asignacion[1] == folio:
                                print("Se procederá a aumentar el folio ya que es el mismo que el anterior")
                                logging.info("Se procederá a aumentar el folio ya que es el mismo que el anterior")
                                folio = obtener_ultimo_folio_auto_asignacion()['folio'] + 1
                                modificar_folio_auto_asignacion(folio, ultima_asignacion[0])
                        print("Folio creado: ", folio)
                        
                        while True:
                            folio_de_viaje = f"{''.join(fecha_completa[:10].split('-'))[3:]}{self.idUnidad}{folio}"
                            if len(folio_de_viaje) == 12:
                                vg.servicio = self.servicio
                                vg.turno = self.comboBox_turno.currentText()
                                vg.folio_asignacion = folio_de_viaje
                                self.settings.setValue('folio_de_viaje', folio_de_viaje)
                                print("Folio de viaje: ", folio_de_viaje)
                                logging.info(f"Folio de viaje: {folio_de_viaje}")
                                aniadir_folio_de_viaje_a_auto_asignacion(folio, folio_de_viaje, fecha_vg)
                                self.rutas = Rutas(self.turno, self.servicio, self.close_signal, self.close_signal_pasaje)
                                self.rutas.setGeometry(0, 0, 800, 440)
                                self.rutas.setWindowFlags(Qt.FramelessWindowHint)
                                self.rutas.show()
                                break
                            if self.intentos == 3:
                                self.intentos = 0
                                ultimo_folio_de_autoasignacion = str(obtener_ultima_asignacion()[1])
                                eliminar_auto_asignacion_por_folio(ultimo_folio_de_autoasignacion)
                                print("No se creo correctamente el folio")
                                GPIO.output(33, False)
                                self.servicio = ""
                                vg.csn_chofer = ""
                                self.settings.setValue('ventana_actual', "")
                                self.settings.setValue('csn_chofer', "")
                                
                                vg.numero_de_operador_inicio = ""
                                vg.numero_de_operador_final = ""
                                vg.nombre_de_operador_inicio = ""
                                vg.nombre_de_operador_final = ""
                                self.settings.setValue('numero_de_operador_inicio', "")
                                self.settings.setValue('numero_de_operador_final', "")
                                self.settings.setValue('nombre_de_operador_inicio', "")
                                self.settings.setValue('nombre_de_operador_final', "")
                                
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)
                                break
                            self.intentos += 1
                    else:
                        print("No hay servicios disponibles1")
                        print("Total de servicios1: ", len(total_de_servicios))
                        GPIO.output(33, False)
                        self.servicio = ""
                        vg.csn_chofer = ""
                        self.settings.setValue('ventana_actual', "")
                        self.settings.setValue('csn_chofer', "")
                        
                        vg.numero_de_operador_inicio = ""
                        vg.numero_de_operador_final = ""
                        vg.nombre_de_operador_inicio = ""
                        vg.nombre_de_operador_final = ""
                        self.settings.setValue('numero_de_operador_inicio', "")
                        self.settings.setValue('numero_de_operador_final', "")
                        self.settings.setValue('nombre_de_operador_inicio', "")
                        self.settings.setValue('nombre_de_operador_final', "")
                        
                        for i in range(5):
                            GPIO.output(12, True)
                            time.sleep(0.055)
                            GPIO.output(12, False)
                            time.sleep(0.055)
                else:
                    origen = obtener_origen_por_numero_de_servicio(int(str(self.comboBox_servicio.currentText()).split(" - ")[0]))
                    total_de_servicios = obtener_servicio_por_numero_de_servicio_y_origen(int(str(self.comboBox_servicio.currentText()).split(" - ")[0]), str(origen[3]).replace("(", "").replace(")", "").replace(",", "").replace("'", ""))
                    if len(total_de_servicios) != 0:
                        vg.servicio = self.comboBox_servicio.currentText()
                        self.settings.setValue('servicio', self.comboBox_servicio.currentText())
                        self.settings.setValue('pension', self.pension_selec)
                        vg.turno = self.comboBox_turno.currentText()
                        self.settings.setValue('turno', self.comboBox_turno.currentText())
                        
                        # Obtenemos el ultimo folio de auto_asignacion en la base de datos
                        ultima_asignacion = obtener_ultima_asignacion()
                        print("La ultima asignacion es: ", ultima_asignacion)
                        
                        guardar_auto_asignacion(self.settings.value('csn_chofer'), f"{self.settings.value('servicio')},{self.settings.value('pension')}", fecha_vg, hora)
                        folio = self.crear_folio()
                        
                        # Revisamos que el folio se haya incrementado.
                        if ultima_asignacion != None:
                            if ultima_asignacion[1] == folio:
                                print("Se procederá a aumentar el folio ya que es el mismo que el anterior")
                                logging.info("Se procederá a aumentar el folio ya que es el mismo que el anterior")
                                folio = obtener_ultimo_folio_auto_asignacion()['folio'] + 1
                                modificar_folio_auto_asignacion(folio, ultima_asignacion[0])
                        
                        print("Folio creado: ", folio)
                        while True:
                            folio_de_viaje = f"{''.join(fecha_completa[:10].split('-'))[3:]}{self.idUnidad}{folio}"
                            if len(folio_de_viaje) == 12:
                                vg.folio_asignacion = folio_de_viaje
                                self.settings.setValue('folio_de_viaje', folio_de_viaje)
                                print("Folio de viaje: ", folio_de_viaje)
                                logging.info(f"Folio de viaje: {folio_de_viaje}")
                                aniadir_folio_de_viaje_a_auto_asignacion(folio, folio_de_viaje, fecha_vg)
                                self.rutas = Rutas(self.turno, self.comboBox_servicio.currentText(), self.close_signal, self.close_signal_pasaje)
                                self.rutas.setGeometry(0, 0, 800, 440)
                                self.rutas.setWindowFlags(Qt.FramelessWindowHint)
                                self.rutas.show()
                                break
                            if self.intentos == 3:
                                self.intentos = 0
                                ultimo_folio_de_autoasignacion = str(obtener_ultima_asignacion()[1])
                                eliminar_auto_asignacion_por_folio(ultimo_folio_de_autoasignacion)
                                print("No se creo correctamente el folio")
                                GPIO.output(33, False)
                                self.servicio = ""
                                vg.csn_chofer = ""
                                self.settings.setValue('ventana_actual', "")
                                self.settings.setValue('csn_chofer', "")
                                
                                vg.numero_de_operador_inicio = ""
                                vg.numero_de_operador_final = ""
                                vg.nombre_de_operador_inicio = ""
                                vg.nombre_de_operador_final = ""
                                self.settings.setValue('numero_de_operador_inicio', "")
                                self.settings.setValue('numero_de_operador_final', "")
                                self.settings.setValue('nombre_de_operador_inicio', "")
                                self.settings.setValue('nombre_de_operador_final', "")
                                
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)
                                break
                            self.intentos += 1
                    else:
                        print("No hay servicios disponibles2")
                        print("Total de servicios2: ", len(total_de_servicios))
                        GPIO.output(33, False)
                        self.servicio = ""
                        vg.csn_chofer = ""
                        self.settings.setValue('ventana_actual', "")
                        self.settings.setValue('csn_chofer', "")
                        
                        vg.numero_de_operador_inicio = ""
                        vg.numero_de_operador_final = ""
                        vg.nombre_de_operador_inicio = ""
                        vg.nombre_de_operador_final = ""
                        self.settings.setValue('numero_de_operador_inicio', "")
                        self.settings.setValue('numero_de_operador_final', "")
                        self.settings.setValue('nombre_de_operador_inicio', "")
                        self.settings.setValue('nombre_de_operador_final', "")
                        
                        for i in range(5):
                            GPIO.output(12, True)
                            time.sleep(0.055)
                            GPIO.output(12, False)
                            time.sleep(0.055)
            else:
                print("No hay pension seleccionada")
                self.servicio = ""
                vg.csn_chofer = ""
                self.settings.setValue('ventana_actual', "")
                self.settings.setValue('csn_chofer', "")
                
                vg.numero_de_operador_inicio = ""
                vg.numero_de_operador_final = ""
                vg.nombre_de_operador_inicio = ""
                vg.nombre_de_operador_final = ""
                self.settings.setValue('numero_de_operador_inicio', "")
                self.settings.setValue('numero_de_operador_final', "")
                self.settings.setValue('nombre_de_operador_inicio', "")
                self.settings.setValue('nombre_de_operador_final', "")
                
                for i in range(5):
                    GPIO.output(12, True)
                    time.sleep(0.055)
                    GPIO.output(12, False)
                    time.sleep(0.055)
        except Exception as e:
            print(e)
            
            self.servicio = ""
            vg.csn_chofer = ""
            self.settings.setValue('ventana_actual', "")
            self.settings.setValue('csn_chofer', "")
            
            vg.numero_de_operador_inicio = ""
            vg.numero_de_operador_final = ""
            vg.nombre_de_operador_inicio = ""
            vg.nombre_de_operador_final = ""
            self.settings.setValue('numero_de_operador_inicio', "")
            self.settings.setValue('numero_de_operador_final', "")
            self.settings.setValue('nombre_de_operador_inicio', "")
            self.settings.setValue('nombre_de_operador_final', "")
            
            for i in range(5):
                GPIO.output(12, True)
                time.sleep(0.055)
                GPIO.output(12, False)
                time.sleep(0.055)
            logging.info(e)

    def crear_folio(self):
        try:
            folio = str(obtener_ultima_asignacion()[1])
            print("Folio de la base de datos: ", folio)
            if len(str(folio)) == 1:
                folio = "0" + str(folio)
            else:
                folio = str(folio)
            return folio
        except Exception as e:
            print(e)
            logging.info(e)

    #Función para manejar el evento de darle click al label cancel
    def handle_cancel(self, event):
        try:
            GPIO.output(33, False)
            vg.csn_chofer = ""
            self.settings.setValue('ventana_actual', "")
            self.settings.setValue('csn_chofer', "")
            
            vg.numero_de_operador_inicio = ""
            vg.numero_de_operador_final = ""
            vg.nombre_de_operador_inicio = ""
            vg.nombre_de_operador_final = ""
            self.settings.setValue('numero_de_operador_inicio', "")
            self.settings.setValue('numero_de_operador_final', "")
            self.settings.setValue('nombre_de_operador_inicio', "")
            self.settings.setValue('nombre_de_operador_final', "")
            
            self.close()
        except Exception as e:
            print(e)
            logging.info(e)

    #Función para manejar el turno seleccionado
    def turno_seleccionado(self, seleccion):
        try:
            self.turno = seleccion
            vg.turno = self.turno
            self.settings.setValue('turno', self.turno)
            #self.guardar_datos()
        except Exception as e:
            print(e)
            logging.info(e)

    #Función para manejar la pension seleccionada
    def pension_seleccionada(self, seleccion):
        try:
            self.pension_selec = seleccion
            self.comboBox_servicio.clear()
            self.lista_servicios = []
            self.lista_servicios_db = obtener_servicios_de_pension(self.pension_selec)
            for s in self.lista_servicios_db:
                servicio = str(s[0]) + " - " + str(s[1]) + " - " + str(s[2])
                self.lista_servicios.append(servicio)
            self.comboBox_servicio.addItems(self.lista_servicios)
        except Exception as e:
            print(e)
            logging.info(e)

    #Función para manejar el servicio seleccionado
    def servicio_seleccionado(self, seleccion):
        try:
            self.servicio = seleccion
        except Exception as e:
            print(e)
            logging.info(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = VentanaChofer()
    GUI.show()
    sys.exit(app.exec())