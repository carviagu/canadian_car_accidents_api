# Canadian Car Accidents: API
API para utilizar el modelo de predicción de la mortalidad de un accidente, basado en el modelo creado 
en el trabajo de *Canadian Car Accidents: Modelo* (https://github.com/carviagu/canadian_car_accidents)

<br> 

---

Autores / Authors:

* Álvaro Serrano del Rincón (a.serranodelrincon@cunef.edu). Repo: https://github.com/aserincon/canadian_car_accidents
* Carlos Viñals Guitart (carlos.vinals@cunef.edu). Repo: https://github.com/carviagu/canadian_car_accidents

---
<br>
<br> 

## Descripción del repositorio

* **api.py** Script principal de la API. Aquí se encuentran los controladores de las instrucciones CRUD y las funciones principales de la misma.
* **model_data.py** Script de preprocesado de los datos. Este limpia los datos recibidos y los prepara para poser ser utilizados por el modelo en su predicción.
* **model** Directorio donde se encuentra el modelo XGBoost creado en el proyecto de modelado y que utiliza la API para realizar sus predicciones
* **reports** Informe del trabajo y creación de la API
* **data** Datos utilizados por la API en su funcionamiento.


## Instrucciones de funcionamiento de la API

### Poner en funcionamiento la API 
1. Para poner en marcha el servidor de la API:

   * Abrir una terminal de ```conda``` con el entorno correspondiente en el directorio del proyecto.
  
   * Ejecutar al siguiente instrucción:
   
```
python api.py
```

Si todo ha ido bien observaremos esto en la terminal:
```
* Serving Flask app "api" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Restarting with stat
Model loaded
 * Debugger is active!
 * Debugger PIN: 182-428-679
 * Running on http://127.0.0.1:12345/ (Press CTRL+C to quit)

```

2. Uso de la API mediante ```Postman```:

