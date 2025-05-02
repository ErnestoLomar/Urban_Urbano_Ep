from glob import glob
import RPi.GPIO as GPIO
import serial
import time
import os
import subprocess
import time
import base64
import sys
import glob
import shutil
from time import strftime

sys.path.insert(1, '/home/pi/Urban_Urbano/db')
sys.path.insert(1, '/home/pi/Urban_Urbano/utils')

from queries import obtener_datos_aforo, insertar_estadisticas_boletera
import variables_globales

##########################################################################################################################################
#INICIAMOS COMUNICACIoN POR LOS PUERTOS Y ACTIVAMOS LOS GPIO NECESARIOS
try:
    ser = serial.Serial('/dev/serial0',115200,timeout=1)
    time.sleep(0.3)
    ser.flushInput()
    ser.flushOutput()
    time.sleep(0.3)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(12, GPIO.OUT)
    time.sleep(2)
    GPIO.setup(31, GPIO.OUT)
    GPIO.setup(35, GPIO.OUT)
    GPIO.output(31, False)
    GPIO.output(35, True)
    print("QUECTEL INICIADO CORRECTAMENTE")
except:
    print("No se pudo comunicar con el minicom")
    
#configuracion FTP Azure
cuenta_azure = "\"account\""
usuario_FTP_azure = "\"Bolftp\""
contra_FTP_azure = "\"vXW4N3$hp@\""
host_FTP_azure = "\"44.224.205.143\""
conf_conexion_FTP_azure = "AT+QFTPCFG="+cuenta_azure+","+usuario_FTP_azure+","+contra_FTP_azure
conexion_FTP_azure = "AT+QFTPOPEN="+host_FTP_azure+",22"

#configuracion FTP webhost
cuenta_webhost = "\"account\""
usuario_FTP_webhost = "\"daslom\""
contra_FTP_webhost = "\"geforceGTX\""
host_FTP_webhost = "\"files.000webhost.com\""
conf_conexion_FTP_webhost = "AT+QFTPCFG="+cuenta_webhost+","+usuario_FTP_webhost+","+contra_FTP_webhost
conexion_FTP_webhost = "AT+QFTPOPEN="+host_FTP_webhost+",21"

contador = 1
id_Unidad = str(obtener_datos_aforo()[1])
nombre = ""
ubicacion = ""
version_MT = ""
tipo = ""
intentos_actualizacion = 0

datos_de_la_unidad = obtener_datos_aforo()

intentos_ftp = 0

