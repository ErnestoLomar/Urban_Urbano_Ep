from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QMouseEvent
import time
import logging
import subprocess
from asignaciones_queries import obtener_asignacion_por_folio_de_viaje, obtener_ultima_asignacion
from PyQt5.QtCore import QSettings
import variables_globales as vg
import datetime
from time import strftime

class DeteccionGeocercasWorker(QObject):
    try:
        finished = pyqtSignal()
        progress = pyqtSignal(dict)
        settings = QSettings('/home/pi/Urban_Urbano/ventanas/settings.ini', QSettings.IniFormat)
    except Exception as e:
        print(e)
        logging.info(e)

    def run(self):
        try:
            try:
                from abrir_ventanas import AbrirVentanas
            except Exception as e:
                print(e)
                
            try:
                ultima_asignacion = obtener_ultima_asignacion()
                print("La ultima asignacion es: ", ultima_asignacion)
            except Exception as e:
                print("Ocurrió un error al obtener la ultima asignacion: ", e)
            
            while True:
                
                import variables_globales
                self.longitud = variables_globales.longitud
                self.latitud = variables_globales.latitud
                
                try:
                    # Obtenemos la fecha completa y hora de la raspberry con el comando 'date'
                    fecha_actual = str(subprocess.run("date", stdout=subprocess.PIPE, shell=True).stdout.decode())
                    #print("La fecha actual de la RPI es: ",fecha_actual)
                    
                    # Obtenemos unicamente la hora del string
                    indice = fecha_actual.find(":")
                    hora_actual = fecha_actual[(int(indice) - 2):(int(indice) + 6)]
                    #print("LA HORA ACTUAL RPI ES: ", hora_actual)
                    
                    '''
                    #Obtenemos la trama dos del viaje actual
                    if len(self.settings.value('folio_de_viaje')) > 0:
                        trama_dos_del_viaje = obtener_asignacion_por_folio_de_viaje(self.settings.value('folio_de_viaje'))
                    else:
                        trama_dos_del_viaje = obtener_asignacion_por_folio_de_viaje(vg.folio_asignacion)'''
                    
                    #Obtenemos la fecha del dia de hoy mediante la librería datetime
                    hoy = datetime.datetime.now().date()
                    
                    # Calculamos la fecha de hace dos días, tomando en cuenta el día actual.
                    fecha_hace_dos_dias = hoy - datetime.timedelta(days=2)
                    
                    # Calculamos la fecha de hace un día, tomando en cuenta el día actual.
                    fecha_ayer = hoy - datetime.timedelta(days=1)
                    
                    # Organizamos la trama 2
                    fecha_completa_trama_dos = str(str(ultima_asignacion).split(",")).replace("'","").replace('"','').replace("[","").replace("]","").replace("(","").replace(")","").replace(" ","").split(",")
                    fecha_de_trama_dos = str(fecha_completa_trama_dos[5]).replace("-","/")
                    hora_trama_dos = str(fecha_completa_trama_dos[6])
                    
                    # A todas las horas obtenidas (fecha_de_trama_dos, hoy, fecha_hace_dos_dias y fecha_ayer) les damos formato 'datetime'
                    fecha_datetime_trama_dos = datetime.datetime.strptime(fecha_de_trama_dos, "%d/%m/%Y")
                    fecha_datetime_hoy = datetime.datetime.strptime(str(hoy).replace("-","/"), "%Y/%m/%d")
                    fecha_datetime_hace_dos_dias = datetime.datetime.strptime(str(fecha_hace_dos_dias).replace("-","/"), "%Y/%m/%d")
                    fecha_datetime_ayer = datetime.datetime.strptime(str(fecha_ayer).replace("-","/"), "%Y/%m/%d")
                    
                    '''
                    # Ya que las tenemos en formato datetime les damos formato dia/mes/año
                    fecha_formateada_trama_dos = fecha_datetime_trama_dos.strftime("%d/%m/%Y")
                    fecha_formateada_hoy = fecha_datetime_hoy.strftime("%d/%m/%Y")
                    fecha_formateada_hace_dos_dias = fecha_datetime_hace_dos_dias.strftime("%d/%m/%Y")
                    fecha_formateada_ayer = fecha_datetime_ayer.strftime("%d/%m/%Y")'''
                    
                    # Fechas formateadas en YY-MM-DD
                    fecha_formateada_trama_dos = int(str(fecha_datetime_trama_dos.strftime("%Y/%m/%d")).replace("/",""))
                    fecha_formateada_hoy = int(str(fecha_datetime_hoy.strftime("%Y/%m/%d")).replace("/",""))
                    fecha_formateada_hace_dos_dias = int(str(fecha_datetime_hace_dos_dias.strftime("%Y/%m/%d")).replace("/",""))
                    fecha_formateada_ayer = int(str(fecha_datetime_ayer.strftime("%Y/%m/%d")).replace("/",""))
                    
                    #print("La fecha de la trama dos formateada es: ", fecha_formateada_trama_dos)
                    #print("La fecha de hoy formateada es: ", fecha_formateada_hoy)
                    #print("La fecha de hace dos dias formateada es: ", fecha_formateada_hace_dos_dias)
                    #print("La fecha de ayer es: ", fecha_formateada_ayer)
                    
                    '''
                    # Crear un objeto QMouseEvent
                    event = QMouseEvent(QMouseEvent.MouseButtonPress, 
                                        AbrirVentanas.cerrar_vuelta.label_fin.mapToGlobal(AbrirVentanas.cerrar_vuelta.label_fin.rect().center()), 
                                        Qt.LeftButton, 
                                        Qt.LeftButton, 
                                        Qt.NoModifier)'''
                    
                    # Verificamos si la hora actual es menor a las 2am
                    if int(hora_actual[:2]) <= 2:
                        
                        # Verificamos que la fecha de la trama dos sea menor o igual a la fecha de hace dos dias o que
                        # la fecha de la trama dos sea menor o igual a la fecha de ayer y ademas la hora de la trama
                        # dos sea menor a las 2am
                        
                        # This code block is checking if the date of the current trip (obtained from
                        # `trama_dos_del_viaje`) is either two or more days ago or if it is from
                        # yesterday and the time of the trip is before 2am. If either of these
                        # conditions is true, it will open two windows (`cerrar_vuelta` and
                        # `cerrar_turno`) and call their respective methods (`terminar_vuelta` and
                        # `cerrar_turno`).
                        if (fecha_formateada_trama_dos <= fecha_formateada_hace_dos_dias) or (fecha_formateada_trama_dos <= fecha_formateada_ayer and int(hora_trama_dos[:2]) <= 2):
                            print("El inicio de viaje es de hace dos dias o mas, o hace un dia pero antes de las 2am.")
                            logging.info("El inicio de viaje es de hace dos dias o mas, o hace un dia pero antes de las 2am.")
                            AbrirVentanas.cerrar_vuelta.cargar_datos()
                            AbrirVentanas.cerrar_vuelta.show()
                            AbrirVentanas.cerrar_vuelta.terminar_vuelta(AbrirVentanas.cerrar_vuelta, False)
                            AbrirVentanas.cerrar_turno.cargar_datos()
                            AbrirVentanas.cerrar_turno.show()
                            AbrirVentanas.cerrar_turno.cerrar_turno(AbrirVentanas.cerrar_turno)
                            variables_globales.detectando_geocercas_hilo = True
                            self.finished.emit()
                            break
                    
                    elif int(hora_actual[:2]) > 2:
                        
                        # Verificamos que la fecha de la trama dos sea menor o igual a la fecha de ayer.
                        
                        # This code block is checking if the date of the current trip (obtained from
                        # `trama_dos_del_viaje`) is from yesterday or earlier. If this condition is
                        # true, it will open two windows (`cerrar_vuelta` and `cerrar_turno`) and call
                        # their respective methods (`terminar_vuelta` and `cerrar_turno`). This is
                        # likely used to close out a trip and end a work shift.
                        if fecha_formateada_trama_dos <= fecha_formateada_ayer:
                            print("El inicio de viaje tiene de diferencia un dia o mas de estar abierto.")
                            logging.info("El inicio de viaje tiene de diferencia un dia o mas de estar abierto.")
                            AbrirVentanas.cerrar_vuelta.cargar_datos()
                            AbrirVentanas.cerrar_vuelta.show()
                            AbrirVentanas.cerrar_vuelta.terminar_vuelta(AbrirVentanas.cerrar_vuelta, False)
                            AbrirVentanas.cerrar_turno.cargar_datos()
                            AbrirVentanas.cerrar_turno.show()
                            AbrirVentanas.cerrar_turno.cerrar_turno(AbrirVentanas.cerrar_turno)
                            variables_globales.detectando_geocercas_hilo = True
                            self.finished.emit()
                            break
                except Exception as e:
                    print(e)
                
                self.detectando_geocercas_hilo = variables_globales.detectando_geocercas_hilo
                if self.detectando_geocercas_hilo == False:
                    variables_globales.detectando_geocercas_hilo = True
                    self.finished.emit()
                    break
                self.progress.emit({"longitud": self.longitud, "latitud": self.latitud})
                time.sleep(5)
        except Exception as e:
            print(e)
            logging.info(e)