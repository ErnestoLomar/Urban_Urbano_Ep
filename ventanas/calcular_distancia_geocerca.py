##########################################
# Autor: Equipo Interfaz
# Fecha de creación: 10/05/2022
# Ultima modificación: 10/05/2022
#
##########################################
import math
import logging

###################################################################################################
# Calcula la distancia entre dos puntos en un plano (el primer punto es el centro de la geocerca, el
# segundo punto es la ubicación actual del dispositivo)
# :return: La distancia entre el centro de la geocerca y la posición real del dispositivo.
####################################################################################################
def calcular_distancia(longitud, latitud, centro_geocerca_longitud, centro_geocerca_latitud ): 
    try:
        longitud_real = longitud
        latitud_real = latitud
        distancia = math.sqrt(math.pow((centro_geocerca_latitud - latitud_real), 2) + math.pow((centro_geocerca_longitud - longitud_real), 2))
        return distancia
    except Exception as e:
        print("Error al calcular la distancia entre el centro de la geocerca y la posición real del dispositivo")
        logging.info(f"Error al calcular la distancia: {e}")