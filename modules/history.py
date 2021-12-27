import pandas as pd
from datetime import datetime


def save_history(call = None, pred = None, prob = None):

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    dates = [dt_string] * len(call)

    temp = pd.DataFrame(data = dates, columns = ['datetime'])

    # Adding input info
    for col in call.columns:
        temp[col] = call[col].astype(str)

    predictions = list()
    proba = list()

    for i in range(len(pred)):
        predictions.append(str(pred[i]))
        proba.append(str(prob[i][0]))

    temp['res_pred'] = predictions
    temp['res_prob'] = proba

    try:
        history = pd.read_csv("./data/history.csv")
        history = pd.concat([history, temp])
    except:
        history = temp

    history.to_csv("./data/history.csv", index=False)

