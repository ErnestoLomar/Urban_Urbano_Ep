##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 12/04/2022
# Ultima modificación: 16/08/2022
#
# Script para la comunicación con el modem.
#
##########################################

#Librerías externas
from PyQt5.QtCore import QObject, pyqtSignal
import time
import logging
from time import strftime
import subprocess
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QSettings
import sys
import datetime
import traceback

sys.path.insert(1, '/home/pi/Urban_Urbano/db')
sys.path.insert(1, '/home/pi/Urban_Urbano/configuraciones_iniciales/actualizacion')

#Librerias propias
from comand import Comunicacion_Minicom, Principal_Modem
import variables_globales
from queries import obtener_datos_aforo, obtener_estadisticas_no_enviadas, actualizar_estado_estadistica_check_servidor, insertar_estadisticas_boletera, obtener_ultima_ACT, eliminar_todas_las_estadisticas_ACT_no_hechas
from asignaciones_queries import guardar_actualizacion, obtener_asignaciones_no_enviadas, actualizar_asignacion_check_servidor, obtener_todas_las_asignaciones_no_enviadas
import variables_globales
from comand import Comunicacion_Minicom, Principal_Modem
import variables_globales
from folio import cargarFolioActual, actualizar_folio
from asignaciones_queries import actualizar_estado_del_viaje_check_servidor, obtener_estado_de_viajes_no_enviados, obtener_asignacion_por_folio_de_viaje, obtener_fin_de_viaje_por_folio_de_viaje
from ventas_queries import obtener_estado_de_ventas_no_enviadas, actualizar_estado_venta_check_servidor, obtener_venta_por_folio_y_foliodeviaje, obtener_estado_de_todas_las_ventas_no_enviadas
from horariosDB import actualizar_estado_hora_check_hecho, obtener_estado_de_todas_las_horas_no_hechas, actualizar_estado_hora_por_defecto
from actualizar import Actualizar

#Creamos un objeto de la clase Principal_Modem
modem = Principal_Modem()

