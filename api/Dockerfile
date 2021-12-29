# Archivo de creacion de la imagen y contenedor de la API.

# Utilizamos la imagen de ubuntu como base
FROM ubuntu

# Preparar la estructura de carpetas (copiamos el directorio de la API)
ADD . /canadian_api
WORKDIR /canadian_api

# Instalamos las dependencias necesarias en el contenedor
RUN apt-get update && apt-get install python3.6 -y && apt-get install python3-pip -y
RUN apt-get install vim -y
RUN pip3 install -r requirements.txt

# Activar la API flask
CMD ["/bin/bash"]


