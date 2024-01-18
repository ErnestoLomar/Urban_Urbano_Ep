##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 16/08/2022
#
# Script de la ventana servicios.
#
##########################################

#Librerías externas
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import logging
import RPi.GPIO as GPIO

#Librerías propias
from pasaje import VentanaPasaje
import variables_globales as variables_globales
from variables_globales import VentanaActual, distancia_minima
from matrices_tarifarias import obtener_servicio_por_numero_de_servicio_y_origen, obtener_transbordos_por_origen_y_numero_de_servicio
from servicio_pensiones import obtener_origen_por_numero_de_servicio
from geocercas_db import obtener_geocerca_de_servicio
from calcular_distancia_geocerca import calcular_distancia
import time
from Detectar_geocercas import DeteccionGeocercasWorker

try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(33, GPIO.OUT)
except Exception as e:
    print("No se pudo inicializar el ventilador: "+str(e))

class Rutas(QWidget):
    
    cerrar_servicios_signal = pyqtSignal()

    def __init__(self, turno: str, servicio_info,close_signal, close_signal_pasaje):
        super().__init__()
        try:
            uic.loadUi("/home/pi/Urban_Urbano//ui/servicios.ui", self)

            #Creamos nuestras variables para la ventana servicios
            self.close_signal = close_signal
            self.close_signal_pasaje = close_signal_pasaje
            self.cerrar_servicios_signal.connect(self.cerrar_por_no_tener_viaje)
            self.servicio_info = servicio_info.split(" - ")
            self.origen_de_servicio = obtener_origen_por_numero_de_servicio(self.servicio_info[0])
            self.ruta = self.servicio_info[0] + "-" + self.servicio_info[1] + "-" + self.servicio_info[2]
            self.de = str(self.origen_de_servicio[3])
            self.geocerca_numero_uno = obtener_geocerca_de_servicio(self.origen_de_servicio[3])
            #print("Geocerca numero uno: "+str(self.geocerca_numero_uno))
            variables_globales.geocerca = f"{self.geocerca_numero_uno[0]},{self.geocerca_numero_uno[1]}"
            self.bandera = False
            self.turno = turno
            self.dos_listas_servicio = True
            self.dos_listas_Tranbordo = True
            self.bandera_mostrar_solo_lista_uno_servicios = False
            self.bandera_mostrar_solo_lista_uno_transbordo = False
            self.geocercas = []
            self.nombres_geocercas_servicios = []
            self.nombres_geocercas_transbordos = []
            self.ida_o_vuelta = ""
            #self.lista_de_datos_retrocedidos = []
            
            #Realizamos configuraciones iniciales de la ventana
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            self.settings.setValue('ventana_actual', "servicios_transbordos")
            self.settings.setValue('en_viaje', "SI")
            self.settings.setValue('origen_actual', self.de)
            self.close_signal.connect(self.close_me)
            self.Parada.setText('De: ' + str(str(self.origen_de_servicio[3]).split("_")[0]))
            variables_globales.ventana_actual = VentanaActual.CERRAR_VUELTA
            self.opcion.clicked.connect(self.cambio)
            self.list_serv.itemClicked.connect(self.item_select_serv1)
            self.list_serv_2.itemClicked.connect(self.item_select_2_serv2)
            self.list_serv_3.itemClicked.connect(self.item_select_3_serv3)
            self.label_avanzar.mousePressEvent = self.handle_avanzar
            self.label_retroceder.mousePressEvent = self.handle_retroceder
            self.list_trans1.itemClicked.connect(self.item_select_trans2)
            self.list_trans2.itemClicked.connect(self.item_select_trans3)
            self.list_trans.itemClicked.connect(self.item_select_trans1)
            self.list_trans1.hide()
            self.list_trans2.hide()
            self.list_trans.hide()
            self.list_serv.setColumnCount(2)
            self.list_serv.setHeaderLabels(["Ruta", "Costo"])
            self.list_serv_2.setColumnCount(2)
            self.list_serv_2.setHeaderLabels(["Ruta", "Costo"])
            self.list_serv_3.setColumnCount(2)
            self.list_serv_3.setHeaderLabels(["Ruta", "Costo"])
            
            self.list_trans.setColumnCount(2)
            self.list_trans.setHeaderLabels(["Ruta", "Costo"])
            self.list_trans1.setColumnCount(2)
            self.list_trans1.setHeaderLabels(["Ruta", "Costo"])
            self.list_trans2.setColumnCount(2)
            self.list_trans2.setHeaderLabels(["Ruta", "Costo"])
            
            self.label_retroceder.setEnabled(False)
            self.label_retroceder.hide()
            self.cargar_servicios(obtener_servicio_por_numero_de_servicio_y_origen(int(self.servicio_info[0]), self.de))
            self.cargar_transbordos(obtener_transbordos_por_origen_y_numero_de_servicio(int(self.servicio_info[0]), self.de))
            GPIO.output(33, True)
            #if detectando_geocercas_hilo == False:
                #print("Iniciando hilo de detección de geocercas")
                #variables_globales.detectando_geocercas_hilo = True
            self.runDeteccionGeocercas()
        except Exception as e:
            print("Error al iniciar la ventana de servicios: "+str(e))
            logging.info(e)

    def runDeteccionGeocercas(self):
        try:
            self.geocercaThread = QThread()
            self.geocercaWorker = DeteccionGeocercasWorker()
            self.geocercaWorker.moveToThread(self.geocercaThread)
            self.geocercaThread.started.connect(self.geocercaWorker.run)
            self.geocercaWorker.finished.connect(self.geocercaThread.quit)
            self.geocercaWorker.finished.connect(self.geocercaWorker.deleteLater)
            self.geocercaThread.finished.connect(self.geocercaThread.deleteLater)
            self.geocercaWorker.progress.connect(self.verificar_geocercas)
            self.geocercaThread.start()
        except Exception as e:
            logging.info(e)

    def verificar_geocercas(self, res: dict):
        try:
            #print("Detectando geocercas")
            #print("Res: "+str(res))
            #print("Todas las geocercas: "+str(self.geocercas))
            if res == None:
                return
            #print("Si hay res")
            longitud = res['longitud']
            latitud = res['latitud']
            if self.geocercas == None:
                return
            print("Detectando geocercas")
            for geocerca in self.geocercas:
                result = calcular_distancia(float(longitud), float(latitud), float(geocerca[3]), float(geocerca[2]))
                if result < distancia_minima:
                    if str(variables_globales.geocerca.split(",")[1]) not in geocerca[1]:
                        self.settings.setValue('geocerca', f"{geocerca[0]},{geocerca[1]}")
                        variables_globales.geocerca = f"{geocerca[0]},{geocerca[1]}"
                        self.cargar_servicios(obtener_servicio_por_numero_de_servicio_y_origen(int(self.servicio_info[0]), geocerca[1]))
                        self.cargar_transbordos(obtener_transbordos_por_origen_y_numero_de_servicio(int(self.servicio_info[0]), geocerca[1]))
                        self.Parada.setText("De: " + str(str(geocerca[1]).split("_")[0]))
                        #print("GEOCERCA DETECTADA: " + str(geocerca[1]))
                        geocerca_desactivada = self.settings.value("geocerca_desactivada")
                        if geocerca_desactivada != "":
                            indice_geocerca_desactivada = self.settings.value("indice_de_geocerca_desactivada")
                            self.geocercas.insert(int(indice_geocerca_desactivada),geocerca_desactivada)
                            self.settings.setValue("geocerca_desactivada", "")
                            self.settings.setValue("indice_de_geocerca_desactivada", 0)
                        break
                        #self.geocercas.remove(geocerca) <--------- Se quito para que no se elimine la geocerca de la lista de geocercas y se pueda volver a marcar
        except Exception as e:
            logging.info(e)

    #Función para cerrar la ventana servicios.
    def close_me(self):
        try:
            variables_globales.detectando_geocercas_hilo = False
            self.geocercas = None
            self.nombres_geocercas_servicios = None
            self.nombres_geocercas_transbordos = None
            variables_globales.geocerca = "0,''"
            self.settings.setValue('geocerca', "0,''")
            self.settings.setValue("geocerca_desactivada", "")
            self.settings.setValue("indice_de_geocerca_desactivada", 0)
            variables_globales.todos_los_servicios_activos = []
            variables_globales.todos_los_transbordos_activos = []
            self.close()
        except Exception as e:
            print("Error al cerrar la ventana de servicios: "+str(e))
            logging.info(e)
            
    def cerrar_por_no_tener_viaje(self):
        try:
            
            variables_globales.detectando_geocercas_hilo = False
            self.geocercas = None
            self.nombres_geocercas_servicios = None
            self.nombres_geocercas_transbordos = None
            variables_globales.geocerca = "0,''"
            self.settings.setValue('geocerca', "0,''")
            self.settings.setValue("geocerca_desactivada", "")
            self.settings.setValue("indice_de_geocerca_desactivada", 0)
            variables_globales.todos_los_servicios_activos = []
            variables_globales.todos_los_transbordos_activos = []
            
            
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
            
            
            variables_globales.ventana_actual = VentanaActual.CHOFER
            self.settings.setValue('servicio', "")
            self.settings.setValue('ventana_actual', "")
            self.settings.setValue('csn_chofer', "")
            variables_globales.csn_chofer = ""
            variables_globales.numero_de_operador_inicio = ""
            variables_globales.numero_de_operador_final = ""
            variables_globales.nombre_de_operador_inicio = ""
            variables_globales.nombre_de_operador_final = ""
            self.settings.setValue('numero_de_operador_inicio', "")
            self.settings.setValue('numero_de_operador_final', "")
            self.settings.setValue('nombre_de_operador_inicio', "")
            self.settings.setValue('nombre_de_operador_final', "")
            
            GPIO.output(33, False)
            
            self.close()
        except Exception as e:
            print("Error al cerrar la ventana de servicios: "+str(e))
            logging.info(e)
            
    #Toma una lista de servicios de la BD y crea una lista de servicios en la GUI.
    def cargar_servicios(self, lista):
        try:
            if len(lista) > 0:
                #print("Lista de servicios:")
                #print(lista)
                self.crear_lista_geocercas(lista, self.nombres_geocercas_servicios)
                #Limpiamos las listas
                self.list_serv_2.clear()
                self.list_serv_3.clear()
                self.list_serv.clear()

                #La lista obtenida la convertimos en una lista de strings
                variables_globales.todos_los_servicios_activos = lista
                self.lista_servicios = lista
                if len(lista) > 10:
                    self.dos_listas_servicio = True
                    # Si hay mas de 8 servicios creamos dos listas
                    if self.bandera == False:
                        self.list_serv_2.show()
                        self.list_serv_3.show()
                        self.list_serv.hide()
                    else:
                        self.list_serv_2.hide()
                        self.list_serv_3.hide()
                        self.list_serv.hide()
                    cont = 0
                    #Un bucle que itera sobre la lista de servicios y los agrega al widget list_serv_2.
                    while cont < 10:
                        servicio = lista[cont]
                        nombre = str(str(servicio[2]).split("_")[0])
                        if len(nombre) > 10:
                            nombre = nombre[0:8]
                        L1 = QTreeWidgetItem([nombre, '$ '+str(servicio[3])])
                        self.list_serv_2.addTopLevelItem(L1)
                        cont = cont + 1

                    #Agregar los elementos al list_serv_3.
                    while cont < len(lista):
                        servicio = lista[cont]
                        nombre = str(str(servicio[2]).split("_")[0])
                        if len(nombre) > 10:
                            nombre = nombre[0:8]
                        L1 = QTreeWidgetItem([nombre, '$ '+str(servicio[3])])
                        self.list_serv_3.addTopLevelItem(L1)
                        cont = cont + 1
                else:
                    self.dos_listas_servicio = False
                    # si hay 8 o menos servicios creamos una lista
                    if self.bandera == False:
                        self.list_serv_2.hide()
                        self.list_serv_3.hide()
                        self.list_serv.show()
                    else:
                        self.list_serv_2.hide()
                        self.list_serv_3.hide()
                        self.list_serv.hide()
                    for servicio in lista:
                        nombre = str(str(servicio[2]).split("_")[0])
                        if len(nombre) > 10:
                            nombre = nombre[0:8]
                        L1 = QTreeWidgetItem([nombre, '$ '+str(servicio[3])])
                        self.list_serv.addTopLevelItem(L1)
            else:
                self.list_serv_2.clear()
                self.list_serv_3.clear()
                self.list_serv.clear()
        except Exception as e:
            print(e)
            logging.info(e)

    #Toma una lista  y agrega cada lista como una fila en un QTreeWidget.
    def cargar_transbordos(self, lista):
        try:
            if len(lista) > 0:
                #print("Lista de transbordos:")
                #print(lista)
                #self.crear_lista_geocercas(lista, self.nombres_geocercas_transbordos)
                variables_globales.todos_los_transbordos_activos = lista
                self.lista_transbordos = lista
                self.list_trans.clear()
                self.list_trans1.clear()
                self.list_trans2.clear()
                self.list_trans1.setColumnCount(2)
                self.list_trans1.setHeaderLabels(["Ruta", "Costo"])
                self.list_trans2.setColumnCount(2)
                self.list_trans2.setHeaderLabels(["Ruta", "Costo"])
                self.list_trans.setColumnCount(2)
                self.list_trans.setHeaderLabels(["Ruta", "Costo"])
                # Crear una lista de servicios y agregarlos al widget list_serv_2.
                if len(lista) > 10:
                    self.dos_listas_Tranbordo = True
                    cont = 0
                    if self.bandera == True:
                        self.list_trans.hide()
                        self.list_trans1.show()
                        self.list_trans2.show()
                    else:
                        self.list_trans.hide()
                        self.list_trans1.hide()
                        self.list_trans2.hide()
                    #Un bucle que itera sobre la lista de servicios y los agrega al widget list_serv_2.
                    while cont < 10:
                        servicio = lista[cont]
                        nombre = str(str(servicio[2]).split("_")[0])
                        if len(nombre) > 10:
                            nombre = nombre[0:8]
                        L1 = QTreeWidgetItem([nombre, '$ '+str(servicio[3])])
                        self.list_trans1.addTopLevelItem(L1)
                        cont = cont + 1

                    #Agregar los elementos al list_serv_3.
                    while cont < len(lista):
                        servicio = lista[cont]
                        nombre = str(str(servicio[2]).split("_")[0])
                        if len(nombre) > 10:
                            nombre = nombre[0:8]
                        L1 = QTreeWidgetItem([nombre, '$ '+str(servicio[3])])
                        self.list_trans2.addTopLevelItem(L1)
                        cont = cont + 1
                else:
                    self.dos_listas_Tranbordo = False
                    if self.bandera == True:
                        self.list_trans.show()
                        self.list_trans1.hide()
                        self.list_trans2.hide()
                    else:
                        self.list_trans.hide()
                        self.list_trans1.hide()
                        self.list_trans2.hide()
                    for transbordo in lista:
                        L1 = QTreeWidgetItem([str(str(transbordo[2]).split("_")[0]), '$ '+str(transbordo[3])])
                        self.list_trans.addTopLevelItem(L1)
            else:
                self.list_trans.clear()
                self.list_trans1.clear()
                self.list_trans2.clear()
        except Exception as e:
            print(e)
            logging.info(e)

    def handle_avanzar(self, event):
        try:
            #self.label_fondo_avanzar.setEnabled(False)
            if self.dos_listas_servicio == False:
                self.vaciar_lista_unica()
                logging.info("Avanzar lista unica")
            else:
                self.vaciar_dos_listas()
                logging.info("Avanzar dos listas")
            #time.sleep(1.5)
            #self.label_fondo_avanzar.setEnabled(True)
            #self.label_fondo_avanzar.hide()
            #self.label_avanzar.setStyleSheet('''background-color: #1E51A5; border-radius: 10px;''')
        except Exception as e:
            logging.info(e)

    def handle_retroceder(self, event):
        #self.lista_de_datos_retrocedidos.append(self.lista_de_datos)
        pass # Aquí va el código para retroceder la lista de servicios y transbordos

    #Toma el primer elemento de un QTreeWidget, lo elimina y luego lo vuelve a agregar al final de la
    #lista.
    def vaciar_lista_unica(self):
        try:
            item = self.list_serv.topLevelItem(1)
            if item != None:
                # Método para ir borrando elementos de la lista de servicios
                item = self.list_serv.topLevelItem(1)
                self.list_serv.takeTopLevelItem(0)
                nombre = item.data(0, 0)
                servicio = self.buscar_servicio(nombre)
                self.de = servicio[2]
                self.Parada.setText("De: " + str(str(servicio[2]).split("_")[0]))
                self.cargar_servicios(obtener_servicio_por_numero_de_servicio_y_origen(int(servicio[5]), self.de))
                self.cargar_transbordos(obtener_transbordos_por_origen_y_numero_de_servicio(int(servicio[5]), self.de))
                if self.settings.value("geocerca_desactivada") == "":
                    self.desactivar_geocerca_actual()
                else:
                    geocerca_desactivada = self.settings.value("geocerca_desactivada")
                    indice_geocerca_desactivada = self.settings.value("indice_de_geocerca_desactivada")
                    self.geocercas.insert(int(indice_geocerca_desactivada),geocerca_desactivada)
                    self.desactivar_geocerca_actual()
                #time.sleep(1.5)
            else:
                self.Parada.setText('De: ' + str(str(self.origen_de_servicio[3]).split("_")[0]))
                self.de = str(self.origen_de_servicio[3])
                self.geocercas = []
                self.nombres_geocercas_servicios = []
                self.nombres_geocercas_transbordos = []
                variables_globales.geocerca = f"{self.geocerca_numero_uno[0]},{self.geocerca_numero_uno[1]}"
                self.settings.setValue('geocerca', "0,''")
                self.settings.setValue("geocerca_desactivada", "")
                self.settings.setValue("indice_de_geocerca_desactivada", 0)
                self.cargar_servicios(obtener_servicio_por_numero_de_servicio_y_origen(int(self.servicio_info[0]), self.origen_de_servicio[3]))
                self.cargar_transbordos(obtener_transbordos_por_origen_y_numero_de_servicio(int(self.servicio_info[0]), self.origen_de_servicio[3]))
                #time.sleep(1.5)
        except Exception as e:
            print(e)
            logging.info(e)

    #Función que vacía las dos listas de servicios.
    def vaciar_dos_listas(self):
        try:
            item = self.list_serv_2.topLevelItem(1)
            if item != None:
                nombre = item.data(0, 0)
                servicio = self.buscar_servicio(nombre)
                self.de = servicio[2]
                self.Parada.setText("De: " + str(str(servicio[2]).split("_")[0]))
                self.cargar_servicios(obtener_servicio_por_numero_de_servicio_y_origen(int(servicio[5]), self.de))
                self.cargar_transbordos(obtener_transbordos_por_origen_y_numero_de_servicio(int(servicio[5]), self.de))
                if self.settings.value("geocerca_desactivada") == "":
                    self.desactivar_geocerca_actual()
                else:
                    geocerca_desactivada = self.settings.value("geocerca_desactivada")
                    indice_geocerca_desactivada = self.settings.value("indice_de_geocerca_desactivada")
                    self.geocercas.insert(int(indice_geocerca_desactivada),geocerca_desactivada)
                    self.desactivar_geocerca_actual()
            #time.sleep(1.5)
        except Exception as e:
            logging.info(e)

    def desactivar_geocerca_actual(self):
        try:
            geocerca_actual = variables_globales.geocerca.split(",")[1] #Obtener el nombre de la geocerca actual
            for geocerca in self.geocercas:
                if geocerca[1] == geocerca_actual: #Geocerca[1] es el nombre de la geocerca
                    indice_geocerca_actual = self.geocercas.index(geocerca)
                    self.settings.setValue("geocerca_desactivada", geocerca)
                    self.settings.setValue("indice_de_geocerca_desactivada", indice_geocerca_actual)
                    self.geocercas.remove(geocerca)
            for geocerca in self.geocercas:
                if str(geocerca[1]) == str(self.de):
                    variables_globales.geocerca = f"{geocerca[0]},{geocerca[1]}"
                    break
        except Exception as e:
            print(e)

    # Si la bandera es verdadera, oculta las dos primeras listas y muestra la tercera lista. Si la
    # bandera es falsa, oculta la tercera lista y muestra las dos primeras listas.
    def cambio(self):
        try:
            # Comprobando si la variable bandera es True. Si es así, establece el texto de la opción del
            # widget en "Transbordo" y oculta los widgets list_trans1 y list_trans2. Luego, comprueba si
            # la variable dos_listas_servicio es Verdadera. Si es así, oculta el widget list_serv y
            # muestra los widgets list_serv_2 y list_serv_3. Si no es así, muestra el widget list_serv y
            # oculta los widgets list_serv_2 y list_serv_3. Si
            if self.bandera:
                self.opcion.setText("Transbordo")
                self.list_trans.hide()
                self.list_trans1.hide()
                self.list_trans2.hide()
                logging.info("Mostrando lista de servicios")
                # Comprobando si la variable dos_listas_servicio es Verdadera. Si es así, oculta el widget
                # list_serv y muestra los widgets list_serv_2 y list_serv_3. Si no es así, muestra el
                # widget list_serv y oculta los widgets list_serv_2 y list_serv_3.
                if self.dos_listas_servicio == True:
                    self.list_serv.hide()
                    if self.bandera_mostrar_solo_lista_uno_servicios == True:
                        self.list_serv_2.show()
                        self.list_serv_3.hide()
                    else:
                        self.list_serv_2.show()
                        self.list_serv_3.show()
                else:
                    self.list_serv.show()
                    self.list_serv_2.hide()
                    self.list_serv_3.hide()
            else:
                # Ocultar list_serv, list_serv_2, list_serv_3 y mostrar list_trans1 y list_trans2.
                self.list_serv.hide()
                self.list_serv_2.hide()
                self.list_serv_3.hide()
                self.opcion.setText("Servicios")
                logging.info("Mostrando lista de transbordos")
                # Mostrar y ocultar los widgets list_trans, list_trans1 y list_trans2.
                if self.dos_listas_Tranbordo == True:
                    self.list_trans.hide()
                    self.list_trans1.show()
                    self.list_trans2.show()
                else:
                    self.list_trans.show()
                    self.list_trans1.hide()
                    self.list_trans2.hide()
            self.bandera = not self.bandera
        except Exception as e:
            logging.info(e)

    #Selección de item
    def item_select_serv1(self):
        try:
            s = self.list_serv.currentItem().data(0, 0)
            self.abrir_ventana_pasaje(s, None)
        except Exception as e:
            logging.info(e)

    #Selección de item
    def item_select_2_serv2(self):
        try:
            s = self.list_serv_2.currentItem().data(0, 0)
            self.abrir_ventana_pasaje(s, None)
        except Exception as e:
            logging.info(e)

    #Selección de item
    def item_select_3_serv3(self):
        try:
            # Obtener el elemento actual de un widget de lista y luego pasarlo a una función.
            s = self.list_serv_3.currentItem().data(0, 0)
            self.abrir_ventana_pasaje(s, None)
        except Exception as e:
            logging.info(e)

    def item_select_trans1(self):
        try:
            # Obtener el elemento actual de un widget de lista y luego pasarlo a una función.
            t = self.list_trans.currentItem().data(0, 0)
            self.abrir_ventana_pasaje(None, t)
        except Exception as e:
            logging.info(e)

    def item_select_trans2(self):
        try:
            # Obtener el elemento actual de un widget de lista y luego pasarlo a una función.
            t = self.list_trans1.currentItem().data(0, 0)
            self.abrir_ventana_pasaje(None, t)
        except Exception as e:
            logging.info(e)

    def item_select_trans3(self):
        try:
            # Obtener el elemento actual de un widget de lista y luego pasarlo a una función.
            t = self.list_trans2.currentItem().data(0, 0)
            self.abrir_ventana_pasaje(None, t)
        except Exception as e:
            logging.info(e)

    #Función para abrir la ventana de pasaje.
    def abrir_ventana_pasaje(self, s, t):
        try:
            if s != None:
                servicio = self.buscar_servicio(s)
                nombre = servicio[2]
                precio = float(servicio[3])
                precio_preferente = float(servicio[4])
                id_tabla_servicio = servicio[0]
                tramo = str(str(str(servicio[1]).split("_")[0]).replace(" ","") + "-" + str(str(servicio[2]).split("_")[0]).replace(" ",""))
                ventana = VentanaPasaje(precio, self.de, nombre, precio_preferente, self.close_signal_pasaje, f"SER,{servicio}", id_tabla_servicio, self.ruta, tramo, self.cerrar_servicios_signal)
                ventana.setGeometry(0, 0, 800, 440)
                ventana.setWindowFlags(Qt.FramelessWindowHint)
                ventana.show()
            else:
                transbordo = self.buscar_transbordos(t)
                nombre = transbordo[2]
                precio = float(transbordo[3])
                precio_preferente = float(transbordo[4])
                id_tabla_transbordo = transbordo[0]
                tramo = str(str(str(transbordo[1]).split("_")[0]).replace(" ","") + "-" + str(str(transbordo[2]).split("_")[0]).replace(" ",""))
                ventana = VentanaPasaje(precio, self.de, nombre, precio_preferente, self.close_signal_pasaje, f"TRA,{transbordo}", id_tabla_transbordo, self.ruta, tramo, self.cerrar_servicios_signal)
                ventana.setGeometry(0, 0, 800, 440)
                ventana.setWindowFlags(Qt.FramelessWindowHint)
                ventana.show()
        except Exception as e:
            logging.info(e)
    # Devuelve el primer servicio en la lista de servicios que tiene un nombre que contiene la cadena
    # pasada como argumento
    def buscar_servicio(self, nombre):
        try:
            for servicio in self.lista_servicios:
                servicio_nombre = servicio[2]
                if nombre in servicio_nombre:
                    return servicio
        except Exception as e:
            logging.info(e)

    def buscar_transbordos(self, nombre):
        try:
            for transbordo in self.lista_transbordos:
                transbordo_nombre = transbordo[2]
                if nombre in transbordo_nombre:
                    return transbordo
        except Exception as e:
            logging.info(e)

    def crear_lista_geocercas(self, lista, nombre_geocercas):
        """
        It takes a list of tuples, and creates a list of geofences from it.
        
        :param lista: list of tuples, each tuple has 3 elements, the first one is the distance between
        the two geofences, the second one is the name of the first geofence and the third one is the
        name of the second geofence
        :param nombre_geocercas: list of strings
        """
        """
        In ispanish: Se pasa por parámetro una 'lista', que contiene ya sea todos los servicios o todos los
        transbordos, y se crea una lista de geocercas a partir de ella.
        ¿Cómo?: En la 'lista' que se pasa por parámetro se encuentran tuplas, cada tupla tiene ciertos elementos,
        pero los que nos importan son el segundo 'origen' y el tercero 'destino'; Tenemos una lista de geocercas,
        y se recorre la lista de geocercas para verificar si el 'origen' y el 'destino' de la tupla se encuentran
        en la lista de geocercas, si es asi no hace nada, pero si no se añaden a 'self.geocercas'.
        """
        if lista != None:
            if len(lista) > 0:
                try:
                    logging.info("Creando lista de geocercas...")
                    lista_cortada = str(str(lista).split("),")).replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(" ","").split('",')
                    contador = 0
                    for i in lista_cortada:
                        if str(str(lista[contador][1]).split("_")[0]) in nombre_geocercas:
                            if str(str(lista[contador][2]).split("_")[0]) in nombre_geocercas:
                                pass
                            else:
                                nombre_geocercas.append(str(str(lista[contador][2]).split("_")[0]))
                                self.geocercas.append(obtener_geocerca_de_servicio(str(lista[contador][2])))
                        else:
                            nombre_geocercas.append(str(str(lista[contador][1]).split("_")[0]))
                            self.geocercas.append(obtener_geocerca_de_servicio(str(lista[contador][1])))
                            if str(str(lista[contador][2]).split("_")[0]) in nombre_geocercas:
                                pass
                            else:
                                nombre_geocercas.append(str(str(lista[contador][2]).split("_")[0]))
                                self.geocercas.append(obtener_geocerca_de_servicio(str(lista[contador][2])))
                        contador += 1
                except Exception as e:
                    print(e)