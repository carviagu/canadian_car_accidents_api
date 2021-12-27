# Dependencies
from flask import Flask, request, jsonify
import pickle
import traceback
import pandas as pd
import numpy as np
import model_data

# API definition
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    if model:
        try:
            json_ = request.json
            print(json_)

            # Read the data
            data = pd.DataFrame(json_)

            # Preprocess the data
            query = model_data.preprocess(data)

            # Prediction
            prediction = list(model.predict(query))

            return jsonify({'prediction': str(prediction)})

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