##########################################################################################################################################
class Principal_Modem: 

        def reiniciar_SIM(self):
            try:
                print("\n#####################################")
                ser.readline()
                ser.readline()
                ser.flushInput()
                ser.flushOutput()
                comando = "AT+QFUN=5\r\n"
                ser.write(comando.encode())
                print(ser.readline())
                time.sleep(5)
                respuesta = ser.readline()
                if 'OK' in respuesta.decode():
                    print("Apagando SIM...")
                    print(respuesta)
                    ser.flushInput()
                    ser.flushOutput()
                else:
                    print("No se pudo inicializar AT+QFUN=5")
                    print(respuesta)
                    time.sleep(2)
                    #self.reiniciar_SIM()
                print("#####################################\n")

                time.sleep(5)

                ser.flushInput()
                ser.flushOutput()
                comando = "AT+QFUN=6\r\n"
                ser.readline()
                ser.write(comando.encode())
                print(ser.readline())
                time.sleep(5)
                respuesta = ser.readline()
                if 'OK' in respuesta.decode():
                    print("Encendiendo SIM...")
                    print(respuesta)
                    ser.flushInput()
                    ser.flushOutput()
                else:
                    print("No se pudo inicializar AT+QFUN=6")
                    print(respuesta)
                    time.sleep(2)
                    #self.reiniciar_SIM()

                time.sleep(5)
                print("#####################################\n")
            except Exception as e:
                print("comand.py, linea 311: "+str(e))

        def inicializar_configuraciones_quectel(self):
            ###########################
            ######   Ernesto   ########
            ###########################
            try:
                print("\x1b[1;32m"+"#####################################")
                ser.readline()
                ser.readline()
                ser.flushInput()
                ser.flushOutput()
                comando = "AT+CPIN?\r\n"
                ser.write(comando.encode())
                i = 0
                while True:    
                    respuesta = ser.readline()
                    print(respuesta.decode())
                    if 'READY' in respuesta.decode() or 'OK' in respuesta.decode():
                        ser.flushInput()
                        ser.flushOutput()
                        break
                    elif i == 5 or 'ERROR' in respuesta.decode():
                        print("\x1b[1;33m"+"No se pudo inicializar AT+CPIN")
                        time.sleep(1)
                        break
                    i = i + 1
                    time.sleep(.5)
                print("\x1b[1;32m"+"#####################################\n")
                
                comando = "AT+CREG?\r\n"
                ser.readline()
                ser.write(comando.encode())
                i = 0
                while True:    
                    respuesta = ser.readline()
                    print(respuesta.decode())
                    if ',1' in respuesta.decode() or ',5' in respuesta.decode() or 'OK' in respuesta.decode():
                        ser.flushInput()
                        ser.flushOutput()
                        break
                    elif i == 5 or 'ERROR' in respuesta.decode():
                        print("No se pudo inicializar AT+CREG?")
                        time.sleep(1)
                        break
                    i = i + 1
                    time.sleep(.5)
                print("\x1b[1;32m"+"#####################################\n")
                
                ser.flushInput()
                ser.flushOutput()
                comando = "AT+CGREG?\r\n"
                ser.readline()
                ser.write(comando.encode())
                i = 0
                while True:    
                    respuesta = ser.readline()
                    print(respuesta.decode())
                    if ',1' in respuesta.decode() or ',5' in respuesta.decode() or 'OK' in respuesta.decode():
                        ser.flushInput()
                        ser.flushOutput()
                        break
                    elif i == 5 or 'ERROR' in respuesta.decode():
                        print("\x1b[1;33m"+"No se pudo inicializar AT+CGREG?")
                        time.sleep(.5)
                        break
                    i = i + 1
                    time.sleep(1)
                print("\x1b[1;32m"+"#####################################\n")
                
                ser.flushInput()
                ser.flushOutput()
                comando = "AT+CCID\r\n"
                ser.readline()
                ser.write(comando.encode())
                i = 0
                while True:    
                    respuesta = ser.readline()
                    print(respuesta.decode())
                    if '+CCID:' in respuesta.decode():
                        print(respuesta)
                        print(str(respuesta.decode()).replace("+CCID","").replace(" ","").replace("\r\n","").replace(":","").replace("AT",""))
                        variables_globales.sim_id = str(respuesta.decode()).replace("+CCID","").replace(" ","").replace(":","").replace("\r\n","")
                        respuesta = ser.readline()
                        print(respuesta)
                        respuesta = ser.readline()
                        print(respuesta)
                        ser.flushInput()
                        ser.flushOutput()
                        break
                    elif i == 10 or 'ERROR' in respuesta.decode():
                        print("\x1b[1;33m"+"No se pudo inicializar AT+CGREG?")
                        time.sleep(1)
                        break
                    i = i + 1
                    time.sleep(.5)
                print("#####################################\n")

                ser.flushInput()
                ser.flushOutput()
                comando = "AT+QICSGP=1,1,\"internet.itelcel.com\",\"\",\"\",1\r\n"
                ser.readline()
                ser.write(comando.encode())
                i = 0
                while True:    
                    respuesta = ser.readline()
                    print(respuesta.decode())
                    if 'OK' in respuesta.decode():
                        ser.flushInput()
                        ser.flushOutput()
                        break
                    elif i == 10 or 'ERROR' in respuesta.decode():
                        print("\x1b[1;33m"+"No se pudo inicializar AT+QICSGP")
                        time.sleep(1)
                        break
                    i = i + 1
                    time.sleep(1)
                print("\x1b[1;32m"+"#####################################\n")

                ser.flushInput()
                ser.flushOutput()
                comando = "AT+QIACT=1\r\n"
                ser.readline()
                ser.write(comando.encode())
                i = 0
                while True:    
                    respuesta = ser.readline()
                    print(respuesta.decode())
                    if 'OK' in respuesta.decode():
                        ser.flushInput()
                        ser.flushOutput()
                        break
                    elif i == 10 or 'ERROR' in respuesta.decode():
                        print("\x1b[1;33m"+"No se pudo inicializar AT+QIACT=1")
                        time.sleep(1)
                        break
                    i = i + 1
                    time.sleep(1)
                print("\x1b[1;32m"+"#####################################")
                
                print("Procedemos a iniciar sesión del GPS")
                ser.flushInput()
                ser.flushOutput()
                comando = "AT+QGPS=1\r\n"
                ser.readline()
                ser.write(comando.encode())
                print(ser.readline())
                time.sleep(1)
                respuesta = ser.readline()
                print("Respuesta: "+str(respuesta))
                respuesta = ser.readline()
                print("Respuesta: "+str(respuesta))
                respuesta = ser.readline()
                print("Respuesta: "+str(respuesta))
                print("#####################################")
                
                ser.flushInput()
                ser.flushOutput()
                comando = "AT+QGPS=1\r\n"
                ser.readline()
                ser.write(comando.encode())
                print(ser.readline())
                time.sleep(1)
                respuesta = ser.readline()
                print("Respuesta: "+str(respuesta))
                respuesta = ser.readline()
                print("Respuesta: "+str(respuesta))
                respuesta = ser.readline()
                print("Respuesta: "+str(respuesta))
                print("#####################################")
            except Exception as e:
                print("FTP.py, linea 171, Error al inicializar SIM: "+str(e))
        
        global verificar_memoria_UFS
        def verificar_memoria_UFS(version_matriz):
            
            try:
                global id_Unidad
                ser.flushInput()
                ser.flushOutput()
                print(ser.readline())
                Aux = ser.readline()
                print(Aux.decode())
                Aux = ser.readline()
                print(Aux.decode())
                
                intentos_eliminar_ufs = 0
                sin_archivos_por_eliminar = False
                
                while True:
                    
                    verificar_archivos = "AT+QFLST=\"*\"\r\n"
                    ser.write(verificar_archivos.encode())
                    
                    time.sleep(.5)
                    
                    for i in range(3):
                        
                        if i >= 2:
                            sin_archivos_por_eliminar = True
                            
                        time.sleep(.3)
                        
                        print("Archivos en quectel:-----------------------------")
                        Aux = ser.readline()
                        print(Aux)
                        
                        if 'update.txt' in Aux.decode():
                            print("Ya existe el archivo update.txt en quectel, procede a eliminarse...")
                            eliminar_archivos = "AT+QFDEL=\"update.txt\"\r\n"
                            ser.write(eliminar_archivos.encode())
                            print(ser.readline())
                            Aux = ser.readline()
                            print(Aux.decode())
                            Aux = ser.readline()
                            print(Aux.decode())
                            sin_archivos_por_eliminar = False
                        if f'{id_Unidad}' in Aux.decode():
                            print(f"Ya existe el archivo {id_Unidad}.txt en quectel, procede a elminarse...")
                            print(ser.readline())
                            Aux = ser.readline()
                            print(Aux.decode())
                            eliminar_archivos = f"AT+QFDEL=\"{id_Unidad}.txt\"\r\n"
                            ser.write(eliminar_archivos.encode())
                            print(ser.readline())
                            Aux = ser.readline()
                            print(Aux.decode())
                            Aux = ser.readline()
                            print(Aux.decode())
                            sin_archivos_por_eliminar = False
                        if f'{version_matriz}' in Aux.decode():
                            print(f"Ya existe el archivo {version_matriz}.txt en quectel, procede a eliminarse...")
                            eliminar_archivos = f"AT+QFDEL=\"{version_matriz}.txt\"\r\n"
                            ser.write(eliminar_archivos.encode())
                            print(ser.readline())
                            Aux = ser.readline()
                            print(Aux.decode())
                            Aux = ser.readline()
                            print(Aux.decode())
                            sin_archivos_por_eliminar = False
                        
                        
                    intentos_eliminar_ufs += 1
                    
                    if intentos_eliminar_ufs >= 3 and not sin_archivos_por_eliminar:
                        print("No se eliminaron todos los archivos correctamente...")
                        break
                    elif sin_archivos_por_eliminar:
                        print("No hay archivos por eliminar")
                        break

                if os.path.exists('/home/pi/update.txt'):
                    print("Ya existe el archivo update.txt en raspebrry, procede a eliminarse...")
                    subprocess.run('rm -rf /home/pi/update.txt', shell=True)
                if os.path.exists(f'/home/pi/{id_Unidad}'):
                    print(f"Ya existe el archivo {id_Unidad}.txt en raspberry, procede a eliminarse...")
                    subprocess.run(f'rm -rf /home/pi/{id_Unidad}', shell=True)
                if os.path.exists('/home/pi/update/'):
                    print("Ya existe directorio update en raspebrry, procede a eliminarse...")
                    subprocess.run('rm -rf /home/pi/update/', shell=True)
                    
                ser.flushInput()
                ser.flushOutput()
                
                return True
            except Exception as e:
                print("Fallo la verificacion de UFS")
                return True
        
        global ConfigurarFTP  
        def ConfigurarFTP(servidor, tamanio,version_matriz):
            try:
                fecha = strftime('%Y/%m/%d').replace('/', '')[2:]
                global version_MT,intentos_actualizacion
                version_MT = version_matriz
                print(f"<<<<<<<<<<<< INTENTO DE ACTUALIZACION: {intentos_actualizacion+1} >>>>>>>>>")
                if servidor == "web":
                    cone=conf_conexion_FTP_webhost+"\r\n"
                    print("esto es cone "+cone)
                    ser.write(cone.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio "+Aux.decode())
                    time.sleep(2)
                    Tiempo="\"rsptimeout\""
                    comando="AT+QFTPCFG="+Tiempo+",180\r\n"
                    ser.write(comando.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio "+Aux.decode())
                    time.sleep(2)
                    transmode="\"transmode\""
                    comando="AT+QFTPCFG="+transmode+",1\r\n"
                    ser.write(comando.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio "+Aux.decode())
                    time.sleep(2)
                    filetype="\"filetype\""
                    comando="AT+QFTPCFG="+filetype+",1\r\n"
                    ser.write(comando.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio "+Aux.decode())
                    ret = IniciarSesionFTP("web", tamanio)
                    return ret
                elif servidor == "azure":
                    
                    # Se empiezan a hacer las configuraciones de la conexion FTP con Azure
                    cone=conf_conexion_FTP_azure+"\r\n"
                    print("esto es cone "+cone)
                    ser.write(cone.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio "+Aux.decode())
                    time.sleep(2)
                    Tiempo="\"rsptimeout\""
                    comando="AT+QFTPCFG="+Tiempo+",180\r\n"
                    ser.write(comando.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio "+Aux.decode())
                    time.sleep(2)
                    transmode="\"transmode\""
                    comando="AT+QFTPCFG="+transmode+",1\r\n"
                    ser.write(comando.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio "+Aux.decode())
                    time.sleep(2)
                    filetype="\"filetype\""
                    comando="AT+QFTPCFG="+filetype+",1\r\n"
                    ser.write(comando.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio "+Aux.decode())
                    ret = IniciarSesionFTP("azure", tamanio)
                    if ret == False:
                        intentos_actualizacion+=1
                        if intentos_actualizacion >= 3:
                            intentos_actualizacion = 0
                            return False
                        else:
                            return ConfigurarFTP(servidor, tamanio, version_matriz)
                    else:
                        return True
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("FTP.py,", exc_tb.tb_lineno, " Error al ConfigurarFTP: "+str(e))
                insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "error", f"MT_{version_matriz}") # Matriz tarifaría
                intentos_actualizacion+=1
                if intentos_actualizacion >= 3:
                    intentos_actualizacion = 0
                    return False
                else:
                    return ConfigurarFTP(servidor, tamanio, version_matriz)
            
##########################################################################################################################################
        #Se establece la conexion con el servidor por medio del FTP
        global IniciarSesionFTP
        def IniciarSesionFTP(servidor, tamanio):
            try:
                fecha = strftime('%Y/%m/%d').replace('/', '')[2:]
                global intentos_ftp, contador, version_MT
                if servidor == "web":
                    comando=conexion_FTP_webhost+"\r\n"
                    ser.write(comando.encode())
                    print("INTENTANDO CONECTAR A SERVIDOR WEBHOST..")
                    time.sleep(5)
                    Aux = ser.readline()
                    print(Aux)
                    print(Aux.decode())
                    time.sleep(3)
                    
                    if "OK" in Aux.decode():
                        print("Conexion exitosa a servidor webhost")
                        time.sleep(5)
                        contador = 0
                        intentos_ftp = 0
                        return UbicarPathFTP("web", tamanio)
                    else:
                        print("Reintentando conectar a servidor webhost...")
                        comando="AT+QFTPCLOSE\r\n"
                        ser.write(comando.encode())
                        time.sleep(5)
                        if contador >= 6:
                            print("No se pudo establecer la conexion con el servidor FTP [web]")
                            return False
                        contador += 1
                        intentos_ftp += 1
                        print(f"contador:{contador}, intentos_ftp:{intentos_ftp}")
                        ret = IniciarSesionFTP("web", tamanio)
                    contador = 0
                    intentos_ftp = 0
                    return ret
                elif servidor == "azure":
                    comando=conexion_FTP_azure+"\r\n"
                    ser.write(comando.encode())
                    print("INTENTANDO CONECTAR A AZURE..")
                    time.sleep(5)
                    Aux = ser.readline()
                    print(Aux)
                    print(Aux.decode())
                    time.sleep(3)
                    
                    if "OK" in Aux.decode():
                        print("Conexion exitosa a azure")
                        time.sleep(5)
                        contador = 0
                        intentos_ftp = 0
                        return UbicarPathFTP("azure", tamanio)
                    else:
                        print("Reintentando conectar a azure...")
                        comando="AT+QFTPCLOSE\r\n"
                        ser.write(comando.encode())
                        time.sleep(5)
                        if intentos_ftp >= 3:
                            print("No se pudo establecer la conexion con el servidor FTP [Azure]")
                            print("intentando conexion alternativa con servidor webhost")
                            ret = ConfigurarFTP("web", tamanio, version_MT)
                        else:
                            contador += 1
                            intentos_ftp += 1
                            print(f"contador:{contador}, intentos_ftp:{intentos_ftp}")
                            ret = IniciarSesionFTP("azure", tamanio)
                    contador = 0
                    intentos_ftp = 0
                    insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "error", f"MT_{version_MT}") # Matriz tarifaría
                    return ret
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("FTP.py,", exc_tb.tb_lineno, " Error al IniciarSesionFTP: "+str(e))
                insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "error", f"MT_{version_MT}") # Matriz tarifaría
                return False
            
##########################################################################################################################################
        #Funcion para establecer la ruta de archivo que se quiere descargar por FTP
        global UbicarPathFTP
        def UbicarPathFTP(servidor, tamanio):#se comienza ubicando la ruta
            try:
                fecha = strftime('%Y/%m/%d').replace('/', '')[2:]
                global id_Unidad,nombre,ubicacion,version_MT,tipo
                if version_MT == False:
                    nombre = id_Unidad
                    ubicacion = "/Actualizaciones/Software/"
                    tipo = "Completo"
                else:
                    nombre = str(version_MT)
                    ubicacion = "/Tarifas/"
                    tipo = "Parcial"


                if servidor == "azure":
                    global intentos_ftp
                    print(f">>>>>>>>>>>>>>>Buscando archivo:{nombre}.txt en la ubicaion:{ubicacion}")
                    #comando = 'AT+QFTPCWD="f/Tarifas/"' + "\r\n"
                    comando = f'AT+QFTPCWD=\"{ubicacion}\"' + "\r\n"
                    print(f"comando:{comando}")

                    ser.write(comando.encode())
                    flush = ser.readline()
                    print("Flush -------------")
                    while flush:
                        print(flush)
                        flush = ser.readline()
                    print("-----------")
                    time.sleep(5)
                    
                    archivo = f"\"{nombre}.txt\""
                    complemento= f"\"UFS:{nombre}.txt\""
                    comando="AT+QFTPGET="+archivo+","+complemento+"\r\n"
                    print(f"comando:{comando}")
                    ser.write(comando.encode())
                    time.sleep(5)
                    print(ser.readline())
                    Reintentar = "false"
                    while True:
                        print("descargando archivo de azure...")
                        Aux = ser.readline()
                        print("descarga: ["+Aux.decode() + "]")
                        if Aux == "+QFTPGET: 0,0":
                            print("Ha ocurrido un error")
                            Reintentar = "True"
                            break
                        if "ERROR" in str(Aux) or "605" in str(Aux) or "625" in str(Aux) or "613" in str(Aux):
                            print("Ha ocurrido un error")
                            Reintentar = "True"
                            break
                        Cortada = Aux.decode()
                        Aux1 = Cortada.split(":")
                        if Aux1[0] == "+QFTPGET":
                            print("Revisando descargada...")
                            Cortada = Aux.decode()
                            Aux1 = Cortada.split(",")
                            if Aux1[0] == f"+QFTPGET: 0":
                                print("Conexion del ftp correcta")
                                if Aux[1] > 0:
                                    if int(Aux1[1]) != int(tamanio):
                                        print("El tamaño del archivo no coincide")
                                        print(f"\tSe esperaba: {tamanio} Bytes, se descargo un archivo de: {Aux1[1]} Bytes")
                                        Reintentar = "True"
                                        break
                                    print("Tamaño de archivo coincide con el esperado")
                                    print("Verificando descarga")
                                    break
                            else:
                                print("Ha ocurrido un error, reintentando...")
                                print(f"Aux1 = {Aux1}")
                                Reintentar = "True"
                                break
                        
                    if Reintentar == "True":
                        return False
                    else:
                        return leerArchivo("azure", tamanio)
                elif servidor == "web":
                    print(f">>>>>>>>>>>>>>>Buscando archivo:{nombre}.txt en la ubicaion:{ubicacion}")
                    comando = f'AT+QFTPCWD=\"{ubicacion}\"' + "\r\n"
                    print(f"comando:{comando}")

                    ser.write(comando.encode())
                    print(ser.readline())
                    Aux = ser.readline()
                    print("salio 1 "+Aux.decode())
                    time.sleep(5)
                    
                    archivo = f"\"{nombre}.txt\""
                    complemento= f"\"UFS:{nombre}.txt\""
                    comando="AT+QFTPGET="+archivo+","+complemento+"\r\n"
                    ser.write(comando.encode())
                    time.sleep(5)
                    print(ser.readline())
                    Reintentar = "false"
                    while True:
                        print("descargando archivo de webhost...")
                        Aux = ser.readline()
                        print(Aux.decode())
                        if Aux == "+QFTPGET: 0,0":
                            print("Ha ocurrido un error")
                            Reintentar = "True"
                            break
                        Cortada = Aux.decode()
                        Aux1 = Cortada.split(":")
                        if Aux1[0] == "+QFTPGET":
                            print("Revisando descargada...")
                            Cortada = Aux.decode()
                            Aux1 = Cortada.split(",")
                            if Aux1[0] == f"+QFTPGET: 0":
                                print("Conexion del ftp correcta")
                                if Aux[1] > 0:
                                    if int(Aux1[1]) != int(tamanio):
                                        print("El tamaño del archivo no coincide")
                                        print(f"\tSe esperaba: {tamanio} Bytes, se descargo un archivo de: {Aux1[1]} Bytes")
                                        Reintentar = "True"
                                        break
                                    print("Tamaño de archivo coincide con el esperado")
                                    print("Verificando descarga")
                                    break
                            else:
                                print("Ha ocurrido un error")
                                Reintentar = "True"
                                break
                        
                    if Reintentar == "True":
                        return False
                    else:
                        return leerArchivo("web", tamanio)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("FTP.py,", exc_tb.tb_lineno, " Error al UbicarPathFTP: "+str(e))
                insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "error", f"MT_{version_MT}") # Matriz tarifaría
                return False
            
##########################################################################################################################################
        #funcion para leer el txt descargado (base 64)
        global leerArchivo
        def leerArchivo(servidor, tamanio):
            try:
                fecha = strftime('%Y/%m/%d').replace('/', '')[2:]
                global nombre
                if servidor == "web":
                    
                    archivo= f"\"{nombre}.txt\""
                    comando="AT+QFDWL="+archivo+"\r\n"
                    ser.write(comando.encode())
                    time.sleep(1)
                    print("Descargando archivo de quectel...")
                    eux = ser.readlines()
                    #print("esto es el archivo: ")
                    #print(eux)
                    print("Ya se descargo el archivo")
                    todo = ""

                    time.sleep(5)

                    file = open(f"{nombre}.txt","w")
                    
                    i=0
                    Base64 = ""
                    
                    while True:
                        i = i + 1
                        if eux[i] == b"CONNECT\r\n":
                            if eux[i+1] != b"\r\n":
                                Base64 = eux[i+1]
                                print("Encontrado")
                                file.write(Base64.decode('UTF-8') + os.linesep)
                                file.close()
                                
                                file = open(f'{nombre}.txt', 'rb') 
                                byte = file.read() 
                                file.close()

                                decodeit = open('update.zip', 'wb') 
                                decodeit.write(base64.b64decode((byte))) 
                                decodeit.close() 
                                break
                            else:
                                print("Reiniciando descarga...")
                                #IniciarSesionFTP()
                                break
                    return ActualizarArchivos(tamanio)
                elif servidor == "azure":
                    global intentos_ftp
                    archivo= f"\"{nombre}.txt\""
                    comando="AT+QFDWL="+archivo+"\r\n"
                    ser.write(comando.encode())
                    time.sleep(1)
                    print("Descargando archivo de quectel...")
                    eux = ser.readlines()
                    print("esto es el archivo: ")
                    print(eux)
                    todo = ""
                    

                    file = open(f"{nombre}.txt","w")

                    i=0
                    Base64 = ""
                    
                    while True:
                        i = i + 1
                        if eux[i] == b"CONNECT\r\n":
                            if eux[i+1] != b"\r\n":
                                Base64 = eux[i+1]
                                print("Encontrado")
                                file.write(Base64.decode('UTF-8') + os.linesep)
                                file.close()
                                
                                file = open(f'{nombre}.txt', 'rb') 
                                byte = file.read() 
                                file.close() 

                                decodeit = open('update.zip', 'wb')
                                decodeit.write(base64.b64decode((byte))) 
                                decodeit.close()
                                break
                            else:
                                print("Reiniciando descarga...")
                                #IniciarSesionFTP()
                                break

                    #-------------Alejandro Valencia Revision de peso de archivo txt descargado
                    time.sleep(2)
                    print(">>>>>> El tamaño Esperado del archivo txt en Bytes es: "+str(int(tamanio)))
                    if os.path.exists(f"/home/pi/{nombre}.txt"):
                        tamanio_del_archivo = os.path.getsize(f"/home/pi/{nombre}.txt")
                        if len(str(tamanio_del_archivo)) > 0:
                            print(">>>>>> El tamaño del archivo txt en Bytes es: "+str(int(tamanio_del_archivo)))
                        if len(str(tamanio_del_archivo)) > 3:
                            print(">>>>>> El tamaño del archivo txt en KBytes es: "+str(int(tamanio_del_archivo)/1024))
                        if len(str(tamanio_del_archivo)) > 6:
                            print(">>>>>> El tamaño del archivo txt en MBytes es: "+str(int(tamanio_del_archivo)/1024/1024))

                        if(int(tamanio) + 3 != tamanio_del_archivo):
                            print(f"El tamaño de los archivos no coinciden")
                            if tamanio > tamanio_del_archivo:
                                print(f"El archivo descargado es menor por {tamanio - tamanio_del_archivo} Bytes")
                            elif tamanio < tamanio_del_archivo:
                                print(f"El archivo descargado es mayor por {tamanio_del_archivo - tamanio} Bytes")
                            print("Borrando archivo txt descargado...")
                            subprocess.run(f'rm -rf {nombre}.txt', shell=True)
                            return False
                    else:
                        print(f"No se puede leer el tamaño del archivo: {nombre}.txt")
                    time.sleep(10)
                    #-----------//////////////////////////////////////////////////////////////
                    return ActualizarArchivos(tamanio)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print("FTP.py,", exc_tb.tb_lineno, " Error al leer archivo: "+str(e))
                insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "error", f"MT_{nombre}") # Matriz tarifaría
                return False
            

    ###################################################################
    #Descompresion y movimiento de archivos
    ###################################################################
    
    #Funcion para descomprimir el archivo descargado
    #unar es una aplicacion que necesita ser installada para que unar -q funcione
    #Archivo descargado del servidor
    #Descomprime el archivo que debe ser un .rar con una carpeta (en .txt)
    #-f es para forzar la sobreescritura si existe ya un archivo igual

        global ActualizarArchivos
        def ActualizarArchivos(tamanio_esperado):
            global nombre, intentos_ftp, tipo
            fecha = strftime('%Y/%m/%d').replace('/', '')[2:]
            time.sleep(1)
            filename = 'update.zip' 
            if os.path.exists(filename):
                try:
                    #-------------Alejandro Valencia Revision de peso de archivo zip descargado
                    if os.path.exists(f"/home/pi/update.zip"):
                        tamanio_del_archivo = os.path.getsize(f"/home/pi/update.zip")
                        if len(str(tamanio_del_archivo)) > 0:
                            print(">>>>>> El tamaño del archivo zip en Bytes es: "+str(int(tamanio_del_archivo)))
                        if len(str(tamanio_del_archivo)) > 3:
                            print(">>>>>> El tamaño del archivo zip en KBytes es: "+str(int(tamanio_del_archivo)/1024))
                        if len(str(tamanio_del_archivo)) > 6:
                            print(">>>>>> El tamaño del archivo zip en MBytes es: "+str(int(tamanio_del_archivo)/1024/1024))

                    else:
                        print(f"No se puede leer el tamaño del archivo: update.zip")
                    time.sleep(10)

                    #-------------//////
                    print("Descomprimiendo...")
                    #Verificamos en que ubicacion 
                    subprocess.run('pwd', shell=True)
                    subprocess.run('rm -rf update.txt', shell=True)
                    subprocess.run(f'rm -rf {nombre}.txt', shell=True)
                    subprocess.run("mv -f /home/pi/update.zip /home/pi/actualizacion/",shell=True)
                    if os.path.exists("/home/pi/update/"):
                        subprocess.run('rm -rf /home/pi/update/', shell=True)
                    subprocess.run("unzip -o /home/pi/actualizacion/update.zip",shell=True)
                    time.sleep(5)
                    print(".zip descomprimido")
                    if os.path.exists("/home/pi/update/"):
                        print("Carpeta descomprimida: update")
                        
                        print("Procedemos a mover los archivos de upate a urban_urbano...")
                        subprocess.run('rm -rf /home/pi/actualizacion/update.zip', shell=True)
                        #subprocess.run("sudo cp -r /home/pi/Urban_Urbano/ /home/pi/antigua/",shell=True)
                        #------------------Alejandro Valencia Actualizacion de archivos
                        if tipo == "Completo":
                            #Actualizacion por formato completo
                            if os.path.exists("/home/pi/antigua/"):
                                subprocess.run('rm -rf /home/pi/antigua/', shell=True)
                            print("Moviendo carpeta Urban_Urbano a carpeta antigua...")
                            subprocess.run('mv -f /home/pi/Urban_Urbano/ /home/pi/antigua/', shell=True)
                            print("Haciendo que carpeta update sea nueva Urban_Urbano...")
                            subprocess.run('mv -f /home/pi/update/ /home/pi/Urban_Urbano/', shell=True)
                            print("Regresando archivos originales, manteniendo los actualizados...")
                            subprocess.run('cp -rn /home/pi/antigua/* /home/pi/Urban_Urbano/', shell=True)
                            time.sleep(5)
                            print("Eliminando carpeta antigua...")
                            subprocess.run('rm -rf /home/pi/antigua/', shell=True)
                            #Dando permisos a carpeta db
                            #subprocess.run('sudo chmod 777 /home/pi/Urban_Urbano/db/*', shell=True)  #Solo archivos especificos
                            subprocess.run('sudo chmod -R a+rwx /home/pi/Urban_Urbano/', shell=True) #Carpeta recursiva

                        elif tipo == "Parcial":
                            #Actualizacion de algunos archivos especificos
                            print("Copiando archivos de update a Urban_Urbano")
                            subprocess.run('cp -rf /home/pi/update/* /home/pi/Urban_Urbano/', shell=True)
                            print("Eliminando carpeta update...")
                            subprocess.run('rm -rf /home/pi/update/', shell=True)
                        #---------------------------------------------------------------
                        #subprocess.run('rm -rf /home/pi/Urban_Urbano', shell=True)
                        #subprocess.run("mv -f /home/pi/update /home/pi/Urban_Urbano",shell=True)
                        if os.path.exists("/home/pi/Urban_Urbano/verificar_carpeta.py"):
                            subprocess.run("mv -f /home/pi/Urban_Urbano/verificar_carpeta.py /home/pi/actualizacion/",shell=True)
                            print("Archivo verificar_carpeta.py movido")
                        
                        print(ser.readline())
                        Aux = ser.readline()
                        print(Aux.decode())
                        eliminar_archivos = "AT+QFDEL=\"update.txt\"\r\n"
                        ser.write(eliminar_archivos.encode())
                        print(ser.readline())
                        Aux = ser.readline()
                        print(Aux.decode())
                        ser.flushInput()
                        ser.flushOutput()
                        
                        print(ser.readline())
                        Aux = ser.readline()
                        print(Aux.decode())
                        eliminar_archivos = f"AT+QFDEL=\"{nombre}.txt\"\r\n"
                        ser.write(eliminar_archivos.encode())
                        print(ser.readline())
                        Aux = ser.readline()
                        print(Aux.decode())
                        Aux = ser.readline()
                        print(Aux.decode())
                        ser.flushInput()
                        ser.flushOutput()
                        
                        print("#############################################")
                        #print("Actualización completada, Reiniciando boletera...")
                        print("Actualización completada...")
                        print("#############################################")
                        
                        if tipo == "Completo":
                            subprocess.run("sudo reboot", shell=True)
                        elif tipo == "Parcial":
                            variables_globales.version_de_MT = nombre
                            print("La version de MT en vg es: ", variables_globales.version_de_MT)
                            insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "MT", variables_globales.version_de_MT) # Matriz tarifaría
                        
                        return True
                    #-----------------------------------------------------------------------------------------------------------INICIA PARCHE
                    elif len(glob.glob("/home/pi/*.db")) > 0:
                        print(f"No existe la carpeta descomprimida como /home/pi/update/")
                        print("Existe un archivo descomprimido del tipo .db")
                        time.sleep(5)
                        subprocess.run('rm -rf /home/pi/actualizacion/update.zip', shell=True)
                        #Revisa si el archivo es el necesario
                        ruta = "/home/pi/"
                        destino = "/home/pi/Urban_Urbano/db"
                        for archivo in os.listdir(ruta):
                            # Verifica si el archivo es un archivo regular (no es una carpeta)
                            if os.path.isfile(os.path.join(ruta, archivo)):
                                if "matrices_tarifarias" in archivo and archivo.endswith(".db"):
                                    nombre_archivo = archivo
                                    print("El nombre del archivo es:", nombre_archivo)
                                    ruta_origen = os.path.join(ruta, nombre_archivo)
                                    ruta_destino = os.path.join(destino, "matrices_tarifarias.db")
                                    shutil.move(ruta_origen, ruta_destino)

                                    print(ser.readline())
                                    Aux = ser.readline()
                                    print(Aux.decode())
                                    eliminar_archivos = "AT+QFDEL=\"update.txt\"\r\n"
                                    ser.write(eliminar_archivos.encode())
                                    print(ser.readline())
                                    Aux = ser.readline()
                                    print(Aux.decode())
                                    ser.flushInput()
                                    ser.flushOutput()
                                    
                                    print(ser.readline())
                                    Aux = ser.readline()
                                    print(Aux.decode())
                                    eliminar_archivos = f"AT+QFDEL=\"{nombre}.txt\"\r\n"
                                    ser.write(eliminar_archivos.encode())
                                    print(ser.readline())
                                    Aux = ser.readline()
                                    print(Aux.decode())
                                    Aux = ser.readline()
                                    print(Aux.decode())
                                    ser.flushInput()
                                    ser.flushOutput()
                                    
                                    variables_globales.version_de_MT = nombre
                                    print("La version de MT en vg es: ", variables_globales.version_de_MT)
                                    insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "MT", variables_globales.version_de_MT) # Matriz tarifaría
                                    
                                    print("#############################################")
                                    print("Actualización completada...")
                                    print("#############################################")
                                    #subprocess.run("sudo reboot", shell=True)
                                    return True
                    #------------------------------------------------------------------------------------------------TERMINA PARCHE
                    else:
                        print(f"No existe la carpeta descomprimida como /home/pi/update/")
                        print("No existe un archivo descomprimido del tipo .db")
                        subprocess.run('rm -rf /home/pi/actualizacion/update.zip', shell=True)
                    print("#############################################")
                    print("Algo fallo")
                    print("#############################################")
                    insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "error", f"MT_{nombre}") # Matriz tarifaría
                    return False
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print("FTP.py,", exc_tb.tb_lineno + str(e))
                    insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "error", f"MT_{nombre}") # Matriz tarifaría
                    return False
            else:
                print ("No se encontró el archivo")
                time.sleep(1)
                insertar_estadisticas_boletera(str(datos_de_la_unidad[1]), fecha, variables_globales.hora_actual, "error", f"MT_{nombre}") # Matriz tarifaría
                return False