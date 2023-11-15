##########################################
# Autor: Ernesto Lomar
# Fecha de creación: 27/04/2022
# Ultima modificación: 15/08/2022
#
# Script para actualizar la hora de la raspberry usando la sim
# la sim te retorna la hora en formato utc y con la libreria pytz la convertimos en hora local
##########################################

#Importamos librerías externas
import sys

sys.path.insert(1, '/home/pi/Urban_Urbano/utils')
sys.path.insert(1, '/home/pi/Urban_Urbano/minicom')

import subprocess
from comand import Principal_Modem, Comunicacion_Minicom
import pytz
from datetime import datetime
import logging

modem = Principal_Modem()

#Función para convertir la fecha de utc a hora local
def utc_to_local(utc_datetime):
    try:
        print("La hora UTC es: "+utc_datetime)
        tz_eastern = pytz.timezone('UTC')
        tz_mexico = pytz.timezone('America/Mexico_City')
        return tz_eastern.localize(datetime.strptime(str(utc_datetime),'%y/%m/%d,%H:%M:%S')).astimezone(tz_mexico).strftime("%Y/%m/%d %H:%M:%S")
    except Exception as e:
        print(e)
        logging.info(e)

#Función para obtener la hora desde la sim
def obtener_hora_sim():
        try:
            comando = modem.do_command("AT+CCLK?").decode()
            comando = comando.replace("+CCLK: ","")
            comando = comando.rstrip("\r\n")
            comando = comando[:-4]
            comando = comando[1:]
            fecha = utc_to_local(comando)
            return fecha;
        except Exception as e:
            print(e)
            logging.info(e)
            raise ValueError(str(e))

#Toma la fecha y la hora del simulador y establece la fecha y la hora de la Raspberry Pi
def actualizar_hora():
    try:
        print("Actualizando hora ...")
        dt = obtener_hora_sim()
        res = bool(datetime.strptime(dt, "%Y/%m/%d %H:%M:%S"))
        
        if res == False:
            print("##################################################################")
            print("Aparentemente la SIM no cuenta con saldo o no esta bien colocada.")
            print("##################################################################")
            print("Error al actualizar hora por SIM, intentando actualizar hora por GPS...")
            res = Comunicacion_Minicom()
            fecha_gps = str(res['fecha'])
            hora_gps = str(str(res['hora']).split(",")[1]).replace("'","")
            if fecha_gps != "" and hora_gps != "" or fecha_gps != None and hora_gps != None:
                dia = fecha_gps[:2]
                mes = fecha_gps[2:4]
                año = fecha_gps[4:6]
                fecha_completa = año+"/"+mes+"/"+dia
                hora = hora_gps[:3]
                minutos = hora_gps[3:5]
                segundos = hora_gps[5:7]
                hora_completa = hora+":"+minutos+":"+segundos
                hora_gps_local = utc_to_local(str(fecha_completa+","+hora_completa).replace(" ",""))
                if bool(datetime.strptime(hora_gps_local, "%Y/%m/%d %H:%M:%S")):
                    year = int(hora_gps_local[0:4])
                    if year >= 2022:
                        subprocess.call(['sudo', 'timedatectl', 'set-ntp', 'false' ], shell=False)
                        subprocess.call(['sudo','date', '-s', '{:}'.format(str(hora_gps_local))], shell=False)
                        print("Hora actualizada por GPS")
                        print("#####################################")
                        return True
                    else:
                        print("Error al actualizar hora por GPS, no coincide el año...")
                        print("#####################################")
                        return False
                print("Error de conversion de hora GPS")
                print("#####################################")
                return False
            else:
                print(f"Ocurrió el error: {res['error']}")
                return False
            
        year = int(dt[0:4])
        
        if (year < 2022):
            print("##################################################################")
            print("Aparentemente la SIM no cuenta con saldo o no esta bien colocada.")
            print("##################################################################")
            print("Error al actualizar hora por SIM, no coincide el año, intentando actualizar hora por GPS...")
            res = Comunicacion_Minicom()
            fecha_gps = str(res['fecha'])
            hora_gps = str(str(res['hora']).split(",")[1]).replace("'","")
            if fecha_gps != "" and hora_gps != "" or fecha_gps != None and hora_gps != None:
                dia = fecha_gps[:2]
                mes = fecha_gps[2:4]
                año = fecha_gps[4:6]
                fecha_completa = año+"/"+mes+"/"+dia
                hora = hora_gps[:3]
                minutos = hora_gps[3:5]
                segundos = hora_gps[5:7]
                hora_completa = hora+":"+minutos+":"+segundos
                hora_gps_local = utc_to_local(str(fecha_completa+","+hora_completa).replace(" ",""))
                if bool(datetime.strptime(hora_gps_local, "%Y/%m/%d %H:%M:%S")):
                    year = int(hora_gps_local[0:4])
                    if year >= 2022:
                        subprocess.call(['sudo', 'timedatectl', 'set-ntp', 'false' ], shell=False)
                        subprocess.call(['sudo','date', '-s', '{:}'.format(str(hora_gps_local))], shell=False)
                        print("Hora actualizada por GPS")
                        print("#####################################")
                        return True
                    else:
                        print("Error al actualizar hora por GPS, no coincide el año...")
                        print("#####################################")
                        return False
                print("Error de conversion de hora GPS")
                print("#####################################")
                return False
            else:
                print(f"Ocurrió el error: {res['error']}")
                return False
            
        subprocess.call(['sudo', 'timedatectl', 'set-ntp', 'false' ], shell=False)
        subprocess.call(['sudo','date', '-s', '{:}'.format(str(dt))], shell=False)
        print("Hora actualizada por SIM...")
        print("#####################################")
        return True  
    except Exception as e:
        print(e)
        logging.info(e)
        return False
