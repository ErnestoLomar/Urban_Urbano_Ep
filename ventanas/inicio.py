##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 13/08/2022
#
# Script principal del programa
#
##########################################

#Librerías externas
import sys
import os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import subprocess
from time import strftime
import faulthandler
import logging

# Importar subdirectorios
sys.path.insert(1, '/home/pi/Urban_Urbano/db')
sys.path.insert(1, '/home/pi/Urban_Urbano/utils')
sys.path.insert(1, '/home/pi/Urban_Urbano/minicom')
sys.path.insert(1, '/home/pi/Urban_Urbano/qworkers')

#Librerías propias
from chofer import VentanaChofer
from eeprom_num_serie import cargar_num_serie
from comand import Principal_Modem
from queries import crear_tablas
import variables_globales as variables_globales
from variables_globales import VentanaActual
from LeerMinicom import LeerMinicomWorker
from LeerTarjeta import LeerTarjetaWorker
from ActualizarIconos import ActualizarIconosWorker
from servicios import Rutas
from queries import obtener_datos_aforo, insertar_aforo, insertar_estadisticas_boletera
from enviar_vuelta import EnviarVuelta

if not os.path.exists("/home/pi/Urban_Urbano/logs"):
    os.makedirs("/home/pi/Urban_Urbano/logs")

try:
    FORMAT = '%(asctime)s %(message)s'
    nombre_log = str(strftime("%Y_%m_%d_%H%_M_%S")) + '.log'
    logging.basicConfig(format=FORMAT, filename='/home/pi/Urban_Urbano/logs/' + nombre_log, filemode='w', level="INFO")
    #Creamos el Logger para generar un log de procedimientos
    faulthandler.enable()
except Exception as e:
    print("Error al crear el log: " + str(e))

#Se instancia un objeto de la clase Principal_Modem
try:
    modem = Principal_Modem()
except Exception as e:
    logging.info("Error al instanciar el objeto de la clase Principal_Modem: " + str(e))
    print("Error al instanciar el objeto de la clase Principal_Modem: " + str(e))

