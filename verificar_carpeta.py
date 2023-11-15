import os
import subprocess
import time
import sys

sys.path.insert(1, '/home/pi/Urban_Urbano/configuraciones_iniciales')

time.sleep(2)

try:
    if os.path.exists("/home/pi/Urban_Urbano/") is not True:
        try:
            if os.path.exists("/home/pi/update") is True:
                print("No existe la carpeta Urban_Urbano pero si la carpeta update de la actualización")
                subprocess.run("sudo mv -f /home/pi/update /home/pi/Urban_Urbano",shell=True)
                print("Se movió el contenido de la carpeta update a la carpeta Urban_Urbano")
                subprocess.run("/usr/bin/python3 /home/pi/Urban_Urbano/configuraciones_iniciales/encender_quectel.py",shell=True)
            elif os.path.exists("/home/pi/antigua/Urban_Urbano/") is True:
                print("No existe la carpeta principal Urban_Urbano así que procedemos a copiar la versión antigua")
                subprocess.run("sudo cp -r /home/pi/antigua/Urban_Urbano /home/pi/Urban_Urbano/",shell=True)
                if os.path.exists("/home/pi/Urban_Urbano/"):
                    print("Se copió la versión antigua correctamente")
                    subprocess.run("/usr/bin/python3 /home/pi/Urban_Urbano/configuraciones_iniciales/encender_quectel.py",shell=True)
                else:
                    print("No se pudo copiar la versión antigua, así que procedemos a descargar la última versión desde el servidor")
                    subprocess.run("cd",shell=True)
                    subprocess.run("git clone https://github.com/ErnestoLomar/Urban_Urbano.git",shell=True)
                    if os.path.exists("/home/pi/Urban_Urbano/"):
                        print("Descarga exitosa")
                        subprocess.run("/usr/bin/python3 /home/pi/Urban_Urbano/configuraciones_iniciales/encender_quectel.py",shell=True)
                    else:
                        print("No se pudo descargar la última versión desde el servidor")
            else:
                print("No existe la carpeta principal Urban_Urbano ni una versión antigua, así que procedemos a descargar la última versión desde el servidor")
                subprocess.run("cd",shell=True)
                subprocess.run("git clone https://github.com/ErnestoLomar/Urban_Urbano.git",shell=True)
                if os.path.exists("/home/pi/Urban_Urbano/"):
                    print("Descarga exitosa")
                    subprocess.run("/usr/bin/python3 /home/pi/Urban_Urbano/configuraciones_iniciales/encender_quectel.py",shell=True)
                else:
                    print("No se pudo descargar la última versión desde el servidor")
        except Exception as e:
            print("No se puede iniciar la carpeta principal Urban_Urbano: "+str(e))
    else:
        subprocess.run("/usr/bin/python3 /home/pi/Urban_Urbano/configuraciones_iniciales/encender_quectel.py",shell=True)
except Exception as e:
    print("Error al copiar los archivos: "+str(e))