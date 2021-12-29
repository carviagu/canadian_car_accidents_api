###############################################
# Script para el guardado de los errores generados
# Los guarda en un log para el mantenimiento del sistema
###############################################

import numpy as np
from datetime import datetime

def log_error(traceback = None, input = None):

    # Preparamos los datos del error
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    code = now.strftime("%d%m%Y%H%M%S")

    error = '\n' + dt_string + " - trace: " + traceback.format_exc() + " - input: " + str(input)

    # Actualizamos el log
    with open('data/log.txt', 'a') as f:
        f.write(error)

    # Devolvemos la referencia del error
    return code
