from datetime import datetime, timedelta
import re
from escpos.printer import Usb
import logging
from time import strftime
import time
from PyQt5.QtCore import QSettings
import variables_globales as vg
import sys
import subprocess

sys.path.insert(1, '/home/pi/Urban_Urbano/db')

from operadores import obtener_operador_por_UID
from ventas_queries import obtener_ultimo_folio_de_item_venta, obtener_total_de_ventas_por_folioviaje
from asignaciones_queries import obtener_asignacion_por_folio_de_viaje, obtener_ultima_asignacion

try:

    def sumar_dos_horas(hora1, hora2):
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
            print("pasaje.py, linea 151: "+str(e))
        
    def imprimir_boleto_normal_con_servicio(ultimo_folio_de_venta, fecha, hora, idUnidad, servicio, tramo, qr):
        try:
            nc='0x04b8'
            ns='0x0e28'

            n_creador_hex = int(nc, 16)
            n_serie_hex = int(ns, 16)

            instancia_impresora = Usb(n_creador_hex, n_serie_hex, 0)
            fecha = str(strftime('%d-%m-%Y')).replace('/', '-')
            settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            instancia_impresora.set(align='center')
            logging.info("Impresora encontrada")
            instancia_impresora.set(align='center')                                                                    
            instancia_impresora.text(f"Folio: {(ultimo_folio_de_venta)}            {fecha} {hora}\n")
            instancia_impresora.text(f"Unidad: {idUnidad}       IMPORTE {qr[6]}:  $ {0}\n")
            instancia_impresora.text(f"Servicio: {servicio}\n")
            tramo_servicio_actual = str(str(tramo).split("-")[0]) + "-" + str(str(servicio).split("-")[2])
            instancia_impresora.text(f"Tramo: {tramo_servicio_actual}\n")
            tipo_de_pasajero = str(qr[6]).lower()
            # Actualizamos el total de folios en el resumen (ticket) de liquidación dependiendo del tipo de pasajero                                      
            if tipo_de_pasajero != "normal":
                
                if tipo_de_pasajero == "estudiante":
                    # Si el pasajero es estudiante actualizamos los datos del settings de info_estudiantes
                    incremento_pasajero = float(settings.value('info_estudiantes').split(",")[0]) + 1
                    incremento_cantidad = float(settings.value('info_estudiantes').split(",")[1])
                    settings.setValue('info_estudiantes', f"{int(incremento_pasajero)},{incremento_cantidad}")
                    
                elif tipo_de_pasajero == "menor":
                    # Si el pasajero es menor actualizamos los datos del settings de info_chicos
                    incremento_pasajero = float(settings.value('info_chicos').split(",")[0]) + 1
                    incremento_cantidad = float(settings.value('info_chicos').split(",")[1])
                    settings.setValue('info_chicos', f"{int(incremento_pasajero)},{incremento_cantidad}")
                    
                elif tipo_de_pasajero == "mayor":
                    # Si el pasajero es mayor actualizamos los datos del settings de info_ad_mayores
                    incremento_pasajero = float(settings.value('info_ad_mayores').split(",")[0]) + 1
                    incremento_cantidad = float(settings.value('info_ad_mayores').split(",")[1])
                    settings.setValue('info_ad_mayores', f"{int(incremento_pasajero)},{incremento_cantidad}")
            else:
                incremento_pasajero = float(settings.value('info_normales').split(",")[0]) + 1
                incremento_cantidad = float(settings.value('info_normales').split(",")[1])
                settings.setValue('info_normales', f"{int(incremento_pasajero)},{incremento_cantidad}")
            instancia_impresora.cut()
            time.sleep(1)
            return True
        except Exception as e:
            print("Sucedio algo al imprimir ticket normal con servicio: "+str(e))
            logging.info(e)
            return False
        
    def imprimir_boleto_normal_sin_servicio(ultimo_folio_de_venta, fecha, hora, idUnidad, tramo, qr):
        try:
            nc='0x04b8'
            ns='0x0e28'

            n_creador_hex = int(nc, 16)
            n_serie_hex = int(ns, 16)

            instancia_impresora = Usb(n_creador_hex, n_serie_hex, 0)
            fecha = str(strftime('%d-%m-%Y')).replace('/', '-')
            hora_actual = strftime('%H:%M:%S')
            settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            instancia_impresora.set(align='center')                                                                    
            instancia_impresora.text(f"Folio: {(ultimo_folio_de_venta)}            {fecha} {hora}\n")
            instancia_impresora.text(f"Unidad: {idUnidad}       IMPORTE {qr[6]}:  $ {0}\n")
            instancia_impresora.text(f"Aparentemente no estas en el servicio correcto\n")
            destino_del_qr = str(str(tramo).split("-")[1])
            instancia_impresora.text(f"No se encontro el destino {destino_del_qr}\n")
            tipo_de_pasajero = str(qr[6]).lower()
            # Actualizamos el total de folios en el resumen (ticket) de liquidación dependiendo del tipo de pasajero                                      
            if tipo_de_pasajero != "normal":
                
                if tipo_de_pasajero == "estudiante":
                    # Si el pasajero es estudiante actualizamos los datos del settings de info_estudiantes
                    incremento_pasajero = float(settings.value('info_estudiantes').split(",")[0]) + 1
                    incremento_cantidad = float(settings.value('info_estudiantes').split(",")[1])
                    settings.setValue('info_estudiantes', f"{int(incremento_pasajero)},{incremento_cantidad}")
                    
                elif tipo_de_pasajero == "menor":
                    # Si el pasajero es menor actualizamos los datos del settings de info_chicos
                    incremento_pasajero = float(settings.value('info_chicos').split(",")[0]) + 1
                    incremento_cantidad = float(settings.value('info_chicos').split(",")[1])
                    settings.setValue('info_chicos', f"{int(incremento_pasajero)},{incremento_cantidad}")
                    
                elif tipo_de_pasajero == "mayor":
                    # Si el pasajero es mayor actualizamos los datos del settings de info_ad_mayores
                    incremento_pasajero = float(settings.value('info_ad_mayores').split(",")[0]) + 1
                    incremento_cantidad = float(settings.value('info_ad_mayores').split(",")[1])
                    settings.setValue('info_ad_mayores', f"{int(incremento_pasajero)},{incremento_cantidad}")
            else:
                incremento_pasajero = float(settings.value('info_normales').split(",")[0]) + 1
                incremento_cantidad = float(settings.value('info_normales').split(",")[1])
                settings.setValue('info_normales', f"{int(incremento_pasajero)},{incremento_cantidad}")
            instancia_impresora.cut()
            time.sleep(1)
            return True
        except Exception as e:
            print("Sucedio algo al imprimir ticket normal sin servicio: "+str(e))
            logging.info(e)
            return False

    def imprimir_boleto_normal_pasaje(folio, fecha, hora, unidad, tipo_pasajero, importe, servicio, tramo):
        try:
            nc='0x04b8'
            ns='0x0e28'

            n_creador_hex = int(nc, 16)
            n_serie_hex = int(ns, 16)

            instancia_impresora = Usb(n_creador_hex, n_serie_hex, 0)
            fecha = str(strftime('%d-%m-%Y')).replace('/', '-')
            instancia_impresora.set(align='center')
            logging.info("Impresora encontrada")
            instancia_impresora.text(f"Folio: {folio}            {fecha} {hora}\n")
            instancia_impresora.text(f"Unidad: {unidad}       IMPORTE {tipo_pasajero}:  $ {importe}\n")
            instancia_impresora.text(f"Servicio: {servicio}\n")
            instancia_impresora.text(f"Tramo: {tramo}\n")
            instancia_impresora.cut()
            time.sleep(1)
            return True
        except Exception as e:
            print(e)
            logging.info(e)
            return False
    
    def imprimir_boleto_con_qr_pasaje(folio, fecha, hora, unidad, tipo_pasajero, importe, servicio, tramo, servicio_o_transbordo):
        try:
            nc='0x04b8'
            ns='0x0e28'

            n_creador_hex = int(nc, 16)
            n_serie_hex = int(ns, 16)

            instancia_impresora = Usb(n_creador_hex, n_serie_hex, 0)
            fecha = str(strftime('%d-%m-%Y')).replace('/', '-')
            instancia_impresora.set(align='center')
            logging.info("Impresora encontrada")
            instancia_impresora.text(f"Folio: {folio}            {fecha} {hora}\n")
            instancia_impresora.text(f"Unidad: {unidad}       IMPORTE {tipo_pasajero}:  $ {importe}\n")
            instancia_impresora.text(f"Servicio: {servicio}\n")
            instancia_impresora.text(f"Tramo: {tramo}\n")
            if 'NE' in servicio_o_transbordo[8]:
                unidad_a_transbordar = str(str(servicio_o_transbordo[7]).split("_")[0]).replace("'", "")
                instancia_impresora.text(f"Transbordar unidad en: {unidad_a_transbordar}\n")
                estimado = "02:00:00"
                hora_antes_de = sumar_dos_horas(hora, estimado)
                instancia_impresora.text(f"Antes de {fecha} {hora_antes_de}\n")
                instancia_impresora.qr(f"{fecha},{hora_antes_de},{unidad},{importe},{servicio},{tramo},{tipo_pasajero},{'st'},{unidad_a_transbordar}",0, 5)
                instancia_impresora.cut()
                time.sleep(1)
                return True
            else:
                unidad_a_transbordar1 = str(str(servicio_o_transbordo[7]).split("_")[0]).replace("'", "")
                unidad_a_transbordar2 = str(str(servicio_o_transbordo[8]).split("_")[0]).replace("'", "")
                instancia_impresora.text(f"Transbordar unidad en: {unidad_a_transbordar1}\n")
                instancia_impresora.text(f"Luego transbordar unidad en: {unidad_a_transbordar2}\n")
                estimado = "02:00:00"
                hora_antes_de = sumar_dos_horas(hora, estimado)
                instancia_impresora.text(f"Antes de {fecha} {hora_antes_de}\n")
                instancia_impresora.qr(f"{fecha},{hora_antes_de},{unidad},{importe},{servicio},{tramo},{tipo_pasajero},{'ct'},{unidad_a_transbordar1},{unidad_a_transbordar2}",0, 5)
                instancia_impresora.cut()
                time.sleep(1)
                return True
        except Exception as e:
            print(e)
            logging.info(e)
            return False
        
    def imprimir_ticket_de_corte(idUnidad, imprimir):
        try:
            settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
            if len(str(vg.fecha_actual)) > 0:
                fecha = str(vg.fecha_actual).replace('/', '-')
            else:
                fecha = subprocess.check_output(['date', '+%d-%m-%Y']).decode().strip()
            total_a_liquidar_bd = 0.0
            total_de_boletos_db = ""
            
            ultima_venta_bd = obtener_ultimo_folio_de_item_venta()
            print("Ultima venta en la base de datos es: "+str(ultima_venta_bd))
            logging.info(f"Ultima venta en la base de datos es: {ultima_venta_bd}")
            
            if (len(settings.value('folio_de_viaje')) != 0):
                total_de_boletos_db = obtener_total_de_ventas_por_folioviaje(settings.value('folio_de_viaje'))
            elif (len(vg.folio_asignacion) != 0):
                total_de_boletos_db = obtener_total_de_ventas_por_folioviaje(vg.folio_asignacion)
            
            if len(total_de_boletos_db) != 0:
                
                print("El tamaño de boletos en la base de datos es: "+str(len(total_de_boletos_db)))
                logging.info(f"El total de boletos en la base de datos es: {len(total_de_boletos_db)}")
                
                # Procedemos a hacer la suma de la liquidación de la base de datos.   
                for p in range(len(total_de_boletos_db)):
                    total_a_liquidar_bd = total_a_liquidar_bd + float(total_de_boletos_db[p][11])
                print("BD - El total a liquidar es: "+str(total_a_liquidar_bd))
                logging.info(f"BD - El total a liquidar es: {total_a_liquidar_bd}")

                # Procedemos a hacer la suma de la liquidación de los contadores del init.
                total_de_folio_aforo_efectivo = int(settings.value('info_estudiantes').split(',')[0]) + int(settings.value('info_normales').split(',')[0]) + int(settings.value('info_chicos').split(',')[0]) + int(settings.value('info_ad_mayores').split(',')[0])
                print("El total de boletos en el aforo es: "+str(total_de_folio_aforo_efectivo))
                logging.info(f"El total de boletos en el aforo es: {total_de_folio_aforo_efectivo}")
                
                # Revisamos si existe una ultima venta en la base de datos.
                if ultima_venta_bd != None:
                    
                    print("Ultima folio de venta en la bd: "+str(ultima_venta_bd[1]))
                    logging.info(f"Ultima folio de venta en la bd: {ultima_venta_bd[1]}")
                    
                    # Verificamos si el total de folios de la base de datos es diferente a los contadores.
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
                else:
                    print("No existe ninguna venta en la base de datos")
                    logging.info("No existe ninguna venta en la base de datos")
                    ultima_venta_bd = [0,0]
                    total_de_folio_aforo_efectivo = 0
                
                # Creamos la conexión con la impresora térmica.
                nc='0x04b8'
                ns='0x0e28'
                n_creador_hex = int(nc, 16)
                n_serie_hex = int(ns, 16)
                instancia_impresora = Usb(n_creador_hex, n_serie_hex, 0)
                hora_actual = vg.hora_actual
                instancia_impresora.set(align='center')
                logging.info("Impresora encontrada")
                
                '''
                if len(settings.value('folio_de_viaje')) > 0:
                    trama_dos_del_viaje = obtener_asignacion_por_folio_de_viaje(settings.value('folio_de_viaje'))
                else:
                    trama_dos_del_viaje = obtener_asignacion_por_folio_de_viaje(vg.folio_asignacion)'''
                    
                try:
                    trama_dos_del_viaje = obtener_ultima_asignacion()
                    print("La ultima asignacion es: ", trama_dos_del_viaje)
                except Exception as e:
                    print("Ocurrió un error al obtener la ultima asignacion: ", e)
                
                try:
                    # Hacemos la impresión de los dos tickets de liquidación.
                    for i in range(2):
                        
                        #GENERAL
                        instancia_impresora.text("GENERAL\n")
                        instancia_impresora.text(f"Fv: {trama_dos_del_viaje[6]}  Sw: {vg.version_del_software}\n")
                        instancia_impresora.text(f"Ultimo folio: {ultima_venta_bd[1]}\n")
                        instancia_impresora.text(f"Unidad: {idUnidad}    Serv: {settings.value('servicio')}\n")
                        instancia_impresora.text(f"Estud:        {str(settings.value('info_estudiantes')).split(',')[0]}  $       {str(settings.value('info_estudiantes')).split(',')[1]}\n")
                        instancia_impresora.text(f"Normal:       {str(settings.value('info_normales')).split(',')[0]}  $       {str(settings.value('info_normales')).split(',')[1]}\n")
                        instancia_impresora.text(f"Menor:        {str(settings.value('info_chicos')).split(',')[0]}  $       {str(settings.value('info_chicos')).split(',')[1]}\n")
                        instancia_impresora.text(f"Ad.May:       {str(settings.value('info_ad_mayores')).split(',')[0]}  $       {str(settings.value('info_ad_mayores')).split(',')[1]}\n")
                        instancia_impresora.text(f"Total a liquidar: $ {total_a_liquidar_bd}\n")
                        instancia_impresora.text(f"Total de folios: {total_de_folio_aforo_efectivo}\n")
                        instancia_impresora.text("\n")
                        
                        #INICIO DE VIAJE
                        instancia_impresora.text("INICIO DE VIAJE\n")
                        inicio_de_viaje_a_mostrar = str(trama_dos_del_viaje[4]) + " " + str(trama_dos_del_viaje[5])
                        instancia_impresora.text(f"Fecha y hora: {inicio_de_viaje_a_mostrar}\n")
                        
                        # Hacemos varias verificaciones para poder mostrar el nombre y numero de empleado en el ticket.
                        if len(vg.nombre_de_operador_inicio) > 0:
                            if len(vg.numero_de_operador_inicio) > 0:
                                instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio} {vg.nombre_de_operador_inicio}\n")
                            else:
                                operador = None
                                if len(settings.value('numero_de_operador_inicio')) != 0:
                                    instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')} {vg.nombre_de_operador_inicio}\n")
                                elif len(settings.value('csn_chofer')) != 0:
                                    operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                    if operador != None:
                                        instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {vg.nombre_de_operador_inicio}\n")
                                elif len(vg.csn_chofer) != 0:
                                    operador = obtener_operador_por_UID(vg.csn_chofer)
                                    if operador != None:
                                        instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {vg.nombre_de_operador_inicio}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {vg.nombre_de_operador_inicio}\n")
                        else:
                            if len(settings.value('nombre_de_operador_inicio')) != 0:
                                if len(vg.numero_de_operador_inicio) > 0:
                                    instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio} {settings.value('nombre_de_operador_inicio')}\n")
                                else:
                                    operador = None
                                    if len(settings.value('numero_de_operador_inicio')) != 0:
                                        instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')} {settings.value('nombre_de_operador_inicio')}\n")
                                    elif len(settings.value('csn_chofer')) != 0:
                                        operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                        if operador != None:
                                            instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                        else:
                                            instancia_impresora.text(f"Quien abrio: {settings.value('nombre_de_operador_inicio')}\n")
                                    elif len(vg.csn_chofer) != 0:
                                        operador = obtener_operador_por_UID(vg.csn_chofer)
                                        if operador != None:
                                            instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                        else:
                                            instancia_impresora.text(f"Quien abrio: {settings.value('nombre_de_operador_inicio')}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {settings.value('nombre_de_operador_inicio')}\n")
                            elif len(vg.numero_de_operador_inicio) > 0:
                                operador = None
                                if len(settings.value('csn_chofer')) != 0:
                                    operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                    if operador != None:
                                        instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio}\n")
                                elif len(vg.csn_chofer) != 0:
                                    operador = obtener_operador_por_UID(vg.csn_chofer)
                                    if operador != None:
                                        instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio}\n")
                            elif len(settings.value('numero_de_operador_inicio')) > 0:
                                operador = None
                                if len(settings.value('csn_chofer')) != 0:
                                    operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                    if operador != None:
                                        instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')}\n")
                                elif len(vg.csn_chofer) != 0:
                                    operador = obtener_operador_por_UID(vg.csn_chofer)
                                    if operador != None:
                                        instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')}\n")
                            elif len(settings.value('csn_chofer')) != 0:
                                operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                if operador != None:
                                    instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: ----------\n")
                            elif len(vg.csn_chofer) != 0:
                                operador = obtener_operador_por_UID(vg.csn_chofer)
                                if operador != None:
                                    instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: ----------\n")
                            else:
                                instancia_impresora.text(f"Quien abrio: ----------\n")
                        
                        operador = None
                        instancia_impresora.text("\n")
                        
                        #FIN DE VIAJE
                        instancia_impresora.text("FIN DE VIAJE\n")
                        instancia_impresora.text(f"Fecha y hora (impresion): {fecha} {hora_actual}\n")
                        # Hacemos varias verificaciones para poder mostrar el nombre y numero de empleado en el ticket.
                        if len(vg.nombre_de_operador_final) > 0:
                            if len(vg.numero_de_operador_final) > 0:
                                instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final} {vg.nombre_de_operador_final}\n")
                            else:
                                operador = None
                                if len(settings.value('numero_de_operador_final')) != 0:
                                    instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')} {vg.nombre_de_operador_final}\n")
                                elif len(settings.value('csn_chofer')) != 0:
                                    operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                    if operador != None:
                                        instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {vg.nombre_de_operador_final}\n")
                                elif len(vg.csn_chofer) != 0:
                                    operador = obtener_operador_por_UID(vg.csn_chofer)
                                    if operador != None:
                                        instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {vg.nombre_de_operador_final}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {vg.nombre_de_operador_final}\n")
                        else:
                            if len(settings.value('nombre_de_operador_final')) != 0:
                                if len(vg.numero_de_operador_final) > 0:
                                    instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final} {settings.value('nombre_de_operador_final')}\n")
                                else:
                                    operador = None
                                    if len(settings.value('numero_de_operador_final')) != 0:
                                        instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')} {settings.value('nombre_de_operador_final')}\n")
                                    elif len(settings.value('csn_chofer')) != 0:
                                        operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                        if operador != None:
                                            instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                        else:
                                            instancia_impresora.text(f"Quien cerro: {settings.value('nombre_de_operador_final')}\n")
                                    elif len(vg.csn_chofer) != 0:
                                        operador = obtener_operador_por_UID(vg.csn_chofer)
                                        if operador != None:
                                            instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                        else:
                                            instancia_impresora.text(f"Quien cerro: {settings.value('nombre_de_operador_final')}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {settings.value('nombre_de_operador_final')}\n")
                            elif len(vg.numero_de_operador_final) > 0:
                                operador = None
                                if len(settings.value('csn_chofer')) != 0:
                                    operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                    if operador != None:
                                        instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final}\n")
                                elif len(vg.csn_chofer) != 0:
                                    operador = obtener_operador_por_UID(vg.csn_chofer)
                                    if operador != None:
                                        instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final}\n")
                            elif len(settings.value('numero_de_operador_final')) > 0:
                                operador = None
                                if len(settings.value('csn_chofer')) != 0:
                                    operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                    if operador != None:
                                        instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')}\n")
                                elif len(vg.csn_chofer) != 0:
                                    operador = obtener_operador_por_UID(vg.csn_chofer)
                                    if operador != None:
                                        instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')}\n")
                            elif len(settings.value('csn_chofer')) != 0:
                                operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                if operador != None:
                                    instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: ----------\n")
                            elif len(vg.csn_chofer) != 0:
                                operador = obtener_operador_por_UID(vg.csn_chofer)
                                if operador != None:
                                    instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: ----------\n")
                            else:
                                instancia_impresora.text(f"Quien cerro: ----------\n")
                        instancia_impresora.cut()
                        logging.info(f"Tickets de corte impresos correctamente.")
                    return True
                except Exception as e:
                    print("Ocurrió algo al hacer la impresión de los tickets de liquidaciónA: ", str(e))
                    logging.info("Ocurrió algo al hacer la impresión de los tickets de liquidación")
            else:
                # Creamos la conexión con la impresora térmica.
                nc='0x04b8'
                ns='0x0e28'
                n_creador_hex = int(nc, 16)
                n_serie_hex = int(ns, 16)
                instancia_impresora = Usb(n_creador_hex, n_serie_hex, 0)
                hora_actual = vg.hora_actual
                instancia_impresora.set(align='center')
                logging.info("Impresora encontrada")
                
                try:
                    trama_dos_del_viaje = obtener_ultima_asignacion()
                    print("La ultima asignacion es: ", trama_dos_del_viaje)
                except Exception as e:
                    print("Ocurrió un error al obtener la ultima asignacion: ", e)
                
                for i in range(2):
                    
                    # GENERAL
                    instancia_impresora.text("General:")
                    instancia_impresora.text(f"Fv: {trama_dos_del_viaje[6]}  Sw: {vg.version_del_software}\n")
                    instancia_impresora.text(f"Ultimo folio: 0\n")
                    instancia_impresora.text(f"Unidad: {idUnidad}    Serv: {settings.value('servicio')}\n")
                    instancia_impresora.text(f"Estud:        {str(settings.value('info_estudiantes')).split(',')[0]}  $       {str(settings.value('info_estudiantes')).split(',')[1]}\n")
                    instancia_impresora.text(f"Normal:       {str(settings.value('info_normales')).split(',')[0]}  $       {str(settings.value('info_normales')).split(',')[1]}\n")
                    instancia_impresora.text(f"Menor:        {str(settings.value('info_chicos')).split(',')[0]}  $       {str(settings.value('info_chicos')).split(',')[1]}\n")
                    instancia_impresora.text(f"Ad.May:       {str(settings.value('info_ad_mayores')).split(',')[0]}  $       {str(settings.value('info_ad_mayores')).split(',')[1]}\n")
                    instancia_impresora.text(f"Total a liquidar: $ {total_a_liquidar_bd}\n")
                    instancia_impresora.text(f"Total de folios: 0\n")
                    instancia_impresora.text("\n")
                    
                    #INICIO DE VIAJE
                    instancia_impresora.text("INICIO DE VIAJE\n")
                    inicio_de_viaje_a_mostrar = str(trama_dos_del_viaje[4]) + " " + str(trama_dos_del_viaje[5])
                    instancia_impresora.text(f"Fecha y hora: {inicio_de_viaje_a_mostrar}\n")
                    # Hacemos varias verificaciones para poder mostrar el nombre y numero de empleado en el ticket.
                    if len(vg.nombre_de_operador_inicio) > 0:
                        if len(vg.numero_de_operador_inicio) > 0:
                            instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio} {vg.nombre_de_operador_inicio}\n")
                        else:
                            operador = None
                            if len(settings.value('numero_de_operador_inicio')) != 0:
                                instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')} {vg.nombre_de_operador_inicio}\n")
                            elif len(settings.value('csn_chofer')) != 0:
                                operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                if operador != None:
                                    instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {vg.nombre_de_operador_inicio}\n")
                            elif len(vg.csn_chofer) != 0:
                                operador = obtener_operador_por_UID(vg.csn_chofer)
                                if operador != None:
                                    instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {vg.nombre_de_operador_inicio}\n")
                            else:
                                instancia_impresora.text(f"Quien abrio: {vg.nombre_de_operador_inicio}\n")
                    else:
                        if len(settings.value('nombre_de_operador_inicio')) != 0:
                            if len(vg.numero_de_operador_inicio) > 0:
                                instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio} {settings.value('nombre_de_operador_inicio')}\n")
                            else:
                                operador = None
                                if len(settings.value('numero_de_operador_inicio')) != 0:
                                    instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')} {settings.value('nombre_de_operador_inicio')}\n")
                                elif len(settings.value('csn_chofer')) != 0:
                                    operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                    if operador != None:
                                        instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {settings.value('nombre_de_operador_inicio')}\n")
                                elif len(vg.csn_chofer) != 0:
                                    operador = obtener_operador_por_UID(vg.csn_chofer)
                                    if operador != None:
                                        instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien abrio: {settings.value('nombre_de_operador_inicio')}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {settings.value('nombre_de_operador_inicio')}\n")
                        elif len(vg.numero_de_operador_inicio) > 0:
                            operador = None
                            if len(settings.value('csn_chofer')) != 0:
                                operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                if operador != None:
                                    instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio}\n")
                            elif len(vg.csn_chofer) != 0:
                                operador = obtener_operador_por_UID(vg.csn_chofer)
                                if operador != None:
                                    instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio}\n")
                            else:
                                instancia_impresora.text(f"Quien abrio: {vg.numero_de_operador_inicio}\n")
                        elif len(settings.value('numero_de_operador_inicio')) > 0:
                            operador = None
                            if len(settings.value('csn_chofer')) != 0:
                                operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                if operador != None:
                                    instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')}\n")
                            elif len(vg.csn_chofer) != 0:
                                operador = obtener_operador_por_UID(vg.csn_chofer)
                                if operador != None:
                                    instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')}\n")
                            else:
                                instancia_impresora.text(f"Quien abrio: {settings.value('numero_de_operador_inicio')}\n")
                        elif len(settings.value('csn_chofer')) != 0:
                            operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                            if operador != None:
                                instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                            else:
                                instancia_impresora.text(f"Quien abrio: ----------\n")
                        elif len(vg.csn_chofer) != 0:
                            operador = obtener_operador_por_UID(vg.csn_chofer)
                            if operador != None:
                                instancia_impresora.text(f"Quien abrio: {operador[1]} {operador[2]}\n")
                            else:
                                instancia_impresora.text(f"Quien abrio: ----------\n")
                        else:
                            instancia_impresora.text(f"Quien abrio: ----------\n")
                    
                    operador = None
                    instancia_impresora.text("\n")
                    
                    #FIN DE VIAJE
                    instancia_impresora.text("FIN DE VIAJE\n")
                    instancia_impresora.text(f"Fecha y hora (impresion): {fecha} {hora_actual}\n")
                    # Hacemos varias verificaciones para poder mostrar el nombre y numero de empleado en el ticket.
                    if len(vg.nombre_de_operador_final) > 0:
                        if len(vg.numero_de_operador_final) > 0:
                            instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final} {vg.nombre_de_operador_final}\n")
                        else:
                            operador = None
                            if len(settings.value('numero_de_operador_final')) != 0:
                                instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')} {vg.nombre_de_operador_final}\n")
                            elif len(settings.value('csn_chofer')) != 0:
                                operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                if operador != None:
                                    instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {vg.nombre_de_operador_final}\n")
                            elif len(vg.csn_chofer) != 0:
                                operador = obtener_operador_por_UID(vg.csn_chofer)
                                if operador != None:
                                    instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {vg.nombre_de_operador_final}\n")
                            else:
                                instancia_impresora.text(f"Quien cerro: {vg.nombre_de_operador_final}\n")
                    else:
                        if len(settings.value('nombre_de_operador_final')) != 0:
                            if len(vg.numero_de_operador_final) > 0:
                                instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final} {settings.value('nombre_de_operador_final')}\n")
                            else:
                                operador = None
                                if len(settings.value('numero_de_operador_final')) != 0:
                                    instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')} {settings.value('nombre_de_operador_final')}\n")
                                elif len(settings.value('csn_chofer')) != 0:
                                    operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                    if operador != None:
                                        instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {settings.value('nombre_de_operador_final')}\n")
                                elif len(vg.csn_chofer) != 0:
                                    operador = obtener_operador_por_UID(vg.csn_chofer)
                                    if operador != None:
                                        instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                    else:
                                        instancia_impresora.text(f"Quien cerro: {settings.value('nombre_de_operador_final')}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {settings.value('nombre_de_operador_final')}\n")
                        elif len(vg.numero_de_operador_final) > 0:
                            operador = None
                            if len(settings.value('csn_chofer')) != 0:
                                operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                if operador != None:
                                    instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final}\n")
                            elif len(vg.csn_chofer) != 0:
                                operador = obtener_operador_por_UID(vg.csn_chofer)
                                if operador != None:
                                    instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final}\n")
                            else:
                                instancia_impresora.text(f"Quien cerro: {vg.numero_de_operador_final}\n")
                        elif len(settings.value('numero_de_operador_final')) > 0:
                            operador = None
                            if len(settings.value('csn_chofer')) != 0:
                                operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                                if operador != None:
                                    instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')}\n")
                            elif len(vg.csn_chofer) != 0:
                                operador = obtener_operador_por_UID(vg.csn_chofer)
                                if operador != None:
                                    instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                                else:
                                    instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')}\n")
                            else:
                                instancia_impresora.text(f"Quien cerro: {settings.value('numero_de_operador_final')}\n")
                        elif len(settings.value('csn_chofer')) != 0:
                            operador = obtener_operador_por_UID(settings.value('csn_chofer'))
                            if operador != None:
                                instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                            else:
                                instancia_impresora.text(f"Quien cerro: ----------\n")
                        elif len(vg.csn_chofer) != 0:
                            operador = obtener_operador_por_UID(vg.csn_chofer)
                            if operador != None:
                                instancia_impresora.text(f"Quien cerro: {operador[1]} {operador[2]}\n")
                            else:
                                instancia_impresora.text(f"Quien cerro: ----------\n")
                        else:
                            instancia_impresora.text(f"Quien cerro: ----------\n")
                    instancia_impresora.cut()
                    logging.info(f"Tickets de corte impresos correctamente.")
                return True
        except Exception as e:
            print(e)
            logging.info(e)
            if imprimir:
                return False
            else:
                return True
except Exception as e:
    print("No hubo comunicacion con impresora")