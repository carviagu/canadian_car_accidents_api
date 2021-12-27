# Dependencies
from flask import Flask, request, jsonify
import pickle
import traceback
import pandas as pd
import modules.preproces as pre # Preprocess data
import modules.history as hist # API historic

# API definition
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Canadian Car Accidents API</h1>
                <p>API created to predict the mortality of an accident.</p>'''

@app.route('/predict', methods=['POST'])
def predict():
    if model:
        try:
            json_ = request.json
            print(json_)

            # Read the data
            data = pd.DataFrame(json_)

            # Preprocess the data
            query = pre.preprocess(data)

            # Prediction
            prediction = list(model.predict(query))
            # Prediction probability
            pred_prob = list(model.predict_proba(query))

            # Save API history
            hist.save_history(data, prediction, pred_prob)

            # Returning prediction results
            results = list()
            for i in range(len(prediction)):
                results.append({'prediction': str(prediction[i]), 'probability': str(pred_prob[i][0])})
            return jsonify(results)

        except:

            return jsonify({'trace': traceback.format_exc()})
    else:
        return ('Error during model load')



if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 12345 # If you don't provide any port the port will be set to 12345

    model = pickle.load(open("model/xgb_opt_model.sav", 'rb')) # Load "xgb_opt_model.sav"
    print ('Model loaded')

    app.run(port=port, debug=True)