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


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Canadian Car Accidents API</h1>
                <p>API created to predict the mortality of an accident.</p>'''


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
            message = '''
            Error during data preprocessing or prediction. 
            Check your data fits API standards. Reference: 
            ''' + code
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


if __name__ == '__main__':
    try:
        port = int(sys.argv[1])  # Utilizamos el puerto indicado
    except:
        port = 5000  # Puerto por defecto 12345

    model = pickle.load(open("model/xgb_opt_model.sav", 'rb'))  # Cargar "xgb_opt_model.sav"
    print('Model loaded')

    app.run(port=port, debug=True)
