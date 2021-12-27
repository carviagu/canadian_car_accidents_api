# Utilizamos la imagen de Jupyter Notebook como base
FROM alpine:3.15

ENV PATH /usr/local/bin:$PATH

# Preparar la estructura de carpetas
RUN mkdir canadian_car_api
RUN cd canadian_car_api
RUN mkdir model

# Instalamos las dependencias necesarias en el contenedor
RUN conda install -c anaconda pandas
RUN conda install -c anaconda numpy
RUN conda install -c anaconda scikit-learn

# Guardamos los archivos importantes
COPY xgb_opt_model.sav ./canadian_car_api/model/xgb_opt_model.sav



