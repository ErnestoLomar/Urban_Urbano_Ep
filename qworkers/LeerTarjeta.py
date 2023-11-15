##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 16/08/2022
#
# Script para la comunicación con la tarjeta.
#
##########################################

#Librerías externas
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
import time
import ctypes
import RPi.GPIO as GPIO
import serial
import logging
from time import strftime
from datetime import datetime, timedelta
import subprocess
from escpos.printer import Usb

#Librerias propias
from matrices_tarifarias import obtener_destino_de_servicios_directos, obtener_destino_de_transbordos
from emergentes import VentanaEmergente
from ventas_queries import insertar_item_venta, obtener_ultimo_folio_de_item_venta
from queries import obtener_datos_aforo
from tickets_usados import insertar_ticket_usado, verificar_ticket_completo, verificar_ticket
import variables_globales as vg

class LeerTarjetaWorker(QObject):
    
    try:
        finished = pyqtSignal()
        progress = pyqtSignal(str)
    except Exception as e:
        print(e)
        logging.info(e)

    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12, GPIO.OUT)
    except Exception as e:
        print("\x1b[1;31;47m"+"No se pudo inicializar el zumbador: "+str(e)+'\033[0;m')
        logging.info(e)
        
    def __init__(self):
        super().__init__()
        self.ultimo_qr = ""
        self.ser = any
        try:
            self.ser = serial.Serial(port='/dev/ttyACM0',baudrate = 115200,timeout=0.5)
        except Exception as e:
            print(e)
            logging.info(e)
            self.restablecer_comunicación_QR()
        try:
            self.lib = ctypes.cdll.LoadLibrary('/home/pi/Urban_Urbano/qworkers/libernesto.so')
            self.lib.ev2IsPresent.restype = ctypes.c_char_p
            self.lib.tipoTiscEV2.restype = ctypes.c_char_p
            self.lib.obtenerVigencia.restype = ctypes.c_char_p
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            self.idUnidad = str(obtener_datos_aforo()[1])
        except Exception as e:
            print(e)
            logging.info(e)
            
    def restar_dos_horas(self, hora_1, hora_2):
        try:
            t1 = datetime.strptime(hora_1, '%H:%M:%S')
            t2 = datetime.strptime(hora_2, '%H:%M:%S')
            return t1 - t2
        except Exception as e:
            print("recorrido_mapa.py, linea 151: "+str(e))
            
    def sumar_dos_horas(self, hora1, hora2):
        try:
            formato = "%H:%M:%S"
            lista = hora2.split(":")
            hora=int(lista[0])
            minuto=int(lista[1])
            segundo=int(lista[2])
            h1 = datetime.strptime(hora1, formato)
            dh = timedelta(hours=hora) 
            dm = timedelta(minutes=minuto)          
            ds = timedelta(seconds=segundo) 
            resultado1 =h1 + ds
            resultado2 = resultado1 + dm
            resultado = resultado2 + dh
            resultado=resultado.strftime(formato)
            return str(resultado)
        except Exception as e:
            print("recorrido_mapa.py, linea 151: "+str(e))

    def run(self):
        try:
            while True:
                try:
                    csn = self.lib.ev2IsPresent().decode(encoding="utf8", errors='ignore')
                    time.sleep(0.01)
                    if csn != "":
                        try:
                            tipo = str(self.lib.tipoTiscEV2().decode(encoding="utf8", errors='ignore')[0:2])
                            if tipo == "KI":
                                datos_completos_tarjeta = str(self.lib.obtenerVigencia().decode(encoding="utf8", errors='ignore'))
                                print("Datos completos de la tarjeta: ",datos_completos_tarjeta)
                                vigenciaTarjeta = datos_completos_tarjeta[:12]
                                print("Vigencia completa de la tarjeta: "+vigenciaTarjeta)
                                
                                # Verificamos que el dato de la vigencia de la tarjeta sea correcto.
                                if len(vigenciaTarjeta) == 12 and int(vigenciaTarjeta[:2]) >= 22:
                                    now = datetime.now()
                                    vigenciaActual = f'{str(now.date())[2:].replace("-","")}'
                                    print("Fecha actual: "+vigenciaActual)
                                    print("Fecha vigencia tarjeta: "+vigenciaTarjeta[:6])
                                    if vigenciaActual <= vigenciaTarjeta[:6]:
                                        print("Tarjeta vigente")
                                        csn = self.lib.ev2IsPresent().decode(encoding="utf8", errors='ignore')
                                        time.sleep(0.01)
                                        if len(csn) == 14:
                                            vg.vigencia_de_tarjeta = vigenciaTarjeta
                                            print("La ventana actual es: ", self.settings.value('ventana_actual'))
                                            if str(self.settings.value('ventana_actual')) != "chofer" and str(self.settings.value('ventana_actual')) != "corte" and str(self.settings.value('ventana_actual')) != "enviar_vuelta" and str(self.settings.value('ventana_actual')) != "cerrar_turno":
                                                if len(vg.numero_de_operador_inicio) > 0 or len(self.settings.value('numero_de_operador_inicio')) > 0:
                                                    vg.numero_de_operador_final = datos_completos_tarjeta[12:17] # OBSERVACION: Si el valor obtenido es un entero se toma como bien la variable.
                                                    vg.nombre_de_operador_final = datos_completos_tarjeta[17:41].replace("*"," ").replace("."," ").replace("-"," ").replace("_"," ")
                                                    self.settings.setValue('numero_de_operador_final', f"{datos_completos_tarjeta[12:17]}")
                                                    self.settings.setValue('nombre_de_operador_final', f"{datos_completos_tarjeta[17:41].replace('*',' ').replace('.',' ').replace('-',' ').replace('_',' ')}")
                                                    print("Numero de operador de final es: "+vg.numero_de_operador_final)
                                                    print("El nombre del operador de final es: ",vg.nombre_de_operador_final)
                                                else:
                                                    vg.numero_de_operador_inicio = datos_completos_tarjeta[12:17] # OBSERVACION: Si el valor obtenido es un entero se toma como bien la variable.
                                                    vg.nombre_de_operador_inicio = datos_completos_tarjeta[17:41].replace("*"," ").replace("."," ").replace("-"," ").replace("_"," ")
                                                    self.settings.setValue('numero_de_operador_inicio', f"{datos_completos_tarjeta[12:17]}")
                                                    self.settings.setValue('nombre_de_operador_inicio', f"{datos_completos_tarjeta[17:41].replace('*',' ').replace('.',' ').replace('-',' ').replace('_',' ')}")
                                                    print("Numero de operador de inicio es: "+vg.numero_de_operador_inicio)
                                                    print("El nombre del operador de inicio es: ",vg.nombre_de_operador_inicio)
                                            vg.csn_chofer_respaldo = csn
                                            self.progress.emit(csn)
                                            GPIO.output(12, True)
                                            time.sleep(0.1)
                                            GPIO.output(12, False)
                                            time.sleep(0.1)
                                            GPIO.output(12, True)
                                            time.sleep(0.1)
                                            GPIO.output(12, False)
                                        else:
                                            GUI = VentanaEmergente("TARJETAINVALIDA", "")
                                            GUI.show()
                                            for i in range(5):
                                                GPIO.output(12, True)
                                                time.sleep(0.055)
                                                GPIO.output(12, False)
                                                time.sleep(0.055)
                                            time.sleep(2)
                                            GUI.close()
                                    else:
                                        GUI = VentanaEmergente("FUERADEVIGENCIA", "")
                                        GUI.show()
                                        for i in range(5):
                                            GPIO.output(12, True)
                                            time.sleep(0.055)
                                            GPIO.output(12, False)
                                            time.sleep(0.055)
                                        time.sleep(2)
                                        GUI.close()
                                else:
                                    GUI = VentanaEmergente("TARJETAINVALIDA", "")
                                    GUI.show()
                                    for i in range(5):
                                        GPIO.output(12, True)
                                        time.sleep(0.055)
                                        GPIO.output(12, False)
                                        time.sleep(0.055)
                                    time.sleep(2)
                                    GUI.close()
                            else:
                                GUI = VentanaEmergente("TARJETAINVALIDA", "")
                                GUI.show()
                                for i in range(5):
                                    GPIO.output(12, True)
                                    time.sleep(0.055)
                                    GPIO.output(12, False)
                                    time.sleep(0.055)
                                time.sleep(2)
                                GUI.close()
                        except Exception as e:
                            print("\x1b[1;31;47m"+"No se pudo leer la tarjeta: "+str(e)+'\033[0;m')
                            continue
                    if self.ser.isOpen():
                        try:
                            # Ya que esta abierta la comunicación con el QR, se verifica si hay un dato por leer
                            try:
                                qr = self.ser.readline()
                            except Exception as e:
                                logging.info(e)
                                self.restablecer_comunicación_QR()
                                
                            if qr.decode() != "": # Si hay un dato por leer se procede a leerlo
                                
                                if str(self.settings.value('folio_de_viaje')) != "": # Si hay un folio de viaje, se verifica si el QR es el mismo que el anterior
                                    
                                    if qr.decode() != self.ultimo_qr: # Si el QR es diferente al anterior, se procede a verificar que sea legitimo
                                        
                                        print("El QR es: "+qr.decode())
                                        qr = qr.decode()
                                        qr_string = qr
                                        qr = qr.split(",")
                                        print("El tamaño del QR es: "+str(len(qr)))
                                        
                                        if len(qr) == 9 or len(qr) == 10: # Si el QR tiene 8 elementos, se dice que es legitimo
                                                    
                                            fecha_qr = qr[0]
                                            fecha = str(strftime('%d-%m-%Y')).replace('/', '-')
                                            
                                            if fecha == fecha_qr: # Si la fecha del QR es igual a la fecha actual, se procede a verificar que el QR no haya caducado en hora
                                                
                                                hora_antes_de_caducar = qr[1]
                                                hora = strftime("%H:%M:%S")
                                                hora = strftime("%H:%M:%S")
                                                hecho = False
                                                tramo = qr[5]
                                                servicio = ""
                                                usted_se_dirige = ""
                                                tipo_de_pasajero = str(qr[6]).lower()
                                                p_n = ""
                                                
                                                if hora <= hora_antes_de_caducar: # Si la hora actual es menor o igual a la hora antes de caducar, se procede como un QR valido
                                                    
                                                    en_geocerca = False

                                                    # verificamos que la geocerca actual sea igual a la geocerca a transbordar
                                                    try:
                                                        doble_tarnsbordo_o_no = str(qr[7])
                                                        if doble_tarnsbordo_o_no == "st":
                                                            if str(str(vg.geocerca.split(",")[1]).split("_")[0]) in str(qr[8]):
                                                                geocarca_a_transbordar = str(qr[8])
                                                                en_geocerca = True
                                                        elif str(str(vg.geocerca.split(",")[1]).split("_")[0]) in str(qr[8]):
                                                            geocarca_a_transbordar = str(qr[8])
                                                            en_geocerca = True
                                                        elif str(str(vg.geocerca.split(",")[1]).split("_")[0]) in str(qr[9]):
                                                            geocarca_a_transbordar = str(qr[9])
                                                            en_geocerca = True
                                                    except Exception as e:
                                                        print(e)
                                                        logging.info(e)
                                                        
                                                    if en_geocerca == True:
                                                    
                                                        es_ticket_usado = verificar_ticket_completo(qr_string)
                                                        
                                                        if es_ticket_usado == None: # Si al verificar el ticket en la base de datos y es None significa que no ha sido usado.
                                                    
                                                            # Verificamos el tipo de pasajero y le asignamos su ID correspondiente.
                                                            
                                                            if tipo_de_pasajero != "normal":
                                                                p_n = "preferente"
                                                                if tipo_de_pasajero == "estudiante":
                                                                    id_tipo_de_pasajero = 1
                                                                elif tipo_de_pasajero == "menor":
                                                                    id_tipo_de_pasajero = 3
                                                                elif tipo_de_pasajero == "mayor":
                                                                    id_tipo_de_pasajero = 4
                                                            else:
                                                                p_n = "normal"
                                                                id_tipo_de_pasajero = 2
                                                            
                                                            print("Tipo de pasajero: ",tipo_de_pasajero)
                                                            print("Id tipo de pasajero: ",id_tipo_de_pasajero)
                                                            print("P/N: ",p_n)
                                                            
                                                            try:
                                                                from impresora import imprimir_boleto_normal_sin_servicio, imprimir_boleto_normal_con_servicio
                                                            except Exception as e:
                                                                print("No se importaron las librerias de impresora")
                                                            
                                                            if doble_tarnsbordo_o_no == "st":
                                                                
                                                                # Verificamos si el destino del QR es un destino de servicio directo
                                                                for servicio_vg in vg.todos_los_servicios_activos:
                                                                    if str(str(tramo).split("-")[1]) in str(servicio_vg[2]):
                                                                        servicio = str(servicio_vg[5]) + "-" + str(str(servicio_vg[1]).split("_")[0]) + "-" + str(str(servicio_vg[2]).split("_")[0])
                                                                
                                                                # Obtenemos el ultimo folio de venta de la base de datos
                                                                ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                                                                if ultimo_folio_de_venta != None:
                                                                    if int(self.settings.value('reiniciar_folios')) == 0:
                                                                        ultimo_folio_de_venta = int(ultimo_folio_de_venta[1]) + 1
                                                                    else:
                                                                        ultimo_folio_de_venta = 1
                                                                        self.settings.setValue('reiniciar_folios', 0)
                                                                else:
                                                                    ultimo_folio_de_venta = 1
                                                                    
                                                                # Procedemos a imprimir el ticket
                                                                
                                                                if servicio != "":
                                                                    usted_se_dirige = str(str(servicio).split("-")[2])
                                                                    hecho = imprimir_boleto_normal_con_servicio(ultimo_folio_de_venta, fecha, hora, self.idUnidad, servicio, tramo, qr)
                                                                    logging.info(f"Tickets de corte impresos correctamente.")
                                                                else:
                                                                    hecho = imprimir_boleto_normal_sin_servicio(ultimo_folio_de_venta, fecha, hora, self.idUnidad, tramo, qr)
                                                                    logging.info(f"Tickets de corte impresos correctamente, pero no se encontró el destino.")
                                                                    
                                                                if hecho:
                                                                    
                                                                    # Guardamos la venta en la base de datos para después poder ser enviada al servidor
                                                                    insertar_item_venta(ultimo_folio_de_venta, str(self.settings.value('folio_de_viaje')), fecha, hora, int(0), int(str(self.settings.value('geocerca')).split(",")[0]), id_tipo_de_pasajero, "t", p_n, tipo_de_pasajero, 0)
                                                                    print("Venta de servicio directo insertada correctamente.")
                                                                    
                                                                    self.ultimo_qr = qr_string
                                                                    self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                                                    
                                                                    insertar_ticket_usado(qr_string)
                                                                    # Mostramos la ventana de venta exitosa dependiendo de si se encontró el destino o no
                                                                    if usted_se_dirige != "":
                                                                        GUI = VentanaEmergente("ACEPTADO", usted_se_dirige)
                                                                        GUI.show()
                                                                        time.sleep(5)
                                                                        GUI.close()
                                                                    else:
                                                                        GUI = VentanaEmergente("ACEPTADO", "No encontrado")
                                                                        GUI.show()
                                                                        time.sleep(5)
                                                                        GUI.close()
                                                                else:
                                                                    # Si hubo un error al imprimir el ticket, suena el zumbador
                                                                    for i in range(5):
                                                                        GPIO.output(12, True)
                                                                        time.sleep(0.055)
                                                                        GPIO.output(12, False)
                                                                        time.sleep(0.055)
                                                                    time.sleep(0.5)
                                                            
                                                            elif doble_tarnsbordo_o_no == "ct":
                                                                
                                                                # Verificamos si el destino del QR es un destino de servicio directo
                                                                for transbordo in vg.todos_los_transbordos_activos:
                                                                    if str(str(tramo).split("-")[1]) in str(transbordo[2]):
                                                                        servicio = str(transbordo[5]) + "-" + str(str(transbordo[1]).split("_")[0]) + "-" + str(str(transbordo[2]).split("_")[0])
                                                                
                                                                # Obtenemos el ultimo folio de venta de la base de datos
                                                                ultimo_folio_de_venta = obtener_ultimo_folio_de_item_venta()
                                                                if ultimo_folio_de_venta != None:
                                                                    if int(self.settings.value('reiniciar_folios')) == 0:
                                                                        ultimo_folio_de_venta = int(ultimo_folio_de_venta[1]) + 1
                                                                    else:
                                                                        ultimo_folio_de_venta = 1
                                                                        self.settings.setValue('reiniciar_folios', 0)
                                                                else:
                                                                    ultimo_folio_de_venta = 1
                                                                    
                                                                if servicio != "":
                                                                    usted_se_dirige = str(str(servicio).split("-")[2])
                                                                    hecho = imprimir_boleto_normal_con_servicio(ultimo_folio_de_venta, fecha, hora, self.idUnidad, servicio, tramo, qr)
                                                                    logging.info(f"Tickets impresos correctamente.")
                                                                else:
                                                                    hecho = imprimir_boleto_normal_sin_servicio(ultimo_folio_de_venta, fecha, hora, self.idUnidad, tramo, qr)
                                                                    logging.info(f"Tickets impresos correctamente, pero no se encontró el destino.")
                                                                                    
                                                                if hecho:
                                                                    
                                                                    # Guardamos la venta en la base de datos para después poder ser enviada al servidor
                                                                    insertar_item_venta(ultimo_folio_de_venta, str(self.settings.value('folio_de_viaje')), fecha, hora, int(0), int(str(self.settings.value('geocerca')).split(",")[0]), id_tipo_de_pasajero, "t", p_n, tipo_de_pasajero, 0)
                                                                    print("Venta de transbordo insertada correctamente.")
                                                                    
                                                                    self.ultimo_qr = qr_string
                                                                    self.settings.setValue('total_de_folios', f"{int(self.settings.value('total_de_folios')) + 1}")
                                                                    
                                                                    insertar_ticket_usado(qr_string)
                                                                    # Mostramos la ventana de venta exitosa dependiendo de si se encontró el destino o no
                                                                    if usted_se_dirige != "":
                                                                        GUI = VentanaEmergente("ACEPTADO", usted_se_dirige)
                                                                        GUI.show()
                                                                        time.sleep(5)
                                                                        GUI.close()
                                                                    else:
                                                                        GUI = VentanaEmergente("ACEPTADO", "No encontrado")
                                                                        GUI.show()
                                                                        time.sleep(5)
                                                                        GUI.close()
                                                                else:
                                                                    # Si hubo un error al imprimir el ticket, suena el zumbador
                                                                    for i in range(5):
                                                                        GPIO.output(12, True)
                                                                        time.sleep(0.055)
                                                                        GPIO.output(12, False)
                                                                        time.sleep(0.055)
                                                                    time.sleep(0.5)
                                                        else:
                                                            print("El QR ya fue usado")
                                                            GUI = VentanaEmergente("UTILIZADO", ".....")
                                                            GUI.show()
                                                            for i in range(5):
                                                                GPIO.output(12, True)
                                                                time.sleep(0.055)
                                                                GPIO.output(12, False)
                                                                time.sleep(0.055)
                                                            time.sleep(4.5)
                                                            GUI.close()
                                                    else:
                                                        print("No se encuentra en la geocerca que debe transbordar")
                                                        if doble_tarnsbordo_o_no == "st":
                                                            GUI = VentanaEmergente("EQUIVOCADO", {qr[8]})
                                                        else:
                                                            GUI = VentanaEmergente("EQUIVOCADO", {qr[8]+" o "+qr[9]})
                                                        GUI.show()
                                                        for i in range(5):
                                                            GPIO.output(12, True)
                                                            time.sleep(0.055)
                                                            GPIO.output(12, False)
                                                            time.sleep(0.055)
                                                        time.sleep(4.5)
                                                        GUI.close()
                                                else:
                                                    print("El QR ya caducó")
                                                    GUI = VentanaEmergente("CADUCO", str(hora_antes_de_caducar))
                                                    GUI.show()
                                                    for i in range(5):
                                                        GPIO.output(12, True)
                                                        time.sleep(0.055)
                                                        GPIO.output(12, False)
                                                        time.sleep(0.055)
                                                    time.sleep(4.5)
                                                    GUI.close()
                                            else:
                                                print("La fecha del QR no es la actual")
                                                GUI = VentanaEmergente("CADUCO", "Fecha diferente")
                                                GUI.show()
                                                for i in range(5):
                                                    GPIO.output(12, True)
                                                    time.sleep(0.055)
                                                    GPIO.output(12, False)
                                                    time.sleep(0.055)
                                                time.sleep(4.5)
                                                GUI.close()
                                        else:
                                            print("El QR no es válido")
                                            GUI = VentanaEmergente("INVALIDO", "")
                                            GUI.show()
                                            for i in range(5):
                                                GPIO.output(12, True)
                                                time.sleep(0.055)
                                                GPIO.output(12, False)
                                                time.sleep(0.055)
                                            time.sleep(4.5)
                                            GUI.close()
                                    else:
                                        print("El ultimo QR se vuelve a pasar")
                                        GUI = VentanaEmergente("UTILIZADO", ".....")
                                        GUI.show()
                                        for i in range(5):
                                            GPIO.output(12, True)
                                            time.sleep(0.055)
                                            GPIO.output(12, False)
                                            time.sleep(0.055)
                                        time.sleep(4.5)
                                        GUI.close()
                                else:
                                    print("No hay ningún viaje activo")
                                    for i in range(5):
                                        GPIO.output(12, True)
                                        time.sleep(0.055)
                                        GPIO.output(12, False)
                                        time.sleep(0.055)
                                    time.sleep(1)
                        except Exception as e:
                            print(e)
                            logging.info(e)
                    else:
                        print("\x1b[1;31;47m"+"No se pudo establecer conexion con QR: "+str(e)+'\033[0;m')
                        self.restablecer_comunicación_QR()
                except Exception as e:
                    print("\x1b[1;31;47m"+"No se pudo establecer conexion: "+str(e)+'\033[0;m')
                    time.sleep(3)
                    logging.info(e)
        except Exception as e:
            print(e)
            logging.info(e)

    def restablecer_comunicación_QR(self):
        try:
            time.sleep(1)
            if self.ser.isOpen():
                print("\x1b[1;32m"+"Puerto ttyACM0 del QR abierto")
                print("\x1b[1;32m"+"Cerrando puerto ttyACM0 del QR")
                self.ser.close()
                self.restablecer_comunicación_QR()
            else:
                print("\x1b[1;32m"+"Puerto ttyACM0 del QR cerrado")
                while self.ser.isOpen() == False:
                    try:
                        print("\x1b[1;33m"+"Intentando abrir puerto ttyACM0 del QR")
                        time.sleep(5)
                        self.ser = serial.Serial(port='/dev/ttyACM0',baudrate = 115200,timeout=1)
                        print("\x1b[1;32m"+"Conexión del puerto ttyACM0 del QR restablecida")
                    except:
                        pass
        except Exception as e:
            print(e)
            logging.info(e)