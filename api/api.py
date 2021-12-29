# Dependencies
import sys
from flask import Flask, request, jsonify
import pickle
import traceback
import pandas as pd
import modules.preproces as pre  # Preprocess data
import modules.history as hist  # API historic
import modules.logger as log  # Log

# API definition
app = Flask(__name__)

## Funciones
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Canadian Car Accidents API</h1>
                <p>API created to predict the mortality of an accident.</p>
                <p> Use ''' + api_url + '''/help to know how to interact with the API</p>'''

@app.route('/help', methods=['GET'])
def help():
    return jsonify({
        'access': 'Use ' + api_url + '/predict to ask for a prediction, body has to include the following parameters',
        'parameters': {
            'C_MNTH': {
                'description': 'Month of the accident',
                'values': ['10', '11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09']
            },
            'C_WDAY': {
                'description': 'Day of the week',
                'values': ['1', '2', '3', '4', '5', '6', '7']
            },
            'C_HOUR': {
                'description': 'Hour',
                'values': ['20', '21', '22', '23', '00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
            },
            'C_VEHS': {
                'description': 'Number of vehicles involved'
            },
            'C_CONF': {
                'description': 'Accident type',
                'values': ['01', '02', '03', '04', '05', '06', '21', '22', '23', '24', '25', '31', '32', '33', '34', '35', '36', '41']
            },
            'C_RCFG': {
                'description': 'Road configuration',
                'values': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
            },
            'C_WTHR': {
                'description': 'Weather conditions',
                'values': ['1', '3', '2', '4', '5', '6', '7']
            },
            'C_RSUR': {
                'description': 'Road surface conditions',
                'values': ['1', '2', '3', '4', '5', '6', '7', '8', '9']
            },
            'C_RALN': {
                'description': 'Road type',
                'values': ['1', '2', '3', '4', '5', '6']
            },
            'C_TRAF': {
                'description': 'Road safety',
                'values': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18']
            }
        }
    })

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
                results.append({'prediction': str(prediction[i]), 'probability': str(pred_prob[i][0])})
            return jsonify({
                'status': 'SUCCESS',
                'results': results
            })

        except:
            # Guardamos los datos del error en el log
            code = log.log_error(traceback, json_)
            message = '''Error during data preprocessing or prediction. Check your data fits API standards. 
            Reference: ''' + code
            print('ERROR:: ' + traceback.format_exc())
            # Devolvemos el error al usuario
            return jsonify({
                'status': 'ERROR',
                'description': message
            })
    else:
        # Guardamos los datos del error en el log
        log.log_error(traceback, 'Internal Server Error. Model not loaded.')
        print('ERROR:: ' + traceback.format_exc())
        # Devolvemos el error al usuario
        return jsonify({
            'status': 'ERROR',
            'description': 'Internal Server Error'
        })

## Inicio
if __name__ == '__main__':
    try:
        port = int(sys.argv[1])  # Utilizamos el puerto indicado
    except:
        port = 5000  # Puerto por defecto 5000

    try:
        host = str(sys.argv[2]) # Utilizamos la ip indicada
    except:
        host = '127.0.0.1' # localhost

    model = pickle.load(open("model/xgb_opt_model.sav", 'rb'))  # Cargar "xgb_opt_model.sav"
    print('Model loaded')

    api_url = 'http://' + host + ':' + str(port)

    # En docker usar host:0.0.0.0
    if host == '127.0.0.1':
        app.run(port=port, debug=True)
    else:
        app.run(host=host, port=port, debug=True)