class Ventana(QWidget):

    def __init__(self):
        
        super(Ventana, self).__init__()
        try:
            #Realizamos configuración de la ventana principal
            self.setGeometry(0, 0, 800, 480)
            self.setWindowFlags(Qt.FramelessWindowHint)
            uic.loadUi("/home/pi/Urban_Urbano/ui/inicio.ui", self)
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat) #Cargamos el archivo de configuración
            crear_tablas() #Creamos las tablas de la base de datos
            self.unidad = obtener_datos_aforo()
            try:
                self.label_unidad.setText(str(self.unidad[1]))
                self.label_socket.setText(str(self.unidad[2]))
            except Exception as e:
                logging.info('No se pudo cargar el aforo, lo añadimos manualmente')
                insertar_aforo(1,21000,8150,0.0, False, 0.0)
                self.label_unidad.setText(str(self.unidad[1]))
            self.label_ser_pc.hide()
            self.label_5.hide()
            self.label_datos_info.hide()
            self.label_datos_cantidad.hide()
            self.label_version_software.setText(variables_globales.version_del_software)

            #Declaramos variables
            self.registrar_usuario = any
            self.hora_actualizada = False
            self.bandera_gps = False

            #Cargamos el numero de serie y version de la tablilla
            respuesta = cargar_num_serie()
            self.label_num_ser.setText(respuesta['state_num_serie'])
            self.label_num_ver.setText(respuesta['state_num_version'])

            self.inicializar()
            
            try:
                from rpi_backlight import Backlight
                self.backlight = Backlight()
                self.Brillo.setValue(100)
                self.Brillo.valueChanged.connect(self.scrollbar_value_changed)
            except Exception as e:
                print("Ocurrió algo al ejecutar la herramienta de brillo: ", e)
                self.backlight = None
                self.Brillo.hide()
            #Creamos instancias de ventanas
            
            #Creamos los hilos
            self.runLeerMinicom() #Hilo para leer minicom
            self.runLeerTarjeta() #Hilo para leer tarjeta
            self.runActualizarIconos() #Hilo para actualizar iconos
            #self.runDeteccionGeocercas()
        except Exception as e:
            logging.info("Error al iniciar la ventana principal: " + str(e))
            print("Error al iniciar la ventana principal: " + str(e))

    def configuracionInicial(self):
        try:
            vuelta = self.settings.value('vuelta')
            csn_chofer = self.settings.value('csn_chofer')
            servicio = str(self.settings.value('servicio'))
            pension = self.settings.value('pension')
            ventana_actual = self.settings.value('ventana_actual')
            turno = self.settings.value('turno')
            geocerca = self.settings.value('geocerca')
            folio_de_viaje = self.settings.value('folio_de_viaje')
            
            nombre_de_operador_inicio = self.settings.value('nombre_de_operador_inicio')
            numero_de_operador_inicio = self.settings.value('numero_de_operador_inicio')
            nombre_de_operador_final = self.settings.value('nombre_de_operador_final')
            numero_de_operador_final = self.settings.value('numero_de_operador_final')
            
            fecha = strftime('%Y/%m/%d').replace('/', '')[2:]
            
            fecha_actual = str(subprocess.run("date", stdout=subprocess.PIPE, shell=True))
            indice = fecha_actual.find(":")
            hora = str(fecha_actual[(int(indice) - 2):(int(indice) + 6)]).replace(":","")
                                
            if ventana_actual is not None and ventana_actual != str(""):
                
                if self.isVisible() == False:
                        print("La ventana principal no está visible")
                        self.setVisible(True) 
                        self.show()
                        self.activateWindow()
                
                if ventana_actual == str("chofer"):
                    logging.info('Se debería de abrir la Ventana de chofer')
                    self.settings.setValue('ventana_actual', "")
                    if len(str(csn_chofer)) > 0:
                        print("El CSN guardado es: ", csn_chofer)
                        insertar_estadisticas_boletera(str(self.unidad[1]), fecha, hora, "ElegirServicio", f"{csn_chofer}")
                    else:
                        insertar_estadisticas_boletera(str(self.unidad[1]), fecha, hora, "ElegirServicio", f"SINCSN")
                    self.settings.setValue('csn_chofer', "")
                    #variables_globales.csn_chofer = csn_chofer
                    #self.ventana_servicio = VentanaChofer(AbrirVentanas.cerrar_vuelta.close_signal, AbrirVentanas.cerrar_vuelta.close_signal_pasaje)
                    #self.ventana_servicio.show()
                    #self.ventana_servicio.activateWindow()
                elif ventana_actual == 'servicios_transbordos':
                    logging.info('Se abrirá Ventana de servicios_transbordos')
                    if len(str(csn_chofer)) > 0:
                        print("El CSN guardado es: ", csn_chofer)
                        insertar_estadisticas_boletera(str(self.unidad[1]), fecha, hora, "DentroServicio", f"{csn_chofer}")
                    else:
                        insertar_estadisticas_boletera(str(self.unidad[1]), fecha, hora, "DentroServicio", f"SINCSN")
                    
                    variables_globales.numero_de_operador_inicio = numero_de_operador_inicio
                    variables_globales.nombre_de_operador_inicio = nombre_de_operador_inicio
                    variables_globales.numero_de_operador_final = numero_de_operador_final
                    variables_globales.nombre_de_operador_final = nombre_de_operador_final
                    
                    variables_globales.vuelta = vuelta
                    variables_globales.servicio = servicio
                    variables_globales.pension = pension
                    variables_globales.csn_chofer = csn_chofer
                    variables_globales.geocerca = geocerca
                    variables_globales.folio_asignacion = folio_de_viaje
                    self.rutas = Rutas(turno, servicio, AbrirVentanas.cerrar_vuelta.close_signal, AbrirVentanas.cerrar_vuelta.close_signal_pasaje)
                    self.rutas.setGeometry(0, 0, 800, 440)
                    self.rutas.setWindowFlags(Qt.FramelessWindowHint)
                    self.rutas.show() 
                    #self.rutas.activateWindow()
                    
                elif ventana_actual == str("corte"):
                    
                    variables_globales.numero_de_operador_inicio = numero_de_operador_inicio
                    variables_globales.nombre_de_operador_inicio = nombre_de_operador_inicio
                    variables_globales.numero_de_operador_final = numero_de_operador_final
                    variables_globales.nombre_de_operador_final = nombre_de_operador_final
                    
                    variables_globales.vuelta = vuelta
                    variables_globales.servicio = servicio
                    variables_globales.pension = pension
                    variables_globales.csn_chofer = csn_chofer
                    variables_globales.geocerca = geocerca
                    variables_globales.folio_asignacion = folio_de_viaje
                    # Cuando es la ventana de corte, debemos abrir la ventana de servicio y la de corte
                    #Abrimos ventana de servicios
                    logging.info('Se abrirá Ventana de servicios_transbordos')
                    self.rutas = Rutas(turno, servicio, AbrirVentanas.cerrar_vuelta.close_signal, AbrirVentanas.cerrar_vuelta.close_signal_pasaje)
                    self.rutas.setGeometry(0, 0, 800, 440)
                    self.rutas.setWindowFlags(Qt.FramelessWindowHint)
                    self.rutas.show() 
                    ##################################################
                    #Abrimos ventana de corte
                    logging.info('Se abrirá Ventana de Corte')
                    AbrirVentanas.cerrar_vuelta.cargar_datos()
                    AbrirVentanas.cerrar_vuelta.show()
                    #AbrirVentanas.cerrar_vuelta.activateWindow()
                elif ventana_actual == str("enviar_vuelta"):
                    variables_globales.vuelta = vuelta
                    variables_globales.servicio = servicio
                    variables_globales.pension = pension
                    variables_globales.csn_chofer = csn_chofer
                    variables_globales.geocerca = geocerca
                    variables_globales.folio_asignacion = folio_de_viaje
                    logging.info('Se abrirá Ventana de enviar vuelta')
                    self.enviar_vualta = EnviarVuelta(AbrirVentanas.cerrar_turno.close_signal)
                    self.enviar_vualta.show()
                    #enviar_vualta.activateWindow()
                elif ventana_actual == str("cerrar_turno"):
                    variables_globales.vuelta = vuelta
                    variables_globales.servicio = servicio
                    variables_globales.pension = pension
                    variables_globales.csn_chofer = csn_chofer
                    variables_globales.geocerca = geocerca
                    variables_globales.folio_asignacion = folio_de_viaje
                    #En este caso, debemos abrir la ventana de enviar_vuelta y la de cerrar turno
                    #Abrimos ventana de enviar vuelta
                    logging.info('Se abrirá Ventana de enviar vuelta')
                    self.enviar_vualta = EnviarVuelta(AbrirVentanas.cerrar_turno.close_signal)
                    self.enviar_vualta.show()  
                    ##################################################
                    #Abrimos ventana de cerrar turno
                    logging.info('Se abrirá Ventana de Cerrar Turno')
                    AbrirVentanas.cerrar_turno.cargar_datos()
                    AbrirVentanas.cerrar_turno.show()
                    #AbrirVentanas.cerrar_turno.activateWindow()
                else:
                    self.settings.setValue("geocerca",'0,""')
                    self.settings.setValue("folio_de_viaje", "")
                    self.settings.setValue("info_estudiantes", "0,0.0")
                    self.settings.setValue("info_normales", "0,0.0")
                    self.settings.setValue("info_chicos", "0,0.0")
                    self.settings.setValue("info_ad_mayores", "0,0.0")
                    self.settings.setValue("total_a_liquidar", "0.0")
                    self.settings.setValue("total_de_folios", 0)
                    
        except Exception as e:
            logging.info("Error al cargar la configuración inicial: " + str(e))
            print("Error al cargar la configuración inicial: " + str(e))

    def reportProgressMinicom(self, res: dict):
        try:
            self.obtener_hora()
            self.flash_sim(res['connection_3g'])
            self.flash_3g(res['signal_3g'])
            self.temperatura()
            if ("error" in res.keys()):
                self.flash_gps("error")
                return
            else:
                self.flash_gps("OK")
        except Exception as e:
            print("inicio.py, linea 160: "+str(e))

    def runLeerMinicom(self):
        try:
            self.minicomThread = QThread()
            self.minicomWorker = LeerMinicomWorker()
            self.minicomWorker.moveToThread(self.minicomThread)
            self.minicomThread.started.connect(self.minicomWorker.run)
            self.minicomWorker.finished.connect(self.minicomThread.quit)
            self.minicomWorker.finished.connect(self.minicomWorker.deleteLater)
            self.minicomThread.finished.connect(self.minicomThread.deleteLater)
            self.minicomWorker.progress.connect(self.reportProgressMinicom)
            self.minicomThread.start()
        except Exception as e:
            logging.info("Error al iniciar el hilo de minicom: " + str(e))
            print("Error al iniciar el hilo de minicom: " + str(e))
    
    def reportProgressIconos(self, res):
        try:
            self.obtener_hora()
            self.temperatura()
            self.flash_sim(res['connection_3g'])
            self.flash_3g(res['signal_3g'])
            self.servidor_ok(res['servidor'])
            self.verificar_datos_pendientes(res['datos_pendientes'])
            if (res['gps'] == "error"):
                logging.info('No se pudo cargar el gps')
                self.flash_gps("error")
                return
            else:
                self.flash_gps("OK")
        except Exception as e:
            logging.info("Error al actualizar los iconos: " + str(e))
            print("Error al actualizar los iconos: " + str(e))

    def runActualizarIconos(self):
        try:
            self.iconosThread = QThread()
            self.iconosWorker = ActualizarIconosWorker()
            self.iconosWorker.moveToThread(self.iconosThread)
            self.iconosThread.started.connect(self.iconosWorker.run)
            self.iconosWorker.finished.connect(self.iconosThread.quit)
            self.iconosWorker.finished.connect(self.iconosWorker.deleteLater)
            self.iconosThread.finished.connect(self.iconosThread.deleteLater)
            self.iconosWorker.progress.connect(self.reportProgressIconos)
            self.iconosThread.start()
        except Exception as e:
            logging.info("Error al iniciar el hilo de iconos: " + str(e))
            print("Error al iniciar el hilo de iconos: " + str(e))

    def runLeerTarjeta(self):
        try:
            self.thread = QThread()
            self.worker = LeerTarjetaWorker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.reportProgressTarjeta)
            self.thread.start()
        except Exception as e:
            logging.info("Error al iniciar el hilo de tarjeta: " + str(e))
            print("Error al iniciar el hilo de tarjeta: " + str(e))
        
    #leer la tarjeta
    def reportProgressTarjeta(self, result):
        try:
        #Si el resultado es una lista y la lista no está vacía, abra la ventana
            if len(result) == 14:
                #Abrir ventana chofer
                if self.settings.value('csn_chofer') == "":
                    variables_globales.csn_chofer = result
                    self.settings.setValue('csn_chofer', result)
                else:
                    if self.settings.value('csn_chofer') != result:
                        variables_globales.csn_chofer = result
                        self.settings.setValue('csn_chofer_dos', result)
                if variables_globales.ventana_actual == VentanaActual.CHOFER and str("chofer") not in str(self.settings.value('ventana_actual')):
                    self.registrar_usuario = VentanaChofer(AbrirVentanas.cerrar_vuelta.close_signal, AbrirVentanas.cerrar_vuelta.close_signal_pasaje)
                    self.registrar_usuario.show()
                elif variables_globales.ventana_actual == VentanaActual.CERRAR_VUELTA:
                    #Abrir ventana cerrar vuelta
                    logging.info('Se abrirá Ventana de Corte')
                    AbrirVentanas.cerrar_vuelta.cargar_datos()
                    AbrirVentanas.cerrar_vuelta.show()
                elif variables_globales.ventana_actual == VentanaActual.CERRAR_TURNO:
                    #Abrir ventana cerrar turno
                    logging.info('Se abrirá Ventana de Cerrar Turno')
                    AbrirVentanas.cerrar_turno.cargar_datos()
                    AbrirVentanas.cerrar_turno.show()
        except Exception as e:
            logging.info("Error al leer la tarjeta: " + str(e))
            print("Error al leer la tarjeta: " + str(e))
            
    def verificar_datos_pendientes(self, cantidad_de_datos):
        if int(cantidad_de_datos) > 0:
            self.label_datos_info.show()
            self.label_datos_cantidad.show()
            self.label_datos_cantidad.setText(f"faltan {cantidad_de_datos} datos por enviar.")
        else:
            self.label_datos_info.hide()
            self.label_datos_cantidad.hide()

    def servidor_ok(self, respuesta):
        try:
            if respuesta == "SI":
                self.label_4.hide()
            else:
                self.label_4.show()
        except Exception as e:
            logging.info("Error al actualizar el servidor: " + str(e))
            print("Error al actualizar el servidor: " + str(e))
    
    #Con este método obtenemos la hora
    def obtener_hora(self):
        try:

            # Obtener la fecha y hora en formato Y/m/d H:M:S
            fecha_hora = subprocess.check_output(['date', '+%Y/%m/%d %H:%M:%S']).decode().strip()

            # Obtener la fecha en formato Y/m/d
            fecha = subprocess.check_output(['date', '+%d-%m-%Y']).decode().strip()

            # Obtener la hora en formato H:M:S
            hora = subprocess.check_output(['date', '+%H:%M:%S']).decode().strip()

            #print("Fecha y hora:", fecha_hora)
            #print("Fecha:", fecha)
            #print("Hora:", hora)
            
            self.label_fecha.setText(fecha_hora)
            
            # Guardamos los datos en variables globales
            variables_globales.fecha_completa_actual = fecha_hora
            variables_globales.fecha_actual = fecha
            variables_globales.hora_actual = hora
            
            #print(variables_globales.fecha_completa_actual)
            #print(variables_globales.fecha_actual)
            #print(variables_globales.hora_actual)
            
            #if self.hora_actualizada == False:
            #    self.hora_actualizada = actualizar_hora()
        except Exception as e:
            print("\x1b[1;31;47m"+str(e)+'\033[0;m')

    #Con este método cambiamos el icono del 3g según la señal
    def flash_3g(self, signal):
        try:
            if(signal == -1):
                return
            if signal >= 20:
                self.label_senal_celular.setPixmap(
                    QPixmap("/home/pi/Urban_Urbano/Imagenes/3G100.png"))
            elif signal < 20 and signal >= 15:
                self.label_senal_celular.setPixmap(
                    QPixmap("/home/pi/Urban_Urbano/Imagenes/3G75.png"))
            elif signal < 15 and signal >= 10:
                self.label_senal_celular.setPixmap(
                    QPixmap("/home/pi/Urban_Urbano/Imagenes/3G50.png"))
            elif signal < 10 and signal > 2:
                self.label_senal_celular.setPixmap(
                    QPixmap("/home/pi/Urban_Urbano/Imagenes/3G25.png"))
            elif signal < 2:
                self.label_senal_celular.setPixmap(
                    QPixmap("/home/pi/Urban_Urbano/Imagenes/3G0.png"))
        except Exception as e:
            logging.info("Error al actualizar el 3g: " + str(e))
            print("Error al actualizar el 3g: " + str(e))

    #Con este método ocultamos o mostramos el icono del sim
    def flash_sim(self, respuesta):
        try:
            if respuesta == "OK\r\n" or respuesta == "+QINISTAT: 7\r\n":
                self.label_state_simcard.hide()
            else:
                self.label_state_simcard.show()
        except Exception as e:
            logging.info("Error al actualizar el sim: " + str(e))
            print("Error al actualizar el sim: " + str(e))

    #Con este método ocultamos o mostramos el icono del gps
    def flash_gps(self, estado):
        try:
            if estado != "OK":
                self.label_conex_gps.setPixmap(
                    QPixmap("/home/pi/Urban_Urbano/Imagenes/noGPS.png"))
                if self.bandera_gps:
                    self.label_conex_gps.hide()
                else:
                    self.label_conex_gps.show()
                self.bandera_gps = not self.bandera_gps
            else:
                self.label_conex_gps.setPixmap(
                    QPixmap("/home/pi/Urban_Urbano/Imagenes/GPS.png"))
                if self.bandera_gps:
                    self.label_conex_gps.hide()
                else:
                    self.label_conex_gps.show()
                self.bandera_gps = not self.bandera_gps
        except Exception as e:
            logging.info("Error al actualizar el gps: " + str(e))
            print("Error al actualizar el gps: " + str(e))

    #Inicializamos las señales de los botones
    def inicializar(self):
        try:
            self.label_font.mousePressEvent = self.handle_ok
            self.label_off.mousePressEvent = self.apagar_sistema
        except Exception as e:
            logging.info("Error al inicializar: " + str(e))
            print("Error al inicializar: " + str(e))

    #Método para manejar el evento click del label ok
    def handle_ok(self, event):
        pass

    #Método para obtener la temperatura de la raspberry
    def temperatura(self):
        try:
            t = subprocess.run("vcgencmd measure_temp", stdout=subprocess.PIPE, shell=True)
            temp = (t.stdout[5:9].decode())
            self.label_temp.setText(temp + "°C")
            if float(temp) < 65:
                self.label_temp.setStyleSheet('color: #7cfc00')
            elif float(temp) >= 65 < 70:
                self.label_temp.setStyleSheet('color: yellow')
            else:
                self.label_temp.setStyleSheet('color: red')
        except Exception as e:
            logging.info("Error al obtener la temperatura: " + str(e))
            print("Error al obtener la temperatura: " + str(e))

    #Método para obtener la mac address
    def pide_mac(self):
        try:
            m = subprocess.run("cat /sys/class/net/eth0/address", stdout=subprocess.PIPE, shell=True)
            mac = (m.stdout[:].decode())
            return mac
        except Exception as e:
            logging.info("Error al obtener la mac: " + str(e))
            print("Error al obtener la mac: " + str(e))
            
    def scrollbar_value_changed(self, value):
        try:
            if self.backlight != None:
                if value >= 10:
                    self.backlight.brightness =value
        except Exception as e:
            print("Ocurrió algo al ejecutar la función del brillo: ", e)
            
    def apagar_sistema(self, event):
        try:
            os.system("sudo shutdown -h now")
        except Exception as e:
            logging.info("Error al apagar el sistema: " + str(e))
            print("Error al apagar el sistema: " + str(e))
        
if __name__ == '__main__':
    print("\x1b[1;32m"+"Iniciando...")
    app = QApplication(['a'])
    GUI = Ventana()
    GUI.show()
    from abrir_ventanas import AbrirVentanas
    GUI.configuracionInicial()
    sys.exit(app.exec())