<p align="center">
    <!--If notebook is in folder notebooks change scr by "../images/logo.png"-->
  <img width="100" height="100" src="../images/logo.png">
</p>

<div>
<h1>Desarrollo de una API para un modelo XGBoost</h1>

Canadian Car Accidents Practice: Parte 2 <br>
<strong>Aprendizaje Automático</strong> <br>
<strong>Master Universitario en Ciencia de Datos</strong>
</div>

<div style='text-align:right'>Álvaro Serrano del Rincón (<i>a.serranodelrincon@cunef.edu</i>)</div>
<div style='text-align:right'>Carlos Viñals Guitart (<i>carlos.vinals@cunef.edu</i>)</div>

---

**Contenidos**

1. [Introducción](#introduction)

2. [Antecendetes](#context)

3. [Diseño](#design)

4. [Desarrollo](#develop)

5. [Ejemplo de uso](#example)

6. [Conclusión](#conclusion)

7. [Referencias](#references)

---

<h2> <a name="introduction"> 1 Introducción </a> </h2>

En este trabajo propone la creación de una API, que tenga como objetivo poner
en funcionamiento un modelo de Aprendizaje Automático. Esta API recibirá llamadas con datos
de accidentes de tráfico y devolverá una predicción indicando la mortalidad de un accidente concreto con una probabilidad.

Para ello haremos uso de Flask como *framework* de desarrollo de esta API en Pyhton. Además se
utilizará Docker para establecer un entorno ajeno al equipo, que permita poner en funcionamiento
la misma y su despliegue. 

<h2> <a name="context"> 2 Antecedentes </a> </h2>

Este trabajo es la continuación del desarrollo de un modelo de predicción de accidentes de tráfico.
El trabajo anteriormente citado, se desarrolló un modelo de Machine Learning que predijera la mortalidad de un accidente dados unos
datos, para ello hicimos uso del dataset *canadian car accidents* y desarrollamos un modelo *XGBoost*. 
Es por ello que aquí nos centraremos en crear la API que pone en funcionamiento y producitiviza este modelo
para su uso. 

<h2> <a name="design"> 3 Diseño </a> </h2>

A continuación definimos las características principales de este sistema que vamos a crear.

### 3.1 Requisitos y funciones

Hemos identificado las principales funciones que deberá cumplir este sistema:

* **Requisito 1**: Devolverá al usuario una predicción indicando si el accidente puede tener al menos una muerte,
  (clase 0) y la probabilidad de esa misma predicción. 
* **Requisito 2**: El sistema llevará a cabo un guardado de las predicciones realizadas. Para cada llamada 
  guardará la fecha y hora de realización, los datos recibidos y las predicciones obtenidas. 
* **Requisito 3**: El sistema gestionará errores. Proporcionando al usuario un mensaje de fallo y guardando en un registro *log*,
  el resumen del error para que el usuario encargado de gestionar el sistema tenga constancia del mismo y que lo causó.

### 3.2 Estructura de la API

Para poder cumplir con estos requisitos la API contará con una serie de módulos que permitan poder llevarlos a cabo. 
En concreto identificamos tres modulos:

1. **Preprocesado de datos.** El sistema deberá preprocesar los datos recibidos para que estos puedan ser utilizados en el modelo,
   el diseño de este módulo respetará el código generado en el trabajo previo de creación del modelo.
2. **Histórico de llamadas.** Este modulo gestionará el registro *csv* de llamadas realizadas, actualizándolo cada vez que se produzca
   una nueva llamada.
3. **Registro de logs.** Este módulo guardará un registro formato *txt* de los errores producidos para su posterior gestión.

Por otro lado se contará con un script base que será la parte central de la API donde se gestionarán las llamadas a la misma, es decir,
el controlador de las funciones de la API.

<h2> <a name="develop"> 4 Desarrollo </a> </h2>

Procedemos a explicar el proceso de implementación de la API mediante Flask.

### 4.1 Módulos

Se han desarrollado tres módulos, para ello hemos creado un directorio en el proyecto denominado ```modules``` donde se
encuentran los scripts correspondientes a cada uno.

#### 4.1.1 Preprocesado de datos

Este modulo realiza la limpieza de los datos y su preparación para que puedan ser consumidos por el modelo. 
Nuestro modelo no hace uso de *pipelines* por lo que la API deberá encargarse de preprocesarlos antes 
de pasárselos al modelo. 

Aquí se muestra el método principal en ```preprocess.py``` que llama a las funciones de limpieza y procesado internas del módulo:

```py
# main
def preprocess(data = None):

    data = data[acc_columns]
    # Reduce categories
    data = category_reduction(data)
    # Missing 
    data = missing(data)
    # Encoding
    data = encode(data)
    # Final data
    data = data[model_columns]

    return data
```

No entramos en mucho detalle a la hora de explicar este módulo, pues el código del mismo se corresponde con el creado 
en el momento de desarrollar el modelo y que se utilizó para limpiar las muestras de entrenamiento y test. Lo más relevante
y que explica la necesidad de este módulo es porque los datos serán recibidos como se encontraban originalmente, pero
nuestro modelo fue creado con unos datos totalmente limpiados y modificados de su formato original. Se puede observar el código
completo de este módulo en el script ```preproces.py```. 

#### 4.1.2 Histórico de datos

Este módulo se encargará de guardar las llamadas a la API. Para ello hemos creado una función que recibirá el input que lee la 
API y las predicciones. Acto seguido juntará esos datos e incorporará la fecha y hora. Para después abrir el fichero csv donde 
se almacenan y añadir la nueva llamada al histórico. 

A continuación se muestra el código de la función de guardado de ```preprocess.py```:

```py
def save_history(call = None, pred = None, prob = None):

    # Fecha de la predicción
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    dates = [dt_string] * len(call)

    temp = pd.DataFrame(data = dates, columns = ['datetime'])

    # Creamos el dataframe de datos
    for col in call.columns:
        temp[col] = call[col].astype(str)

    predictions = list()
    proba = list()

    # Guardamos las predicciones de los mismos
    for i in range(len(pred)):
        predictions.append(str(pred[i]))
        proba.append(str(prob[i][0]))

    temp['res_pred'] = predictions
    temp['res_prob'] = proba

    # Lo guardamos en el histórico
    try:
        history = pd.read_csv("./data/history.csv")
        history = pd.concat([history, temp])
    except:
        history = temp

    history.to_csv("./data/history.csv", index=False)
```

Se puede analizar el código completo de este scritp en el fichero ````history.py````.

#### 4.1.3 Logger de errores

Este módulo guarda la información de los errores ocurridos en el sistema en caso de fallos. Este
hace uso de un archivo txt donde guarda las trazas del error así como otra información relevante.
A continuación se muestra el código correspondiente en ````logger.py````:

```py
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
```

Observamos que el código devuelve una especie de referencia. Más adelante entederemos su uso. 

### 4.2 API

Una vez hemos desarrollado los módulos de funcionamiento del sistema. Ahora nos centramos en el script
principal que es la propia API y que gestionará las llamadas a la misma. 

Sin entrar en mucho detalle nos centraremos en los pasos principales para su creación. Primero importaremos 
las librerías principales. Aquí se puede observar el código:

```py
# Dependencies
import sys
from flask import Flask, request, jsonify
import pickle
import traceback
import pandas as pd
import modules.preproces as pre  # Preprocess data
import modules.history as hist  # API historic
import modules.logger as log  # Log
```

Destacamos algunas librerías:

* Flask: framework de desarrollo de la API, además usamos *request* que nos
  permite gestionar las llamadas a la API y *jsonify* que utilizamos para devolver las respuestas del servidor en formato JSON.
* Pickle: para abrir el modelo que guardamos en su momento mediante esta misma librería.
* Traceback: para gestionar los errores que puedan ocurrir en el modelo.
* Sys: nos permitirá gestionar aspetos de la inicializacion de la api como el puerto de acceso.

Además destacamos que importamos los scripts correspondientes a los módulos que hemos creado.

Ahora iniciaremos la API. Para ello escribimos la siguiente instrucción que hará la declaración de la misma.

```py
app = Flask(__name__)
```

Una vez inicializada creamos el código que iniciará de forma efectiva la API conforme hagamos la llamada.

```py
if __name__ == '__main__':
    try:
        port = int(sys.argv[1])  # Utilizamos el puerto indicado
    except:
        port = 5000  # Puerto por defecto 5000

    try:
        host = str(sys.argv[2]) # Utilizamos la ip indicada
    except:
        host = '127.0.0.1' # localhost

    model = pickle.load(open("model/xgb_opt_model.sav", 'rb')) 

    if host == '127.0.0.1':
        app.run(port=port, debug=True)
    else:
        app.run(host=host, port=port, debug=True)
```

Explicamos ahora que hace el siguiente código. Primero establece el puerto de conexión de la API. Si se 
lo hemos indicado utilizará el indicado, si no se lo hemos indicado hará uso del puerto por defecto (5000). Hacemos
lo mismo con la dirección del host. Normalmente se usará la dirección del host, sin embargo para su uso en
docker lo conectaremos con un host en concreto. Finalmente, cargamos el modelo que creamos en su momento y se
iniciará la app con los parámetros indicados. 

Ahora crearemos la función de predicción de la API. Esto se escribe antes de la función de inicio que hemos visto
anteriormente. 

El código correspondiente al método de predicción es el siguiente:

```py
@app.route('/predict', methods=['POST'])
def predict():
    if model:
        json_ = 'None'
        try:
            json_ = request.json
            print(json_)
            # Leemos los datos
            data = pd.DataFrame(json_)

            # Procesamos los datos
            query = pre.preprocess(data)

            # Predicción
            prediction = list(model.predict(query))
            # Probabilidad de predicción
            pred_prob = list(model.predict_proba(query))

            # Guardamos la tarea realizada en el histórico
            hist.save_history(data, prediction, pred_prob)

            # Devolvemos las predicciones realizadas.
            results = list()
            for i in range(len(prediction)):
                results.append({'prediction': str(prediction[i]), 
                                 'probability': str(pred_prob[i][0])})
            return jsonify({
                'status': 'SUCCESS',
                'results': results
            })

        except:
            # Guardamos los datos del error en el log
            code = log.log_error(traceback, json_)
            message = '''Error code: ''' + code
            print('ERROR:: ' + traceback.format_exc())
            # Devolvemos el error al usuario
            return jsonify({
                'status': 'ERROR',
                'description': message
            })
    else:
        # Guardamos los datos del error en el log
        log.log_error(traceback, 'Model not loaded correctly.')
        print('ERROR:: ' + traceback.format_exc())
        # Devolvemos el error al usuario
        return jsonify({
            'status': 'ERROR',
            'description': 'Internal Server Error'
        })
```

Observamos el indicador ````@app.route()```` que mapea en la url la función ````predict````, además le indicamos
que el método es ````POST````, a través del cual el usuario subirá sus datos del accidente en formato JSON en el cuerpo de la solicitud.

Primero verificamos que el modelo está cargado correctamente. Sino es así se devolverá un error, 
observamos como usamos el *logger* para guardar la traza del error y los datos del mismo. Acto seguido leemos la solicitud.
Esta se transforma a un dataframe y se pasa al módulo de preprocesado para que transforme los datos. Finalmente estos se pasan al modelo
que realiza la predicción y un predict_probability. Se guarda el histórico de llamadas y se devuelven los datos en formato 
JSON al usuario. 

Si hubiera algún error se ejecutaría el código después del ````except```` que devolvería el error al usuario. 

Con esto ya tendriamos todo el código base de nuestra API. Se pueden crear más métodos y otras utilidades. Se puede
ver el código completo de nuestra API en archivo ````api.py````.

Ahora podriamos ponerla en funcionamiento. Para ejecutar la API abrimos una terminal
en el mismo directorio donde tenemos el fichero ````api.py````.
Y escribimos la siguiente orden.

```shell
python api.py 
```

Observamos que no hemos indicado puerto ni host. Se usarán los establecidos por defecto.
Si todo ha ido bien se mostrará en la terminal el siguiente output. 

```shell
 Model loaded
 * Serving Flask app "api" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Restarting with stat
Model loaded
 * Debugger is active!
 * Debugger PIN: 238-827-473
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

No entraremos ahora en explicar como usar la API, se puede observar su funcionamiento en el capítulo siguiente mediante Postman.

### 4.3 Docker

La siguiente y última fase es desplegar la API, para ello usaremos un contenedor Docker. Esto es muy útil pues
permite ejecutar la API en un sistema aislado sin verse afectado por dependencias externas y ser fácilmente desplegado.

Para poder crear un contenedor de Docker primero creamos un archivo denominado Dockerfile. Este tendrá las instrucciones 
para crear una imagen en la que se basará el contenedor. El archivo Dockerfile se debe crear en el mismo directorio donde
tenemos los archivos de la API. Se muestra el código a continuación:

```dockerfile
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
```

Explicamos un poco que hace este código. Primero, mediante ````FROM```` utilizamos como base una imagen de Ubuntu, una distribución de Linux que es un entorno
adecuado para crear estos contenedores y poder gestionar desde la terminal el mismo. Acto seguido usamos ````ADD```` para copiar todos
los ficheros de la API en la máquina virtual llamamos a la carpeta contenedora ````canadian_api````, y establecemos esta carpeta como directorio principal del sistema. 
Después mediante ````RUN```` actualizamos el sistema, instalamos python, pip y vim para gestionar paquetes y poder ejecutar la API en python. 
Además instalamos todos los paquetes que utiliza nuestra API y que hemos establecido en ````requeriments.txt````. El ````CMD```` establece la orden
principal para ejecutar la terminal del sistema.

**requeriments.txt**

Este archivo tiene el listado de dependencias de la API. Aquí se muestran las dependencias que contiene el fichero:

```text
python-dateutil==2.8.2
pytz==2021.3
numpy==1.20.3
pandas==1.3.4
itsdangerous==1.1.0
MarkupSafe==2.0.1
Jinja2==2.11.2
Werkzeug==2.0.2
click==7.1.2
flask==1.1.2
xgboost==1.5.1
scipy==1.7.3
scikit-learn==1.0.1
```

Estas dependencias se corresponden con los imports realizados en las librerías y otras relacionadas con el modelo
que utilizamos como ````xgboost```` y ````scikit-learn````. Para saber la versión exacta que se necesita se puede realizar
en el entorno de anaconda la instrucción ````pip show <nombredelpaquete>```` y se podrá observar la versión así como otras dependencias
necesarias. 

Una vez tenemos el Dockerfile listo creamos la imagen de Docker, para ello ejecutamos la siguiente instrucción:

```shell
docker build -t canadian_api .
```

Con ````-t```` establecemos el nombre de la imagen. El ````.```` indica a docker el directorio a partir del cual debe de
crear la imagen, el buscará en este directorio para crear la imagen. 

Una vez creada la imagen, creamos el contenedor mediante el siguiente comando:

```shell
docker run -it -p 5000:5000 canadian_api bash
```

Esto creará el contenedor y lo activará. Nos abrirá la terminal del sistema y ya podremos ejecutar la API.

```shell
root@95aefd9aa3da:/canadian_api# ls
Dockerfile  api.py  data  model  modules  requirements.txt
root@95aefd9aa3da:/canadian_api# python3 api.py 5000 0.0.0.0
Model loaded
 * Serving Flask app "api" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://172.17.0.2:5000/ (Press CTRL+C to quit)
 * Restarting with stat
Model loaded
 * Debugger is active!
 * Debugger PIN: 107-073-561
```

En el siguiente capítulo explicamos como utilizar la API.

<h2> <a name="example"> 5 Ejemplo de uso </a> </h2>



A continuación mostramos las intrucciones para hacer uso de la API mediante ```Postman```:

* Accedemos a Postman y abrimos una nueva pestaña para usar una API.
* Indicamos que la función a usar es POST (1).
* Escribimos la dirección de la API con la función predict (2): ```http://localhost:5000/predict```.
* Marcamos que vamos a darle los datos en el cuerpo de la llamada ```Body``` (3).
* Marcamos la opción ```raw``` (4).
* Indicamos que está en formato JSON (5).
* Escribimos los datos de un accidente:
  
  ```json
  [
    {"C_MNTH": "01", "C_WDAY": "1", "C_HOUR": "20", 
    "C_VEHS": 2, "C_CONF": "01", "C_RCFG": "01", "C_WTHR": "1", 
    "C_RSUR": "1", "C_RALN": "1", "C_TRAF": "01", "C_PERS": 2}
  ]
  ```
* Enviamos la solicitud a la API (6).

![](../images/Postman_scheme.png)

Si todo ha ido bien observaremos la predicción devuelta por la API abajo de la pantalla.
Además veremos en la terminal como se ha ejecutado una predicción.

```shell
[{'C_MNTH': '01', 'C_WDAY': '1', 'C_HOUR': '20', 'C_VEHS': 2, 'C_CONF': '01', 'C_RCFG': '01', 'C_WTHR': '1', 'C_RSUR': '1', 'C_RALN': '1', 'C_TRAF': '01', 'C_PERS': 2}]
172.17.0.1 - - [29/Dec/2021 20:46:30] "POST /predict HTTP/1.1" 200 -
```

Si miramos en el archivo ```history.csv``` de la carpeta data la predicción se habrá guardado.

```shell
root@95aefd9aa3da:/canadian_api# cd data
root@95aefd9aa3da:/canadian_api/data# ls
history.csv  log.txt
root@95aefd9aa3da:/canadian_api/data# cat history.csv
datetime,C_MNTH,C_WDAY,C_HOUR,C_VEHS,C_CONF,C_RCFG,C_WTHR,C_RSUR,C_RALN,C_TRAF,C_PERS,res_pred,res_prob
29/12/2021 20:46:29,01,1,20,2,01,01,1,1,1,01,2,1,0.24353099
root@95aefd9aa3da:/canadian_api/data#
```

Si producimos un error, por ejemplo introduciendo un valor erróneo en la solicitud se generará la traza en el logger.

```shell
root@95aefd9aa3da:/canadian_api/data# cat log.txt
29/12/2021 01:11:53 - trace: Traceback (most recent call last):
  File "C:\Users\carviagu\Documents\GitHub\canadian_car_accidents_api\api.py", line 36, in predict
    prediction = list(model.predict(query))
  File "C:\Users\carviagu\anaconda3\envs\ML_P1\lib\site-packages\xgboost\sklearn.py", line 1284, in predict
    class_probs = super().predict(
  File "C:\Users\carviagu\anaconda3\envs\ML_P1\lib\site-packages\xgboost\sklearn.py", line 881, in predict
    predts = self.get_booster().inplace_predict(
  File "C:\Users\carviagu\anaconda3\envs\ML_P1\lib\site-packages\xgboost\core.py", line 2033, in inplace_predict
    data, _ = _ensure_np_dtype(data, data.dtype)
  File "C:\Users\carviagu\anaconda3\envs\ML_P1\lib\site-packages\xgboost\data.py", line 138, in _ensure_np_dtype
    data = data.astype(np.float32, copy=False)
ValueError: could not convert string to float: 'E'
 - input: [{'C_MNTH': '12', 'C_WDAY': '1', 'C_HOUR': '23', 'C_VEHS': 3, 'C_CONF': 'E', 'C_RCFG': '01', 'C_WTHR': '1', 'C_RSUR': '1', 'C_RALN': '1', 'C_TRAF': '05', 'C_PERS': '1'}]
```

<h2> <a name="conlusion"> 6 Conclusiones </a> </h2>

Hemos creado una API mediante Flask de un modelo de aprendizaje automático. Esta API se ha creado dentro de un contenedor
de Docker. La API devuelve tanto una predicción de mortalidad como la probabilidad de mortalidad asociada. 

Sin embargo, se pueden llevar a cabo más tareas para mejorarla:

* Gestion de errores avanzada. Se pueden gestionar mejor los errores de la API proporcionando códigos de error
  asociado y dando mayor información sobre el error al usuario.
* Incorporar un cliente. Desarollar un cliente mediante HMTL, CSS y JavaScript que permita facilitar el uso de la API, 
  proporcione una interfaz más amigable al usuario y aporte más información.
* Sistema de monitorización. Crear una interfaz de monitorización, se ha desarrollado el histórico de llamdas.
  Faltaría monitorizar el tiempo de ejecuación, coste y otros aspectos relevantes del sistema.

<h2> <a name="references"> 7 Referencias </a> </h2>

- *Dockerfile reference*. (2021, 23 diciembre). Docker Documentation. https://docs.docker.com/engine/reference/builder/

- Rajan, S. (2021, 14 octubre). *Deploying Supervised Machine Learning Model Using Flask and Docker*. Analytics Vidhya. Recuperado 3 de enero de 2022, de https://www.analyticsvidhya.com/blog/2021/10/an-end-to-end-guide-on-approaching-an-ml-problem-and-deploying-it-using-flask-and-docker/

- Sayak, P. (s. f.). *Turning Machine Learning Models into APIs with Python Flask*. DataCamp Community. Recuperado 3 de enero de 2022, de https://www.datacamp.com/community/tutorials/machine-learning-models-api-python

- Sivan, V. (2021, 20 diciembre). *Deploy your Flask REST API on Docker - Nerd For Tech*. Medium. Recuperado 3 de enero de 2022, de https://medium.com/nerd-for-tech/deploy-your-flask-rest-api-on-docker-909f5cfa8b0b

- Vasques, X. (2021a, diciembre 19). *Build and Run a Docker Container for your Machine Learning Model*. Medium. Recuperado 3 de enero de 2022, de https://towardsdatascience.com/build-and-run-a-docker-container-for-your-machine-learning-model-60209c2d7a7f

- Vasques, X. (2021b, diciembre 19). *Machine Learning Prediction in Real Time Using Docker and Python REST APIs with Flask*. Medium. Recuperado 3 de enero de 2022, de https://towardsdatascience.com/machine-learning-prediction-in-real-time-using-docker-and-python-rest-apis-with-flask-4235aa2395eb

- Viñals Guitart, C., & Serano Del Rincón, A. (2021, 20 diciembre). GitHub - carviagu/canadian_car_accidents. GitHub. https://github.com/carviagu/canadian_car_accidents 

---

<div style='text-align:center'>Elaborado por Álvaro Serrano del Rincón (<i>a.serranodelrincon@cunef.edu</i>)</div>
<div style='text-align:center'>y Carlos Viñals Guitart (<i>carlos.vinals@cunef.edu</i>)</div>