#Es un QObject que emite una señal cuando está hecho.
class LeerMinicomWorker(QObject):

    def __init__(self) -> None:
        super().__init__()
        try:
            modem.abrir_puerto()
            self.settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            self.idUnidad = str(obtener_datos_aforo()[1])
        except Exception as e:
            print("\x1b[1;31;47m"+"LeerMinicom.py, linea 39: "+str(e)+'\033[0;m')
            logging.info("LeerMinicom.py, linea 39: "+str(e))
        try:
            self.intentos_envio = 0
            self.recibido_folio_webservice = 0
            self.lista_de_datos_por_enviar = []
            self.intentos_conexion_gps = 0
        except Exception as e:
            print("\x1b[1;31;47m"+"LeerMinicom.py, linea 47: "+str(e)+'\033[0;m')
            logging.info("LeerMinicom.py, linea 47: "+str(e))
    try:
        finished = pyqtSignal()
        progress = pyqtSignal(dict)
        hora_actualizada = False
    except Exception as e:
        print("\x1b[1;31;47m"+"LeerMinicom.py, linea 64: "+str(e)+'\033[0;m')
        logging.info("LeerMinicom.py, linea 64: "+str(e))

    #Crea un nuevo hilo, y en ese hilo ejecuta una función que emite una señal cada segundo
    def run(self):
        
        try:
            self.contador_servidor = 0
            respuesta = cargarFolioActual()
            self.folio = respuesta['folio']
            if self.folio != 1:
                self.folio = self.folio + 1
            id_folio = respuesta['id']
            self.reenviar = self.folio
        except Exception as e:
            logging.info("Error al actualizar folio: "+str(e))
            print("\x1b[1;31;47m"+"LeerMinicom.py, linea 66: "+str(e)+'\033[0;m')
        try:
            while True:
                
                if self.folio == self.reenviar + 30:
                    #self.reenviar_varios_datos_servidor()
                    self.reenviar = self.folio

                res = Comunicacion_Minicom()
                res['signal_3g'] = modem.signal_3g()
                res['connection_3g'] = modem.conex_3g()
                variables_globales.signal = res['signal_3g']
                variables_globales.connection_3g = res['connection_3g']
                folio_asignacion_viaje = variables_globales.folio_asignacion
                fecha_completa = strftime('%Y-%m-%d %H:%M:%S')
                fecha = strftime("%m/%d/%Y")
                hora = strftime("%H:%M:%S")
                dia = strftime("%d-%m-%Y")
                enviado = ''
                trama_3_con_folio = ''
                trama_3_sin_folio = ''
                
                if ("error" not in res.keys()):
                    #GPS FUNCIONA
                    variables_globales.longitud = res['longitud']
                    variables_globales.latitud = res['latitud']
                    variables_globales.velocidad = res['velocidad']
                    variables_globales.GPS = "ok"
                    self.intentos_conexion_gps = 0

                    actualizar_folio(id_folio, self.folio, fecha)

                    if self.contador_servidor >= 12:
                        
                        if folio_asignacion_viaje != 0:
                            print("Enviando trama 3 con viaje")
                            logging.info("Enviando trama 3 con viaje")
                            trama_3_con_folio = "[3"+","+str(self.folio)+','+str(folio_asignacion_viaje)+","+hora+","+str(res['latitud'])+","+str(res['longitud'])+","+str(variables_globales.geocerca.split(",")[0])+","+str(res['velocidad']+"]")
                            result = modem.mandar_datos(trama_3_con_folio)
                            enviado = result['enviado']
                            if enviado == True:
                                print("\x1b[1;32m"+"#############################################")
                                print("\x1b[1;32m"+"Trama GNSS enviada: "+trama_3_con_folio)
                                print("\x1b[1;32m"+"#############################################")
                                logging.info('Trama enviada: '+trama_3_con_folio)
                            else:
                                logging.info('Trama no enviada: '+trama_3_con_folio)
                                print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                                print("\x1b[1;31;47m"+"Trama GNSS no enviada: "+trama_3_con_folio+'\033[0;m')
                                print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            self.reeconectar_socket(enviado)
                            self.folio = self.folio + 1
                            self.realizar_accion(result)
                        else:
                            print("Enviando trama 3 sin viaje")
                            logging.info("Enviando trama 3 sin viaje")
                            folio_de_viaje_sin_viaje = f"{''.join(fecha_completa[:10].split('-'))[3:]}{self.idUnidad}{99}"
                            trama_3_sin_folio = "[3"+","+str(self.folio)+','+str(folio_de_viaje_sin_viaje)+","+hora+","+str(res['latitud'])+","+str(res['longitud'])+","+str(variables_globales.geocerca.split(",")[0])+","+str(res['velocidad']+"]")
                            result = modem.mandar_datos(trama_3_sin_folio)
                            enviado = result['enviado']
                            if enviado == True:
                                print("\x1b[1;32m"+"#############################################")
                                print("\x1b[1;32m"+"Trama GNSS enviada: "+trama_3_sin_folio)
                                print("\x1b[1;32m"+"#############################################")
                                logging.info('Trama enviada: '+trama_3_sin_folio)
                            else:
                                logging.info('Trama no enviada: '+trama_3_sin_folio)
                                print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                                print("\x1b[1;31;47m"+"Trama GNSS no enviada: "+trama_3_sin_folio+'\033[0;m')
                                print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            self.reeconectar_socket(enviado)
                            self.folio = self.folio + 1
                            self.realizar_accion(result)
                        self.contador_servidor = 0
                else:
                    variables_globales.GPS = "error"
                    print("\x1b[1;31;47m"+"Error al obtener coordenadas GPS"+'\033[0;m')
                    logging.info('Error al obtener datos del GPS')
                    if self.intentos_conexion_gps >= 5:
                        modem.reconectar_gps()
                        self.intentos_conexion_gps = 0
                    self.intentos_conexion_gps+=1
                    self.contador_servidor = 0
                    
                if self.contador_servidor == 0 or self.contador_servidor == 4 or self.contador_servidor == 8 or self.contador_servidor >= 12:
                    try:
                        print("\x1b[1;32m"+"Verificando si hay datos en la BD por enviar...")
                        for j in range(6):
                            total_de_asignaciones_no_enviadas = obtener_todas_las_asignaciones_no_enviadas()
                            fin_de_viajes_no_enviados = obtener_estado_de_viajes_no_enviados()
                            total_de_ventas_no_enviadas = obtener_estado_de_todas_las_ventas_no_enviadas()
                            total_de_estadisticas_no_enviadas = obtener_estadisticas_no_enviadas()
                            
                            if len(total_de_asignaciones_no_enviadas) != 0:
                                self.lista_de_datos_por_enviar.append(f"{total_de_asignaciones_no_enviadas[0][4]}{total_de_asignaciones_no_enviadas[0][5]},asignacion")
                            if len(total_de_ventas_no_enviadas) != 0:
                                self.lista_de_datos_por_enviar.append(f"{total_de_ventas_no_enviadas[0][3]}{total_de_ventas_no_enviadas[0][4]},venta")
                            if len(fin_de_viajes_no_enviados) != 0:
                                self.lista_de_datos_por_enviar.append(f"{fin_de_viajes_no_enviados[0][3]}{fin_de_viajes_no_enviados[0][4]},finviaje")
                            if len(total_de_estadisticas_no_enviadas) != 0:
                                self.lista_de_datos_por_enviar.append(f"{total_de_estadisticas_no_enviadas[0][2]}{total_de_estadisticas_no_enviadas[0][3]},estadistica")
                            
                            if len(self.lista_de_datos_por_enviar) != 0:
                                #print("Lista de datos: ", self.lista_de_datos_por_enviar)
                                primer_dato = self.lista_de_datos_por_enviar[0].split(",")
                                menor_operacion = int(str(primer_dato[0]).replace(":", "").replace("-", ""))
                                menor = primer_dato[0]
                                tipo_de_dato = primer_dato[1]
                                for i in range(len(self.lista_de_datos_por_enviar)):
                                    #print("Item de lista: ", self.lista_de_datos_por_enviar[i])
                                    dato = self.lista_de_datos_por_enviar[i].split(",")
                                    if int(str(dato[0]).replace(":", "").replace("-", "")) < menor_operacion:
                                        menor = dato[0]
                                        menor_operacion = int(str(dato[0]).replace(":", "").replace("-", ""))
                                        tipo_de_dato = dato[1]
                                #print("El menor es: "+str(menor))
                                #print("El menor operacion es: "+str(menor_operacion))
                                #print("El tipo de dato es: "+str(tipo_de_dato))
                                if 'asignacion' in tipo_de_dato:
                                    print("Enviando asignacion")
                                    self.enviar_inicio_de_viaje()
                                    print("\n")
                                if 'venta' in tipo_de_dato:
                                    print("Enviando venta")
                                    self.enviar_venta()
                                    print("\n")
                                if 'finviaje' in tipo_de_dato:
                                    print("Enviando fin de viaje")
                                    self.enviar_fin_de_viaje()
                                    print("\n")
                                if 'estadistica' in tipo_de_dato:
                                    print("Enviando estadistica")
                                    self.enviar_trama_informativa()
                                    print("\n")
                                self.lista_de_datos_por_enviar = []
                        print("\x1b[1;32m"+"Terminando de verificar si hay datos en la BD por enviar...")
                    except Exception as e:
                        logging.info('Error al enviar datos al servidor: '+str(e))
                        print("\x1b[1;31;47m"+"Error al enviar datos al servidor: "+str(e)+'\033[0;m')
                
                try:
                    
                    ####### VERIFICAR SI SE PUEDE CREAR LA TRAMA ACT #######
                    self.crear_tramas_ACT()
                    ############################################################
                    
                    ####### VERIFICAR SI HAY QUE PONER POR DEFECTO LA BASE DE DATOS HORAS #######
                
                    # The code is checking if the length of the string representation of the result of the
                    # function `obtener_ultima_ACT()` is greater than 2. If it is, it assigns the value of
                    # the third element of the first element of the result of `obtener_ultima_ACT()` to
                    # the variable `fecha_str`. It then converts `fecha_str` to a `datetime` object using
                    # the format "%Y-%m-%d" and assigns it to the variable `fecha_datetime`.
                    reiniciar_valores_por_defecto = False
                    
                    if len(str(obtener_ultima_ACT())) > 2:
                        fecha_str = obtener_ultima_ACT()[0][2]
                        fecha_datetime = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
                        if fecha_datetime.strftime("%Y-%m-%d") != datetime.date.today().strftime("%Y-%m-%d"):
                            reiniciar_valores_por_defecto = True
                            print("Es un dia diferente")
                            
                    # Obtener la hora actual
                    hora_actual = datetime.datetime.now().time()
                    
                    # The code is checking if the current time is between 23:35:00 and 23:59:59 or if the
                    # variable `reiniciar_valores_por_defecto` is true. If either condition is true, it
                    # calls the `actualizar_estado_hora_por_defecto()` function, updates some values, and
                    # prints a message indicating whether the database hours were successfully updated or
                    # not.
                    if int(str(hora_actual.strftime("%H:%M:%S")).replace(":",""))  >= 233500 and int(str(hora_actual.strftime("%H:%M:%S")).replace(":",""))  <= 235959 or reiniciar_valores_por_defecto:
                        
                        hecho_horas = actualizar_estado_hora_por_defecto()
                        
                        intentos_cambiar = 0
                        
                        if not hecho_horas:
                            while not hecho_horas or intentos_cambiar <= 5:
                                hecho_horas = actualizar_estado_hora_por_defecto()
                                intentos_cambiar += 1
                            if hecho_horas:
                                print("Se actualizaron las BD horas a por defecto 2")
                            else:
                                print("No se actualizaron las BD horas a por defecto")
                        else:
                            print("Se actualizaron las BD horas a por defecto")
                            
                            
                        # Luego verificamos si la hora actual es mayor a la hora de la BD
                        obtener_todas_las_horasdb = obtener_estado_de_todas_las_horas_no_hechas()
                        for i in range(len(obtener_todas_las_horasdb)):
                            hora_iteracion = obtener_todas_las_horasdb[i]
                            hora_actual = datetime.datetime.now().time()
                            if int(str(hora_actual.strftime("%H:%M:%S")).replace(":","")) >= int(str(hora_iteracion[1]).replace(":","")):
                                hecho = actualizar_estado_hora_check_hecho("OK", hora_iteracion[0])
                                if hecho:
                                    print("Se actualizo la hora")
                    ############################################################
                except Exception as e:
                    print("Error al actualizar horas por defecto: "+str(e))
                    logging.info("Error al actualizar horas por defecto: "+str(e))        
                
                self.progress.emit(res)
                time.sleep(5)
                self.contador_servidor = self.contador_servidor + 1
        except Exception as e:
            print("\x1b[1;31;47m"+"LeerMinicom.py, linea 155: "+str(e)+'\033[0;m')
            logging.info("LeerMinicom.py, linea 155: "+str(e))
            
    def crear_tramas_ACT(self):
        
        obtener_todas_las_horasdb = obtener_estado_de_todas_las_horas_no_hechas()
        residuo = int(self.idUnidad) % 30
        
        for i in range(len(obtener_todas_las_horasdb)):
    
            hora_iteracion = obtener_todas_las_horasdb[i]
            
            # Obtener la hora actual
            hora_actual = datetime.datetime.now().time()

            # Convertir la hora_iteracion a un objeto datetime
            hora_iteracion_datetime = datetime.datetime.strptime(str(hora_iteracion[1]), "%H:%M:%S").time()
            
            # Sumar el residuo como minutos
            hora_iteracion_sumada = (datetime.datetime.combine(datetime.datetime.today(), hora_iteracion_datetime) + datetime.timedelta(minutes=residuo)).time()
            
            """
            print("Unidad:", str(self.idUnidad))
            print("Residuo:", str(residuo))
            print("Hora actual:", str(hora_actual.strftime("%H:%M:%S")))
            print("Hora iteracion sumada:", str(hora_iteracion_sumada.strftime("%H:%M:%S")))"""

            # Comparar las horas
            if int(str(hora_actual.strftime("%H:%M:%S")).replace(":","")) >= int(str(hora_iteracion_sumada).replace(":","")):
                
                hecho = actualizar_estado_hora_check_hecho("OK", hora_iteracion[0])
                
                if hecho:
                    
                    #print("Ya se actualizó la hora check en servidor de:", str(hora_iteracion))
                    fecha_actual = datetime.date.today()
                    
                    ultima_trama_act = obtener_ultima_ACT()
                    #print("Ultima trama ACT: ", ultima_trama_act)
                    insert_hecho = False
                    
                    if len(ultima_trama_act) > 0:
                            
                            fecha_ultima_trama_act = ultima_trama_act[0][2]
                            hora_ultima_trama_act = ultima_trama_act[0][3]
                            check_servidor_ultima_trama_act = ultima_trama_act[0][6]
                            
                            ultima_trama_timestamp = datetime.datetime.strptime("{} {}".format(fecha_ultima_trama_act, hora_ultima_trama_act), "%Y-%m-%d %H:%M:%S")
                            tiempo_transcurrido = (datetime.datetime.now() - ultima_trama_timestamp).total_seconds() / 60  # Diferencia en minutos

                            if tiempo_transcurrido <= 20 or check_servidor_ultima_trama_act == "NO":
                                print("Ya se ha insertado la trama de ACT dentro de los últimos 20 minutos")
                                actualizar_estado_hora_check_hecho("OK", hora_iteracion[0])
                                continue
                            else:
                                print("No se insertó la trama de ACT en los últimos 20 minutos")
                                eliminar_todas_las_estadisticas_ACT_no_hechas()
                                insert_hecho = insertar_estadisticas_boletera(str(self.idUnidad), fecha_actual.strftime("%Y-%m-%d"), hora_actual.strftime("%H:%M:%S"), "ACT", "")
                    else:
                        eliminar_todas_las_estadisticas_ACT_no_hechas()
                        insert_hecho = insertar_estadisticas_boletera(str(self.idUnidad), fecha_actual.strftime("%Y-%m-%d"), hora_actual.strftime("%H:%M:%S"), "ACT", "")
                        print("Es la primera trama ACT")
                    
                    if insert_hecho:
                        print("Se insertó la estadística de ACT")
                    else:
                        
                        ultima_trama_act = obtener_ultima_ACT()
                        
                        if len(ultima_trama_act) > 0:
                                
                                fecha_ultima_trama_act = ultima_trama_act[0][2]
                                hora_ultima_trama_act = ultima_trama_act[0][3]
                                check_servidor_ultima_trama_act = ultima_trama_act[0][6]
                                
                                ultima_trama_timestamp = datetime.datetime.strptime("{} {}".format(fecha_ultima_trama_act, hora_ultima_trama_act), "%Y-%m-%d %H:%M:%S")
                                tiempo_transcurrido = (datetime.datetime.now() - ultima_trama_timestamp).total_seconds() / 60  # Diferencia en minutos

                                if tiempo_transcurrido <= 20 or check_servidor_ultima_trama_act == "NO":
                                    print("Ya se ha insertado la trama de ACT dentro de los últimos 20 minutos")
                                    actualizar_estado_hora_check_hecho("OK", hora_iteracion[0])
                                else:
                                    print("No se insertó la trama de ACT en los últimos 20 minutos")
                                    actualizar_estado_hora_check_hecho("NO", hora_iteracion[0])
                        else:
                            print("No se insertó la trama de ACT y no hay tramas ACT en la BD")
                            actualizar_estado_hora_check_hecho("NO", hora_iteracion[0])
                else:
                    print("No se actualizo la hora check")
                        

    def realizar_accion(self, result):
        """
        Si la clave "accion" esta en el diccionario de resultados del servidor, entonces el valor de la clave
        "accion" se asigna a la variable accion. Si accion es igual a "APAGAR", entonces la raspberrry se
        apaga. Si accion es igual a "REINICIAR", entonces se reinicia la raspberry. Si accion es igual a
        "ACTUALIZAR", entonces se actualiza el raspberry
        """
        try:
            if "accion" in result.keys():
                accion = str(result['accion']).replace("SKT", "")
                print("La accion a realizar es: " + accion)
                logging.info('La accion a realizar es: '+accion)
                fecha = strftime('%Y/%m/%d').replace('/', '')[2:]
                
                # Procedemos a obtener la hora de la boletera
                fecha_actual = str(subprocess.run("date", stdout=subprocess.PIPE, shell=True))
                indice = fecha_actual.find(":")
                hora = str(fecha_actual[(int(indice) - 2):(int(indice) + 6)]).replace(":","")
                if "A" in accion:
                    try:
                        print("Entro a A")
                        logging.info('Entro a A')
                        datos = accion.split(',')
                        if len(datos) == 2:
                            if self.recibido_folio_webservice <= 3:
                                self.recibido_folio_webservice +=1
                                self.settings.setValue("folio_de_viaje_webservice",datos[1])
                                print("Folio de web service recibido correctamente")
                                logging.info('Folio de web service recibido correctamente')
                            else:
                                if variables_globales.folio_asignacion == 0:
                                    self.recibido_folio_webservice = 0
                                    print("Reiniciando folio de web service")
                                    logging.info('Reiniciando folio de web service')
                    except Exception as e:
                        logging.info('Error al hacer accion A: '+str(e))
                        print("LeerMinicom.py, linea 138: "+str(e))
                if "B" in accion:
                    try:
                        logging.info('Entro a B')
                        total_de_ventas_no_enviadas = obtener_estado_de_ventas_no_enviadas()
                        total_de_inicio_de_viajes_no_enviados = obtener_asignaciones_no_enviadas()
                        total_de_fin_de_viajes_no_enviados = obtener_estado_de_viajes_no_enviados()
                        if len(total_de_ventas_no_enviadas) == 0 and len(total_de_inicio_de_viajes_no_enviados) == 0 and len(total_de_fin_de_viajes_no_enviados) == 0:
                            guardar_actualizacion('REINICIAR', fecha, 1)    
                            modem.cerrar_socket()
                            print("REINICIAR")
                            logging.info("Reinicio de raspberry por petición del servidor")
                            subprocess.run("sudo reboot", shell=True)
                        else:
                            while True:
                                if len(total_de_ventas_no_enviadas) == 0 and len(total_de_inicio_de_viajes_no_enviados) == 0 and len(total_de_fin_de_viajes_no_enviados) == 0:
                                    break
                                else:
                                    self.enviar_venta()
                                    self.enviar_inicio_de_viaje()
                                    self.enviar_fin_de_viaje()
                                    time.sleep(1)
                                    total_de_ventas_no_enviadas = obtener_estado_de_ventas_no_enviadas()
                                    total_de_inicio_de_viajes_no_enviados = obtener_asignaciones_no_enviadas()
                                    total_de_fin_de_viajes_no_enviados = obtener_estado_de_viajes_no_enviados()
                                    time.sleep(2)
                            guardar_actualizacion('REINICIAR', fecha, 1)    
                            modem.cerrar_socket()
                            print("REINICIAR")
                            logging.info("Reinicio de raspberry por petición del servidor")
                            subprocess.run("sudo reboot", shell=True)
                    except Exception as e:
                        print("LeerMinicom.py, linea 225: "+str(e))
                elif "C" in accion:
                    try:
                        logging.info('Entro a C')
                        folio_asignacion_viaje = variables_globales.folio_asignacion
                        if folio_asignacion_viaje == 0:
                            datos = accion.split(',')
                            if len(datos) == 3:
                                try:
                                    total_de_ventas_no_enviadas = obtener_estado_de_ventas_no_enviadas()
                                    total_de_inicio_de_viajes_no_enviados = obtener_asignaciones_no_enviadas()
                                    total_de_fin_de_viajes_no_enviados = obtener_estado_de_viajes_no_enviados()
                                    if len(total_de_ventas_no_enviadas) == 0 and len(total_de_inicio_de_viajes_no_enviados) == 0 and len(total_de_fin_de_viajes_no_enviados) == 0:
                                        guardar_actualizacion('ACTUALIZAR', fecha, 1)
                                        logging.info("Actualizando raspberry por petición del servidor")
                                        ventana_actualzar = Actualizar()
                                        ventana_actualzar.show()
                                        ventana_actualzar.actualizar_raspberrypi(int(datos[1]), False)
                                    else:
                                        while True:
                                            if len(total_de_ventas_no_enviadas) == 0 and len(total_de_inicio_de_viajes_no_enviados) == 0 and len(total_de_fin_de_viajes_no_enviados) == 0:
                                                break
                                            else:
                                                self.enviar_venta()
                                                self.enviar_inicio_de_viaje()
                                                self.enviar_fin_de_viaje()
                                                time.sleep(1)
                                                total_de_ventas_no_enviadas = obtener_estado_de_ventas_no_enviadas()
                                                total_de_inicio_de_viajes_no_enviados = obtener_asignaciones_no_enviadas()
                                                total_de_fin_de_viajes_no_enviados = obtener_estado_de_viajes_no_enviados()
                                                time.sleep(2)
                                        guardar_actualizacion('ACTUALIZAR', fecha, 1)
                                        logging.info("Actualizando raspberry por petición del servidor")
                                        ventana_actualzar = Actualizar()
                                        ventana_actualzar.show()
                                        ventana_actualzar.actualizar_raspberrypi(int(datos[1]), False)
                                except Exception as e:
                                    print("LeerMinicom.py, linea 258: "+str(e))
                        else:
                            insertar_estadisticas_boletera(str(self.idUnidad), fecha, hora, "FTP", f"En viaje")
                    except Exception as e:
                        print("LeerMinicom.py, linea 239: "+str(e))
                elif "T" in accion:
                    try:
                        print("Entro a T, actualizar matriz tarifaría")
                        logging.info('Entro a T, actualizar matriz tarifaría')
                        datos = accion.split(',')
                        if len(datos) == 3:
                            if len(str(datos[1])) == 12:
                                if variables_globales.version_de_MT < str(datos[1]):
                                    print(f"Se procedera a actualizar la MT de {variables_globales.version_de_MT} a {str(datos[1])}")
                                    logging.info(f"Se procedera a actualizar la MT de {variables_globales.version_de_MT} a {str(datos[1])}")
                                    try:
                                        ventana_actualzar = Actualizar()
                                        ventana_actualzar.show()
                                        ventana_actualzar.actualizar_raspberrypi(str(datos[2]).replace("\n","").replace("\r",""), str(datos[1]))
                                    except Exception as e:
                                        print(f"No se logro hacer la actualizacion de la matriz tarifaría: {e}")
                                        logging.info(f"No se logro hacer la actualizacion de la matriz tarifaría: {e}")
                                else:
                                    print(f"No se puede actualizar la MT porque {variables_globales.version_de_MT} es igual a {str(datos[1])}")
                                    logging.info(f"No se puede actualizar la MT porque {variables_globales.version_de_MT} es igual a {str(datos[1])}")
                    except Exception as e:
                        print("Error al hacer accion T: " + str(e))
                        logging.info('Error al hacer accion T: '+str(e))
                        print("LeerMinicom.py, linea 138: "+str(e))
                elif "I" in accion:
                    try:
                        print("Entro a I, para realizar instruccion")
                        logging.info("Entro a I, para realizar instruccion")
                        datos = accion.split(',')
                        if len(datos) == 2:
                            comando = str(datos[1])
                            proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            salida, errores = proceso.communicate()
                            if proceso.returncode == 0:
                                print("Comando ejecutado correctamente:")
                                insertar_estadisticas_boletera(str(self.idUnidad), fecha, hora, "CMD", f"OK,{comando}")
                                print(salida.decode("utf-8"))
                            else:
                                print(f"Error al ejecutar el comando. Código de salida: {proceso.returncode}")
                                insertar_estadisticas_boletera(str(self.idUnidad), fecha, hora, "CMD", f"ERR,{comando}")
                                print(errores.decode("utf-8"))
                    except Exception as e:
                        print("Error al hacer accion I: " + str(e))
                        logging.info('Error al hacer accion I: '+str(e))
                        print("LeerMinicom.py, linea 138: "+str(e))
        except Exception as e:
            print("LeerMinicom.py, linea 255: "+str(e))

    def reeconectar_socket(self, enviado: bool):
        # Si el número de intentos de enviar un mensaje a través de tcp es 10, el socket se cierra y
        # se abre uno nuevo.
        try: 
            print("\x1b[1;32m"+'numero de intentos'+ str(int(self.intentos_envio) + 1))
            if enviado != True:
                self.intentos_envio = self.intentos_envio + 1
                if self.intentos_envio == 2:
                    try:
                        logging.info('Creando una nueva conexion con el socket')
                        print("\x1b[1;33m"+"Creando un nuevo socket...")
                        modem.cerrar_socket()
                        modem.abrir_puerto()
                    except Exception as e:
                        print("\x1b[1;31;47m"+"LeerMinicom.py, linea 176: "+str(e)+'\033[0;m')
                elif self.intentos_envio == 4:
                    try:
                        logging.info('Reiniciando el quectel')
                        print("\x1b[1;33m"+"Reiniciando el quectel...")
                        modem.cerrar_socket()
                        modem.reiniciar_QUEQTEL()
                        modem.reiniciar_configuracion_quectel()
                        modem.abrir_puerto()
                    except Exception as e:
                        print("\x1b[1;31;47m"+"LeerMinicom.py, linea 196: "+str(e)+'\033[0;m')
                elif self.intentos_envio == 6:
                    try:
                        logging.info('Se cambiara de socket')
                        print("\x1b[1;33m"+"Cambiando de socket...")
                        modem.cerrar_socket()
                        modem.cambiar_socket()
                        modem.reiniciar_configuracion_quectel()
                        modem.abrir_puerto()
                    except Exception as e:
                        print("\x1b[1;31;47m"+"LeerMinicom.py, linea 196: "+str(e)+'\033[0;m')
                elif self.intentos_envio >= 8:
                    print("\x1b[1;33m"+"Restableciendo socket...")
                    modem.cambiar_socket(1)
                    self.intentos_envio = 0
            else:
                self.intentos_envio = 0
        except Exception as e:
            print("\x1b[1;31;47m"+"LeerMinicom.py, linea 178: "+str(e)+'\033[0;m')
            
    def calcular_checksum(self, Trama):
        checksum = 0
        for char in Trama:
            checksum += ord(char)
        return str(checksum)[-3:].replace(" ", "")
    
    def enviar_inicio_de_viaje(self):
        try:
            asignaciones = obtener_asignaciones_no_enviadas()

            if len(asignaciones) > 0:
                for asignacion in asignaciones:
                    try:
                        id = asignacion[0]
                        csn_chofer = asignacion[2]
                        servicio_pension = str(asignacion[3]).replace("-", ",").split(",")[0]
                        hora_inicio = asignacion[5]
                        folio_de_viaje = asignacion[6]
                        estado_servidor_inicio = asignacion[7]
                        
                        if len(csn_chofer) == 0:
                            print("\x1b[1;33m"+"#############################################")
                            print("\x1b[1;33m"+"El csn esta vació en trama 2, haciendo primer candado de seguridad...")
                            logging.info("El csn esta vació en trama 2, haciendo primer candado de seguridad...")
                            intentos = 1
                            while True:
                                asignacioness = obtener_asignaciones_no_enviadas()[0]
                                csn_chofer = asignacioness[2]
                                if intentos == 5 or len(csn_chofer) != 0:
                                    print("\x1b[1;33m"+"#############################################")
                                    break
                                intentos = intentos + 1
                                
                        if len(csn_chofer) == 0:
                            print("\x1b[1;33m"+"#############################################")
                            print("\x1b[1;33m"+"El csn esta vació en trama 2, haciendo segundo candado de seguridad...")
                            logging.info("El csn esta vació en trama 2, haciendo segundo candado de seguridad...")
                            intentos2 = 1
                            while True:
                                csn_chofer = self.settings.value('csn_chofer')
                                if intentos2 == 5 or len(csn_chofer) != 0:
                                    print("\x1b[1;33m"+"#############################################")
                                    break
                                intentos2 = intentos2 + 1
                        if len(csn_chofer) == 0:
                            print("\x1b[1;33m"+"#############################################")
                            print("\x1b[1;33m"+"El csn esta vació en trama 2, haciendo tercer candado de seguridad...")
                            logging.info("El csn esta vació en trama 2, haciendo tercer candado de seguridad...")
                            intentos3 = 1
                            while True:
                                csn_chofer = variables_globales.csn_chofer
                                if intentos3 == 5 or len(csn_chofer) != 0:
                                    print("\x1b[1;33m"+"#############################################")
                                    break
                                intentos3 = intentos3 + 1
                                
                        if len(csn_chofer) == 0:
                            print("\x1b[1;33m"+"#############################################")
                            print("\x1b[1;33m"+"El csn esta vació en trama 2, haciendo cuarto candado de seguridad...")
                            logging.info("El csn esta vació en trama 2, haciendo cuarto candado de seguridad...")
                            if len(variables_globales.csn_chofer_respaldo) != 0:
                                csn_chofer = variables_globales.csn_chofer_respaldo
                                print("\x1b[1;33m"+"#############################################")

                        trama_2 = "2,"+str(folio_de_viaje)+","+str(hora_inicio)+","+str(csn_chofer)+","+servicio_pension
                        checksum_2 = self.calcular_checksum(trama_2)
                        trama_2 = "["+trama_2+","+str(checksum_2)+"]"
                        print("\x1b[1;32m"+"Enviando inicio de viaje: "+trama_2)
                        logging.info("Enviando inicio de viaje: "+trama_2)
                        result = modem.mandar_datos(trama_2)
                        enviado = result['enviado']

                        if enviado == True:
                            try:
                                
                                checksum_socket_t2 = str(result["accion"]).replace("SKT","")[:3]
                                #print("El checksum t2 es: ", checksum_socket_t2)
                                
                                if checksum_socket_t2 in checksum_2:
                                    actualizar_asignacion_check_servidor("OK",id)
                                    print("\x1b[1;32m"+"#############################################")
                                    print("\x1b[1;32m"+"Trama de inicio de viaje enviada: ", estado_servidor_inicio)
                                    print("\x1b[1;32m"+"#############################################")
                                    logging.info("Trama de inicio de viaje enviada")
                                    variables_globales.csn_chofer_respaldo = ""
                                    self.realizar_accion(result)
                                else:
                                    print("\x1b[1;31;47m"+"El checksum no coincide"+'\033[0;m')
                            except Exception as e:
                                print("LeerMinicom.py, linea 376: "+str(e))
                        else:
                            logging.info("No se pudo enviar la trama de inicio de viaje")
                            print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            print("\x1b[1;31;47m"+"Trama de inicio de viaje no enviada"+'\033[0;m')
                            print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            
                        self.reeconectar_socket(enviado)
                    except Exception as e:
                        print("LeerMinicom.py, linea 378: "+str(e))
        except Exception as e:
            print("LeerMinicom.py, linea 380: "+str(e))

    def enviar_fin_de_viaje(self):
        try:
            viajes = obtener_estado_de_viajes_no_enviados()

            if len(viajes) > 0:
                for viaje in viajes:
                    try:
                        id = viaje[0]
                        csn_chofer = viaje[1]
                        hora_inicio = viaje[4]
                        total_de_folio_aforo_efectivo = viaje[5]
                        total_de_folio_aforo_tarjeta = viaje[6]
                        total_aforo_efectivo = viaje[7]
                        folio_de_viaje = viaje[8]
                        estado_servidor_fin = viaje[9]

                        trama_4 = "4,"+str(folio_de_viaje)+","+str(hora_inicio)+","+str(csn_chofer)+","+str(total_de_folio_aforo_efectivo)+","+str(total_de_folio_aforo_tarjeta)+","+str(total_aforo_efectivo)
                        checksum_4 = self.calcular_checksum(trama_4)
                        trama_4 = "["+trama_4+","+str(checksum_4)+"]"
                        print("\x1b[1;32m"+"Enviando cierre de viaje: "+trama_4)
                        logging.info("Enviando cierre de viaje: "+trama_4)
                        result = modem.mandar_datos(trama_4)
                        enviado = result['enviado']

                        if enviado == True:
                            try:
                                
                                checksum_socket_t4 = str(result["accion"]).replace("SKT","")[:3]
                                #print("El checksum t4 es: ", checksum_socket_t4)
                                
                                if checksum_socket_t4 in checksum_4:
                                    actualizar_estado_del_viaje_check_servidor("OK",id)
                                    print("\x1b[1;32m"+"#############################################")
                                    print("\x1b[1;32m"+"Trama de fin de viaje enviada")
                                    print("\x1b[1;32m"+"#############################################")
                                    logging.info("Trama de fin de viaje enviada")
                                    self.realizar_accion(result)
                                else:
                                    print("\x1b[1;31;47m"+"El checksum no coincide"+'\033[0;m')
                            except Exception as e:
                                print("LeerMinicom.py, linea 376: "+str(e))
                        else:
                            print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            print("\x1b[1;31;47m"+"Trama de fin de viaje no enviada"+'\033[0;m')
                            print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            logging.info("No se pudo enviar la trama de fin de viaje")
                        self.reeconectar_socket(enviado)
                    except Exception as e:
                        print("LeerMinicom.py, linea 378: "+str(e))
        except Exception as e:
            print("LeerMinicom.py, linea 380: "+str(e))
    
    def enviar_venta(self):
        try:
            ventas = obtener_estado_de_ventas_no_enviadas()

            if len(ventas) > 0:
                for venta in ventas:
                    try:
                        id = venta[0]
                        folio_aforo_venta = venta[1]
                        folio_de_viaje = venta[2]
                        hora_db = venta[4]
                        id_del_servicio_o_transbordo = venta[5]
                        id_geocerca = venta[6]
                        id_tipo_de_pasajero = venta[7]
                        transbordo_o_no = venta[8]
                        estado_servidor_venta = venta[12]

                        trama_5 = "5,"+str(folio_aforo_venta)+","+str(folio_de_viaje)+","+str(hora_db)+","+str(id_del_servicio_o_transbordo)+","+str(id_geocerca)+","+str(id_tipo_de_pasajero)+","+str(transbordo_o_no)
                        checksum_5 = self.calcular_checksum(trama_5)
                        trama_5 = "["+trama_5+","+str(checksum_5)+"]"
                        print("\x1b[1;32m"+"Enviando venta: "+trama_5)
                        logging.info("Enviando venta: "+trama_5)
                        result = modem.mandar_datos(trama_5)
                        enviado = result['enviado']

                        if enviado == True:
                            try:
                                
                                checksum_socket_t5 = str(result["accion"]).replace("SKT","")[:3]
                                #print("El checksum t5 es: ", checksum_socket_t5)
                                
                                if checksum_socket_t5 in checksum_5:
                                    actualizar_estado_venta_check_servidor("OK",id)
                                    print("\x1b[1;32m"+"#############################################")
                                    print("\x1b[1;32m"+"Trama de venta enviada")
                                    print("\x1b[1;32m"+"#############################################")
                                    logging.info("Trama de venta enviada")
                                    self.realizar_accion(result)
                                else:
                                    print("\x1b[1;31;47m"+"El checksum no coincide"+'\033[0;m')
                            except Exception as e:
                                print("LeerMinicom.py, linea 376: "+str(e))
                        else:
                            print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            print("\x1b[1;31;47m"+"Trama de venta no enviada"+'\033[0;m')
                            print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            logging.info("No se pudo enviar la trama de venta")
                        self.reeconectar_socket(enviado)
                    except Exception as e:
                        print("LeerMinicom.py, linea 378: "+str(e))
                        print(traceback.format_exc())
        except Exception as e:
            print("LeerMinicom.py, linea 380: "+str(e))
            print(traceback.format_exc())
            
    def enviar_trama_informativa(self):
        try:
            estadisticas = obtener_estadisticas_no_enviadas()

            if len(estadisticas) > 0:
                for estadistica in estadisticas:
                    try:
                        idMuestreo_estadistica = estadistica[0]
                        idUnidad_estadistica = estadistica[1]
                        fecha_estadistica = estadistica[2]
                        hora_estadistica = estadistica[3]
                        columna_estadistica = estadistica[4]
                        valor_estadistica = estadistica[5]

                        trama_9 = '[9'+","+str(idUnidad_estadistica)+","+str(fecha_estadistica)+","+str(hora_estadistica)+","+str(columna_estadistica)+","+str(valor_estadistica)+"]"
                        print("\x1b[1;32m"+"Enviando trama 9: "+trama_9)
                        logging.info("Enviando estadistica: "+trama_9)
                        result = modem.mandar_datos(trama_9)
                        enviado = result['enviado']

                        if enviado == True:
                            try:
                                actualizar_estado_estadistica_check_servidor("OK",idMuestreo_estadistica)
                                print("\x1b[1;32m"+"#############################################")
                                print("\x1b[1;32m"+"Trama de estadistica enviada")
                                print("\x1b[1;32m"+"#############################################")
                                logging.info("Trama de estadistica enviada")
                                self.realizar_accion(result)
                            except Exception as e:
                                print("LeerMinicom.py, linea 376: "+str(e))
                                print(traceback.format_exc())
                        else:
                            print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            print("\x1b[1;31;47m"+"Trama de estadistica no enviada"+'\033[0;m')
                            print("\x1b[1;31;47m"+"#############################################"+'\033[0;m')
                            logging.info("No se pudo enviar la trama de estadistica")
                        self.reeconectar_socket(enviado)
                    except Exception as e:
                        print("LeerMinicom.py, linea 378: "+str(e))
                        print(traceback.format_exc())
        except Exception as e:
            print("LeerMinicom.py, linea 380: "+str(e))
            print(traceback.format_exc())