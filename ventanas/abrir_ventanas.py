#Librerías propias
from corte import corte
from cerrar_turno import CerrarTurno
from PyQt5.QtCore import QObject
import logging
class AbrirVentanas(QObject):
    try:
        cerrar_turno = CerrarTurno()
        cerrar_vuelta = corte(cerrar_turno.close_signal)
    except Exception as e:
        logging.error(f"Error al abrir las ventanas: {e}")